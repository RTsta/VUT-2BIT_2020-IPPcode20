ZIPNAME=xnacar00
.PHONY: zip parse_test interpret_test mysrc both_test
	
parse_test:
	php test.php --directory=./tests/parse-only --parse-only --recursive --jexamxml=./other/jexamxml/jexamxml.jar >./tests/result.html

interpret_test:
	php test.php --directory=./tests/interpret-only/ --int-only --recursive >./tests/result.html
	
both_test:
	php test.php --directory=./tests/both --recursive >./tests/result.html
	
mysrc:
	php parse.php <$(file_path).src >$(file_path).mysrc
	
zip:
	zip ./other/$(ZIPNAME).zip parse.php interpret.py test.php readme1.md readme2.md rozsireni
	
upload:
	scp ./other/$(ZIPNAME).zip $(ZIPNAME)@merlin.fit.vutbr.cz:IPP