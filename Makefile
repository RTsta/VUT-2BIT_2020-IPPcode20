NAME= xnacar00

zip:
	zip $(NAME) parse.php readme1.md
	
mydebug:
	php parse.php <discord_test/debug/debug.src >discord_test/debug/debug.xml
	python3 interpret.py --source=discord_test/debug/debug.xml --input=discord_test/debug/interpret_stdin_debug.input

debug_interpret:
	python3 interpret.py --source=discord_test/int-only/vyzi_tests/should-pass/from-parse-only/every_instruction_program.src
	
debug both:
	php parse.php <discord_test/debug/debug.src >discord_test/debug/debug.xml
	python3 interpret.py --source=discord_test/debug/debug.xml --input=discord_test/debug/interpret_stdin_debug.input