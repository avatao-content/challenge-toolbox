<?php
require_once 'db.php';

error_reporting(E_ALL);
ini_set('display_errors', 1);

if (isset($_GET['id']) && !empty($_GET['id']) ) {
        $db     = new SQLite3(DB_PATH);
        $result = $db->query('SELECT * FROM products WHERE id = "' . $_GET['id'] . '"');
        $product   = $result->fetchArray(SQLITE3_ASSOC);
        $db->close();
        
        if (isset($product['id']) && !empty($product['id'])) {
            print("<html>ID: " . $product['id'] . "<br>");
            print("NAME: " . $product['name'] . "<br>");
            print("PRICE: " . $product['price'] . "</html>");
            die();
        } else {
            print("Invalid product ID");	
	}
    }
    
    

else {

    print("Usage: /products.php?id=1");
    
   
}
?>

