
<?php
if (!isset($_SERVER["HTTP_HOST"])) {
  parse_str($argv[1], $_GET);
  parse_str($argv[1], $_POST);
}

if($_POST["type"]==1){
	//Add Flow
	$command = escapeshellcmd('/var/www/html/SENSS/add_flow.py');
	$output = shell_exec($command);
	echo $output;
}
if($_POST["type"]==2){
	//Filter Flow
	$command = escapeshellcmd('/var/www/html/SENSS/filter_flow.py');
	$output = shell_exec($command);
	echo $output;
}

if($_POST["type"]==3){
	//Request Stats
	$command = escapeshellcmd('/var/www/html/SENSS/request_flow_stats.py');
	$output = shell_exec($command);
	echo $output;
}

if($_POST["type"]==4){
	//Request Stats
	$command = escapeshellcmd('/var/www/html/SENSS/get_routes.py munich 165.0.0.0');
	$output = shell_exec($command);
	echo $output;
}

if($_POST["type"]==5){
	//Change Routes

	$request=$_POST["request"];
	$r=base64_encode($request);
	$command = escapeshellcmd('/var/www/html/SENSS/change_routes.py '.$r);
	$output = shell_exec($command);
	echo $output;

}

?>
