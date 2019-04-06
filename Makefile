NAME= xnacar00

zip:
	zip $(NAME) parse.php readme1.md
	
debug:
	php parse.php <discord_test/debug/debug.src >discord_test/debug/debug.xml
	python3 interpret.py