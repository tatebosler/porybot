<?php

// This is a PHP script that can be run on the command line to pull data from
// Pokémon Showdown battle records. We're training from random battles, not
// competitive.
// 
// @author Tate Bosler

$f = './logs';
$io = popen ( '/usr/bin/du -sk ' . $f, 'r' );
$size = fgets ( $io, 4096);
$size = substr ( $size, 0, strpos ( $size, "\t" ) );
pclose ( $io );

if ($size > 128000) {
    die('Directory size limit exceeded');
}

require "vendor/autoload.php";
use PHPHtmlParser\Dom;

// Get cURL resource
$curl = curl_init();
// Set some options - we are passing in a useragent too here
curl_setopt_array($curl, [
    CURLOPT_RETURNTRANSFER => 1,
    CURLOPT_URL => 'https://replay.pokemonshowdown.com/search?format=gen1ou',
]);
// Send the request & save response to $resp
$resp = curl_exec($curl);

$dom = new Dom;
$dom->load($resp);

$list = $dom->find('a[href^="/gen1ou"]');

foreach ($list as $link) {
    echo $link->href."\n";
    curl_setopt_array($curl, [
        CURLOPT_RETURNTRANSFER => 1,
        CURLOPT_URL => "https://replay.pokemonshowdown.com{$link->href}.log",
    ]);
    $data = curl_exec($curl);
    $id = explode('-', $link->href)[1];
    
    file_put_contents(__DIR__."/logs/$id.txt", $data);
}
curl_close($curl);
