import sys, socket
import dnslib
#from pprint import pprint
from copy import deepcopy
import re
import logging

class DNSServer:
	def __init__(self):
		self.port = 53

		self.ttl = 5
		self.resolve = {}
		self.resolv_orig = {}

		self.wildcard = []

	def add_wildcard(self, domain, ip, alt):
		self.wildcard.append({"domain": domain, "ip": ip, "alt":alt})

	def add_resolve(self, domain, ip, alt):
		self.resolve[domain] = {"ip":ip, "alt":alt}
		self.resolv_orig[domain] = {"ip":ip, "alt":alt}

	def trigger_change_domain(self, domain):
		if self.resolve[domain].get("alt", None) != None:
			self.resolve[domain]["ip"] = self.resolve[domain]["alt"]
		

	def trigger_change(self):
		for key in self.resolve:
			self.trigger_change_domain(key)

	def change_resolve(self, domain, toip):
		self.resolve[domain] = {"ip": toip, "alt":None}

	# Restore original
	def revert_resolv(self):
		self.resolve = deepcopy(self.resolv_orig)

	def find_wildcard(self, qname):
		ret = None
		for w in self.wildcard:
			a = re.match(w.get("domain", ""), qname)
			if a:
				self.resolve[qname] = {"ip":w.get("ip"), "alt":w.get("alt")}
				ret = w.get("ip")
				break
		return ret

	def domain2ip(self, qdomain, ips):
		ans = []
		if type(ips) == list:
			for ip in ips:
				ans.append( {
					qdomain : dnslib.RR(
						qdomain,
						rdata=dnslib.A(ip),
						ttl=self.ttl
					)
				})
		elif type(ips) == str:
			ans.append( {
				qdomain : dnslib.RR(
					qdomain,
					rdata=dnslib.A(ips),
					ttl=self.ttl
				)
			})

		return ans

	def find_answers(self, d, client):
		ans = []

		for i in range(0, len(d.questions)):
			qstr = str(d.questions[i].get_qname()).lower()
			logging.info("DNS from %s query: %s", client, qstr)

			if qstr[:-1] in self.resolve:
				ans = self.domain2ip(qstr[:-1], self.resolve[qstr[:-1]].get("ip"))
			else:
				ret = self.find_wildcard(qstr[:-1])
				ans = self.domain2ip(qstr[:-1], ret)
		return (d, ans)


	def answer(self, data, client):
		try:
			d = dnslib.DNSRecord.parse(data)
		except:
			logging.warning("Unable to parse DNS packet from: %s", client)
			return None

		(d, ans) = self.find_answers(d, client)
		
		ret = d.reply()
		for a in ans:
			for key, value in a.items():
				ret.add_answer(value)

		return ret.pack()



def udpServer(ip, port, dns):
	logging.info("Starting DNS server at %s:%i", ip, port)
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	server_address = (ip, port)

	sock.bind(server_address)
	while True:
		try:
			data, client = sock.recvfrom(4096)
		except:
			logging.info("Closing the connection")
			sock.close()
			break
		if data:
#			logging.info("DNS query from: %s", client[0])
			data = dns.answer(data, client[0])
			if data != None:
				sock.sendto(data, client)


