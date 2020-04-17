<?php

function printHelp()
{
}

class Arguments
{
    private $dir;
    private $recursive;
    private $parseScriptFile;
    private $intScriptFile;
    private $parseOnly;
    private $intOnly;
    private $jexamxml;

    function __construct()
    {
        $this->dir = getcwd(); //default dir
        $this->recursive = false;
        $this->parseScriptFile = "parse.php";
        $this->intScriptFile = "interpret.py";
        $this->parseOnly = false;
        $this->intOnly = false;
        $this->jexamxml = "/pub/courses/ipp/jexamxml/jexamxml.jar";

    }

    function setDirectory($name)
    {
        $this->dir = $name;
    }

    function setParseScriptFile($name)
    {
        $this->parseScriptFile = $name;
    }

    function setIntScriptFile($name)
    {
        $this->intScriptFile = $name;
    }

    function setRecursive()
    {
        $this->recursive = true;
    }

    function setParseOnly()
    {
        $this->parseOnly = true;
    }

    function setIntOnly()
    {
        $this->intOnly = true;
    }

    function setJexamxml($name)
    {
        $this->jexamxml = $name;
    }

    function getRecursive()
    {
        return $this->recursive;
    }

    function getParseScriptFile()
    {
        return $this->parseScriptFile;
    }

    function getIntScriptFile()
    {
        return $this->intScriptFile;
    }

    function getParseOnly()
    {
        return $this->parseOnly;
    }

    function getIntOnly()
    {
        return $this->intOnly;
    }

    function getJexamxml()
    {
        return $this->jexamxml;
    }

    function getDir()
    {
        return $this->dir;
    }

    function load()
    {
        $shortopts = "";

        $longopts = array(
            "help::",
            "directory::",
            "recursive::",
            "parse-script::",
            "int-script::",
            "parse-only::",
            "int-only::",
            "jexamxml::"
        );

        $options = getopt($shortopts, $longopts);

        if ($options == false){
            exit(10);
        }

        if (array_key_exists("help", $options)) {
            printHelp();
        }

        if (array_key_exists("directory", $options)) {
            if (is_dir($options["directory"])) {
                $this->setDirectory($options["directory"]);
            } else {
                exit(11);
            }
        }

        //• --recursive testy bude hledat nejen v zadaném adresáři, ale i rekurzivně ve všech jeho podadresářích;
        if (array_key_exists("recursive", $options)) {
            $this->setRecursive();
        }

        //• --parse-script=file soubor se skriptem v PHP 7.3 pro analýzu zdrojového kódu v IPP- code19 (chybí-li tento parametr,
        // tak implicitní hodnotou je parse.php uložený v aktuálním adresáři);
        if (array_key_exists("parse-script", $options)) {
            $this->setParseScriptFile($options["parse-script"]);
        }

        //• --int-script=file soubor se skriptem v Python 3.6 pro interpret XML reprezentace kódu v IPPcode19 (chybí-li tento parametr,
        // tak implicitní hodnotou je interpret.py uložený v aktuálním adresáři);
        if (array_key_exists("int-script", $options)) {
            $this->setIntScriptFile($options["int-script"]);
        }

        //--parse-only bude testován pouze skript pro analýzu zdrojového kódu v IPPcode20 (tento parametr se nesmí kombinovat s parametry --int-only a --int-script), výstup s referenčním výstupem (soubor s příponou out) porovnávejte nástrojem A7Soft JExamXML (viz [2]);
        if (array_key_exists("parse-only", $options)) {
            if (!array_key_exists("int-only", $options) && !array_key_exists("int-script", $options)) {
                $this->setParseOnly();
            }
        }

        //--int-only bude testován pouze skript pro interpret XML reprezentace kódu v IPPcode20 (tento parametr se nesmí kombinovat s parametry --parse-only a --parse-script). Vstupní program reprezentován pomocí XML bude v souboru s příponou src.
        if (array_key_exists("int-only", $options) && !array_key_exists("parse-only", $options) && !array_key_exists("parse-script", $options)) {
            $this->setIntOnly();
        }

        // --jexamxml=file soubor s JAR balíčkem s nástrojem A7Soft JExamXML. Je-li parametr vynechán uvažuje se implicitní umístění /pub/courses/ipp/jexamxml/jexamxml.jar na serveru Merlin, kde bude test.php hodnocen.
        if (array_key_exists("jexamxml", $options)) {
            $this->setJexamxml($options["jexamxml"]);
        } else {
            // exit(10);
        }
    }

}

class Tests
{
    private $srcFiles;
    private Arguments $arguments;

    function __construct($arguments)
    {
    }

    public static function scanForSrc($where)
    {
        $srcFiles = array();
        $tmp = glob($where . '/*.src');
        if ($tmp != false) {
            $srcFiles = array_merge($srcFiles, $tmp);
        }//todo co když je false
        return $srcFiles;
    }

    // $srcFile is string pathname of src file and the method check if there is appropriate rc file, if the file doesnt exist it creates new one
    public static function checkRcFile($srcFile)
    {
        $x = substr($srcFile, 0, strrpos($srcFile, '.'));
        $x = $x . ".rc";
        if (!file_exists($x)) {
            $file = fopen($x, "w");
            fwrite($file, "0\n");
        }
    }

    public static function checkInFile($srcFile)
    {
        $x = substr($srcFile, 0, strrpos($srcFile, '.'));
        $x = $x . ".in";
        if (!file_exists($x)) {
            $file = fopen($x, "w");
            fwrite($file, "");
        }
    }

    public static function checkOutFile($srcFile)
    {
        $x = substr($srcFile, 0, strrpos($srcFile, '.'));
        $x = $x . ".out";
        if (!file_exists($x)) {
            $file = fopen($x, "w");
            fwrite($file, "");
        }
    }

    public static function scanForDirRecursively($dir)
    {
        //najdu všechny složky, které obsahuje kořenová složka a pak v cyklu postupně prohledávám i tyto podsložky a
        // postupně je přidávám do jednoho velkého pole $directories
        $directories = array($dir);
        $directories = array_merge($directories, glob($dir . '/*', GLOB_ONLYDIR));
        $count = count($directories);

        for ($i = 1; $i < $count; $i++) {
            $tmp = glob($directories[$i] . '/*', GLOB_ONLYDIR);
            $directories = array_merge($directories, $tmp);

            $count = count($directories);
        }
        return $directories;
    }
}

class HTMLtemplate
{
    public static function printHeader($modeType)
    {
        echo("
<!DOCTYPE html>
<html lang=\"en\">
    <head>
    <meta http-equiv=\"Content-Type\" content=\"text/html; charset=UTF-8\" />
    <title>IPPcode20 - test results</title>
    <style>

        table {
        border: none;
        }

        table.resultsTable {
            border-spacing:0;
        }
        .resultsTable td, th {
            border: 1px solid #dddddd;
            text-align: left;
            padding: 8px;
        }

        .resultsTable tr:nth-child(even) {
            background-color: #dddddd;
        }
        .correct {
            background-color: #98FB98;
        }
        #incorrect{
            background-color: #FF9CAF;
            border: 1px solid #B22222;
            }
        .myfont {
            font-family: Arial, Helvetica, sans-serif;
        }
    </style>
    </head>
    <body class='myfont'>
    <table style=\"margin-left:auto;margin-right:auto;\">
        <tr><td><h1>Testing mode: $modeType </h1></td></tr>
        <tr><td><div>Time: " . date("H:i:s") . "</div></td></tr>
        <tr><td><h2>Results</h2><table class='resultsTable'>
            <tr>
                <th>NO.</th><th></th><th>TOTAL</th><th>NAME</th><th>RET. CODE</th><th>PASSED</th><th>NOTE</th>
            </tr>");
    }

    public static function printTest($testNo, $total, $testName, $retCode, $passed, $note = "")
    {
        $id = "";
        if ($passed == "OK" && $note == "") {
            $id = "";;
        } elseif ($passed == "FAIL") {
            $id = "id=\"incorrect\"";
        }
        echo ('<tr ' . $id . '><td style="text-align:right;">' . $testNo . '</td>
                <td>/</td>
                <td>' . $total . '</td>
                <td>' . $testName . '</td>
                <td style="text-align:center;">' . $retCode . '</td>
                <td>' . $passed . '</td>
                <td>' . $note . '</td>
                </tr>');
    }

    public static function printStatistics($noOfPassed, $noOfFailed)
    {
        echo ('
</table></td></tr>
<tr><td><h2>Statistics</h2>
<table class=\'resultsTable\'>
<tr class=\'correct\'><td>PASSED</td><td>' . $noOfPassed . '</td></tr>
<tr><td>FAILED</td><td>' . $noOfFailed . '</td></tr>
<tr><td>SUCCESS</td><td>' . ($noOfPassed / ($noOfPassed + $noOfFailed) * 100) . ' %</td></tr>
</table></td></tr>
</table>
');
    }

    public static function printFooter()
    {
        echo "
            </body>
            </html>";
    }
}

/* loading program arguments */
$arg = new Arguments();
$arg->load();

/* making list of all directories with test files*/
$directoryList = array($arg->getDir());
if ($arg->getRecursive()) {
    $directoryList = Tests::scanForDirRecursively($arg->getDir());
}

/* searching for all testfiles in directories*/
$srcList = array();
foreach ($directoryList as $oneDirectory) {
    $srcList = array_merge($srcList, Tests::scanForSrc($oneDirectory));
}
/* searching and creating all other files that are required */
foreach ($srcList as $oneSrc) {
    Tests::checkRcFile($oneSrc);
    Tests::checkInFile($oneSrc);
    Tests::checkOutFile($oneSrc);
}

$noOfPassed = 0;
$noOfFails = 0;

if ($arg->getParseOnly()) {
    HTMLtemplate::printHeader("parse-only");
    foreach ($srcList as $oneScr) {
        $parse_out = "";
        $testName = substr($oneScr, 0, strrpos($oneScr, '.'));
        $expectedReturnCode = (int)file_get_contents($testName . ".rc");
        $expectedOutput = file_get_contents($testName . ".out");
        exec("php7.4 " . $arg->getParseScriptFile() . " <$testName.src", $parse_out, $parse_ret);


        if ($expectedReturnCode == $parse_ret && $parse_ret == 0) {
            $diff_out = "";
             $temp2 = false;
             $temp2 = tmpfile();
             fwrite($temp2,implode( "\n", $parse_out ));

             exec("java -jar ".$arg->getJexamxml()." ".stream_get_meta_data($temp2)['uri']." ".$testName.".out",$diff_out,$diff_ret);
             fwrite($temp2,"");
             fclose($temp2);
             $temp2 = false;
             if ($diff_ret == 0){
                 HTMLtemplate::printTest(($noOfPassed + $noOfFails + 1), count($srcList), basename($testName), $parse_ret, "OK");
                 $noOfPassed++;
             } else{
                 HTMLtemplate::printTest(($noOfPassed + $noOfFails + 1),count($srcList),basename($testName),$parse_ret,"FAIL","PARSER ERR - EXPECTED: ".$expectedReturnCode."<br> DIFF MSG: ". implode( "<br>", $diff_out ));
                 $noOfFails++;
             }
        }else if ($expectedReturnCode == $parse_ret && $parse_ret != 0) {
            HTMLtemplate::printTest(($noOfPassed + $noOfFails + 1), count($srcList), basename($testName), $parse_ret, "OK");
            $noOfPassed++;
        } else {
            HTMLtemplate::printTest(($noOfPassed + $noOfFails + 1), count($srcList), basename($testName), $parse_ret, "FAIL");
            $noOfFails++;
        }
    }
} else if ($arg->getIntOnly()) {
    HTMLtemplate::printHeader("int-only");
    foreach ($srcList as $oneScr) {
        $interpret_out = "";
        $testName = substr($oneScr, 0, strrpos($oneScr, '.'));
        $expectedReturnCode = (int)file_get_contents($testName . ".rc");
        $expectedOutput = file_get_contents($testName . ".out");
        exec("python3.8 " . $arg->getIntScriptFile() . " --source=$testName.src --input=$testName.in", $interpret_out, $interpret_ret);

        if ($expectedReturnCode == $interpret_ret && $interpret_ret == 0) {
            $diff_out = "";
            $temp2 = false;
            $temp2 = tmpfile();
            fwrite($temp2, implode("\n", $interpret_out));

            exec("diff " . stream_get_meta_data($temp2)['uri'] . " " . $testName . ".out", $diff_out, $diff_ret);
            fwrite($temp2, "");
            fclose($temp2);
            $temp2 = false;
            if ($diff_ret == 0) {
                HTMLtemplate::printTest(($noOfPassed + $noOfFails + 1), count($srcList), basename($testName), $interpret_ret, "OK");
                $noOfPassed++;
            } else {
                HTMLtemplate::printTest(($noOfPassed + $noOfFails + 1), count($srcList), basename($testName), $interpret_ret, "FAIL", "INTERPRET ERR - EXPECTED: " . $expectedReturnCode . "<br> DIFF MSG: " . implode("<br>", $diff_out));
                $noOfFails++;
            }
        } else if ($expectedReturnCode == $interpret_ret && $interpret_ret != 0) {
            HTMLtemplate::printTest(($noOfPassed + $noOfFails + 1), count($srcList), basename($testName), $interpret_ret, "OK");
            $noOfPassed++;
        } else {
            HTMLtemplate::printTest(($noOfPassed + $noOfFails + 1), count($srcList), basename($testName), $interpret_ret, "FAIL", "EXPECTED: " . $expectedReturnCode);
            $noOfFails++;
        }
    }
} else {
    HTMLtemplate::printHeader("both");
    foreach ($srcList as $oneScr) {
        $parse_out = "";
        $interpret_out = "";
        $temp = false;

        $testName = substr($oneScr, 0, strrpos($oneScr, '.'));
        $expectedReturnCode = (int)file_get_contents($testName . ".rc");
        $expectedOutput = file_get_contents($testName . ".out");

        exec("php7.4 " . $arg->getParseScriptFile() . " <$testName.src", $parse_out, $parse_ret);
        if ($parse_ret != 0) {
            HTMLtemplate::printTest(($noOfPassed + $noOfFails + 1), count($srcList), basename($testName), $parse_ret, "FAIL", "PARSER");
            $noOfFails++;
            continue;
        }

        $temp = tmpfile();
        fwrite($temp, implode("\n", $parse_out));
        exec("python3.8 " . $arg->getIntScriptFile() . " --input=$testName.in --source=" . stream_get_meta_data($temp)['uri'], $interpret_out, $interpret_ret);

        fwrite($temp, "");
        fclose($temp);
        $temp = false;
        if ($expectedReturnCode == $interpret_ret && $expectedReturnCode == 0) {
            $diff_out = "";
            $temp2 = false;
            $temp2 = tmpfile();
            fwrite($temp2, implode("\n", $interpret_out));

            exec("diff " . stream_get_meta_data($temp2)['uri'] . " " . $testName . ".out", $diff_out, $diff_ret);
            fwrite($temp2, "");
            fclose($temp2);
            $temp2 = false;
            if ($diff_ret == 0) {
                HTMLtemplate::printTest(($noOfPassed + $noOfFails + 1), count($srcList), basename($testName), $interpret_ret, "OK");
                $noOfPassed++;
            } else {
                HTMLtemplate::printTest(($noOfPassed + $noOfFails + 1), count($srcList), basename($testName), $interpret_ret, "FAIL", "INTERPRET ERR - EXPECTED: " . $expectedReturnCode . "<br> DIFF MSG: " . implode("<br>", $diff_out));
                $noOfFails++;
            }
        } else if ($expectedReturnCode == $interpret_ret && $expectedReturnCode != 0) {
            HTMLtemplate::printTest(($noOfPassed + $noOfFails + 1), count($srcList), basename($testName), $interpret_ret, "OK");
            $noOfPassed++;
        } else {
            HTMLtemplate::printTest(($noOfPassed + $noOfFails + 1), count($srcList), basename($testName), $interpret_ret, "FAIL", "INTERPRET ERR - EXPECTED: " . $expectedReturnCode);
            $noOfFails++;
        }
    }
}

HTMLtemplate::printStatistics($noOfPassed, $noOfFails);
HTMLtemplate::printFooter();
?>
