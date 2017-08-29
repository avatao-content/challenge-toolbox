#### Please use this template for creating reflected or stored XSS challenges!

First create a web application with a Cross-Site Scripting vulnerability in `/solvable/` (*you can use various baseimages*)

**CHECKING STORED XSS**
  1. Edit the **URL** variable in `/controller/opt/server.py` (*please use relative URL*) - this will be visited by PhantomJS
  2. Adjust the `/%s/test` endpoint (***URL** and **INJECT_ARGS***)

**CHECKING REFLECTED XSS**

  1. Set `enable_flag_input` to **true** in `config.yml` (*PhantomJS will visit the submitted URL*)
  2. Adjust the `/%s/test` endpoint (*remove the payload injection part and set **URL** to the solution URL*)

**Bonus info:** The domain / IP of the submitted URL doesn't matter - only the path and query (`/asd.php?a=abc&b=123`)
 
**GENERAL INSTRUCTIONS**

 * If there are external resources on the visited page PhantomJS will freeze while loading them (*because the internet access is disabled in the running container*). It's not a problem, the subprocess is killed after **3 seconds**, however using CDNs (*e.g. `<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">`*) instead of including **CSS** and **JS** files in the solvable may ruin your challenge (*even if it works locally*).

**Bonus tip:** Warn users in your description (*"`IMPORTANT:`**Please do not use external links in your payload, otherwise your solution will be rejected!**"*).
 * `/opt/phantomjs25` is [currently in beta](https://groups.google.com/forum/#!msg/phantomjs/AefOuwkgBh0/BsUiXD21DgAJ) - we recommend using it. You can also use the [official, stable release](http://phantomjs.org/download.html) if you want (`/opt/phantomjs21`), but it won't recognize newer javascript functions (*e.g. [ParentNode.append()](https://developer.mozilla.org/en-US/docs/Web/API/ParentNode/append)*).
 * `/opt/check.js` is perfect for finding alert boxes, however you can extend its logic if you need to do more complicated stuff!
