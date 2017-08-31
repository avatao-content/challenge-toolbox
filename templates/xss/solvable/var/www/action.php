<?php

if( isset( $_POST[ 'name' ] ) && isset( $_POST[ 'message' ] ) ) {

	// Update database
        $db = new SQLite3('/db/database.sqlite3');

	$message = trim( $_POST[ 'message' ] );
	// Replacing HTML tags with empty string
	while (preg_match('/<[^>]*>/', $message)){
		$message = preg_replace('/<[^>]*>/', '', $message);
	}
	$name    = trim( $_POST[ 'name' ] );
	// Replacing HTML tags with empty string
	while (preg_match('/<[^>]*>/', $name)){
		$name = preg_replace('/<[^>]*>/', '', $name);
	}

	$message = stripslashes( $message );
	$message = SQLite3::escapeString( $message );

	$name = SQLite3::escapeString( $name );
	if (!empty($name) || !empty($message)) {
                $db->query("INSERT INTO guestbook(name, message) VALUES ('$name','$message')");
                $db->close();
	}
	else {
		header("Location: /guestbook.php");
	}
}

header("Location: /guestbook.php");
exit;
?>
