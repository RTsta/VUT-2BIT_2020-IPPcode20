# VUT-2BIT_2020-IPPcode20
## Autor
- Arthur Nácar (xnacar00)

## Popis
### Parser (parser.php) 
Následující dokumentace popisuje parser nestrukturovaného imperativního jazyka **IPPcode20**. Cílem byla syntaktická kontrola a převod vstupního jazyka do jeho XML reprezentace.  

Jako první se provádí kontrola argumentů a jejich správnost. Dochází také k vytvoření instance třídy DOMDocument, která nám slouží k sestavení validního XML dokumentu. Dále je soubor načítán po řádcích a testován na přítomnost hlavičky. Ta musí, jak vyplývá z dokumentace, být vždy uvedena na prvním neprázdním řádku vstupního souboru. Její přítomnost je testována funkcí `headerCheck`. Její absence vede k ukončení skryptu s chybovou hodnotou 21.
  
  

Hlavní smyčka programu prochází soubor a jednotlivé řádky podstupují syntaktickou kontrolu funkcí `checkLine`. Tato funkce funguje jako deterministický stavový automat, který porovnává první slovo řádku vstupího programu se zabudovaným polem klíčových slov. Nenalezne-li shodu, je řádek dále testován, ná správnost počtu argumentů dané instrukce a na přítomnost komentářů. Pokud testy vyjdou negativně, dochází k vypsáni chyby 22 na standardní chybový výstup.  
Protože instrukce přijímají různý počet operandů, jsou rozděleny do skupin podle jejich počtu a typu, pro zajištění přehlednější čitelnosti kódu.  
Každá instrukce přijímá nula až tři operandy a jejich správný počet kontroluje funkce `numberOfArgumentsOnLineCheck`. U instrukcí, které přijímají jako operand `symb` nebo `var` se parametr dále syntakticky kontroluje funkcí `variableCheck`. Pokud je argument konstanta typu řetězec, dochází k převodu escape sekvencí na jejich ASCII reprezentaci a funkce vrací dvouprvkové pole, kde se na prvním prvku pole nachází typ přijatého symbolu a na druhém prvku prvku jeho hodnota.  
Takto zpracované argumenty se společně s názvem instrukce předávají funkci `printResult`, která uloží instrukci a její argumenty do _DOMDocumentu_.

S posledním řádkem vstupu končí i hlavní smyčka programu a XML reprezentace IPPcodu20 z DOMDocumentu je vytištěna na standartní výstup a program je ukončen s návratovou hodnotou 0.

### Interpret (interpret.py)
Druhou části projektu je interpret jazyka `IPPcode20`, psaný v jazyce **Python** ve verzi **3.8**. a byl testován na funkčnost na školním serveru Merlin.   
Interpret přijímá vstup ve formátu XML, který byl vytvořen souborem `parse.php`.

Po spuštění skryptu je vytvořen objekt třídy `Ippcode`, který reprezentuje XML vstup. Během volání konstruktoru dochází ke kontrole XML souboru na přítomnost a syntaktickou správnost hlavičky a správnost kořenového elementu. Pokud kořenový element neobsahuje atribut *program* s hodnotou `IPPcode20`, nebo obsahuje jiné nežádoucí atributy, interpret je ukončen s příslušnou návratovou hodnotou, dle zadání. Důležitou součástí třídy `Ippcode` je metoda `next_instruction()`, jejichž návratovou hodnotou je další řádek s instrukcí určenou ke zpracovaní.  

Než dojde k samotnému vyhodnocení jednotlivých instrukcí, tak vstupním souborem prochází funkce `load_labels()`, která načte a uloží všechna návěští do třídy `Labelholder`. Tato třída je pouze rozšířením pythnovského slovníku, sloužící pouze k uchování pořadového čísla instrukce následucící po návěští. Při vykonávání programu slouží k jednoduššímu pohybu v rámci kódu.  

Nejdůležitější části programu je třída `Instruction`, která obsahuje statické metody odpovídající instrukcím jazyka. V hlavním těle programu procházíme elementy XML souboru reprezentující instrukce a voláme jednotlivé metody této třídy. Po zavolání každé metody třídy `Instruction ` dochází k syntaktické analýze instrukce a jejích argumentů, podobné té, která je prováděna v souboru `parse.php`. Celou syntaktickou analyzu provádí třída `Syntax` a její metody. V případě platné syntaxe následuje i sémantická kontrola.  
Třída sdružující metody pro semantickou kontrolu se nazývá `Semantics` Kontrolujeme hlavně existenci proměnné v uvedeném rámci. Pokud to povaha instrukce vyžaduje tak testijeme, zda-li byla proměnná inicializována a jestli se jedná o správný datový typ. Součásti sémnatické kontroly je také kontrola správnosti práce s datovým zásobníkem, jedinečnost názvu návěští. Každý ze sémantických nedostatků je ihned ohlášen na standardní chybový výstup a interpretace je přerušena.  

Celý datový model je reprezentován dvěma entitami. Strukturou `data_stack` typu `list`, která představuje datový zásobník a třídou `Frameholder`, která je rozšířením slovníku.  
Třída `Frameholder` obsahuje pouze tři prvky, které korespondují s  jednotlivými rámci. Protože definice jazyka umožňuje několikanásobné vytvoření lokálního rámce, tak jednotlivé lokální rámce jsou uchovány v rámci třídy ve struktuře `list`, která nabízí podobnou funkcionalitu, jako zásobník.

### Testovací skrypt (test.php)