Implementační dokumentace k 2. úloze do IPP 2019/2020  
Jméno a příjmení: Arthur_Nacar  
Login: xnacar00

# IPP - projekt (2020) - část 2
## interpret.py
Druhou části projektu je interpret jazyka `IPPcode20`, psaný v jazyce **Python** ve verzi **3.8**. a byl testován na funkčnost na školním serveru Merlin.   
Interpret přijímá vstup ve formátu XML, který byl vytvořen souborem `parse.php`.

Po spuštění skryptu je vytvořen objekt třídy `Ippcode`, který reprezentuje XML vstup. Během volání konstruktoru dochází ke kontrole XML souboru na přítomnost a syntaktickou správnost hlavičky a správnost kořenového elementu. Pokud kořenový element neobsahuje atribut *program* s hodnotou `IPPcode20`, nebo obsahuje jiné nežádoucí atributy, interpret je ukončen s příslušnou návratovou hodnotou, dle zadání. Důležitou součástí třídy `Ippcode` je metoda `next_instruction()`, jejichž návratovou hodnotou je další řádek s instrukcí určenou ke zpracovaní.  

Než dojde k samotnému vyhodnocení jednotlivých instrukcí, tak vstupním souborem prochází funkce `load_labels()`, která načte a uloží všechna návěští do třídy `Labelholder`. Tato třída je pouze rozšířením pythnovského slovníku, sloužící pouze k uchování pořadového čísla instrukce následucící po návěští. Při vykonávání programu slouží k jednoduššímu pohybu v rámci kódu.  

Nejdůležitější části programu je třída `Instruction`, která obsahuje statické metody odpovídající instrukcím jazyka. V hlavním těle programu procházíme elementy XML souboru reprezentující instrukce a voláme jednotlivé metody této třídy. Po zavolání každé metody třídy `Instruction ` dochází k syntaktické analýze instrukce a jejích argumentů, podobné té, která je prováděna v souboru `parse.php`. Celou syntaktickou analyzu provádí třída `Syntax` a její metody. V případě platné syntaxe následuje i sémantická kontrola.  
Třída sdružující metody pro semantickou kontrolu se nazývá `Semantics` Kontrolujeme hlavně existenci proměnné v uvedeném rámci. Pokud to povaha instrukce vyžaduje tak testijeme, zda-li byla proměnná inicializována a jestli se jedná o správný datový typ. Součásti sémnatické kontroly je také kontrola správnosti práce s datovým zásobníkem, jedinečnost názvu návěští. Každý ze sémantických nedostatků je ihned ohlášen na standardní chybový výstup a interpretace je přerušena.  

Celý datový model je reprezentován dvěma entitami. Strukturou `data_stack` typu `DataStack`, což je třída odvozená od listu. Ta představuje datový zásobník a třídou `Frameholder`, která je rozšířením slovníku.  
Třída `Frameholder` obsahuje pouze tři prvky, které korespondují s  jednotlivými rámci. Protože definice jazyka umožňuje několikanásobné vytvoření lokálního rámce, tak jednotlivé lokální rámce jsou uchovány v rámci třídy ve struktuře `list`, která nabízí podobnou funkcionalitu, jako zásobník.

## test.php