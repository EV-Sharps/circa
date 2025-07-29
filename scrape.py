
import requests
import os
import json

def parse():
	with open("response") as fh:
		response = json.load(fh)

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
	callAPI()