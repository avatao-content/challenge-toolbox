var page = require('webpage').create();
var fs = require('fs');
var path = '/opt/result.txt';

var host = "localhost:8888";
var url = "http://"+host+"/guestbook.php";
var timeout = 2000;

page.onAlert = function(alertText){
    fs.write(path, "XSS FOUND", 'w');
    phantom.exit();
};
 
page.settings.resourceTimeout = timeout;
page.onResourceTimeout = function(e) {
    console.log("Error timeout")
};
 
page.open(url, function(status) {
    console.log("[INFO] rendered page");
    setTimeout(function(){
        phantom.exit();
    }, 100);
});
