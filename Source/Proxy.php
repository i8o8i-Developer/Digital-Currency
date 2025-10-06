<?php
// Simple PHP Proxy To Call The Python API If You Prefer PHP To Make Requests From The Browser (Same-Origin)
$path = $_SERVER['REQUEST_URI'];
$method = $_SERVER['REQUEST_METHOD'];
$body = file_get_contents('php://input');

$api = 'http://localhost:5000' . $path;
$ch = curl_init($api);
curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $method);
if ($body) curl_setopt($ch, CURLOPT_POSTFIELDS, $body);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: application/json'));
$res = curl_exec($ch);
$code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
http_response_code($code);
echo $res;
?>