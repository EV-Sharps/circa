
from shared import *

def downloadResponse(cookie, sport):
	#cookie = "_ga_1PZGDRY6F5=GS2.1.s1754837516$o4$g1$t1754837523$j53$l0$h0; ASP.NET_SessionId=aek1zwfztdsk1kbeofvyqntr; KeepBets=false; gDetails=%5B%5D; lDetails=%5B%5D; _ga=GA1.1.2076399515.1754779621; GvcSessionKey=aek1zwfztdsk1kbeofvyqntr; NativeApp=true; NativeAppKey=true"
	ref = "https://ia.circasports.com/Web-CIRCAIOWA/sports/sportsoddssummary?sportName=pro%20baseball&sportId=23&leagueId=1138&leagueName=MLB%20-%20PLAYER%20TO%20HIT%20A%20HOME%20RUN"
	leagueIds = "5,548,618,532,620,554,1124,1138,1930,1125,1928,1139,1935,1792,1275,1241"
	if sport == "futures":
		ref = "https://ia.circasports.com/Web-CIRCAIOWA/sports/sportsoddssummary?sportName=pro%20fb&sportId=11&leagueId=1982&leagueName=NFL%20-%20TOTAL%20REG%20SEASON%20PASSING%20YARDS"
		leagueIds = "567,568,2159,571,713,1338,580,613,581,2213,612,690,324,1086,1781,1088,1786,1948,1126,2238,1776,1777,1778,1780,1982,1983,1984,2240,2241,1142,1403,1094,1498,1784,1785,1779,18,1968"
	elif sport == "nfl":
		ref = "https://ia.circasports.com/Web-CIRCAIOWA/sports/sportsoddssummary?sportName=pro%20fb&sportId=11&leagueId=568&leagueName=NFL"
		leagueIds = "568,2159,571,713,1338,580,613,581,2213,612,690,324,1086,1781,1088,1786,1948,1126,2238,1776,1777,1778,1780,1982,1983,1984,2240,2241,1142,1403,1094,1498,1784,1785,1779,18,1968"
	elif sport == "ncaaf":
		ref = "https://ia.circasports.com/Web-CIRCAIOWA/sports/sportsoddssummary?sportName=ncaa%20fb&sportId=all&leagueId=574&leagueName=NCAA%20FB"
		leagueIds = "574,575,1297,1058,1059,349,1369,1749,977,1005,1007,1006,1789"


	command = """curl 'https://ia.circasports.com/MobileService//api/sports/getLeagueGamesAnon' \
-X POST \
-H 'Host: ia.circasports.com' \
-H 'Accept: application/json, text/plain, */*' \
-H 'Sec-Fetch-Site: same-origin' \
-H 'Accept-Language: en-US,en;q=0.9' \
-H 'Sec-Fetch-Mode: cors' \
-H 'Origin: https://ia.circasports.com' \
-H 'User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148' \
-H 'Referer: """+ref+"""' \
-H 'Connection: keep-alive' \
-H 'Sec-Fetch-Dest: empty' \
-H 'Content-Type: application/json' \
--cookie '"""+cookie+"""' \
--data-raw '{"LeagueId":0,"LeagueIds":\""""+leagueIds+"""\","LineTypeId":1,"OddsFormat":"moneyline"}' \
--proxy http://localhost:9090 \
-o response.json
"""

	os.system(command)

def parseSport(sport):

	#with open(f"{sport}_response.json") as fh:
	with open("response.json") as fh:
		response = json.load(fh)

	#with open(f"{sport}_response.json", "w") as fh:
	#	json.dump(response, fh, indent=4)

	data = {}
	for row in response["Games"]:
		a,h = row["VTeam"], row["HTeam"]
		if sport == "nfl":
			game = f"{convertNFL(a)} @ {convertNFL(h)}"
		else:
			game = f"{a} @ {h}".lower()

		if not row["GameLine"]:
			continue
		if sport == "nfl" and not row.get("Heading", "").startswith("NFL WEEK"):
			continue
		elif sport == "ncaaf" and row["LeagueName"] != "NCAA FB":
			continue

		data.setdefault(game, {})
		if row["GameLine"]["VSpreadPoints"]:
			line = str(float(row["GameLine"]["VSpreadPoints"].replace("½", ".5")))
			ou = row["GameLine"]["VSpreadOdds"]+"/"+row["GameLine"]["HSpreadOdds"]
			if ou == "/":
				ou = ""
			data[game]["spread"] = {
				line: ou.replace("EV", "+100")
			}
		if row["GameLine"]["OverPoints"]:
			line = str(float(row["GameLine"]["OverPoints"].split(" ")[-1].replace("½", ".5")))
			ou = row["GameLine"]["OverOdds"]+"/"+row["GameLine"]["UnderOdds"]
			if ou == "/":
				ou = ""
			data[game]["total"] = {
				line: ou.replace("EV", "+100")
			}
		if row["GameLine"]["VOdds"]:
			ou = row["GameLine"]["VOdds"]+"/"+row["GameLine"]["HOdds"]
			data[game]["ml"] = ou.replace("EV", "+100")

	with open(f"{sport}.json", "w") as fh:
		json.dump({"updated": datetime.now().isoformat(), "data": data}, fh, indent=4)


def parseFutures():
	with open("response.json") as fh:
		response = json.load(fh)

	data = {}
	dt = datetime.now().isoformat()
	for row in response["Games"]:
		prop = ""
		if row["LeagueName"].startswith("NFL - TOTAL REG SEASON"):
			prop = " ".join(row["LeagueName"].lower().split(" ")[-2:])\
				.replace("yards", "yd")\
				.replace("passing", "pass")\
				.replace("receiving", "rec")\
				.replace("rushing", "rush")\
				.replace(" ", "_")
		else:
			continue

		player = parsePlayer(row["Heading"].split(" (")[0])
		line = str(row["GameLine"]["RawTotalOver"])

		data.setdefault(prop, {})
		data[prop].setdefault(player, {})
		data[prop][player].setdefault(line, {})
		data[prop][player][line] = f"""{row["GameLine"]["RawOverOdds"]}/{row["GameLine"]["RawUnderOdds"]}"""

	with open("futures.json", "w") as fh:
		json.dump(data, fh, indent=4)

def parse(movement):
	with open("response.json") as fh:
		response = json.load(fh)

	old = {}
	if movement:
		with open("circa.json") as fh:
			old = json.load(fh).get("data", {})
		with open("movement.json") as fh:
			move_data = json.load(fh)

	data = {}
	dt = str(datetime.now())[:10]
	print("")
	print(datetime.now().isoformat())
	print("")
	for row in response["Games"]:
		prop = ""
		if row["LeagueName"] == "MLB - PLAYER TO HIT A HOME RUN":
			prop = "hr"
		elif row["LeagueName"] == "MLB - PITCHING PROPS":
			prop = "k"
		elif row["LeagueName"] == "MLB - PLAYER TO STEAL A BASE":
			prop = "sb"
		elif row["LeagueName"] == "MLB - PLAYER TOTAL BASES":
			prop = "tb"
		elif row["LeagueName"] == "MLB - PLAYER TO RECORD A HIT":
			prop = "h"
		elif row["LeagueName"] == "MLB - PLAYER TO RECORD RBI":
			prop = "rbi"
		elif row["LeagueName"] == "MLB - 1ST 5 INNINGS":
			prop = "f5"
		elif row["LeagueName"] == "MLB - 1ST INNING RUN YES/NO":
			prop = "rfi"
		else:
			continue

		if row["Heading"].startswith("DH G"):
			print("double", row["Heading"])
			continue

		game = row["Heading"].replace("WHITE SOX", "CHW").replace("BLUE JAYS", "TOR").replace("RED SOX", "BOS").split(" ")[0]
		circaGame = game
		a,h = map(str, game.split("/"))

		if prop == "f5":
			game = f"{convertMGMMLBTeam(a)} @ {convertMGMMLBTeam(h)}"
			data.setdefault(game, {})
			if row["GameLine"]["VSpreadOdds"]:
				line = str(float(row["GameLine"]["VSpreadPoints"].replace("½", ".5")))
				ou = row["GameLine"]["VSpreadOdds"]+"/"+row["GameLine"]["HSpreadOdds"]
				data[game]["f5_spread"] = {
					line: ou.replace("EV", "+100")
				}
			if row["GameLine"]["OverOdds"]:
				line = str(float(row["GameLine"]["OverPoints"].split(" ")[-1].replace("½", ".5")))
				ou = row["GameLine"]["OverOdds"]+"/"+row["GameLine"]["UnderOdds"]
				data[game]["f5_total"] = {
					line: ou.replace("EV", "+100")
				}
			if row["GameLine"]["VOdds"]:
				ou = row["GameLine"]["VOdds"]+"/"+row["GameLine"]["HOdds"]
				data[game]["f5_ml"] = ou.replace("EV", "+100")
			continue

		game = f"{convertTeam(a)} @ {convertTeam(h)}"
		player = parsePlayer(row["Heading"].split(" (")[0].split(circaGame+" ")[-1])
		if "gm2" in player:
			game = f"{convertTeam(a)}-gm2 @ {convertTeam(h)}-gm2"
		player = player.replace("dh gm1 ", "").replace("dh gm2 ", "")
		data.setdefault(game, {})
		data[game].setdefault(prop, {})
		if prop == "rfi":
			game = f"{convertMGMMLBTeam(a)} @ {convertMGMMLBTeam(h)}"
			data[game]["rfi"] = f"""{row["GameLine"]["VOdds"]}/{row["GameLine"]["HOdds"]}""".replace("EV", "+100")
		elif prop == "hr":
			ou = f"""{row["GameLine"]["VOdds"]}/{row["GameLine"]["HOdds"]}"""
			data[game]["hr"][player] = ou
			if movement:
				try:
					if game not in old or player not in old[game].get("hr", {}):
						move_data.append({
							"game": game,
							"player": player,
							"ou": ou,
							"from": "",
							"dt": datetime.now().isoformat()
						})
						print("adding", game, player, ou)
					elif ou != old[game]["hr"][player]:
						print(game, player, old[game]["hr"][player], " TO ", ou)
						move_data.append({
							"game": game,
							"player": player,
							"ou": ou,
							"from": old[game]["hr"][player],
							"dt": datetime.now().isoformat()
						})
				except:
					pass
		elif prop in ["h", "sb", "rbi"]:
			data[game][prop].setdefault(player, {})
			data[game][prop][player]["0.5"] = f"""{row["GameLine"]["VOdds"]}/{row["GameLine"]["HOdds"]}"""
		else:
			data[game][prop].setdefault(player, {})
			line = str(row["GameLine"]["RawTotalOver"])
			ou = f"""{row["GameLine"]["OverOdds"]}/{row["GameLine"]["UnderOdds"]}"""
			data[game][prop][player][line] = ou.replace("EV", "+100")

	for game, gData in old.items():
		if game not in data:
			data[game] = gData

	print("")
	with open("circa.json", "w") as fh:
		json.dump({"updated": datetime.now().isoformat(), "data": data}, fh, indent=4)

	if movement:
		with open("movement.json", "w") as fh:
			json.dump(move_data, fh, indent=4)


def callAPI():
	url = "https://ia.circasports.com/MobileService//api/sports/getLeagueGamesAnon"

	headers = {
		"Host": "ia.circasports.com",
		"Accept": "application/json, text/plain, */*",
		"Sec-Fetch-Site": "same-origin",
		"Accept-Language": "en-US,en;q=0.9",
		"Sec-Fetch-Mode": "cors",
		"Origin": "https://ia.circasports.com",
		"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
		"Referer": "https://ia.circasports.com/Web-CIRCAIOWA/sports/sportsoddssummary?sportName=pro%20baseball&sportId=23&leagueId=1138&leagueName=MLB%20-%20PLAYER%20TO%20HIT%20A%20HOME%20RUN",
		"Connection": "keep-alive",
		"Sec-Fetch-Dest": "empty",
		"Content-Type": "application/json",
	}

	cookies = {
		"_ga_1PZGDRY6F5": "GS2.1.s1753804426$o1$g1$t1753804446$j40$l0$h0",
		"ASP.NET_SessionId": "l2ajou5kvipbfec5fwxi1bg1",
		"KeepBets": "false",
		"gDetails": "[]",
		"lDetails": "[]",
		"_ga": "GA1.1.656371136.1753804427",
		"GvcSessionKey": "l2ajou5kvipbfec5fwxi1bg1",
		"NativeApp": "true",
		"NativeAppKey": "true",
		"registration": "no"
	}

	payload = {
		"LeagueId": 0,
		"LeagueIds": "5,548,618,532,620,554,1124,1138,1930,1125,1928,1139,1935,1792,1275,1241",
		"LineTypeId": 1,
		"OddsFormat": "moneyline"
	}

	proxies = {
		"http": "http://localhost:9090",
		"https": "http://localhost:9090",
	}

	response = requests.post(url, headers=headers, cookies=cookies, json=payload, proxies=proxies)

	print(response.status_code)
	print(response.text)

	with open("response", "w") as fh:
		fh.write(response.text)


if __name__ == "__main__":
	#callAPI()
	parser = argparse.ArgumentParser()
	parser.add_argument("--nfl", action="store_true")
	parser.add_argument("--ncaab", action="store_true")
	parser.add_argument("--ncaaf", action="store_true")
	parser.add_argument("--futures", action="store_true")
	parser.add_argument("--movement", "-m", action="store_true")
	parser.add_argument("--cookie", "-c")
	args = parser.parse_args()

	sport = "mlb"
	if args.nfl:
		sport = "nfl"
	elif args.ncaaf:
		sport = "ncaaf"
	elif args.futures:
		sport = "futures"

	if args.cookie:
		downloadResponse(args.cookie, sport)
	

	if sport in ["nfl", "ncaaf"]:
		parseSport(sport)
	elif sport == "futures":
		parseFutures()
	else:
		parse(args.movement)		




