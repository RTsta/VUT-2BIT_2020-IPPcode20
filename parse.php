<?php
$input = STDIN;
$order = 1;

argumentsCheck($argv);

if (posix_isatty($input)){
	errorHandel(21);
}

try {
	$domDocument = new DOMDocument('1.0','UTF-8');
} catch (Exception $e) {
	errorHandel(99);
}

$domDocument->formatOutput = true;
if (headerCheck($input)){
	$domProgram = $domDocument->createElement('program');
	$domDocument->appendChild($domProgram);

	$domLanguage = $domDocument->createAttribute('language');
	$domLanguage->value = 'IPPcode19';
	$domProgram->appendChild($domLanguage);
} else {
	errorHandel(21);
}

while ($line = fgets($input)){
	checkLine($line);
}

echo $domDocument->saveXML();

//--------------------------------------------------------------------------------------------------
/*
	Chcecking if the givven word is beginig of comment or not
*/
function commentCheck($word){
	return $word[0] == '#' ? true : false;
}

/*
	Function loads arguments and runs appropriate methods depadnding on the arguments
*/
function argumentsCheck($arguments){
	if (count($arguments) == 2 && $arguments[1] == "--help"){
		printHelp();
	} else if (count($arguments) > 2){
		errorHandel(10);
	}

}

/*
	Checking if the file in SRDIN includes header ".IPPcode19"
*/
function headerCheck($line){
	$line1 = fgets($line);
	if ($line1 == ".IPPcode19\n" || preg_match("/^\.IPPcode19\s*#/", $line1)){
		return true;
	}
	return false;
}

function variableCheck($word){
	$typeAndValue = explode ("@", $word);
	$typeAndValue[1] = preg_replace('/\#[A-z]*/', "", $typeAndValue[1]);
	$constantsArr = array("string","int", "bool");

	if (count($typeAndValue) != 2){
		//error invalid format
	}

	switch ($typeAndValue[0]) {
		case 'string':
			for ($i = 0; $i < strlen($typeAndValue[1]); $i++){
				if ($typeAndValue[1][$i] == '\\' && is_numeric($typeAndValue[1][$i+1]) && is_numeric($typeAndValue[1][$i+2]) && is_numeric($typeAndValue[1][$i+3]) ){
					$tmp = $typeAndValue[1][$i+1].$typeAndValue[1][$i+2].$typeAndValue[1][$i+3];
					$typeAndValue[1][$i] = convertStrNumberToChar($tmp);

					for ($j = $i+1; $j < strlen($typeAndValue[1])-3; $j++){
						$typeAndValue[1][$j] = $typeAndValue[1][$j+3];
					}
					$typeAndValue[1] = substr($typeAndValue[1], 0, -3);
				}
			}
			return $typeAndValue;
			break;
		case 'int':
			return $typeAndValue;
		case 'bool':
			$typeAndValue[1] = strtolower($typeAndValue[1]);
			return $typeAndValue;
			break;
		case "GF":
		case "TF":
		case "LF":
			$typeAndValue[1] = $typeAndValue[0]."@".$typeAndValue[1];
			$typeAndValue[0] = "var";
			return $typeAndValue;
		case "nil":
			return $typeAndValue;
		default:
			break;
	}
}

function checkLine($line){
	$line = preg_replace('/\s+/', ' ',$line);
	$line_arr = explode(' ',trim($line));
	$keyWords = array("MOVE", "CREATEFRAME", "PUSHFRAME", "POPFRAME", "DEFVAR", "CALL", "RETURN", "PUSHS", "POPS", "ADD", "SUB", "MUL", "IDIV", "LT" ,"GT" ,"EQ", "AND", "OR", "NOT", "INT2CHAR", "STRI2INT", "READ", "WRITE", "CONCAT", "STRLEN", "GETCHAR", "SETCHAR", "TYPE", "LABEL", "JUMP", "JUMPIFEQ", "JUMPIFNEQ", "EXIT", "DPRINT", "BREAK");

	//regex pattern @([A-z]+) kterů použiji na argumenty, které tisknu a ještě z nich musím oddělat zavináč a nahradit všechny divný znaky

	switch (strtoupper($line_arr[0])){
		case $keyWords[0]: //MOVE 2
		case $keyWords[19]: //INT2CHAR 3
		case $keyWords[24]: //STRLEN
		case $keyWords[27]: //TYPE
			numberOfArgumentsOnLineCheck($line_arr, 2);
			$printableResult1 = variableCheck($line_arr[2]);
			printResult(strtoupper($line_arr[0]), "var", $line_arr[1], $printableResult1[0], $printableResult1[1]);
			break;
		case $keyWords[1]: //CREATEFRAME 0
		case $keyWords[2]: //PUSHFRAME 0
		case $keyWords[3]: //POPFRAME 0
		case $keyWords[6]: //RETURN 0
		case $keyWords[34]: //BREAK
			numberOfArgumentsOnLineCheck($line_arr, 0);
			printResult(strtoupper($line_arr[0]));
			break;
		case $keyWords[4]: //DEFVAR 1
		case $keyWords[8]: //POPS 2
			numberOfArgumentsOnLineCheck($line_arr, 1);
			printResult(strtoupper($line_arr[0]), "var", $line_arr[1]);
			break;
		case $keyWords[5]: //CALL 1
			numberOfArgumentsOnLineCheck($line_arr, 1);
			printResult(strtoupper($line_arr[0]), "label", $line_arr[1]);
			break;
		case $keyWords[7]: //PUSHS 1
		case $keyWords[22]: //WRITE
			numberOfArgumentsOnLineCheck($line_arr, 1);
			$printableResult1 = variableCheck($line_arr[1]);
			printResult(strtoupper($line_arr[0]), $printableResult1[0], $printableResult1[1]);
			break;
		case $keyWords[9]: //ADD 3
		case $keyWords[10]: //SUB 3
		case $keyWords[11]: //MUL 3
		case $keyWords[12]: //IDIV 3
		case $keyWords[13]: //LT 3
		case $keyWords[14]: //GT 3
		case $keyWords[15]: //EQ 3
		case $keyWords[16]: //AND 3
		case $keyWords[17]: //OR 3
		case $keyWords[18]: //NOT 3
		case $keyWords[20]: //STR2INT 3
		case $keyWords[23]: //CONCAT
		case $keyWords[25]: //GETCHAR
		case $keyWords[26]: //SETCHAR
			numberOfArgumentsOnLineCheck($line_arr, 3);
			$printableResult1 = variableCheck($line_arr[2]);
			$printableResult2 = variableCheck($line_arr[3]);
			printResult(strtoupper($line_arr[0]), "var", $line_arr[1], $printableResult1[0], $printableResult1[1], $printableResult2[0], $printableResult2[1] );
			break;
		case $keyWords[21]: //READ 2
			numberOfArgumentsOnLineCheck($line_arr, 2);
			printResult(strtoupper($line_arr[0]), "var", $line_arr[1], "type", $line_arr[2]);
			break;
		case $keyWords[28]: //LABEL
		case $keyWords[29]: //JUMP
			numberOfArgumentsOnLineCheck($line_arr, 1);
			printResult(strtoupper($line_arr[0]), "label", $line_arr[1]);
			break;
		case $keyWords[30]: //JUMPIFEQ
		case $keyWords[31]: //JUMPIFNEQ
			numberOfArgumentsOnLineCheck($line_arr, 3);
			$printableResult1 = variableCheck($line_arr[2]);
			$printableResult2 = variableCheck($line_arr[3]);
			printResult(strtoupper($line_arr[0]), "label", $line_arr[1], $printableResult1[0], $printableResult1[1], $printableResult2[0], $printableResult2[1] );
			break;
		case $keyWords[32]: //EXIT
		case $keyWords[33]: //DPRINT
			numberOfArgumentsOnLineCheck($line_arr, 1);
			$printableResult1 = variableCheck($line_arr[2]);
			printResult(strtoupper($line_arr[0]), $printableResult1[0], $printableResult1[1]);
			break;
		default:
			if ( !commentCheck($line_arr[0]) ){
				errorHandel(22);
			}
			break;
    }
}

/**
Function that prints output on XML format.
*/
function printResult($instruction, $arg1type = NULL, $arg1data = "", $arg2type = NULL, $arg2data = "", $arg3type = NULL, $arg3data = ""){

    global $domDocument;
    global $domProgram;
    global $order;
    $domInstruction = $domDocument->createElement('instruction');
    $domProgram->appendChild($domInstruction);

    $domOrder = $domDocument->createAttribute('order');
    $domOrder->value = $order++;
    $domInstruction->appendChild($domOrder);

    $domOpcode = $domDocument->createAttribute('opcode');
    $domOpcode->value = $instruction;
    $domInstruction->appendChild($domOpcode);

    if ($arg1type != NULL){
        $domArg1 = $domDocument->createElement('arg1');
        $domArg1->nodeValue = $arg1data;
        $domInstruction->appendChild($domArg1);

        $domType = $domDocument->createAttribute('type');
        $domType->value = $arg1type;
        $domArg1->appendChild($domType);
    }

    if ($arg1type != NULL && $arg2type != NULL) {
        $domArg2 = $domDocument->createElement('arg2');
        $domArg2->nodeValue = $arg2data;
        $domInstruction->appendChild($domArg2);

        $domType = $domDocument->createAttribute('type');
        $domType->value = $arg2type;
        $domArg2->appendChild($domType);
    }

    if ($arg1type != NULL && $arg2type != NULL && $arg3type != NULL){
        $domArg3 = $domDocument->createElement('arg3');
        $domArg3->nodeValue = $arg3data;
        $domInstruction->appendChild($domArg3);

        $domType = $domDocument->createAttribute('type');
        $domType->value = $arg3type;
        $domArg3->appendChild($domType);
    }
}

/**
Error handling function
*/
function errorHandel($errorNum){
	fwrite(STDERR, $errorNum."\n");
	exit($errorNum);
}

/**
Function that handles wether there is an appropriate number of argument on line.
Also chescking, wether the arguments are valid.
*/
function numberOfArgumentsOnLineCheck($line_arr, $noOfArgumentsItTakes){
	$count = count($line_arr);
	if ($count != $noOfArgumentsItTakes+1){
		if ($count < $noOfArgumentsItTakes+1){
			errorHandel(22);
		}

		if ($count > $noOfArgumentsItTakes+1){
			if ( !(commentCheck($line_arr[$noOfArgumentsItTakes+1]) || (strpos($line_arr[$noOfArgumentsItTakes],"#") !== false)) ){
				errorHandel(22);
			}
		}
	}

	for ($i = $noOfArgumentsItTakes; $i > 0 ; $i--){
		if (commentCheck($line_arr[$i])){
			errorHandel(22);
		}
	}
}

/*
Printing help
*/
function printHelp(){
	echo "Help!\nI need somebody\nhelp\nnot just anybody\nhelp\nyou know I need someone\nHELP\n";
	exit(0);
}

function convertStrNumberToChar($strNumber){
	$strNumber = ltrim($strNumber, '0');
	return chr($strNumber);
}

?>