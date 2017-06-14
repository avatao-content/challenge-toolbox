<!DOCTYPE html>
<html lang="en">
<head>
  <title>Alert Me If You Can Inc.</title>
  <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" type="text/css" href="css/bootstrap.min.css">
  <link rel="stylesheet" type="text/css" href="style.css">
</head>
<body>

<nav class="navbar navbar-inverse">
  <div class="container-fluid">
    <div class="navbar-header">
      <a class="navbar-brand" href="/index.php"><span class="glyphicon glyphicon-home" style="padding-right:10px;"></span>Home</a>
    </div>
  </div>
</nav>

<div class="container-fluid">
  <div class="row content">
    <div class="col-sm-2 sidenav" style="padding-top:20px; text-align: center;">
      <h4>Alert Me If You Can</h4>
      <ul class="nav nav-pills nav-stacked">
        <li><a href="/index.php">Home</a></li>
        <li class="active"><a href="/guestbook.php">Guestbook</a></li>
      </ul><br>
    </div>

    <div class="col-sm-8">
      <div class="col-sm-8" style="padding-top:20px;">
          <form method="post" name="guestform" action="action.php">
          <table class="table" width="550" border="0" cellpadding="2" cellspacing="1">
          <tr>
          <td><input name="name" class="form-control" placeholder="Name" autofocus="true" type="text" size="30" maxlength="10"></td>
          </tr>
          <tr>
          <td><textarea name="message" class="form-control" placeholder="Enter message here" cols="50" rows="3" maxlength="500"></textarea></td>
          </tr>
          <tr>
          <td style="text-align: center;"><input name="btnSign" type="submit" class="btn btn-lg btn-primary" value="Sign Guestbook"></td>
          </tr>
          </table>
          </form>       
      </div>
      <div class="row col-sm-12 col-sm-offset-2">
        <?php
            $db = new SQLite3('/db/database.sqlite3');

            // Create connection
            $results = $db->query('SELECT * FROM guestbook');
            $exists = FALSE;

            // output data of each row
            while($row = $results->fetchArray()) {
                $exists = TRUE;
                echo '<div class="col-sm-10">';
                echo "<h4><small>Name: </small>" . $row["name"]. "</h4><p>" 
                 . "<h4><small>Message: </small>" . $row["message"]. "</h4></p>";
                echo '</div>';
            }
            if($exists != TRUE){
                echo '<div class="col-sm-10">';
                echo "<h4>No messages yet.</h4>";
                echo '</div>';
            }
          ?>
      </div>
    </div>
  </div>
</div> 

<footer class="container-fluid">
  <p>Welcome to Alert Me If You Can! This is a place to learn new technologies in a safe and secure way. Website created by Péter Fejér.</p>
</footer>

</body>
</html>
