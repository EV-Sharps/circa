
import argparse,requests,os,json,unicodedata
from datetime import datetime

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

def convertNFL(team):
	team = team.lower()
	ts = {
		"cowboys": "dal",
		"chiefs": "kc",
		"chargers": "lac",
		"eagles": "phi",
		"steelers": "pit",
		"jets": "nyj",
		"dolphins": "mia",
		"colts": "ind",
		"panthers": "car",
		"jaguars": "jax",
		"giants": "sf",
		"commanders": "wsh",
		"bengals": "cin",
		"browns": "cle",
		"raiders": "lv",
		"patriots": "ne",
		"cardinals": "stl",
		"saints": "no",
		"bucs": "tb",
		"falcons": "atl",
		"titans": "ten",
		"broncos": "den",
		"49ers": "sf",
		"seahawks": "sea",
		"lions": "det",
		"packers": "gb",
		"texans": "tex",
		"rams": "lar",
		"ravens": "bal",
		"bills": "buf",
		"vikings": "min",
		"bears": "chi"
	}
	return ts.get(team, team)