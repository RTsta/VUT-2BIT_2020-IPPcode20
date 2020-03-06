<?php
$input = STDIN;
$order = 1;

argumentsCheck($argv);

if (posix_isatty($input)) {
    errorHandel(21);
}

try {
    $domDocument = new DOMDocument('1.0', 'UTF-8');
} catch (Exception $e) {
    errorHandel(99);
}

$domDocument->formatOutput = true;
if (headerCheck($input)) {
    $domProgram = $domDocument->createElement('program');
    $domDocument->appendChild($domProgram);

    $domLanguage = $domDocument->createAttribute('language');
    $domLanguage->value = 'IPPcode20';
    $domProgram->appendChild($domLanguage);
} else {
    errorHandel(21);
}

while ($line = fgets($input)) {
    checkLine($line);
}

echo $domDocument->saveXML();

//--------------------------------------------------------------------------------------------------
/*
	Checking if the given word is begining of comment or not
*/
function commentCheck($word)
{
    return $word[0] == '#' ? true : false;
}

/*
	Function loads arguments and runs appropriate methods depadnding on the arguments
*/
function argumentsCheck($arguments)
{
    if (count($arguments) == 2 && $arguments[1] == "--help") {
        printHelp();
    } else if (count($arguments) > 2) {
        errorHandel(10);
    }

}

/*
	Checking if the file in STDIN includes header ".IPPcode20"
*/
function headerCheck($line)
{
    $line1 = strtoupper(fgets($line));
    $line1 = preg_replace('/\s+/', '', $line1);


    do {
        if ($line1 == ".IPPCODE20\n" || $line1 == ".IPPCODE20" || preg_match("/^\.IPPCODE20\s*#/", $line1)) {
            return true;
        }
        if ($line1 != false && !commentCheck($line1)) {

            return false;
        }
        $line1 = strtoupper(fgets($line));
    } while ($line1 != false);
    return false;
}

function checkStringForEscape($word)
{
    for ($i = 0; $i < strlen($word); $i++) {
        if ($word[$i] == '\\' && ((strlen($word) - $i) < 2)) { //ošetření případu, kdy je lomítko \ u konce řádku
            errorHandel(23);
        }
        if ($word[$i] == '\\') {
            if (is_numeric($word[$i + 1]) && is_numeric($word[$i + 2]) && is_numeric($word[$i + 3])) {
                $tmp = $word[$i + 1] . $word[$i + 2] . $word[$i + 3];
                $word[$i] = convertStrNumberToChar($tmp);

                for ($j = $i + 1; $j < strlen($word) - 3; $j++) {
                    $word[$j] = $word[$j + 3];
                }
                $word = substr($word, 0, -3);
            } else {
                errorHandel(23);
            }
        }
    }
    return $word;
}

function checkInt($word){
    if (preg_match("/(^[+-]?[0]{1}[1-9]{2}\d*$)|(^[-+]?[1-9]{1}\d*$)/",$word) || preg_match("/^\d+$/",$word)){
        return true;
    }
    return false;
}

/*
	Checking the validity of variable, whether is it correct type
*/
function symbCheck($word)
{
    $typeAndValue = explode("@", $word);
    if (count($typeAndValue) < 2) {
        errorHandel(23);
    }
    $typeAndValue[1] = preg_replace('/\#.*/', "", $typeAndValue[1]);
    if (count($typeAndValue) != 2) {
        errorHandel(23);
    }

    switch ($typeAndValue[0]) {
        case 'string':
            $typeAndValue[1] = checkStringForEscape($typeAndValue[1]);
            return $typeAndValue;
        case 'int':
            if (!checkInt($typeAndValue[1])){
                errorHandel(23);
            }
            return $typeAndValue;
        case 'bool':
            if ($typeAndValue[1] != "true" && $typeAndValue[1] != 'false') {
                errorHandel(23);
            }
            return $typeAndValue;
        case "GF":
        case "TF":
        case "LF":
            if (!checkIdentificator($typeAndValue[1])) {
                errorHandel(23);
            }
            $typeAndValue[1] = $typeAndValue[0] . "@" . $typeAndValue[1];
            $typeAndValue[0] = "var";
            return $typeAndValue;
        case "nil":
            if ($typeAndValue[1] != "nil") {
                errorHandel(23);
            }
            return $typeAndValue;
        default:
            errorHandel(23);
            break;
    }
}

function varCheck($word)
{
    $typeAndValue = explode("@", $word);
    if (count($typeAndValue) < 2) {
        errorHandel(23);
    }
    $typeAndValue[1] = preg_replace('/\#.*/', "", $typeAndValue[1]);
    if (count($typeAndValue) != 2) {

        errorHandel(23);
    }

    switch ($typeAndValue[0]) {
        case "GF":
        case "TF":
        case "LF":
            if (!checkIdentificator($typeAndValue[1])) {
                errorHandel(23);
            }
            $typeAndValue[1] = $typeAndValue[0] . "@" . $typeAndValue[1];
            $typeAndValue[0] = "var";
            return $typeAndValue;
        default:
            errorHandel(23);
            break;
    }
}

function labelCheck($word)
{
    $typeAndValue = explode("@", $word);
    if (count($typeAndValue) > 1) {
        errorHandel(23);
    }

    if (!checkIdentificator($word)) {
        errorHandel(23);
    }
}

function typeCheck($word)
{

    switch ($word) {
        case "int":
        case "string":
        case "bool":
            break;
        default:
            errorHandel(23);
    }

}

function checkIdentificator($word)
{
    if (!preg_match('/^[a-z]|[A-Z]|[-]|[$]|[&]|[%]|[*]|[!]|[?]|[_]{1}/', $word)) {
        return false;
    }

    if (preg_match('/^[\x01-\x1F]|[\x22]|[\x27-\x29]|[\x2B-\x2C]|[\x2E-\x2F]|[\x3A-\x3E]|[\x60]|[\x7B-\xFF]{1}/', $word)) {
        return false;
    }
    if (preg_match('/^\\\{1}/',$word)){return false;}
    return true;
}

/*
	Function that looks for match of givven instruction and keyword 
*/
function checkLine($line)
{
    $line = preg_replace('/\s+/', ' ', $line);
    $line_arr = explode(' ', trim($line));
    $keyWords = array("MOVE", "CREATEFRAME", "PUSHFRAME", "POPFRAME", "DEFVAR",
        "CALL", "RETURN", "PUSHS", "POPS", "ADD",
        "SUB", "MUL", "IDIV", "LT", "GT",
        "EQ", "AND", "OR", "NOT", "INT2CHAR",
        "STRI2INT", "READ", "WRITE", "CONCAT", "STRLEN",
        "GETCHAR", "SETCHAR", "TYPE", "LABEL", "JUMP",
        "JUMPIFEQ", "JUMPIFNEQ", "EXIT", "DPRINT", "BREAK");

    //regex pattern @([A-z]+) který použiji na argumenty, které tisknu a ještě z nich musím oddělat zavináč a nahradit všechny divný znaky

    switch (strtoupper($line_arr[0])) {
        //KEYWORD ⟨var⟩ ⟨symb⟩
        case $keyWords[0]: //MOVE 2
        case $keyWords[19]: //INT2CHAR 3
        case $keyWords[24]: //STRLEN
        case $keyWords[27]: //TYPE
        case $keyWords[18]: //NOT 2
            numberOfArgumentsOnLineCheck($line_arr, 2);
            $printableResult1 = varCheck($line_arr[1]);
            $printableResult2 = symbCheck($line_arr[2]);
            printResult(strtoupper($line_arr[0]), $printableResult1[0], $printableResult1[1], $printableResult2[0], $printableResult2[1]);
            break;
        //KEYWORD
        case $keyWords[1]: //CREATEFRAME 0
        case $keyWords[2]: //PUSHFRAME 0
        case $keyWords[3]: //POPFRAME 0
        case $keyWords[6]: //RETURN 0
        case $keyWords[34]: //BREAK
            numberOfArgumentsOnLineCheck($line_arr, 0);
            printResult(strtoupper($line_arr[0]));
            break;
        //KEYWORD ⟨var⟩
        case $keyWords[4]: //DEFVAR 1
        case $keyWords[8]: //POPS 2
            numberOfArgumentsOnLineCheck($line_arr, 1);
            $printableResult1 = varCheck($line_arr[1]);
            printResult(strtoupper($line_arr[0]), $printableResult1[0], $printableResult1[1]);
            break;
        //KEYWORD ⟨label⟩
        case $keyWords[5]: //CALL 1
            numberOfArgumentsOnLineCheck($line_arr, 1);
            labelCheck($line_arr[1]);
            printResult(strtoupper($line_arr[0]), "label", $line_arr[1]);
            break;
        //KEYWORD ⟨symb⟩
        case $keyWords[7]: //PUSHS 1
        case $keyWords[22]: //WRITE
            numberOfArgumentsOnLineCheck($line_arr, 1);
            $printableResult1 = symbCheck($line_arr[1]);
            printResult(strtoupper($line_arr[0]), $printableResult1[0], $printableResult1[1]);
            break;
        //KEYWORD ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
        case $keyWords[9]: //ADD 3
        case $keyWords[10]: //SUB 3
        case $keyWords[11]: //MUL 3
        case $keyWords[12]: //IDIV 3
        case $keyWords[13]: //LT 3
        case $keyWords[14]: //GT 3
        case $keyWords[15]: //EQ 3
        case $keyWords[16]: //AND 3
        case $keyWords[17]: //OR 3
        case $keyWords[20]: //STR2INT 3
        case $keyWords[23]: //CONCAT
        case $keyWords[25]: //GETCHAR
        case $keyWords[26]: //SETCHAR
            numberOfArgumentsOnLineCheck($line_arr, 3);
            $printableResult0 = varCheck($line_arr[1]);
            $printableResult1 = symbCheck($line_arr[2]);
            $printableResult2 = symbCheck($line_arr[3]);
            printResult(strtoupper($line_arr[0]), $printableResult0[0], $printableResult0[1], $printableResult1[0], $printableResult1[1], $printableResult2[0], $printableResult2[1]);
            break;
        //KEYWORD ⟨var⟩ ⟨type⟩
        case $keyWords[21]: //READ 2
            numberOfArgumentsOnLineCheck($line_arr, 2);
            $printableResult1 = varCheck($line_arr[1]);
            typeCheck($line_arr[2]);
            printResult(strtoupper($line_arr[0]), $printableResult1[0], $printableResult1[1], "type", $line_arr[2]);
            break;
        //KEYWORD ⟨label⟩
        case $keyWords[28]: //LABEL
        case $keyWords[29]: //JUMP
            numberOfArgumentsOnLineCheck($line_arr, 1);
            labelCheck($line_arr[1]);
            printResult(strtoupper($line_arr[0]), "label", $line_arr[1]);
            break;
        //KEYWORD ⟨label⟩ ⟨symb1⟩ ⟨symb2⟩
        case $keyWords[30]: //JUMPIFEQ
        case $keyWords[31]: //JUMPIFNEQ
            numberOfArgumentsOnLineCheck($line_arr, 3);
            labelCheck($line_arr[1]);
            $printableResult1 = symbCheck($line_arr[2]);
            $printableResult2 = symbCheck($line_arr[3]);
            printResult(strtoupper($line_arr[0]), "label", $line_arr[1], $printableResult1[0], $printableResult1[1], $printableResult2[0], $printableResult2[1]);
            break;
        //KEYWORD ⟨symb⟩
        case $keyWords[32]: //EXIT
        case $keyWords[33]: //DPRINT
            numberOfArgumentsOnLineCheck($line_arr, 1);
            $printableResult1 = symbCheck($line_arr[1]);
            printResult(strtoupper($line_arr[0]), $printableResult1[0], $printableResult1[1]);
            break;
        case "":
            break;
        default:
            if (!commentCheck($line_arr[0])) {
                errorHandel(22);
            }
            break;
    }
}

/**
 * Function that prints output on XML format.
 */
function printResult($instruction, $arg1type = NULL, $arg1data = "", $arg2type = NULL, $arg2data = "", $arg3type = NULL, $arg3data = "")
{
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

    if ($arg1type != NULL) {
        $arg1data = htmlspecialchars($arg1data, ENT_QUOTES | ENT_XML1, 'UTF-8');

        $domArg1 = $domDocument->createElement('arg1');
        $domArg1->nodeValue = $arg1data;
        $domInstruction->appendChild($domArg1);

        $domType = $domDocument->createAttribute('type');
        $domType->value = $arg1type;
        $domArg1->appendChild($domType);
    }

    if ($arg1type != NULL && $arg2type != NULL) {
        $arg2data = htmlspecialchars($arg2data, ENT_QUOTES | ENT_XML1, 'UTF-8');

        $domArg2 = $domDocument->createElement('arg2');
        $domArg2->nodeValue = $arg2data;
        $domInstruction->appendChild($domArg2);

        $domType = $domDocument->createAttribute('type');
        $domType->value = $arg2type;
        $domArg2->appendChild($domType);
    }

    if ($arg1type != NULL && $arg2type != NULL && $arg3type != NULL) {
        $arg3data = htmlspecialchars($arg3data, ENT_QUOTES | ENT_XML1, 'UTF-8');

        $domArg3 = $domDocument->createElement('arg3');
        $domArg3->nodeValue = $arg3data;
        $domInstruction->appendChild($domArg3);

        $domType = $domDocument->createAttribute('type');
        $domType->value = $arg3type;
        $domArg3->appendChild($domType);
    }
}

/**
 * Error handling function
 */
function errorHandel($errorNum)
{
    fwrite(STDERR, $errorNum . "\n");
    exit($errorNum);
}

/**
 * Function that handles whether there is an appropriate number of argument on line.
 * Also checking, whether the arguments are valid.
 */
function numberOfArgumentsOnLineCheck($line_arr, $noOfArgumentsItTakes)
{
    $count = count($line_arr);
    if ($count != $noOfArgumentsItTakes + 1) {
        //there is fewer arguments than it shoud be
        if ($count < $noOfArgumentsItTakes + 1) {
            errorHandel(23);
        }

        //other arguments are just a comments
        if ($count > $noOfArgumentsItTakes + 1) {
            if (!(commentCheck($line_arr[$noOfArgumentsItTakes + 1]) || (strpos($line_arr[$noOfArgumentsItTakes], "#") !== false))) {
                errorHandel(23);
            }
        }
    }

    //checking if the arguments are real and not being comments
    for ($i = $noOfArgumentsItTakes; $i > 0; $i--) {
        if (commentCheck($line_arr[$i])) {
            errorHandel(23);
        }
    }
}

/*
Printing help
*/
function printHelp()
{
    echo "Help!\nI need somebody\nhelp\nnot just anybody\nhelp\nyou know I need someone\nHELP\n";
    exit(0);
}

function convertStrNumberToChar($strNumber)
{
    $strNumber = (int)ltrim($strNumber, '0');
    return chr($strNumber);
}

?>