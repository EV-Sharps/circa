
function FindProxyForURL(url, host) {
	// Your Mac (mitmproxy) host/port:
	  var PROXY = "PROXY 10.0.0.253:9090";  // change to your listen port/IP
	  var DIRECT = "DIRECT";

	  // Common local bypasses
	  if (isPlainHostName(host) ||
	      shExpMatch(host, "localhost") ||
	      isInNet(host, "10.0.0.0", "255.255.255.0") ||
	      isInNet(host, "192.168.0.0", "255.255.0.0") ||
	      isInNet(host, "172.16.0.0", "255.240.0.0")) {
	    return DIRECT;
	  }

	  // Only proxy these domains (edit as needed)
	  if (dnsDomainIs(host, "circasports.com")) {
	    return DIRECT;
	  }

	  // Example: match by URL path if useful (NOT Referer)
	  // if (shExpMatch(url, "*://*/sportsbook/*")) { return PROXY; }

	  // Everything else goes direct
	  return DIRECT;
}