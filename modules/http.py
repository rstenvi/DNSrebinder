import BaseHTTPServer
import SocketServer
import SimpleHTTPServer
import threading
import argparse
from contextlib import contextmanager
import os, sys
import urlparse
import re
import random, string
import json
import netifaces
import logging
import cfg

# Formatting string used for creating and deleting iptable rules
iptables_format="-s %s -i %s -p tcp --destination-port %i -j DROP"

def unblock_ip(ip, interface, port):
	logging.info("Unblocking %s", ip)
	cmd="iptables -D INPUT " + iptables_format % (ip, interface, port)
	os.system(cmd)

def validIP(address):
	parts = address.split(".")
	if len(parts) != 4:
		return None
	for item in parts:
		try:
			i = int(item)
		except:
			return None
	return ".".join(parts)

def path2params(path):
	parsed = urlparse.urlparse(path)
	try:
		params = dict([p.split('=') for p in parsed[4].split('&')])
	except:
		params = {}
	return params


def revert_iptables():
	if cfg.config.get("iptables_modified", False):
		if cfg.config.get("iptables", None) != None:
			os.system("iptables-restore < " + cfg.config["iptables"])
		else:
			os.system("iptables -F INPUT")
		cfg.config["iptables_modified"] = False

class MyRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
	def do_GET(self):
		if self.path == '/clear' and self.client_address[0] == "127.0.0.1":
			cfg.dnsServer.revert_resolv()
			revert_iptables()
			self.send_response(200)

		elif self.path.startswith("/trigger"):
			client = validIP(self.client_address[0])
			try:
				host = self.headers['Host']
			except:
				logging.error("Unable to retrieve host")
				return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

			params = path2params(self.path)
			if params.get("block", "false").lower() == "true":
				port = cfg.config.get("args", {}).get("port", 80)
				cmd="iptables -I INPUT 1 " + iptables_format % (client, cfg.config["args"]["interface"], port)
				logging.debug("Running command: %s", cmd)
				os.system(cmd)
				os.system("iptables -L -n")
				cfg.config["iptables_modified"] = True
				if params.get("time") != None:
					try:
						wait = int(params["time"])
					except:
						logging.error("Cannot convert parameter to int: %s", params.get("time"))
						wait = None
					if wait != None:
						call = threading.Timer(wait, unblock_ip, (client, cfg.config["args"]["interface"], port, ))
						call.start()

			logging.debug("Trigger on domain: %s", host)
			cfg.dnsServer.trigger_change_domain(host.split(":")[0])
			self.send_response(200)
		
		elif self.path.startswith("/rebind"):
			try:
				host = self.headers["Host"]
			except:
				host = "error"
			self.send_response(200)
			self.end_headers()
			self.wfile.write("OK")

		elif self.path.startswith("/redirect"): 
			parsed = urlparse.urlparse(self.path)
			try:
				params = dict([p.split('=') for p in parsed[4].split('&')])
			except:
				params = {}

			# Try and get subdomain (in order):
			# 1. From parameter in URL
			# 2. From config
			# 3. "a"
			sub = params.get("sub", cfg.config.get("default_subdomain", "a"))
		
			# We remove all special characters and convert to lowercase
			sub = ''.join(e for e in sub if e.isalnum()).lower()

			r = ''.join(random.choice(string.ascii_lowercase) for _ in range(12))
			self.send_response(302)

			# Browser should not cache response
			self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
			self.send_header("Pragma", "no-cache")
			self.send_header("Expires", "0")

			# Send location header
			try:
				self.send_header("Location","http://" + r + "." + sub + "." + cfg.config["args"]["root"] + cfg.config.get("redirect_path", "/"))
			except:
				logging.warning("Unable to set location header")
			self.end_headers()
		
		elif self.path.startswith("/finished"): 
			parsed = urlparse.urlparse(self.path)
			try:
				params = dict([p.split('=') for p in parsed[4].split('&')])
			except:
				params = {}

			logging.info("%s: %s", self.client_address[0], params)
			self.send_response(200)
			self.end_headers()
			self.wfile.write('{"status":"OK"}\n');

		# No custom event, we should just serve files
		else:
			host = self.headers["Host"]
			served = False
			for s in cfg.config.get("hosts", []):
				f = s.get("domain")
				if f != None and host.endswith(f):
					with cd(s.get("path", ".")):
						if os.path.isdir(p):
							self.send_response(403)
							self.end_headers()
						else:
							SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
						served = True

			# We have no custom code to deal with it, we don't allow listing of
			# files, but any file can be served
			if served == False:
				p = SimpleHTTPServer.SimpleHTTPRequestHandler.translate_path(self, self.path)
				if os.path.isdir(p):
					self.send_response(403)
					self.end_headers()
				else:
					return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

	# Override log_message so that we can print to file as well
	def log_message(self, format, *args):
		logging.info("%s : %s", self.client_address[0], format%args)


class ThreadedHTTPServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
	"""Handle requests in a separate thread."""

@contextmanager
def cd(newdir):
	prevdir = os.getcwd()
	os.chdir(os.path.expanduser(newdir))
	try:
		yield
	finally:
		os.chdir(prevdir)

def serve(d, ip, port):
	# Have not found a good way to suppress "server"-header, but we can change it
	SimpleHTTPServer.SimpleHTTPRequestHandler.server_version = "Apache"
	BaseHTTPServer.BaseHTTPRequestHandler.sys_version = "3.2.1"
	
	Handler = MyRequestHandler
	SocketServer.TCPServer.allow_reuse_address = True
	httpd = ThreadedHTTPServer((ip, port), Handler)

	try:
		with cd(d):
			logging.info("Starting web server at %s:%i", ip, port)
			httpd.serve_forever()
	except:
		pass
	finally:
		logging.info("Closing web server")
		httpd.server_close()
		revert_iptables()
		if cfg.config.get("args", {}).get("firewall") != None:
			os.remove(args.get("firewall"))
		raise

	return


