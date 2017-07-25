from copy import deepcopy

config = {}
dnsServer = None

def init(c, d):
	global config
	global dnsServer
	config = deepcopy(c)
	dnsServer = d
