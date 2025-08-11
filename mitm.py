# mitmproxy -s circa_token_dump.py
from mitmproxy import http, ctx
import json, os, re, time


UPSTREAM = ("0.0.0.0", 9090)
REFERER_MATCH = "HOME"
COOKIE_SAVE_PATH = "cookie.json"
CIRCA_HOST = "ia.circasports.com"

def load(loader):
	ctx.log.info(f"[SelectiveProxy] Loaded. Using upstream {UPSTREAM} when Referer contains '{REFERER_MATCH}'")
	_ensure_cookie_file()

def _ensure_cookie_file():
	if not os.path.exists(COOKIE_SAVE_PATH):
		with open(COOKIE_SAVE_PATH, "w") as f:
			json.dump({}, f)

def _load_cookie_store():
	try:
		with open(COOKIE_SAVE_PATH, "r") as f:
			return json.load(f)
	except Exception:
		return {}

def _save_cookie_store(store: dict):
	tmp = COOKIE_SAVE_PATH + ".tmp"
	with open(tmp, "w") as f:
		json.dump(store, f, indent=2, sort_keys=True)
	os.replace(tmp, COOKIE_SAVE_PATH)

def request(flow: http.HTTPFlow):
	# Decide routing based on Referer
	referer = flow.request.headers.get("Referer") or flow.request.headers.get("referer") or ""
	#print("ref", referer)
	if ("circasports.com" in flow.request.pretty_host and REFERER_MATCH in referer):
		# Route this single request via the upstream proxy
		ctx.log.info("in here")
		try:
			flow.live.change_upstream_proxy(server=UPSTREAM)  # mitmproxy >=8
			ctx.log.info(f"[SelectiveProxy] Using upstream for {flow.request.url} (Referer matched)")
		except Exception as e:
			ctx.log.warn(f"[SelectiveProxy] change_upstream_proxy failed: {e}")
	else:
		try:
			flow.live.change_upstream_proxy(server=None)
		except:
			pass
		return

	# Save Cookie header (per host)
	cookie = flow.request.headers.get("Cookie")
	if cookie:
		host = flow.request.host
		store = _load_cookie_store()
		store.setdefault(host, {})
		store[host]["last_request_cookie"] = cookie
		store[host]["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
		_save_cookie_store(store)
		ctx.log.info(f"[SelectiveProxy] Saved Cookie for {host} ({len(cookie)} chars)")

def response(flow: http.HTTPFlow):
	# Optionally capture Set-Cookie from the response
	set_cookie = flow.response.headers.get_all("Set-Cookie")
	if set_cookie:
		host = flow.request.host
		store = _load_cookie_store()
		store.setdefault(host, {})
		store[host].setdefault("set_cookies", [])
		store[host]["set_cookies"].extend(set_cookie)
		store[host]["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
		_save_cookie_store(store)
		ctx.log.info(f"[SelectiveProxy] Captured {len(set_cookie)} Set-Cookie header(s) for {host}")