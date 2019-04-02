import xml.etree.ElementTree as ET
import sys


########################################################################
class Ippcode:
    """docstring for Ippcode"""
    def __init__(self, file):
        tree = ET.parse(file) 
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

    def next_instruction(self):
        if self.currentLine < len(self.root):
            self.currentLine += 1

            for element in self.root:
                if int(element.attrib["order"]) == self.currentLine:
                    return element
        else:
            return None




########################################################################
class Variables(dict):
    ...


class Frameholder(dict):
    def __init__(self):
        super(dict, self).__init__()
        self["GF"] = Variables()
        self["TF"] = None
        self["LF"] = list()

    def new_lf(self):
        self["LF"].append(Variables())

########################################################################
class Instruction:
    xml_block = None
    frames = Frameholder() 

    # MOVE ⟨var⟩ ⟨symb⟩
    @staticmethod
    def ipp_move():
        Syntax.check("var","symb")
    # CREATEFRAME
    @staticmethod
    def ipp_createframe():
        Syntax.check()

    # PUSHFRAME
    @staticmethod
    def ipp_pushframe():
        Syntax.check()

    # POPFRAME
    @staticmethod
    def ipp_popframe():
        Syntax.check()

    # DEFVAR ⟨var⟩
    @staticmethod
    def ipp_defvar():
        Syntax.check("var")

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

    # ADD ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
    @staticmethod
    def ipp_add():
        Syntax.check("var", "symb", "symb")

    # SUB ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
    @staticmethod
    def ipp_sub():
        Syntax.check("var", "symb", "symb")

    # MUL ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
    @staticmethod
    def ipp_mul():
        Syntax.check("var", "symb", "symb")

    # IDIV ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
    @staticmethod
    def ipp_idiv():
        Syntax.check("var", "symb", "symb")

    # LT / GT / EQ ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
    @staticmethod
    def ipp_lt_gt_eq():
        Syntax.check("var", "symb", "symb")

    # AND / OR / NOT ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
    @staticmethod
    def ipp_logic_op():
        ... # Syntax.check("var", "symb", "symb")

    # INT2CHAR ⟨var⟩ ⟨symb⟩
    @staticmethod
    def ipp_int2char():
        Syntax.check("var","symb")

    # STRI2INT ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
    @staticmethod
    def ipp_stri2int():
        Syntax.check("var", "symb", "symb")

    # READ ⟨var⟩ ⟨type⟩
    @staticmethod
    def ipp_read():
        Syntax.check("var", "type")

    # WRITE ⟨symb⟩
    @staticmethod
    def ipp_write():
        Syntax.check("symb")

    # CONCAT ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
    @staticmethod
    def ipp_concat():
        Syntax.check("var", "symb", "symb")

    # STRLEN ⟨var⟩ ⟨symb⟩
    @staticmethod
    def ipp_strlen():
        Syntax.check("var", "symb")

    # GETCHAR ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
    @staticmethod
    def ipp_getchar():
        Syntax.check("var", "symb", "symb")

    # SETCHAR ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
    @staticmethod
    def ipp_setchat():
        Syntax.check("var", "symb", "symb")

    # TYPE ⟨var⟩ ⟨symb⟩
    @staticmethod
    def ipp_type():
        Syntax.check("var", "symb")

    # LABEL ⟨label⟩
    @staticmethod
    def ipp_label():
        Syntax.check("label")

    # JUMP ⟨label⟩
    @staticmethod
    def ipp_jump():
        Syntax.check()

    # JUMPIFEQ ⟨label⟩ ⟨symb1⟩ ⟨symb2⟩
    @staticmethod
    def ipp_jumpifeq():
        Syntax.check("label", "symb", "symb")

    # JUMPIFNEQ ⟨label⟩ ⟨symb1⟩ ⟨symb2⟩
    @staticmethod
    def ipp_jumpifneq():
        Syntax.check("label", "symb", "symb")

    # EXIT ⟨symb⟩
    @staticmethod
    def ipp_exit():
        Syntax.check("symb")

    # DPRINT ⟨symb⟩
    @staticmethod
    def ipp_dprint():
        Syntax.check("symb")

    # BREAK
    @staticmethod
    def ipp_break():
        Syntax.check()


class Syntax:

    @staticmethod
    def check(arg1=None, arg2=None, arg3=None):
        arguments = locals()
        position ={
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
        return arg.attrib["type"] == "label" and arg.text != ""

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
xmlobject = Ippcode('discord_test/parse-only/Basic_tests/EveryInstruction.out')
Instruction.variables = Variables()

while True:
    a = xmlobject.next_instruction()
    if a is None:
        break

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
