# DNSRebinder

Tool for performing DNS rebinding attacks. 

## DNS server (dns.py)

Simple DNS server that only resolves domain names specified in config-file. All
other DNS requests simply return an empty response. The DNS-server also supports
wildcard-domains where all other subdomains of a domain return the same IP.

## HTTP server (http.py)

The HTTP-server is used for two things:

1. Serve static files
1. Implement API endpoints that can be used to support a DNS rebinding attack.

### API endpoints

1. `/clear` - Will revert back to settings when program was started. This API is
only available from 127.0.0.1. Since hostname is ignored, you can use:
`curl -i http://127.0.0.1/clear`
1. `/trigger?block=true|false&time=<int>` - Make DNS change and alternatively block access
from client IP address to web server. Default value for block if nothing is
specified is false. Time-parameter is only evaluated is block=true, if
specified, the IP address will be unblocked in the given number of seconds.
1. `/rebind` - An endpoint that returns `{"host":"<hostname>"}`. Used to check which
server JavaScript is communicating with
1. `/redirect?sub=<string>` - Redirect to a random subdomain with this format:
<random string>.<sub>.<root domain name>
1. `/finished?name1=value1,...,nameN=valueN` - Used to indicate that DNS rebinding
has finished. The values included will be printed along with the client's IP
address.

### IPtables

If you plan to use the API /trigger?block=true, you should verify that it doen't
cause any problems with you current firewall setup. Below are some notes:

1. When blocking a client a new rule is added to the top of the input chain
1. When calling /clear from localhost or exiting the program, iptables -F INPUT
is called, exception below:
	1. If the paramater --firewall /path/to/file is added, the program will take a
	backup of iptables in the beginning and restore this instead of flushing
	1. If iptables has remained unmodified during the program, rules will not be
	flushed.



## Config file

Below is an example of a config file with comments describing what the options
are used for. NB! In the JSON-file passed to the program, comments are not
supported.

~~~
{
// Path to use when calling HTTP endpoint /redirect. If not specified, "/" is
// used. Specifying this is mostly useful if you want to prevent crawling of
// your site. The web server does not allow directory listing, the attacker
// therefore has to know the appropriate links.
"redirect_path":"/",

// When calling HTTP endpoint /redirect, what should the default subdomain be.
// If not specified, 'a' is used.
"default_subdomain":"a",

// List of domains that should be translated. This is most useful for
// standard DNS behavior (expected behaviour for an authoritative DNS server).
"domains": [
 {"domain":"example.com", "ip":"1.2.3.4"},
 {"domain":"www.example.com", "ip":"1.2.3.4"},

 // Same as above, but regex is used to specify a number of sudomains. This
 // should be used in conjunction with HTTP endpoint /redirect. The subdomain
 // used there should match the 'a' and 'b' below. The second example shows that
 // you can use multiple A-records for 1 DNS name.
 // "alt" is the IP address that should when rebinding the IP address.
 {"wildcard":"[a-zA-Z0-9]+\\.a\\.example\\.com", "ip":"1.2.3.4", "alt":"192.168.0.1"},
 {"wildcard":"[a-zA-Z0-9]+\\.b\\.example\\.com", "ip":["1.2.3.4", "192.168.0.1], "alt":"192.168.0.1"},
],

// This is used to host different directories when a specific hostname is used.
// This is normally not needed, but could be useful in some cases. NB! you also
// have to specify DNS entry above.
// Two notes:
// 1. The domain match is first-match and it includes everything that ends with
// the string below.
// 2. If the path is a local path, it is based from the root path given to the
// web server on the command line
"hosts":[
 {"domain":"www.example.com", "path":"example"}
]
}
~~~


## Browser Test

A test of different browsers and how they implemented protections against DNS
rebinding was performed in July 2017. The result of the test can be found
[here](https://rstenvi.github.io/dnsrebinder/) while the code can be found
[here](browsertest/).

If you want to run the test yourself, you have to replace the domain name in the
[config file](browsertest/config.json). The remaining code should work without
any modifications.

The command to run the test-server from this directory would be similar to this:

~~~
sudo python DNSRebinder.py -d browsertest/www/ -c browsertest/config.json -r example.com -I eth0
~~~
