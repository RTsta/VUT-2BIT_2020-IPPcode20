import xml.etree.ElementTree as ET
import sys
import ast # evaluation of True/False in READ


########################################################################
class Ippcode:
    def __init__(self, file):
        try:
            tree = ET.parse(file)
        except ET.ParseError:
            print("Error - unable to read XML file", file=sys.stderr)
            exit(31)
        self.root = tree.getroot()
        self.currentLine = 0

        if not self.header_check():
            # throw error
            print("error - missing header", file=sys.stderr)

    def header_check(self):
        if self.root.attrib['language'] == "IPPcode19":
            return True
        else:
            return False

    def jump_to_instruction(self, line):
        self.currentLine = line-1

    def next_instruction(self):
        if self.currentLine < len(self.root):
            self.currentLine += 1

            for element in self.root:
                if int(element.attrib["order"]) == self.currentLine:
                    return element
            else:
                self.next_instruction()
        else:
            return None


########################################################################
class Variables(dict):
    ...

class Labelholder(dict):
    def __init__(self):
        super(dict, self).__init__()

    def exist(self, name):
        return name in self.keys()

class Frameholder(dict):
    def __init__(self):
        super(dict, self).__init__()
        self["GF"] = Variables()
        self["TF"] = None
        self["LF"] = list()

    def new_lf(self):
        self["LF"].append(Variables())

    def new_tf(self):
        self["TF"] = Variables()

    def is_in_gf(self, var):
        return var in self["GF"].keys()

    def is_in_tf(self, var):
        return var in self["TF"].keys()

    def is_in_lf(self, var):
        return var in self["LF"][-1].keys()

    def modify_in_gf(self, what, new_value):
        self["GF"][what] = new_value

    def modify_in_tf(self, what, new_value):
        self["TF"][what] = new_value

    def modify_in_lf(self, what, new_value):
        self["LF"][-1][what] = new_value

    def frame_exist(self, which):
        return self[which] is not None

    def var_exist(self, where, var_name):
        if where == "LF" and (self["LF"] is None or self["LF"] == []):
            print("Error - Semantic error at line "+str(Instruction.xml_block.attrib["order"])+" - Local frame doesnt exist", file=sys.stderr)
            return False

        is_in_switch = {"GF": self.is_in_gf, "TF": self.is_in_tf, "LF": self.is_in_lf}
        if is_in_switch[where](var_name) is False:
            print("Error - Semantic error at line "+str(Instruction.xml_block.attrib["order"])+" - variable doesnt exist", file=sys.stderr)
            return False
        return True

    def load_var_value(self, where, var_name):
        if not self.var_exist(where, var_name):
            return
        if where == "LF":
            return self["LF"][-1][var_name]
        else:
            return self[where][var_name]

    def modify_var(self, where, var_name, new_value):
        if not self.var_exist(where, var_name):
            return
        modify_in_switch = {"GF": self.modify_in_gf, "TF": self.modify_in_tf, "LF": self.modify_in_lf, }
        modify_in_switch[where](var_name, new_value)


########################################################################
class Instruction:
    xml_block = None

    # arg [type:var     |frame:GF   |value:promena] <--> GF@promena
    # arg [type:int     |frame:""   |value:5      ] <--> int@5
    # arg [type:string  |frame:""   |value:"ahoj" ] <--> string@ahoj
    @staticmethod
    def decomponent_symb(arg_no):
        arguments = {"arg1": 0, "arg2": 1, "arg3": 2}

        symb = {"type": Instruction.xml_block[arguments[arg_no]].attrib["type"], "frame": "", "value": ""}

        if Syntax.arg_is_var(Instruction.xml_block[arguments[arg_no]]):
            return Instruction.decompont_var(arg_no)
        elif Syntax.arg_is_const(Instruction.xml_block[arguments[arg_no]]):
            symb["value"] = Instruction.xml_block[arguments[arg_no]].text
        return symb

    @staticmethod
    def decompont_var(arg_no):
        arguments = {"arg1": 0, "arg2": 1, "arg3": 2}
        var = {"type": Instruction.xml_block[arguments[arg_no]].attrib["type"],
               "frame": Instruction.xml_block[arguments[arg_no]].text[:2],
               "value": Instruction.xml_block[arguments[arg_no]].text[3:]}
        return var

    # MOVE ⟨var⟩ ⟨symb⟩
    @staticmethod
    def ipp_move():                                                                                 # ano
        Syntax.check("var", "symb")
        arg1 = Instruction.decompont_var("arg1")
        arg2 = Instruction.decomponent_symb("arg2")

        if not frame.var_exist(arg1["frame"], arg1["value"]):
            return

        frame.modify_var(arg1["frame"], arg1["value"], arg2["value"])

    # CREATEFRAME
    @staticmethod
    def ipp_createframe():                                                                          # ano
        Syntax.check()
        frame.new_tf()

    # PUSHFRAME
    @staticmethod
    def ipp_pushframe():                                                                            # ano
        Syntax.check()
        if not frame.frame_exist("TF"):
            print("Error – Semantic error at line "+str(Instruction.xml_block.attrib["order"])+" - frame doesnt not exist", file=sys.stderr)
            return exit(55)

        frame["LF"].append(frame["TF"])

    # POPFRAME
    @staticmethod
    def ipp_popframe():                                                                             # ano
        Syntax.check()
        if not frame["LF"]:
            print("Error – Semantic error at line"+str(Instruction.xml_block.attrib["order"])+" - frame doesnt not exist", file=sys.stderr)
            return exit(55)
        frame["TF"] = frame["LF"].pop()

    # DEFVAR ⟨var⟩
    @staticmethod
    def ipp_defvar():
        Syntax.check("var")
        arg1 = Instruction.decompont_var("arg1")

        if not frame.frame_exist(arg1["frame"]):
            print("Error – Semantic error at line"+str(Instruction.xml_block.attrib["order"])+" - frame doesnt not exist", file=sys.stderr)
            return

        if arg1["frame"] == "GF" or arg1["frame"] == "TF":
            frame[arg1["frame"]][Instruction.xml_block[0].text[3:]] = None
        elif arg1["frame"] == "LF":
            frame[arg1["frame"]][-1][Instruction.xml_block[0].text[3:]] = None

    # CALL ⟨label⟩
    @staticmethod
    def ipp_call():
        Syntax.check("label")

    # RETURN
    @staticmethod
    def ipp_return():
        Syntax.check()

    # PUSHS ⟨symb⟩
    @staticmethod
    def ipp_pushs():
        Syntax.check("symb")

    # POPS ⟨var⟩
    @staticmethod
    def ipp_pops():
        Syntax.check("var")

    @staticmethod
    def ipp_arithmetic(operator):
        Syntax.check("var", "symb", "symb")
        arg1 = Instruction.decompont_var("arg1")
        arg2 = Instruction.decomponent_symb("arg2")
        arg3 = Instruction.decomponent_symb("arg3")

        operand1 = arg2["value"]
        operand2 = arg3["value"]

        if arg2["type"] == "var":
            operand1 = frame.load_var_value(arg2["frame"], arg2["value"])
        if arg3["type"] == "var":
            operand2 = frame.load_var_value(arg3["frame"], arg3["value"])

        operation = {
            "add": int(operand1)+int(operand2),
            "sub": int(operand1)-int(operand2),
            "mul": int(operand1)*int(operand2),
            "idiv": int(operand1)/int(operand2),
        }

        frame.modify_var(arg1["frame"], arg1["value"], operation[operator])

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

    # LT / GT / EQ ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
    @staticmethod
    def ipp_lt_gt_eq(operator):
        Syntax.check("var", "symb", "symb")
        arg1 = Instruction.decompont_var("arg1")
        arg2 = Instruction.decomponent_symb("arg2")
        arg3 = Instruction.decomponent_symb("arg3")

        operand1 = arg2["value"]
        operand2 = arg3["value"]

        if arg2["type"] == "var":
            operand1 = frame.load_var_value(arg2["frame"], arg2["value"])
        if arg3["type"] == "var":
            operand2 = frame.load_var_value(arg3["frame"], arg3["value"])

        operation = {
            "LT": int(operand1) < int(operand2),
            "GT": int(operand1) > int(operand2),
            "EQ": operand1 == operand2
        }
        frame.modify_var(arg1["frame"], arg1["value"], operation[operator])

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

        operand1 = arg2["value"]
        operand2 = arg3["value"]

        if arg2["type"] == "var":
            operand1 = frame.load_var_value(arg2["frame"], arg2["value"])

        if arg3["type"] == "var":
            operand2 = frame.load_var_value(arg3["frame"], arg3["value"])

        operation = {
            "LT": int(operand1) and int(operand2),
            "GT": int(operand1) or int(operand2),
            "EQ": operand1 == operand2
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
        Instruction.ipp_logic_op("not")

    # INT2CHAR ⟨var⟩ ⟨symb⟩
    @staticmethod
    def ipp_int2char():
        Syntax.check("var", "symb")
        arg1 = Instruction.decompont_var("arg1")
        arg2 = Instruction.decomponent_symb("arg2")

        if not frame.var_exist(arg1["frame"], arg1["value"]):
            return

        if arg2["type"] == "var":
            int2char = frame.load_var_value(arg2["frame"], arg2["value"])
        else:
            int2char = arg2["value"]

        try:
            int2char = chr(int2char)
            frame.modify_var(arg1["frame"], arg1["value"], int2char)
        except ValueError:
            print("Error - Semantic error at line"+str(Instruction.xml_block.attrib["order"])+" - value is not a char", file=sys.stderr)

    # STRI2INT ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
    @staticmethod
    def ipp_stri2int():
        Syntax.check("var", "symb", "symb")
        arg1 = Instruction.decompont_var("arg1")
        arg2 = Instruction.decomponent_symb("arg2")
        arg3 = Instruction.decomponent_symb("arg3")

        if not frame.var_exist(arg1["frame"], arg1["value"]):
            return

        if arg2["type"] == "var":
            stri2int = frame.load_var_value(arg2["frame"], arg2["value"])
        else:
            stri2int = arg2["value"]

        if arg3["type"] == "var":
            char_pos = frame.load_var_value(arg3["frame"], arg3["value"])
        else:
            char_pos = arg3["value"]
        try:
            result = ord(stri2int[char_pos])
        except TypeError:
            exit(58)
        frame.modify_var(arg1["frame"], arg1["value"], result)

    # READ ⟨var⟩ ⟨type⟩
    @staticmethod
    def ipp_read():
        Syntax.check("var", "type")
        arg1 = Instruction.decompont_var("arg1")
        type_of_input = Instruction.xml_block[1].text
        read = input()
        type_switch = {
            "int": int,
            "string": str,
            "bool": ast.literal_eval,
        }
        frame.modify_var(arg1["frame"], arg1["value"], type_switch[type_of_input](read))

    # WRITE ⟨symb⟩
    @staticmethod
    def ipp_write():
        Syntax.check("symb")
        arg1 = Instruction.decomponent_symb("arg1")

        if arg1["frame"] == "":
            variable_to_write = arg1["value"]
        else:
            variable_to_write = frame.load_var_value(arg1["frame"], arg1["value"])

        print(variable_to_write)

    # CONCAT ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
    @staticmethod
    def ipp_concat():
        Syntax.check("var", "symb", "symb")
        arg1 = Instruction.decompont_var("arg1")
        arg2 = Instruction.decomponent_symb("arg2")
        arg3 = Instruction.decomponent_symb("arg3")

        if not frame.var_exist(arg1["frame"], arg1["value"]):
            return

        if arg2["type"] == "var":
            concat1 = frame.load_var_value(arg2["frame"], arg2["value"])
        else:
            concat1 = arg2["value"]

        if arg3["type"] == "var":
            concat2 = frame.load_var_value(arg3["frame"], arg3["value"])
        else:
            concat2 = arg3["value"]

        frame.modify_var(arg1["frame"], arg1["value"], str(concat1) + str(concat2))

    # STRLEN ⟨var⟩ ⟨symb⟩
    @staticmethod
    def ipp_strlen():
        Syntax.check("var", "symb")
        arg1 = Instruction.decompont_var("arg1")
        arg2 = Instruction.decomponent_symb("arg2")

        if not frame.var_exist(arg1["frame"], arg1["value"]):
            return

        if arg2["type"] == "var":
            string = frame.load_var_value(arg2["frame"], arg2["value"])
        else:
            string = arg2["value"]

        frame.modify_var(arg1["frame"], arg1["value"], len(str(string)))

    # GETCHAR ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
    @staticmethod
    def ipp_getchar():
        Syntax.check("var", "symb", "symb")
        arg1 = Instruction.decompont_var("arg1")
        arg2 = Instruction.decomponent_symb("arg2")
        arg3 = Instruction.decomponent_symb("arg3")

        if not frame.var_exist(arg1["frame"], arg1["value"]):
            return

        if arg2["type"] == "var":
            string = frame.load_var_value(arg2["frame"], arg2["value"])
        else:
            string = arg2["value"]

        if arg3["type"] == "var":
            char_pos = frame.load_var_value(arg3["frame"], arg3["value"])
        else:
            char_pos = arg3["value"]

        frame.modify_var(arg1["frame"], arg1["value"], str(string)[int(char_pos)])

    # SETCHAR ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
    @staticmethod
    def ipp_setchat():
        Syntax.check("var", "symb", "symb")
        arg1 = Instruction.decompont_var("arg1")
        arg2 = Instruction.decomponent_symb("arg2")
        arg3 = Instruction.decomponent_symb("arg3")

        if not frame.var_exist(arg1["frame"], arg1["value"]):
            return

        if arg2["type"] == "var":
            position = frame.load_var_value(arg2["frame"], arg2["value"])
        else:
            position = arg2["value"]

        if arg3["type"] == "var":
            new_char = frame.load_var_value(arg3["frame"], arg3["value"])
        else:
            new_char = arg3["value"]

        string = frame.load_var_value(arg1["frame"], arg1["value"])
        string[int(position)] = new_char[0]
        frame.modify_var(arg1["frame"], arg1["value"], string)

    # TYPE ⟨var⟩ ⟨symb⟩
    @staticmethod
    def ipp_type():
        Syntax.check("var", "symb")
        arg1 = Instruction.decompont_var("arg1")
        arg2 = Instruction.decomponent_symb("arg2")

        if arg2["type"] == "var":
            type_of_symb = frame.load_var_value(arg2["frame"], arg2["value"])
            if type(type_of_symb) is int:
                type_of_symb = "int"
            elif type(type_of_symb) is str:
                type_of_symb = "string"
            elif type(type_of_symb) is bool:
                type_of_symb = "bool"
            else:
                type_of_symb = "nil"
        else:
            type_of_symb = arg2["type"]

        frame.modify_var(arg1["frame"], arg1["value"], type_of_symb)

    # LABEL ⟨label⟩
    @staticmethod
    def ipp_label():
        Syntax.check("label")

        new_label = Instruction.xml_block[0].text
        if labels.exist(new_label):
            print("Error - semantic error at line "+str(Instruction.xml_block.attrib["order"])+" - label exist", file=sys.stderr)
            exit(52)

        labels[str(new_label)] = int(Instruction.xml_block.attrib["order"])
        print(labels)

    # JUMP ⟨label⟩
    @staticmethod
    def ipp_jump():
        Syntax.check("label")

        if not labels.exist(Instruction.xml_block[0].text):
            print("Error - semantic error at line " + str(Instruction.xml_block.attrib["order"]) + " - label does not exist", file=sys.stderr)
            exit(-1)

        xmlobject.currentLine = int(labels[str(Instruction.xml_block[0].text)])



    # JUMPIFEQ ⟨label⟩ ⟨symb1⟩ ⟨symb2⟩
    @staticmethod
    def ipp_jumpifeq():
        Syntax.check("label", "symb", "symb")
        arg2 = Instruction.decomponent_symb("arg2")
        arg3 = Instruction.decomponent_symb("arg3")

        if not labels.exist(Instruction.xml_block[0].text):
            print("Error - semantic error at line " + str(Instruction.xml_block.attrib["order"]) + " - label does not exist", file=sys.stderr)
            exit(-1)

            operand1 = arg2["value"]
            operand2 = arg3["value"]

            if arg2["type"] == "var":
                operand1 = frame.load_var_value(arg2["frame"], arg2["value"])

            if arg3["type"] == "var":
                operand2 = frame.load_var_value(arg3["frame"], arg3["value"])

            if type(operand1) is not type(operand2):
                exit(53)

            if not labels.exist(Instruction.xml_block[0].text):
                print("Error - semantic error at line " + str(
                    Instruction.xml_block.attrib["order"]) + " - label does not exist", file=sys.stderr)
                exit(-1)

            if operand1 == operand2:
                xmlobject.currentLine = int(labels[str(Instruction.xml_block[0].text)])


    # JUMPIFNEQ ⟨label⟩ ⟨symb1⟩ ⟨symb2⟩
    @staticmethod
    def ipp_jumpifneq():
        Syntax.check("label", "symb", "symb")
        arg2 = Instruction.decomponent_symb("arg2")
        arg3 = Instruction.decomponent_symb("arg3")

        if not labels.exist(Instruction.xml_block[0].text):
            print("Error - semantic error at line " + str(Instruction.xml_block.attrib["order"]) + " - label does not exist", file=sys.stderr)
            exit(-1)

            operand1 = arg2["value"]
            operand2 = arg3["value"]

            if arg2["type"] == "var":
                operand1 = frame.load_var_value(arg2["frame"], arg2["value"])

            if arg3["type"] == "var":
                operand2 = frame.load_var_value(arg3["frame"], arg3["value"])

            if type(operand1) is not type(operand2):
                exit(53)

            if not labels.exist(Instruction.xml_block[0].text):
                print("Error - semantic error at line " + str(
                    Instruction.xml_block.attrib["order"]) + " - label does not exist", file=sys.stderr)
                exit(-1)

            if operand1 != operand2:
                xmlobject.currentLine = int(labels[str(Instruction.xml_block[0].text)])

    # EXIT ⟨symb⟩
    @staticmethod
    def ipp_exit():                                                                             # ano
        Syntax.check("symb")
        arg1 = Instruction.decomponent_symb("arg1")

        if arg1["type"] == "var":
            exit_code = frame.load_var_value(arg1["frame"], arg1["value"])
        else:
            exit_code = arg1["value"]

        if 0 <= int(exit_code) <= 49:
            exit(exit_code)
        else:
            exit(57)

    # DPRINT ⟨symb⟩
    @staticmethod
    def ipp_dprint():                                                                           # ano
        Syntax.check("symb")
        arg1 = Instruction.decomponent_symb("arg1")

        if arg1["frame"] == "":
            variable_to_write = arg1["value"]
        else:
            variable_to_write = frame.load_var_value(arg1["frame"], arg1["value"])

        print(variable_to_write, file=sys.stderr)

    # BREAK
    @staticmethod
    def ipp_break():                                                                            # ano
        Syntax.check()
        print("")
        print("---------------------------------------------------------")
        print("Line:            " + str(act_order), file=sys.stderr)
        print("GLOBAL FRAME:    " + str(frame["GF"]), file=sys.stderr)
        print("TEMPORARY FRAME: " + str(frame["TF"]), file=sys.stderr)
        print("LOCAL FRAME:     " + str(frame["LF"]), file=sys.stderr)
        print("---------------------------------------------------------")

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
            print("Error – Syntactic error in " + str(Instruction.xml_block.attrib["opcode"]) + " - number of arguments", file=sys.stderr)

        actions = {
            "var": Syntax.arg_is_var,
            "symb": Syntax.arg_is_symb,
            "label": Syntax.arg_is_label,
            "type": Syntax.arg_is_type,
        }
        for x in arguments:
            if actions[arguments[x]](Instruction.xml_block[position[x]]) is False:
                print("Error – Syntactic error in " + str(Instruction.xml_block.attrib["opcode"]) + " - invalid format of arguments", file=sys.stderr)

    @staticmethod
    def no_of_arguments_check(no_of_arguments):
        return len(Instruction.xml_block) == no_of_arguments

    @staticmethod
    def arg_is_label(arg):
        return arg.attrib["type"] == "label"

    @staticmethod
    def arg_is_var(arg):
            return arg.attrib["type"] == "var" and (arg.text.startswith('GF@') or arg.text.startswith('TF@') or arg.text.startswith('LF@'))

    @staticmethod
    def arg_is_const(arg):
        if arg.attrib["type"] == "int":
            try:
                int(arg.text)
                return True
            except ValueError:
                return False
        elif arg.attrib["type"] == "bool":
            if arg.text == "true" or arg.text == "false":
                return True
            return False
        elif arg.attrib["type"] == "string":
            return True
        else:
            return False

    @staticmethod
    def arg_is_symb(arg):
        return Syntax.arg_is_const(arg) or Syntax.arg_is_var(arg)

    @staticmethod
    def arg_is_type(arg):
        return arg.attrib["type"] == "type" and (
                    arg.text == "string" or arg.text == "int" or arg.text == "bool")


########################################################################
xmlobject = Ippcode('discord_test/debug/debug.xml')
frame = Frameholder()
labels = Labelholder()


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
        "ADD": Instruction.ipp_add,
        "SUB": Instruction.ipp_sub,
        "MUL": Instruction.ipp_mul,
        "IDIV": Instruction.ipp_idiv,
        "LT": Instruction.ipp_lt_gt_eq,
        "GT": Instruction.ipp_lt_gt_eq,
        "EQ": Instruction.ipp_lt_gt_eq,
        "AND": Instruction.ipp_logic_op,
        "OR": Instruction.ipp_logic_op,
        "NOT": Instruction.ipp_logic_op,
        "INT2CHAR": Instruction.ipp_int2char,
        "STRI2INT": Instruction.ipp_stri2int,
        "READ": Instruction.ipp_read,
        "WRITE": Instruction.ipp_write,
        "CONCAT": Instruction.ipp_concat,
        "STRLEN": Instruction.ipp_strlen,
        "GETCHAR": Instruction.ipp_getchar,
        "SETCHAR": Instruction.ipp_setchat,
        "TYPE": Instruction.ipp_type,
        "LABEL": Instruction.ipp_label,
        "JUMP": Instruction.ipp_jump,
        "JUMPIFEQ": Instruction.ipp_jumpifeq,
        "JUMPIFNEQ": Instruction.ipp_jumpifneq,
        "EXIT": Instruction.ipp_exit,
        "DPRINT": Instruction.ipp_dprint,
        "BREAK": Instruction.ipp_break,
                }
    Instruction.xml_block = a
    instructions_switch[a.attrib["opcode"].upper()]()
