
import argparse
import requests
import os
import json
import unicodedata

from datetime import datetime

def convertTeam(team):
	if team == "B0S":
		return "bos"
	team = team.lower().replace(".", "").replace(":", "")
	t = team.replace(" ", "")[:3].strip()
	if "cubs" in team:
		return "chc"
	elif t == "art":
		return "ari"
	elif t == "80s":
		return "bos"
	elif t == "cii":
		return "cin"
	elif t in ["chi", "chy", "chk", "cws", "chv"]:
		return "chw"
	elif t in ["kan", "kcr"]:
		return "kc"
	elif "dodgers" in team:
		return "lad"
	elif t == "los":
		return "laa"
	elif t == "nil":
		return "mil"
	elif t in ["nia", "mta"]:
		return "mia"
	elif t in ["nin", "win", "hin"]:
		return "min"
	elif t == "nyh":
		return "nym"
	elif t == "ny":
		return "nym"
	elif t == "nyn":
		return "nym"
	elif t == "new":
		if "yankees" in team:
			return "nyy"
		return "nym"
	elif t == "pht":
		return "phi"
	elif t == "ath" or t == "the":
		return "ath"
	elif t == "was":
		return "wsh"
	elif t == "sdp":
		return "sd"
	elif t == "sfg":
		return "sf"
	elif t == "san":
		if "padres" in team:
			return "sd"
		return "sf"
	elif t in ["tam", "tbr"]:
		return "tb"

	if t == "oak":
		return "ath"
	return t

def convertMGMMLBTeam(team):
	team = team.lower()
	if team in ["diamondbacks", "d`backs"]:
		return "ari"
	elif team == "braves":
		return "atl"
	elif team == "orioles":
		return "bal"
	elif team == "red sox":
		return "bos"
	elif team == "cubs":
		return "chc"
	elif team == "white sox":
		return "chw"
	elif team == "reds":
		return "cin"
	elif team == "guardians":
		return "cle"
	elif team == "rockies":
		return "col"
	elif team == "tigers":
		return "det"
	elif team == "astros":
		return "hou"
	elif team == "royals":
		return "kc"
	elif team == "angels":
		return "laa"
	elif team == "dodgers":
		return "lad"
	elif team == "marlins":
		return "mia"
	elif team == "brewers":
		return "mil"
	elif team == "twins":
		return "min"
	elif team == "mets":
		return "nym"
	elif team == "yankees":
		return "nyy"
	elif team == "athletics":
		return "ath"
	elif team == "phillies":
		return "phi"
	elif team == "pirates":
		return "pit"
	elif team == "padres":
		return "sd"
	elif team == "giants":
		return "sf"
	elif team == "mariners":
		return "sea"
	elif team == "cardinals":
		return "stl"
	elif team == "rays":
		return "tb"
	elif team == "rangers":
		return "tex"
	elif team == "blue jays":
		return "tor"
	elif team == "nationals":
		return "wsh"
	return team

def strip_accents(text):
	try:
		text = unicode(text, 'utf-8')
	except NameError: # unicode is a default on python 3
		pass
	text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode("utf-8")
	return str(text)

def parsePlayer(player):
	player = strip_accents(player).lower().replace(".", "").replace("'", "").replace("_", " ").replace("-", " ").replace(" jr", "").replace(" sr", "").replace(" iv", "").replace(" iii", "").replace(" ii", "")
	player = player.split(" (")[0]
	return player

def parseNFL():
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
			old = json.load(fh)

	data = {}
	dt = str(datetime.now())[:10]
	data[dt] = {}
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
		else:
			continue

		if row["Heading"].startswith("DH GM"):
			print("double", row["Heading"])
			continue

		game = row["Heading"].replace("BLUE JAYS", "TOR").split(" ")[0]
		circaGame = game
		a,h = map(str, game.split("/"))

		if prop == "f5":
			game = f"{convertMGMMLBTeam(a)} @ {convertMGMMLBTeam(h)}"
			data[dt].setdefault(game, {})
			if row["GameLine"]["VSpreadOdds"]:
				line = str(float(row["GameLine"]["VSpreadPoints"].replace("½", ".5")))
				ou = row["GameLine"]["VSpreadOdds"]+"/"+row["GameLine"]["HSpreadOdds"]
				data[dt][game]["f5_spread"] = {
					line: ou.replace("EV", "+100")
				}
			if row["GameLine"]["OverOdds"]:
				line = str(float(row["GameLine"]["OverPoints"].split(" ")[-1].replace("½", ".5")))
				ou = row["GameLine"]["OverOdds"]+"/"+row["GameLine"]["UnderOdds"]
				data[dt][game]["f5_total"] = {
					line: ou.replace("EV", "+100")
				}
			if row["GameLine"]["VOdds"]:
				ou = row["GameLine"]["VOdds"]+"/"+row["GameLine"]["HOdds"]
				data[dt][game]["f5_ml"] = ou.replace("EV", "+100")
			continue

		game = f"{convertTeam(a)} @ {convertTeam(h)}"
		player = parsePlayer(row["Heading"].split(" (")[0].split(circaGame+" ")[-1])
		data[dt].setdefault(game, {})
		data[dt][game].setdefault(prop, {})
		if prop == "hr":
			ou = f"""{row["GameLine"]["VOdds"]}/{row["GameLine"]["HOdds"]}"""
			over = ou.split("/")[0]
			data[dt][game]["hr"][player] = ou
			if movement:
				try:
					if ou != old[dt][game]["hr"][player]:
						print(game, player, old[dt][game]["hr"][player], " TO ", ou)
				except:
					pass
		elif prop in ["h", "sb", "rbi"]:
			data[dt][game][prop].setdefault(player, {})
			data[dt][game][prop][player]["0.5"] = f"""{row["GameLine"]["VOdds"]}/{row["GameLine"]["HOdds"]}"""
		else:
			data[dt][game][prop].setdefault(player, {})
			line = str(row["GameLine"]["RawTotalOver"])
			data[dt][game][prop][player][line] = f"""{row["GameLine"]["OverOdds"]}/{row["GameLine"]["UnderOdds"]}"""

	with open("circa.json", "w") as fh:
		json.dump(data, fh, indent=4)


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
	parser.add_argument("--movement", "-m", action="store_true")
	args = parser.parse_args()

	if args.nfl:
		parseNFL()
	else:
		parse(args.movement)