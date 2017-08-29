var page = require('webpage').create();
var system = require('system');
var fs = require('fs');
var path = '/opt/result.txt';

var host = "localhost:8888";
var url = "http://"+host+system.args[1];
var timeout = 2000;

console.log(url)

page.onAlert = function(alertText){
    fs.write(path, "XSS FOUND", 'w');
};
 
page.settings.resourceTimeout = timeout;
page.onResourceTimeout = function(e) {
    setTimeout(function(){
        console.log("Error timeout")
        phantom.exit();
    }, 1);
};
 
page.open(url, function(status) {
    console.log("[INFO] rendered page");
    setTimeout(function(){
        phantom.exit();
    }, 1);
});
