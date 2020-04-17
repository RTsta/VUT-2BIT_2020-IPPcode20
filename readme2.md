Implementační dokumentace k 2. úloze do IPP 2019/2020  
Jméno a příjmení: Arthur_Nacar  
Login: xnacar00

# IPP - projekt (2020) - část 2
## interpret.py
Druhou části projektu je interpret jazyka `IPPcode20`, psaný v jazyce **Python** ve verzi **3.8**. Funkčnost interpretu byla testována na školním serveru Merlin. Interpret přijímá vstup ve formátu XML, který byl vytvořen souborem `parse.php`.

Po spuštění skryptu je vytvořen objekt třídy `Ippcode`, který reprezentuje XML vstup. Během volání konstruktoru dochází ke kontrole XML souboru na přítomnost a syntaktickou správnost celého soboru. Dochází k ukončení programu v případě nalezení nežádoucích elementů nebo neznámých atributů. Mimo jiné, při této kontrole dochází také k načtení všech hodnot `order`, které se ukládají v poli, aby mohly být následně využity pro pohyb mezi instrukcemi `IPPcodu20`. Důležitou součástí třídy `Ippcode` je metoda `next_instruction()`, jejichž návratovou hodnotou je další řádek s instrukcí určenou ke zpracovaní.  

Než dojde k samotnému provedení jednotlivých instrukcí, tak vstupním souborem prochází funkce `load_labels()`, která načte a uloží všechna návěští do třídy `Labelholder`. Tato třída je rozšířením pythnovského slovníku, sloužící pouze k uchování pořadového čísla instrukce, která následuje po návěští. Při vykonávání programu slouží k jednoduššímu pohybu v rámci kódu.  

Nejdůležitější části programu je třída `Instruction`, která obsahuje statické metody odpovídající instrukcím jazyka. V hlavním těle programu procházíme elementy XML souboru reprezentující instrukce a voláme jednotlivé metody této třídy. Po zavolání každé metody třídy `Instruction ` dochází k syntaktické analýze instrukce a jejích argumentů, podobné té, která je prováděna v souboru `parse.php`.  
Celou syntaktickou analýzu provádí třída `Syntax` a její metody. Dochází zde zejména ke kontrole počtu argumentů a zdali instrukce přijímá uvedené typy argumentů. V případě platné syntaxe následuje i sémantická kontrola.  
Třída sdružující metody pro sémantickou kontrolu se nazývá `Semantics` Kontrolujeme hlavně existenci proměnné v uvedeném rámci. Pokud to povaha instrukce vyžaduje tak testujeme, zdali byla proměnná inicializována a jestli se jedná o správný datový typ. Součásti sémantické kontroly je také kontrola správnosti práce s datovým zásobníkem, jedinečnost názvu návěští. Každý ze sémantických nedostatků je ihned ohlášen na standardní chybový výstup a interpretace je přerušena.  

Celý datový model je reprezentován dvěma entitami. Strukturou `data_stack` typu `DataStack`, což je třída odvozená od listu a představuje datový zásobník a třídou `Frameholder`, která je rozšířením slovníku. Třída `Frameholder` obsahuje pouze tři prvky, které korespondují s jednotlivými rámci. Protože definice jazyka umožňuje několikanásobné vytvoření lokálního rámce, tak jednotlivé lokální rámce jsou uchovány v rámci třídy ve struktuře `list`, která nabízí podobnou funkcionalitu, jako zásobník.

V interpretu bylo implementováno několik rozšíření funkcionality. Oproti základnímu zadání interpret zpracovává a podporuje aritmetiku s čísly typu `float`. Dalším rozšířením, které bylo zapracováno, je podpora pokročilých zásobníkových instrukcí. 

## test.php
Tento skript slouží k automatizovanému testování parseru a interpretu. Průběh skriptu je rozdělen do několika fází.  
 
1. zpracování argumentů programu  
2. nalezení zdrojových souborů  
3. degenerování chybějících soborů  
4. spuštění testu  
5. vyhodnocení a zobrazení výstupu   

Uchování hodnot argumentů zajišťuje třída `Arguments`. Metodou `Arguments->load()` se stará o zpracování všech zadaných argumentů programu.

Třída `Tests` prochází adresář a načítá zdrojové soubory s příponou `.src`. Jejich adresářové cesty jsou ukládány v poli, aby mohly být v další fázi spuštěny. Pokud byl nastaven parametr `--recursive`, tak jsou v průběhu vyhledávání zdrojových souborů vyhledávány i podadresáře, aby mohlo docházet k hledání zdrojových souborů i v těchto podadresářích. Tato třída také dogenerovává zbývající soubory s příponami `.in`, `.out`, `.rc`, pokud v adresáři s testy chybí.

Následuje spuštění a vyhodnocení testů. Výsledky testů jsem tištěny na standartní výstup dle šablon z třídy `HTMLtemplate`.