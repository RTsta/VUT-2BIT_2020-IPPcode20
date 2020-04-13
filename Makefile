ZIPNAME=xnacar00
.PHONY: zip parse_test interpret_test mysrc
	
parse_test:
	php test.php --directory=./tests/parse-only/ --parse-only --recursive >./tests/result.html

interpret_test:
	python3 interpret.py --source=./tests//add/add.src --input=./tests/add/add.in
	
mysrc:
	php parse.php <$(file_path).src >$(file_path).mysrc
	
zip:
	zip ./other/$(ZIPNAME).zip parse.php interpret.py test.php readme1.md readme2.md rozsireni
	
upload:
	scp ./other/$(ZIPNAME).zip $(ZIPNAME)@merlin.fit.vutbr.cz:IPP