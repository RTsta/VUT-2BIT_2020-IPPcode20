Implementační dokumentace k 2. úloze do IPP 2018/2019  
Jméno a příjmení: Arthur_Nacar  
Login: xnacar00

# IPP - projekt (2019) - část 2
## interpret.py
Druhou části projektu je interpret jazyka `IPPcode19`, psaný v jazyce **Python** ve verzi **3.6.4**. a byl testován na funkčnost na školním serveru Merlin.   
Interpret přijímá vstup ve formátu XML, který byl vytvořen souborem `parse.php`.

Po spuštění skryptu je vytvořen objekt třídy `Ippcode`, který reprezentuje načtený XML vstup. Během volání konstruktoru dochází ke kontrole XML souboru na správnost hlavičky a správnost kořenového elementu. Pokud kořenový element neobsahuje atribut program s hodnotou `IPPcode19`, nebo obsahuje jiné nežádoucí atributy, program je ihned ukončen s příslušnou návratovou hodnotou, dle zadání. Důležitou součástí třídy `Ippcode` je metoda `next_instruction()`, která navrací aktuální instrukci určenou ke zpracovaní.  

Než dojde ke zpracovávání a vyhodnocení jednotlivých instrukcí, tak souborem prochází funkce `load_labels()`, která načte a uloží všechna návěští do třídy `Labelholder`, která je rozšířením pythnovského slovníku. Tato třída slouží pouze k uchování pořadového čísla instrukce pod klíčem návěští, která následuje po návěští. Při vykonávání samotného programu slouží k jednoduššímu pohybu v rámci kódu.  

Nejdůležitější části programu je třída `Instruction`, která obsahuje statické metody odpovídající instrukcím jazyka. V hlavním těle programu procházíme elementy XML souboru reprezentující instrukce a voláme jednotlivé metody této třídy. Po zavolání každé metody třídy `Instrukce` dochází k syntaktické analýze instrukce a jejích argumentů, podobné té, která je prováděna v souboru `parse.php`. Celou syntaktickou analýzu provádí třída `Syntax` a její metody. V případě bezchybné syntaxe je v metodách prováděna i sémantická analýza. Sémantická analýza se skládá z kontroly existence proměnné na uvedeném rámci, správnost práce s datovým zásobníkem, jedinečnost názvu návěští. Analýza je následována samotným provedením instrukce.

Celý datový model je reprezentován dvěma entitami. Strukturou `data_stack` typu `list`, která představuje datový zásobník a třídou `Frameholder`, která je rozšířením slovníku. Třída `Frameholder` má tři atributy, které odpovídají jednotlivým rámcům. Jelikož je zadáním povoleno několikanásobné vytváření lokálního rámce, tak jednotlivé lokální rámce jsou uchovány v rámci třídy ve struktuře `list`, která nabízí podobnou funkcionalitu, jako zásobník.