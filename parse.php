<?php
$input = STDIN;
$order = 1;

//@todo kontrola argumentu (--help)
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
	$domLanguage->value = '.IPPcode19';
	$domProgram->appendChild($domLanguage);
} else {
	errorHandel(21);
}

while ($line = fgets($input)){
	checkLine($line);
}

echo $domDocument->saveXML();

//--------------------------------------------------------------------------------------------------

function argumentsCheck($arguments){
	if (count($arguments) == 2 && $arguments[1] == "--help"){
		printHelp();
	} else if (count($arguments) > 2){
		errorHandel(10);
	}

}

function headerCheck($line){
	return (fgets($line) == ".IPPcode19\n");
}

function variableCheck($word){
	$typeAndValue = explode ("@", $word);
	$constantsArr = array("string","int", "bool");

	if (count($typeAndValue) != 2){
		//error invalid format
	}

	switch ($typeAndValue[0]) {
		case 'string':
			//replace escape sequences
			return "string";
			break;
		case 'int':
			return "int";
			break;
		case 'bool':
			return "bool";
			break;
		case "GF":
		case "TF":
		case "LF":
			return "var";
			break;
		default:
			//return error
			return false;
			break;
	}
}

function checkLine($line){
	$line_arr = explode(' ',trim($line));

	$keyWords = array("MOVE", "CREATEFRAME", "PUSHFRAME", "POPFRAME", "DEFVAR", "CALL", "RETURN", "PUSHS", "POPS", "ADD", "SUB", "MUL", "IDIV", "LT" ,"GT" ,"EQ", "AND", "OR", "NOT", "INT2CHAR", "STRI2INT", "READ", "WRITE", "CONCAT", "STRLEN", "GETCHAR", "SETCHAR", "TYPE", "LABEL", "JUMP", "JUMPIFEQ", "JUMPIFNEQ", "EXIT", "DPRINT", "BREAK");

	switch (strtoupper($line_arr[0])){
		case $keyWords[0]: //MOVE 2
		case $keyWords[19]: //INT2CHAR 3
		case $keyWords[24]: //STRLEN
		case $keyWords[27]: //TYPE
			printResult(strtoupper($line_arr[0]), "var", $line_arr[1], variableCheck($line_arr[2]), $line_arr[2]);
			break;
		case $keyWords[1]: //CREATEFRAME 0
		case $keyWords[2]: //PUSHFRAME 0
		case $keyWords[3]: //POPFRAME 0
		case $keyWords[6]: //RETURN 0
		case $keyWords[34]: //BREAK
			printResult(strtoupper($line_arr[0]));
			break;
		case $keyWords[4]: //DEFVAR 1
		case $keyWords[8]: //POPS 2
			printResult(strtoupper($line_arr[0]), "var", $line_arr[1]);
			break;
		case $keyWords[5]: //CALL 1
			printResult(strtoupper($line_arr[0]), "label", $line_arr[1]);
			break;
		case $keyWords[7]: //PUSHS 1
		case $keyWords[22]: //WRITE
			printResult(strtoupper($line_arr[0]), variableCheck($line_arr[1]), $line_arr[1]);
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
			printResult(strtoupper($line_arr[0]), "var", $line_arr[1], variableCheck($line_arr[2]), $line_arr[2], variableCheck($line_arr[3]), $line_arr[3]);
			break;
		case $keyWords[21]: //READ 2
			printResult(strtoupper($line_arr[0]), "var", $line_arr[1], "type", $line_arr[2]);
			break;
		case $keyWords[28]: //LABEL
		case $keyWords[29]: //JUMP
			printResult(strtoupper($line_arr[0]), "label", $line_arr[1]);
			break;
		case $keyWords[30]: //JUMPIFEQ
		case $keyWords[31]: //JUMPIFNEQ
			printResult(strtoupper($line_arr[0]), "label", $line_arr[1], variableCheck($line_arr[2]), $line_arr[2], variableCheck($line_arr[3]), $line_arr[3]);
			break;
		case $keyWords[32]: //EXIT
		case $keyWords[33]: //DPRINT
			printResult(strtoupper($line_arr[0]), "var", $line_arr[1], variableCheck($line_arr[2]), $line_arr[2], variableCheck($line_arr[3]), $line_arr[3]);
			break;
		default:
			if ($line_arr[0][0] != '#'){
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
function which prints HELP
*/

function printHelp(){
	echo "Help!\nI need somebody\nhelp\nnot just anybody\nhelp\nyou know I need someone\nHELP\n";
	exit(0);
}

?>