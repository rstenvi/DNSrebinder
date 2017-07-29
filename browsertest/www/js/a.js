
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
	var l = window.location.toString();
	var p = window.location.pathname.toString();

	// Handle case where "/" is the path
	if(p != "/")    {var s = l.search(p);}
	else    {s = l.length-1;}

	return l.substring(0,s);
}

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


