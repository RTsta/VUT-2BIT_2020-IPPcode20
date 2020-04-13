import xml.etree.ElementTree as ET
import sys


def errorHandel(number, message=None):
	if message is not None:
		print(message,file=sys.stderr)
	print(number, file=sys.stderr)
	exit(number)


def mydebugprint(string):
	print("x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x", file=sys.stderr)
	print(str(string), file=sys.stderr)
	print("x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x", file=sys.stderr)


# ---------------------------------------------------------------------------------------------------------------IPPCODE
class Ippcode:
	def __init__(self, file):
		try:
			tree = ET.parse(file)
			self.root = tree.getroot()
			self.listOfOrderNumbers = list()
			self.minOrder = 1
			self.maxOrder = 1
			self.currentOrder = 1

			if not self.header_check():
				errorHandel(21, "Error - missing or wrong header")
			self.check_structure()
			self.listOfOrderNumbers.sort()
			if self.listOfOrderNumbers != []:
				self.minOrder = min(self.listOfOrderNumbers)
				self.maxOrder = max(self.listOfOrderNumbers)
				self.currentOrder = self.minOrder-1
			if self.minOrder < 1:
				errorHandel(32, "Error - negative order number or zero order number")
		except ET.ParseError:
			errorHandel(31, "Error - unable to read XML file")
		except FileNotFoundError:
			errorHandel(11, "Error - unable to read XML file")

	def header_check(self):
		for attribute in self.root.attrib:
			if attribute not in ["language", "name", "description"]:
				errorHandel(32, "Error - unknown atrtribute in header")

		if self.root.attrib['language'] != "IPPcode20":
			errorHandel(32, "Error - missing or wrong header")
		return True

	def jump_to_instruction(self, line):
		self.currentOrder = 0

	def check_structure(self):
		for element in self.root:
			if element.tag != 'instruction':
				errorHandel(32,"Error - unknown XML tag")
			if len(element.attrib) != 2:
				errorHandel(32, "Error - extra XML attributes in tag")
			for attribute in element.attrib:
				if attribute not in ["order", "opcode"]:
					errorHandel(32, "Error - unknown atrtribute in header",)
			try:
				loadedOrder = int(element.attrib["order"])
				if loadedOrder in self.listOfOrderNumbers:
					errorHandel(32, "Error - duplicit order")
				self.listOfOrderNumbers.append(loadedOrder)
			except ValueError:
				errorHandel(32, "Error - order is not number")

	def next_instruction(self):
		if self.listOfOrderNumbers == []:
			return None
		succ = False
		for numb in self.listOfOrderNumbers:
			if numb > self.currentOrder:
				self.currentOrder = numb
				succ = True
				break
		# už žádné další číslo není
		if not succ:
			return None
		for element in self.root:
			if int(element.attrib["order"]) == self.currentOrder:
				return element
		else:
			return None


# -------------------------------------------------------------------------------------------------------------DATASTACK
class DataStack(list):
	def __init__(self):
		super(list, self).__init__()

	def topElem_is_correct_type(self,expected_type):
		self.is_enought_elements(1)
		var_value = self[-1]
		if expected_type == "int" and type(var_value) is int:
			return True
		if expected_type == "bool" and type(var_value) is bool:
			return True
		if expected_type == "nil" and type(var_value) is None:
			return True
		if expected_type == "string" and type(var_value) is str:
			return True
		if expected_type == "float" and type(var_value) is float:
			return True
		if expected_type == "number" and (type(var_value) is float or type(var_value) is int):
			return True
		return False

	def topElem_check_type(self, expected_type):
		if not self.topElem_is_correct_type(expected_type):
			errorHandel(53, "Error – Semantic error at line  " + str(
				Instruction.xml_block.attrib["order"]) + " - incompatible types")

	def is_enought_elements(self, number_of_elements):
		if len(self) < number_of_elements:
			errorHandel(56, "Error - semantic error at line " + str(
				Instruction.xml_block.attrib["order"]) + " - not enought elements on data stack")

# -------------------------------------------------------------------------------------------------------------VARIABLES
class Variable(dict):
	...


# -----------------------------------------------------------------------------------------------------------LABELHOLDER
class Labelholder(dict):
	def __init__(self):
		super(dict, self).__init__()

	def exist(self, name):
		return name in self.keys()


# -----------------------------------------------------------------------------------------------------------FRAMEHOLDER
class Frameholder(dict):
	def __init__(self):
		super(dict, self).__init__()
		self["GF"] = dict()
		self["TF"] = None
		self["LF"] = list()

	def new_lf(self):
		self["LF"].append(dict())

	def new_tf(self):
		self["TF"] = dict()

	def frame_exist(self, which):
		if which == "LF":
			return self[which] != []
		else:
			return self[which] is not None

	def new_var(self, where, var_name):
		if where == "GF" or where == "TF":
			self[where][var_name] = Variable()
			self[where][var_name]["init"] = False
			self[where][var_name]["value"] = None
		elif where == "LF":
			self[where][-1][var_name] = Variable()
			self[where][-1][var_name]["init"] = False
			self[where][-1][var_name]["value"] = None

	def is_in_gf(self, var_name):
		return var_name in self["GF"].keys()

	def is_in_tf(self, var_name):
		return var_name in self["TF"].keys()

	def is_in_lf(self, var_name):
		return var_name in self["LF"][-1].keys()

	def var_exist(self, where, var_name):
		if not self.frame_exist(where):
			errorHandel(55, "Error - Semantic error at line " + str(
				Instruction.xml_block.attrib["order"]) + " - Local frame doesnt exist")
			return False

		is_in_switch = {"GF": self.is_in_gf, "TF": self.is_in_tf, "LF": self.is_in_lf}
		if is_in_switch[where](var_name) is False:
			return False
		return True

	def var_correct_type(self, where, var_name, expected_type):
		self.var_exist(where, var_name)
		var_value = self.load_var_value(where, var_name)
		if expected_type == "int" and type(var_value) is int:
			return True
		if expected_type == "bool" and type(var_value) is bool:
			return True
		if expected_type == "nil" and type(var_value) is None:
			return True
		if expected_type == "string" and type(var_value) is str:
			return True
		if expected_type == "float" and type(var_value) is float:
			return True
		if expected_type == "number" and (type(var_value) is float or type(var_value) is int):
			return True
		return False

	def var_was_definied(self, where, var_name):
		if where == "LF" and (self["LF"] is None or self["LF"] == []):
			errorHandel(55, "Error - Semantic error at line " + str(
				Instruction.xml_block.attrib["order"]) + " - Local frame doesnt exist")
			return False

		is_in_switch = {"GF": self.is_in_gf, "TF": self.is_in_tf, "LF": self.is_in_lf}
		if is_in_switch[where](var_name) is True:
			errorHandel(52, "Error - Semantic error at line " + str(
				Instruction.xml_block.attrib["order"]) + " - variable was already defiened")
			return True
		return False

	def var_is_init(self, where, var_name):
		return self.load_var(where, var_name)["init"]

	def modify_in_gf(self, what, new_value):
		var = self.load_var("GF", what)
		var["value"] = new_value
		var["init"] = True

	def modify_in_tf(self, what, new_value):
		var = self.load_var("TF", what)
		var["value"] = new_value
		var["init"] = True

	def modify_in_lf(self, what, new_value):
		var = self.load_var("LF", what)
		var["value"] = new_value
		var["init"] = True

	def load_var(self, where, var_name):
		if not self.var_exist(where, var_name):
			return
		if where == "LF":
			return self["LF"][-1][var_name]
		else:
			return self[where][var_name]

	def load_var_value(self, where, var_name):
		return self.load_var(where, var_name)["value"]

	def modify_var(self, where, var_name, new_value):
		if not self.var_exist(where, var_name):
			return
		modify_in_switch = {"GF": self.modify_in_gf, "TF": self.modify_in_tf, "LF": self.modify_in_lf, }
		modify_in_switch[where](var_name, new_value)

	def symb_exist(self, symb_type, symb_frame, symb_value):
		if symb_type == "var":
			return self.var_exist(symb_frame, symb_value)
		elif symb_type == "string" or symb_type == "int" or symb_type == "bool" or symb_type == "nil" or symb_type == "float":
			return True
		else:
			return False

	def symb_is_init(self, symb_type, symb_frame, symb_value):
		if symb_type == "var":
			return self.var_is_init(symb_frame, symb_value)
		elif symb_type == "string" or symb_type == "int" or symb_type == "bool" or symb_type == "nil" or symb_type == "float":
			return True
		else:
			return False

	''' Function returns the value of symb, that means if it is var, than it loads the value 
	from frame otherwise it returns value from symbol'''

	def load_symb(self, arg):
		value = arg["value"]
		if arg["type"] == "var":
			value = self.load_var_value(arg["frame"], arg["value"])
		return value

	def symb_check_type(self, symb_type, symb_frame, symb_value, expected_type):
		if symb_type == "var":
			return self.var_correct_type(symb_frame, symb_value, expected_type)
		elif symb_type == expected_type:
			return True
		elif (symb_type == "int" or symb_type == "float") and expected_type == "number":
			return True
		return False


class Semantics:
	@staticmethod
	def check_type(symb_or_var, arg, expected_type):
		if symb_or_var == "var":
			if not frame.var_correct_type(arg["frame"], arg["value"], expected_type):
				errorHandel(53, "Error – Semantic error at line  " + str(
					Instruction.xml_block.attrib["order"]) + " - incompatible types")
		else:
			if not frame.symb_check_type(arg["type"], arg["frame"], arg["value"], expected_type):
				errorHandel(53, "Error – Semantic error at line  " + str(
					Instruction.xml_block.attrib["order"]) + " - incompatible types")
		return

	@staticmethod
	def check_existence(symb_or_var, arg):
		if symb_or_var == "var":
			if not frame.var_exist(arg["frame"], arg["value"]):
				errorHandel(54, "Error – Semantic error at line " + str(
					Instruction.xml_block.attrib["order"]) + " - variable doesn't not exist")
		else:
			if not frame.symb_exist(arg["type"], arg["frame"], arg["value"]):
				errorHandel(54, "Error – Semantic error at line " + str(
					Instruction.xml_block.attrib["order"]) + " - variable doesn't not exist")
		return

	@staticmethod
	def check_init(arg):
		if arg["type"] == "var":
			if not frame.var_is_init(arg["frame"], arg["value"]):
				errorHandel(56, "Error – Semantic error at line " + str(
					Instruction.xml_block.attrib["order"]) + " - variable is not initialized")
		return

	@staticmethod
	def check_existence_and_init(symb_or_var, arg):
		Semantics.check_existence(symb_or_var,arg)
		Semantics.check_init(arg)
		return

	@staticmethod
	def label_existence(label):
		if not labels.exist(label):
			errorHandel(52, "Error - semantic error at line " + str(
				Instruction.xml_block.attrib["order"]) + " - label does not exist")


# -----------------------------------------------------------------------------------------------------------INSTRUCTION
class Instruction:
	xml_block = None

	# arg [type:var     |frame:GF   |value:promena] <--> GF@promena
	# arg [type:int     |frame:""   |value:5      ] <--> int@5
	# arg [type:string  |frame:""   |value:"ahoj" ] <--> string@ahoj
	@staticmethod
	def decomponent_symb(arg_no):
		chidrenTags = []
		for a in Instruction.xml_block:
			chidrenTags.append(a.tag)
		if arg_no not in chidrenTags:
			errorHandel(32, "Error – Syntactic error at line " + str(Instruction.xml_block.attrib["order"]) + " - expected " + str(
					arg_no))

		rigtArg = Instruction.xml_block[0]
		for a in Instruction.xml_block:
			if a.tag == arg_no:
				rigtArg = a

		symb = {"type": rigtArg.attrib["type"], "frame": "", "value": ""}

		if Syntax.arg_is_var(rigtArg):
			return Instruction.decompont_var(arg_no)
		elif Syntax.arg_is_const(rigtArg):
			if str(symb["type"]) == "int":
				symb["value"] = int(rigtArg.text)
			elif str(symb["type"]) == "bool":
				symb["value"] = rigtArg.text != "false"
			elif str(symb["type"]) == "nil":
				symb["value"] = None
			elif str(symb["type"]) == "string":
				symb["value"] = rigtArg.text #fixme neumí číst hashtag
			if str(symb["type"]) == "float":
				try:
					symb["value"] = float(rigtArg.text)
				except:
					symb["value"] = float.fromhex(rigtArg.text)
		return symb

	@staticmethod
	def decompont_var(arg_no):
		chidrenTags = []
		for a in Instruction.xml_block:
			chidrenTags.append(a.tag)
		if arg_no not in chidrenTags:
			errorHandel(32, "Error – Syntactic error at line " + str(Instruction.xml_block.attrib["order"]) + " - expected " + str(
					arg_no))

		rigtArg = Instruction.xml_block[0]
		for a in Instruction.xml_block:
			if a.tag == arg_no:
				rigtArg = a

		var = {
			"type": rigtArg.attrib["type"],
			"frame": rigtArg.text[:2],
			"value": rigtArg.text[3:]
		}
		return var

	@staticmethod
	def decompont_label(arg_no):
		chidrenTags = []
		for a in Instruction.xml_block:
			chidrenTags.append(a.tag)
		if arg_no not in chidrenTags:
			errorHandel(32, "Error – Syntactic error at line " + str(Instruction.xml_block.attrib["order"]) + " - expected " + str(
					arg_no))

		rigtArg = Instruction.xml_block[0]
		for a in Instruction.xml_block:
			if a.tag == arg_no:
				rigtArg = a

		return str(rigtArg.text)

	# MOVE ⟨var⟩ ⟨symb⟩
	@staticmethod
	def ipp_move():  # ano
		Syntax.check("var", "symb")
		arg1 = Instruction.decompont_var("arg1")
		arg2 = Instruction.decomponent_symb("arg2")

		Semantics.check_existence("var", arg1)
		Semantics.check_existence_and_init("symb", arg2)

		value = frame.load_symb(arg2)

		frame.modify_var(arg1["frame"], arg1["value"], value)

	# CREATEFRAME
	@staticmethod
	def ipp_createframe():  # ano
		Syntax.check()
		frame.new_tf()

	# PUSHFRAME
	@staticmethod
	def ipp_pushframe():  # ano
		Syntax.check()
		if not frame.frame_exist("TF"):
			errorHandel(55, "Error – Semantic error at line " + str(
				Instruction.xml_block.attrib["order"]) + " - frame doesn't not exist")

		frame["LF"].append(frame["TF"])
		frame["TF"] = None

	# POPFRAME
	@staticmethod
	def ipp_popframe():  # ano
		Syntax.check()
		if not frame["LF"]:
			errorHandel(55, "Error – Semantic error at line" + str(
				Instruction.xml_block.attrib["order"]) + " - frame doesn't not exist")
		frame["TF"] = frame["LF"].pop()

	# DEFVAR ⟨var⟩
	@staticmethod
	def ipp_defvar():  # ano
		Syntax.check("var")
		arg1 = Instruction.decompont_var("arg1")

		if not frame.frame_exist(arg1["frame"]):
			errorHandel(55, "Error – Semantic error at line  " + str(
				Instruction.xml_block.attrib["order"]) + " - frame doesn't not exist")

		if frame.var_was_definied(arg1["frame"], arg1["value"]):
			errorHandel(52, "Error – Semantic error at line  " + str(
				Instruction.xml_block.attrib["order"]) + " - variable was already defiened")

		frame.new_var(arg1["frame"], arg1["value"])

	# CALL ⟨label⟩
	@staticmethod
	def ipp_call():
		Syntax.check("label")
		arg1 = Instruction.decompont_label("arg1")

		if not labels.exist(arg1):
			errorHandel(52, "Error - semantic error at line " + str(
				Instruction.xml_block.attrib["order"]) + " - label does not exist")

		data_stack.append(int(Instruction.xml_block.attrib["order"]) + 1)

		xmlobject.currentOrder = int(labels[str(arg1)])

	# RETURN
	@staticmethod
	def ipp_return():
		Syntax.check()
		try:
			xmlobject.currentOrder = int(data_stack.pop()) - 1
		except IndexError:
			errorHandel(56, "Error - semantic error at line " + str(
				Instruction.xml_block.attrib["order"]) + " - poping from empty stack",)

	# PUSHS ⟨symb⟩
	@staticmethod
	def ipp_pushs():
		Syntax.check("symb")
		arg1 = Instruction.decomponent_symb("arg1")

		Semantics.check_existence_and_init("symb", arg1)

		operand1 = frame.load_symb(arg1)
		data_stack.append(operand1)

	# POPS ⟨var⟩
	@staticmethod
	def ipp_pops():
		Syntax.check("var")
		arg1 = Instruction.decompont_var("arg1")
		Semantics.check_existence("var", arg1)
		if not data_stack:
			errorHandel(56, "Error - semantic error at line " + str(
				Instruction.xml_block.attrib["order"]) + " - data stack is empty")

		frame.modify_var(arg1["frame"], arg1["value"], data_stack.pop())

	# CLEARS
	@staticmethod
	def ipp_clears():
		data_stack.clear()

	# SARITHMETICS
	@staticmethod
	def ipp_sarithmetic(operator):
		if not data_stack:
			errorHandel(56, "Error - semantic error at line " + str(
				Instruction.xml_block.attrib["order"]) + " - data stack is empty")

		data_stack.is_enought_elements(2)

		data_stack.topElem_check_type("number")
		operand2 = data_stack.pop()
		data_stack.topElem_check_type("number")
		operand1 = data_stack.pop()
		try:
			operationInt = {
				"adds": int(operand1) + int(operand2),
				"subs": int(operand1) - int(operand2),
				"muls": int(operand1) * int(operand2),
				"idivs": int(operand1) / int(operand2),
			}

			operationFloat = {
				"adds": float(operand1) + float(operand2),
				"subs": float(operand1) - float(operand2),
				"muls": float(operand1) * float(operand2),
				"divs": float(operand1) / float(operand2),
			}
			if type(operand1) is float or type(operand2) is float:
				data_stack.append(float(operationFloat[operator]))
			else:
				data_stack.append(int(operationInt[operator]))
		except ZeroDivisionError:
			errorHandel(57, "Error – Semantic error at line  " + str(
				Instruction.xml_block.attrib["order"]) + " - dividing by zero")

	# ADDS
	@staticmethod
	def ipp_adds():
		Instruction.ipp_sarithmetic("adds")

	# SUBS
	@staticmethod
	def ipp_subs():
		Instruction.ipp_sarithmetic("subs")

	# MULS
	@staticmethod
	def ipp_muls():
		Instruction.ipp_sarithmetic("muls")

	# IDIVS
	@staticmethod
	def ipp_idivs():
		Instruction.ipp_sarithmetic("idivs")

	# DIVS
	@staticmethod
	def ipp_divs():
		Instruction.ipp_sarithmetic("divs")

	# SLOGIC_OP ⟨var⟩
	@staticmethod
	def ipp_slogic_op(operator):
		if not data_stack:
			errorHandel(56, "Error - semantic error at line " + str(
				Instruction.xml_block.attrib["order"]) + " - data stack is empty")
		data_stack.is_enought_elements(2)

		data_stack.topElem_check_type("bool")
		operand2 = data_stack.pop()
		data_stack.topElem_check_type("bool")
		operand1 = data_stack.pop()

		operation = {
			"ands": operand1 and operand2,
			"ors": operand1 or operand2,
		}
		data_stack.append(operation[operator])

	# SOR
	@staticmethod
	def ipp_ors():
		Instruction.ipp_slogic_op("ors")

	# SAND
	@staticmethod
	def ipp_ands():
		Instruction.ipp_slogic_op("ands")

	# SLT SGT SEQ  ⟨var⟩
	@staticmethod
	def ipp_lts_gts_eqs(operator):
		if not data_stack:
			errorHandel(56, "Error - semantic error at line " + str(
				Instruction.xml_block.attrib["order"]) + " - data stack is empty")
		operand2 = data_stack.pop()
		operand1 = data_stack.pop()

		if operator == "EQS":
			if type(operand1) is not type(operand2):
				if not (operand1 is None or operand2 is None):
					errorHandel(53, "Error - semantic error at line " + str(
						Instruction.xml_block.attrib["order"]) + " - incompatible operand types")
		else:
			if (type(operand1) is not type(operand2)) or (operand1 is None and operand2 is None):
				errorHandel(53, "Error - semantic error at line " + str(
					Instruction.xml_block.attrib["order"]) + " - incompatible operand types")

		if operator == "LTS":
			data_stack.append(operand1 < operand2)
		elif operator == "GTS":
			data_stack.append(operand1 > operand2)
		else:
			data_stack.append(operand1 == operand2)

	# LT / GT / EQ ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
	@staticmethod
	def ipp_lts():
		Instruction.ipp_lts_gts_eqs("LTS")

	# LT / GT / EQ ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
	@staticmethod
	def ipp_gts():
		Instruction.ipp_lts_gts_eqs("GTS")

	# LT / GT / EQ ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
	@staticmethod
	def ipp_eqs():
		Instruction.ipp_lts_gts_eqs("EQS")

	@staticmethod
	def ipp_nots():
		data_stack.topElem_check_type("bool")
		operand1 = data_stack.pop()
		data_stack.append(not operand1)

	# INT2CHAR ⟨var⟩ ⟨symb⟩
	@staticmethod
	def ipp_int2chars():
		if not data_stack:
			errorHandel(56, "Error - semantic error at line " + str(
				Instruction.xml_block.attrib["order"]) + " - data stack is empty")
		data_stack.topElem_check_type("int")
		try:
			int2char = int(data_stack.pop())
			int2char = chr(int2char)
			data_stack.append(int2char)
		except ValueError:
			errorHandel(58, "Error - Semantic error at line" + str(
				Instruction.xml_block.attrib["order"]) + " - value is not a char")

	# STRI2INT ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
	@staticmethod
	def ipp_stri2ints():
		if not data_stack:
			errorHandel(56, "Error - semantic error at line " + str(
				Instruction.xml_block.attrib["order"]) + " - data stack is empty")
		data_stack.topElem_check_type("int")
		char_pos = int(data_stack.pop())
		data_stack.topElem_check_type("string")
		stri2int = data_stack.pop()

		if int(char_pos) < 0:
			errorHandel(58, "Error - Semantic error at line" + str(
				Instruction.xml_block.attrib["order"]) + " - position is out of index")

		try:
			result = ord(stri2int[char_pos])
			data_stack.append(result)
		except TypeError:
			errorHandel(58, "Error - Semantic error at line" + str(
				Instruction.xml_block.attrib["order"]) + " - illegal arguments")
		except IndexError:
			errorHandel(58, "Error - Semantic error at line" + str(
				Instruction.xml_block.attrib["order"]) + " - position is out of index")

	# INT2FLOAT ⟨var⟩ ⟨symb⟩
	@staticmethod
	def ipp_int2floats():
		if not data_stack:
			errorHandel(56, "Error - semantic error at line " + str(
				Instruction.xml_block.attrib["order"]) + " - data stack is empty")
		data_stack.topElem_check_type("int")
		int2float = int(data_stack.pop())
		int2float = float(int2float)
		data_stack.append(int2float)

	# INT2FLOAT ⟨var⟩ ⟨symb⟩
	@staticmethod
	def ipp_float2ints():
		if not data_stack:
			errorHandel(56, "Error - semantic error at line " + str(
				Instruction.xml_block.attrib["order"]) + " - data stack is empty")
		data_stack.topElem_check_type("float")
		float2int = float(data_stack.pop())
		float2int = int(float2int)
		data_stack.append(float2int)

	# JUMPIFEQ ⟨label⟩ ⟨symb1⟩ ⟨symb2⟩
	@staticmethod
	def ipp_jumpifeqs():
		Syntax.check("label")
		arg1 = Instruction.decompont_label("arg1")
		Semantics.label_existence(arg1)

		if not data_stack:
			errorHandel(56, "Error - semantic error at line " + str(
				Instruction.xml_block.attrib["order"]) + " - data stack is empty")

		operand2 = data_stack.pop()
		operand1 = data_stack.pop()

		if type(operand1) is not type(operand2):
			if not (operand1 is None or operand2 is None):
				errorHandel(53, "Error - semantic error at line " + str(
					Instruction.xml_block.attrib["order"]) + " - incompatible operand types")

		if operand1 == operand2:
			xmlobject.currentOrder = int(labels[arg1])

	# JUMPIFNEQ ⟨label⟩ ⟨symb1⟩ ⟨symb2⟩
	@staticmethod
	def ipp_jumpifneqs():
		Syntax.check("label")
		arg1 = Instruction.decompont_label("arg1")
		Semantics.label_existence(arg1)

		if not data_stack:
			errorHandel(56, "Error - semantic error at line " + str(
				Instruction.xml_block.attrib["order"]) + " - data stack is empty")

		operand2 = data_stack.pop()
		operand1 = data_stack.pop()

		if type(operand1) is not type(operand2):
			if not (operand1 is None or operand2 is None):
				errorHandel(53, "Error - semantic error at line " + str(
					Instruction.xml_block.attrib["order"]) + " - incompatible operand types")

		if operand1 != operand2:
			xmlobject.currentOrder = int(labels[arg1])

	@staticmethod
	def ipp_arithmetic(operator):
		Syntax.check("var", "symb", "symb")

		arg1 = Instruction.decompont_var("arg1")
		arg2 = Instruction.decomponent_symb("arg2")
		arg3 = Instruction.decomponent_symb("arg3")

		Semantics.check_existence("var", arg1)
		Semantics.check_existence_and_init("symb", arg2)
		Semantics.check_existence_and_init("symb", arg3)
		Semantics.check_type("symb", arg2, "number")
		Semantics.check_type("symb", arg3, "number")

		operand1 = frame.load_symb(arg2)
		operand2 = frame.load_symb(arg3)

		#I think making aritmectics operations with different types int/float should be allowed and the result will be always float
		if type(operand1) is not type(operand2):
			errorHandel(53, "Error - semantic error at line " + str(
				Instruction.xml_block.attrib["order"]) + " - incompatible operand types")

		try:
			operationInt = {
				"add": int(operand1) + int(operand2),
				"sub": int(operand1) - int(operand2),
				"mul": int(operand1) * int(operand2),
				"idiv": int(operand1) / int(operand2),
			}

			operationFloat = {
				"add": float(operand1) + float(operand2),
				"sub": float(operand1) - float(operand2),
				"mul": float(operand1) * float(operand2),
				"div": float(operand1) / float(operand2),
			}
			if type(operand1) is float or type(operand2) is float:
				frame.modify_var(arg1["frame"], arg1["value"], float(operationFloat[operator]))
			else:
				frame.modify_var(arg1["frame"], arg1["value"], int(operationInt[operator]))
		except ZeroDivisionError:
			errorHandel(57, "Error – Semantic error at line  " + str(
				Instruction.xml_block.attrib["order"]) + " - dividing by zero")

	# ADD ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
	@staticmethod
	def ipp_add():
		Instruction.ipp_arithmetic("add")

	# SUB ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
	@staticmethod
	def ipp_sub():
		Instruction.ipp_arithmetic("sub")

	# MUL ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
	@staticmethod
	def ipp_mul():
		Instruction.ipp_arithmetic("mul")

	# IDIV ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
	@staticmethod
	def ipp_idiv():
		Instruction.ipp_arithmetic("idiv")

	@staticmethod
	def ipp_div():
		Instruction.ipp_arithmetic("div")

	# LT / GT / EQ ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
	@staticmethod
	def ipp_lt_gt_eq(operator):
		Syntax.check("var", "symb", "symb")

		arg1 = Instruction.decompont_var("arg1")
		arg2 = Instruction.decomponent_symb("arg2")
		arg3 = Instruction.decomponent_symb("arg3")

		Semantics.check_existence("var", arg1)
		Semantics.check_existence_and_init("symb", arg2)
		Semantics.check_existence_and_init("symb", arg3)

		operand1 = frame.load_symb(arg2)
		operand2 = frame.load_symb(arg3)

		if operator == "EQ":
			if type(operand1) is not type(operand2):
				if not (operand1 is None or operand2 is None):
					errorHandel(53, "Error - semantic error at line " + str(
						Instruction.xml_block.attrib["order"]) + " - incompatible operand types")
		else:
			if (type(operand1) is not type(operand2)) or (operand1 is None and operand2 is None):
				errorHandel(53, "Error - semantic error at line " + str(
					Instruction.xml_block.attrib["order"]) + " - incompatible operand types")

		if operator == "LT":
			frame.modify_var(arg1["frame"], arg1["value"], operand1 < operand2)
		elif operator == "GT":
			frame.modify_var(arg1["frame"], arg1["value"], operand1 > operand2)
		else:
			frame.modify_var(arg1["frame"], arg1["value"], operand1 == operand2)

	# LT / GT / EQ ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
	@staticmethod
	def ipp_lt():
		Instruction.ipp_lt_gt_eq("LT")

	# LT / GT / EQ ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
	@staticmethod
	def ipp_gt():
		Instruction.ipp_lt_gt_eq("GT")

	# LT / GT / EQ ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
	@staticmethod
	def ipp_eq():
		Instruction.ipp_lt_gt_eq("EQ")

	# AND / OR / NOT ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
	@staticmethod
	def ipp_logic_op(operator):
		Syntax.check("var", "symb", "symb")
		arg1 = Instruction.decompont_var("arg1")
		arg2 = Instruction.decomponent_symb("arg2")
		arg3 = Instruction.decomponent_symb("arg3")

		Semantics.check_existence("var", arg1)
		Semantics.check_existence_and_init("symb", arg2)
		Semantics.check_existence_and_init("symb", arg3)

		Semantics.check_type("symb", arg2, "bool")
		Semantics.check_type("symb", arg3, "bool")

		operand1 = frame.load_symb(arg2)
		operand2 = frame.load_symb(arg3)

		operation = {
			"and": operand1 and operand2,
			"or": operand1 or operand2,
		}
		frame.modify_var(arg1["frame"], arg1["value"], operation[operator])

	@staticmethod
	def ipp_and():
		Instruction.ipp_logic_op("and")

	@staticmethod
	def ipp_or():
		Instruction.ipp_logic_op("or")

	@staticmethod
	def ipp_not():
		Syntax.check("var", "symb")
		arg1 = Instruction.decompont_var("arg1")
		arg2 = Instruction.decomponent_symb("arg2")

		Semantics.check_existence("var", arg1)

		Semantics.check_existence_and_init("symb", arg2)
		Semantics.check_type("symb", arg2, "bool")

		operand1 = frame.load_symb(arg2)
		frame.modify_var(arg1["frame"], arg1["value"], not operand1)

	# INT2CHAR ⟨var⟩ ⟨symb⟩
	@staticmethod
	def ipp_int2char():
		Syntax.check("var", "symb")
		arg1 = Instruction.decompont_var("arg1")
		arg2 = Instruction.decomponent_symb("arg2")

		Semantics.check_existence("var", arg1)

		Semantics.check_existence_and_init("symb", arg2)
		Semantics.check_type("symb", arg2, "int")

		int2char = int(frame.load_symb(arg2))

		try:
			int2char = chr(int2char)
			frame.modify_var(arg1["frame"], arg1["value"], int2char)
		except ValueError:
			errorHandel(58, "Error - Semantic error at line" + str(
				Instruction.xml_block.attrib["order"]) + " - value is not a char")

	# STRI2INT ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
	@staticmethod
	def ipp_stri2int():
		Syntax.check("var", "symb", "symb")
		arg1 = Instruction.decompont_var("arg1")
		arg2 = Instruction.decomponent_symb("arg2")
		arg3 = Instruction.decomponent_symb("arg3")

		Semantics.check_existence("var", arg1)
		Semantics.check_existence_and_init("symb", arg2)
		Semantics.check_type("symb", arg2, "string")
		Semantics.check_existence_and_init("symb", arg3)
		Semantics.check_type("symb", arg3, "int")

		stri2int = frame.load_symb(arg2)
		char_pos = int(frame.load_symb(arg3))

		if int(char_pos) < 0:
			errorHandel(58, "Error - Semantic error at line" + str(
				Instruction.xml_block.attrib["order"]) + " - position is out of index")

		try:
			result = ord(stri2int[char_pos])
			frame.modify_var(arg1["frame"], arg1["value"], result)
		except TypeError:
			errorHandel(58, "Error - Semantic error at line" + str(
				Instruction.xml_block.attrib["order"]) + " - illegal arguments")
		except IndexError:
			errorHandel(58, "Error - Semantic error at line" + str(
				Instruction.xml_block.attrib["order"]) + " - position is out of index")

	# INT2FLOAT ⟨var⟩ ⟨symb⟩
	@staticmethod
	def ipp_int2float():
		Syntax.check("var", "symb")
		arg1 = Instruction.decompont_var("arg1")
		arg2 = Instruction.decomponent_symb("arg2")

		Semantics.check_existence("var", arg1)

		Semantics.check_existence_and_init("symb", arg2)
		Semantics.check_type("symb", arg2, "int")

		int2float = int(frame.load_symb(arg2))
		int2float = float(int2float)
		frame.modify_var(arg1["frame"], arg1["value"], int2float)

	# INT2FLOAT ⟨var⟩ ⟨symb⟩
	@staticmethod
	def ipp_float2int():
		Syntax.check("var", "symb")
		arg1 = Instruction.decompont_var("arg1")
		arg2 = Instruction.decomponent_symb("arg2")

		Semantics.check_existence("var", arg1)

		Semantics.check_existence_and_init("symb", arg2)
		Semantics.check_type("symb", arg2, "float")

		float2int = float(frame.load_symb(arg2))
		float2int = int(float2int)
		frame.modify_var(arg1["frame"], arg1["value"], float2int)

	# READ ⟨var⟩ ⟨type⟩
	@staticmethod
	def ipp_read():
		Syntax.check("var", "type")
		arg1 = Instruction.decompont_var("arg1")
		type_of_input = str(Instruction.xml_block[1].text)

		Semantics.check_existence("var", arg1)

		if input_file is None:
			read = input()
		else:
			read = input_file.readline()
			if read == '':
				frame.modify_var(arg1["frame"], arg1["value"], None)
				return
			else:
				read = read[:-1]  # removes last \n that adds readline
		try:
			if type_of_input == "bool":
				frame.modify_var(arg1["frame"], arg1["value"], str(read).lower() == "true")
			elif type_of_input == "string":
				frame.modify_var(arg1["frame"], arg1["value"], str(read))
			elif type_of_input == "int":
				frame.modify_var(arg1["frame"], arg1["value"], int(read))
			else:
				frame.modify_var(arg1["frame"], arg1["value"], None)
		except:
			frame.modify_var(arg1["frame"], arg1["value"], None)

	# WRITE ⟨symb⟩
	@staticmethod
	def ipp_write():
		Syntax.check("symb")
		arg1 = Instruction.decomponent_symb("arg1")

		Semantics.check_existence_and_init("symb", arg1)

		variable_to_write = frame.load_symb(arg1)
		if type(variable_to_write) is bool:
			if variable_to_write is True:
				print("true", end="")
			else:
				print("false", end="")
		elif type(variable_to_write) is int or type(variable_to_write) is str:
			print(variable_to_write, end="")
		elif variable_to_write is None:
			print("", end="")
		else:
			print("", end="")

	# CONCAT ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
	@staticmethod
	def ipp_concat():
		Syntax.check("var", "symb", "symb")
		arg1 = Instruction.decompont_var("arg1")
		arg2 = Instruction.decomponent_symb("arg2")
		arg3 = Instruction.decomponent_symb("arg3")

		Semantics.check_existence("var", arg1)
		Semantics.check_existence_and_init("symb", arg2)
		Semantics.check_existence_and_init("symb", arg3)

		Semantics.check_type("symb", arg2, "string")
		Semantics.check_type("symb", arg3, "string")

		concat1 = frame.load_symb(arg2)
		concat2 = frame.load_symb(arg3)

		frame.modify_var(arg1["frame"], arg1["value"], str(concat1) + str(concat2))

	# STRLEN ⟨var⟩ ⟨symb⟩
	@staticmethod
	def ipp_strlen():
		Syntax.check("var", "symb")
		arg1 = Instruction.decompont_var("arg1")
		arg2 = Instruction.decomponent_symb("arg2")

		Semantics.check_existence("var", arg1)
		Semantics.check_existence_and_init("symb", arg2)
		Semantics.check_type("symb", arg2, "string")

		string = str(frame.load_symb(arg2))

		frame.modify_var(arg1["frame"], arg1["value"], len(string))

	# GETCHAR ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
	@staticmethod
	def ipp_getchar():
		Syntax.check("var", "symb", "symb")
		arg1 = Instruction.decompont_var("arg1")
		arg2 = Instruction.decomponent_symb("arg2")
		arg3 = Instruction.decomponent_symb("arg3")

		Semantics.check_existence("var", arg1)
		Semantics.check_existence_and_init("symb", arg2)
		Semantics.check_existence_and_init("symb", arg3)

		Semantics.check_type("symb", arg2, "string")
		Semantics.check_type("symb", arg3, "int")

		string = str(frame.load_symb(arg2))
		char_pos = int(frame.load_symb(arg3))

		if int(char_pos) < 0:
			errorHandel(58, "Error - Semantic error at line" + str(
				Instruction.xml_block.attrib["order"]) + " - position is out of index")

		try:
			frame.modify_var(arg1["frame"], arg1["value"], str(string)[int(char_pos)])
		except IndexError:
			errorHandel(58, "Error - Semantic error at line" + str(
				Instruction.xml_block.attrib["order"]) + " - position is out of index")

	# SETCHAR ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
	@staticmethod
	def ipp_setchat():
		Syntax.check("var", "symb", "symb")
		arg1 = Instruction.decompont_var("arg1")
		arg2 = Instruction.decomponent_symb("arg2")
		arg3 = Instruction.decomponent_symb("arg3")

		Semantics.check_existence_and_init("var", arg1)
		Semantics.check_existence_and_init("symb", arg2)
		Semantics.check_existence_and_init("symb", arg3)

		Semantics.check_type("symb", arg1, "string")
		Semantics.check_type("symb", arg2, "int")
		Semantics.check_type("symb", arg3, "string")

		string = str(frame.load_var_value(arg1["frame"], arg1["value"]))
		index = int(frame.load_symb(arg2))
		new_char = str(frame.load_symb(arg3))

		if index < 0 or index >= len(string) or new_char == "":
			errorHandel(58, "Error - Semantic error at line" + str(
				Instruction.xml_block.attrib["order"]) + " - position is out of index")

		string = string[:index] + new_char[0] + string[index + 1:]

		frame.modify_var(arg1["frame"], arg1["value"], string)

	# TYPE ⟨var⟩ ⟨symb⟩
	@staticmethod
	def ipp_type():
		Syntax.check("var", "symb")
		arg1 = Instruction.decompont_var("arg1")
		arg2 = Instruction.decomponent_symb("arg2")

		Semantics.check_existence("var", arg1)
		Semantics.check_existence("symb", arg2)

		if arg2["type"] == "var":
			var = frame.load_var_value(arg2["frame"], arg2["value"])
			if type(var) is int:
				type_of_symb = "int"
			elif type(var) is str:
				type_of_symb = "string"
			elif type(var) is bool:
				type_of_symb = "bool"
			elif var is None and frame.var_is_init(arg2["frame"], arg2["value"]):
				type_of_symb = "nil"
			else:
				type_of_symb = ""
		else:
			type_of_symb = arg2["type"]

		frame.modify_var(arg1["frame"], arg1["value"], type_of_symb)

	# LABEL ⟨label⟩
	@staticmethod
	def ipp_label():
		Syntax.check("label")
		new_label = Instruction.decompont_label("arg1")
		if labels.exist(new_label):
			errorHandel(52, "Error - semantic error at line " + str(Instruction.xml_block.attrib["order"]) + " - label exist")
		labels[str(new_label)] = int(Instruction.xml_block.attrib["order"])

	# JUMP ⟨label⟩
	@staticmethod
	def ipp_jump():
		Syntax.check("label")
		arg1 = Instruction.decompont_label("arg1")

		Semantics.label_existence(arg1)

		xmlobject.currentOrder = int(labels[arg1])

	# JUMPIFEQ ⟨label⟩ ⟨symb1⟩ ⟨symb2⟩
	@staticmethod
	def ipp_jumpifeq():
		Syntax.check("label", "symb", "symb")
		arg2 = Instruction.decomponent_symb("arg2")
		arg3 = Instruction.decomponent_symb("arg3")
		arg1 = Instruction.decompont_label("arg1")

		Semantics.label_existence(arg1)
		Semantics.check_existence_and_init("symb", arg2)
		Semantics.check_existence_and_init("symb", arg3)

		operand1 = frame.load_symb(arg2)
		operand2 = frame.load_symb(arg3)

		if type(operand1) is not type(operand2):
			if not (operand1 is None or operand2 is None):
				errorHandel(53, "Error - semantic error at line " + str(
					Instruction.xml_block.attrib["order"]) + " - incompatible operand types")

		if operand1 == operand2:
			xmlobject.currentOrder = int(labels[arg1])

	# JUMPIFNEQ ⟨label⟩ ⟨symb1⟩ ⟨symb2⟩
	@staticmethod
	def ipp_jumpifneq():
		Syntax.check("label", "symb", "symb")
		arg2 = Instruction.decomponent_symb("arg2")
		arg3 = Instruction.decomponent_symb("arg3")
		arg1 = Instruction.decompont_label("arg1")

		Semantics.label_existence(arg1)

		Semantics.label_existence(arg1)
		Semantics.check_existence_and_init("symb", arg2)
		Semantics.check_existence_and_init("symb", arg3)

		operand1 = frame.load_symb(arg2)
		operand2 = frame.load_symb(arg3)

		if type(operand1) is not type(operand2):
			if not (operand1 is None or operand2 is None):
				errorHandel(53, "Error - semantic error at line " + str(
					Instruction.xml_block.attrib["order"]) + " - incompatible operand types")

		if operand1 != operand2:
			xmlobject.currentOrder = int(labels[arg1])

	# EXIT ⟨symb⟩
	@staticmethod
	def ipp_exit():  # ano
		Syntax.check("symb")
		arg1 = Instruction.decomponent_symb("arg1")

		Semantics.check_existence_and_init("symb", arg1)
		Semantics.check_type("symb", arg1, "int")

		exit_code = int(frame.load_symb(arg1))

		if 0 <= exit_code <= 49:
			errorHandel(exit_code)
		else:
			errorHandel(57, "Error - semantic error at line " + str(
					Instruction.xml_block.attrib["order"]) + " - invalid exit number")

	# DPRINT ⟨symb⟩
	@staticmethod
	def ipp_dprint():  # ano
		Syntax.check("symb")
		arg1 = Instruction.decomponent_symb("arg1")

		Semantics.check_existence_and_init("symb", arg1)

		variable_to_write = frame.load_symb(arg1)

		print(variable_to_write, file=sys.stderr)

	# BREAK
	@staticmethod
	def ipp_break():  # ano
		Syntax.check()
		print("")
		print("---------------------------------------------------------")
		print("Line:            " + str(act_order), file=sys.stderr)
		print()
		print("GLOBAL FRAME:    " + str(frame["GF"]), file=sys.stderr)
		print("TEMPORARY FRAME: " + str(frame["TF"]), file=sys.stderr)
		print("LOCAL FRAME:     " + str(frame["LF"]), file=sys.stderr)
		print("DATA STACK:      " + str(data_stack), file=sys.stderr)
		print()
		print("LABELS:          " + str(labels), file=sys.stderr)
		print("---------------------------------------------------------")

	# SKIP the instruction
	@staticmethod
	def ipp_skip():
		...


# ----------------------------------------------------------------------------------------------------------------SYNTAX
class Syntax:

	@staticmethod
	def check(arg1=None, arg2=None, arg3=None):
		arguments = locals()
		position = {
			"arg1": 0,
			"arg2": 1,
			"arg3": 2,
		}

		for key, val in list(arguments.items()):
			if arguments[key] is None:
				arguments.pop(key, None)
				position.pop(key, None)

		if Syntax.no_of_arguments_check(len(arguments)) is False:
			errorHandel(32, "Error – Syntactic error in " + str(Instruction.xml_block.attrib["opcode"]) + " - number of arguments")

		actions = {
			"var": Syntax.arg_is_var,
			"symb": Syntax.arg_is_symb,
			"label": Syntax.arg_is_label,
			"type": Syntax.arg_is_type,
		}

		# prostě projedu všechny childnodes a postupně si "odškrkávám", které jsem objevil a mají tam být. poznačuji,
		# že tam byli tím, že je popnu z dict() arguments. Pokud nějaký arguments v dict() zbyte, znamená to, že jsem
		# jej nenašel v cyklu a je tam navíc
		for key, val in list(arguments.items()):
			for childElement in Instruction.xml_block:
				if childElement.tag == key:
					if actions[arguments[key]](childElement) is False:
						errorHandel(32, "Error – Syntactic error in " + str(
							Instruction.xml_block.attrib["opcode"]) + " - invalid format of arguments")
					else:
						arguments.pop(key, None)

		if len(arguments) > 0:
			errorHandel(32, "Error – Syntactic error in " + str(Instruction.xml_block.attrib["opcode"]) + " - number of arguments")

	@staticmethod
	def no_of_arguments_check(no_of_arguments):
		return len(Instruction.xml_block) == no_of_arguments

	@staticmethod
	def arg_is_label(arg):
		return arg.attrib["type"] == "label"

	@staticmethod
	def arg_is_var(arg):
		return arg.attrib["type"] == "var" and (
				arg.text.startswith('GF@') or arg.text.startswith('TF@') or arg.text.startswith('LF@'))

	@staticmethod
	def arg_is_const(arg):
		if arg.attrib["type"] == "int":
			try:
				int(arg.text)
				return True
			except ValueError:
				return False
		elif arg.attrib["type"] == "float":
			fnumber = arg.text
			try:
				float(fnumber)
				return True
			except ValueError:
				try:
					float.fromhex(fnumber)
					return True
				except:
					return False
		elif arg.attrib["type"] == "bool":
			if arg.text == "true" or arg.text == "false":
				return True
			return False
		elif arg.attrib["type"] == "nil":
			if arg.text == "nil":
				return True
			return False
		elif arg.attrib["type"] == "string":
			if arg.text is None:
				arg.text = ""
			to_convert = arg.text
			new_string = ""
			position = 0
			while position < len(to_convert):
				if to_convert[position] == '#':
					break
				if to_convert[position] == "\\":
					if (len(to_convert) - position) < 2:
						errorHandel(32, "Error - invalid format of escape sequence")

					if to_convert[position + 1].isdigit() and to_convert[position + 2].isdigit() and to_convert[
						position + 3].isdigit():
						mychr = chr(int(to_convert[position + 1]) * 100 + int(to_convert[position + 2]) * 10 + int(
							to_convert[position + 3]))
						new_string += mychr
						position += 4
						continue
					else:
						errorHandel(32, "Error - invalid format of escape sequence")
				else:
					new_string += to_convert[position]
					position += 1

			if '\\' in new_string:
				return False

			arg.text = new_string
			return True
		else:
			return False

	@staticmethod
	def arg_is_symb(arg):
		return Syntax.arg_is_const(arg) or Syntax.arg_is_var(arg)

	@staticmethod
	def arg_is_type(arg):
		return arg.attrib["type"] == "type" and (
				arg.text == "string" or arg.text == "int" or arg.text == "bool" or arg.text == "float")


# ------------------------------------------------------------------------------------------------------------------MAIN
def print_help():
	print("\n")
	print("***********************************************************************************************************")
	print("* IPPcode20 - interpret.py")
	print("***********************************************************************************************************")
	print("* Arguments:")
	print("* \t--help")
	print("* \t--source=file - vstupní soubor s XML reprezentací zdrojového kódu")
	print("* \t--input=file soubor se vstupy pro samotnou interpretaci zadaného zdrojového kódu.")
	print("*")
	print("* \tNote: Alespoň jeden z parametrů (--source nebo --input) musí být vždy zadán.")
	print("***********************************************************************************************************")
	print("\n")


def load_labels():
	old_order = xmlobject.currentOrder
	while True:
		tmp = xmlobject.next_instruction()
		if tmp is None:
			xmlobject.currentOrder = old_order
			return
		if tmp.attrib["opcode"].upper() == "LABEL":
			Instruction.xml_block = tmp
			Instruction.ipp_label()


# ----------------------------------------------------------------------------------------------------------------SCRIPT
source_file = None
input_file = None

if len(sys.argv) > 1:
	if sys.argv[1] == "--help":
		print_help()
		errorHandel(0)

	if str(sys.argv[1]).startswith("--source="):
		source_file = str(sys.argv[1])[9:]
		if len(sys.argv) > 2:
			if str(sys.argv[2]).startswith("--input="):
				input_file = str(sys.argv[2])[8:]
	elif str(sys.argv[1]).startswith("--input="):
		input_file = str(sys.argv[1])[8:]
		if len(sys.argv) > 2:
			if str(sys.argv[2]).startswith("--source="):
				source_file = str(sys.argv[2])[9:]
			else:
				source_file = str(sys.stdin)
	else:
		errorHandel(10, "Error - invalid arguments")
else:
	errorHandel(10, "Error - invalid arguments")

if input_file is not None:
	try:
		input_file = open(input_file)
	except:
		errorHandel(11, "Error - Unable to open --input file")

xmlobject = Ippcode(source_file)
frame = Frameholder()
labels = Labelholder()
data_stack = DataStack()
load_labels()

while True:
	a = xmlobject.next_instruction()
	if a is None:
		break
	act_order = a.attrib["order"]
	instructions_switch = {
		"MOVE": Instruction.ipp_move,
		"CREATEFRAME": Instruction.ipp_createframe,
		"PUSHFRAME": Instruction.ipp_pushframe,
		"POPFRAME": Instruction.ipp_popframe,
		"DEFVAR": Instruction.ipp_defvar,
		"CALL": Instruction.ipp_call,
		"RETURN": Instruction.ipp_return,
		"PUSHS": Instruction.ipp_pushs,
		"POPS": Instruction.ipp_pops,
		"CLEARS": Instruction.ipp_clears,
		"ADDS": Instruction.ipp_adds,
		"SUBS": Instruction.ipp_subs,
		"MULS": Instruction.ipp_muls,
		"IDIVS": Instruction.ipp_idivs,
		"DIVS": Instruction.ipp_divs,
		"ANDS": Instruction.ipp_ands,
		"ORS": Instruction.ipp_ors,
		"LTS": Instruction.ipp_lts,
		"GTS": Instruction.ipp_gts,
		"EQS": Instruction.ipp_eqs,
		"NOTS": Instruction.ipp_nots,
		"INT2CHARS": Instruction.ipp_int2chars,
		"STRI2INTS": Instruction.ipp_stri2ints,
		"INT2FLOATS": Instruction.ipp_int2floats,
		"FLOAT2INTS": Instruction.ipp_float2ints,
		"JUMPIFEQS": Instruction.ipp_jumpifeqs,
		"JUMPIFNEQS": Instruction.ipp_jumpifneqs,
		"ADD": Instruction.ipp_add,
		"SUB": Instruction.ipp_sub,
		"MUL": Instruction.ipp_mul,
		"IDIV": Instruction.ipp_idiv,
		"DIV": Instruction.ipp_div,
		"LT": Instruction.ipp_lt,
		"GT": Instruction.ipp_gt,
		"EQ": Instruction.ipp_eq,
		"AND": Instruction.ipp_and,
		"OR": Instruction.ipp_or,
		"NOT": Instruction.ipp_not,
		"INT2CHAR": Instruction.ipp_int2char,
		"STRI2INT": Instruction.ipp_stri2int,
		"INT2FLOAT": Instruction.ipp_int2float,
		"FLOAT2INT": Instruction.ipp_float2int,
		"READ": Instruction.ipp_read,
		"WRITE": Instruction.ipp_write,
		"CONCAT": Instruction.ipp_concat,
		"STRLEN": Instruction.ipp_strlen,
		"GETCHAR": Instruction.ipp_getchar,
		"SETCHAR": Instruction.ipp_setchat,
		"TYPE": Instruction.ipp_type,
		"LABEL": Instruction.ipp_skip,
		"JUMP": Instruction.ipp_jump,
		"JUMPIFEQ": Instruction.ipp_jumpifeq,
		"JUMPIFNEQ": Instruction.ipp_jumpifneq,
		"EXIT": Instruction.ipp_exit,
		"DPRINT": Instruction.ipp_dprint,
		"BREAK": Instruction.ipp_break,
	}
	Instruction.xml_block = a
	try:
		instructions_switch[a.attrib["opcode"].upper()]()
	except KeyError:
		errorHandel(32, "Error – Syntactic error at line " + str(Instruction.xml_block.attrib["order"]) + " - invalid instruction")
