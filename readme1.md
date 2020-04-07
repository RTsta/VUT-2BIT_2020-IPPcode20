Implementační dokumentace k 1. úloze do IPP 2019/2020  
Jméno a příjmení: Arthur_Nacar  
Login: xnacar00

#IPP - projekt (2020)
## Parser (parser.php) 
Následující dokumentace popisuje parser nestrukturovaného imperativního jazyka **IPPcode20**. Cílem byla syntaktická kontrola a převod vstupního jazyka do jeho XML reprezentace.  

Jako první se provádí kontrola argumentů a jejich správnost. Dochází také k vytvoření instance třídy DOMDocument, která nám slouží k sestavení validního XML dokumentu. Dále je soubor načítán po řádcích a testován na přítomnost hlavičky. Ta musí být, jak vyplývá z dokumentace, vždy uvedena na prvním neprázdném řádku vstupního souboru. Její přítomnost je testována funkcí `headerCheck`. V případě absence hlavičky dojde k ukončení skriptu s chybovou hodnotou 21.

Hlavní smyčka programu prochází soubor a jednotlivé řádky podstupují syntaktickou kontrolu v rámci metody `checkLine`. Tato metoda funguje jako deterministický stavový automat, který porovnává první slovo řádku vstupního programu se zabudovaným polem klíčových slov. Nenalezne-li shodu, je řádek dále testován na správnost počtu argumentů dané instrukce a na přítomnost komentářů. Pokud testy vyjdou negativně, dochází k vypsáni chyby 22 na standardní chybový výstup.  
Protože instrukce přijímají různý počet operandů, jsou rozděleny do skupin podle jejich počtu a typu, pro zajištění přehlednější čitelnosti kódu.  
Každá instrukce přijímá nula až tři operandy a jejich správný počet kontroluje funkce `numberOfArgumentsOnLineCheck`. U instrukcí, které přijímají jako operand `symb` nebo `var` se parametr dále syntakticky kontroluje funkcí `variableCheck`. Pokud je argument konstantou typu řetězec, dochází k převodu escape sekvencí na jejich ASCII reprezentaci a funkce vrací dvouprvkové pole, jehož prvním prvkem je typ přijatého symbolu a druhým prvkem je jeho hodnota.  
Takto zpracované argumenty se společně s názvem instrukce předávají funkci `printResult`, která uloží instrukci a její argumenty do _DOMDocumentu_.

S posledním řádkem vstupu končí i hlavní smyčka programu a XML reprezentace IPPcodu20 z DOMDocumentu je vytištěna na standardní výstup. Program je ukončen s návratovou hodnotou 0.
