import string

DIGITS = "01234567890"
LETTERS = string.ascii_letters + "_"


class TT:
    INT = "INT"
    FLOAT = "FLOAT"
    BOOL = "BOOL"
    STRING = "STRING"
    IDENTIFIER = "IDENTIFIER"
    KEYWORD = "KEYWORD"
    EQ = "EQ"
    PLUS = "PLUS"
    MINUS = "MINUS"
    MULT = "MULT"
    DIV = "DIV"
    FDIV = "FDIV"
    MODU = "MODU"
    POW = "POW"
    LSQUARE = "LSQUARE"
    RSQUARE = "RSQUARE"
    LPAR = "LPAR"
    RPAR = "RPAR"
    LCURLY = "LCURLY"
    RCURLY = "RCURLY"
    EE = "EE"
    NE = "NE"
    LT = "LT"
    GT = "GT"
    LTE = "LTE"
    GTE = "GTE"
    COMMA = "COMMA"
    NEWLINE = "NEWLINE"
    EOF = "EOF"
    COLON = "COLON"
    SPACE = "SPACE"

    SINGLE_CHAR_TOK = {
        "+": PLUS,
        "-": MINUS,
        "%": MODU,
        "(": LPAR,
        ")": RPAR,
        "[": LSQUARE,
        "]": RSQUARE,
        "{": LCURLY,
        "}": RCURLY,        
        ",": COMMA,
        ":": COLON,
    }


NON_VALUE_TOKS = {
    TT.EQ: "=",
    TT.PLUS: "+",
    TT.MINUS: "-",
    TT.MULT: "*",
    TT.DIV: "/",
    TT.FDIV: "//",
    TT.MODU: "%",
    TT.POW: "**",
    TT.LSQUARE: "[",
    TT.RSQUARE: "]",
    TT.LPAR: "(",
    TT.LCURLY: "{",
    TT.RCURLY: "}",
    TT.RPAR: ")",
    TT.EE: "==",
    TT.NE: "!=",
    TT.LT: "<",
    TT.GT: ">",
    TT.LTE: "<=",
    TT.GTE: ">=",
    TT.COMMA: ",",
    TT.COLON: ":",
    TT.SPACE: " ",
}

KEYWORDS = [
    "and",
    "or",
    "not",
    "if",
    "elif",
    "else",
    "for",
    "to",
    "step",
    "while",
    "func",
    "break",
    "continue",
    "return",
]


class Position:
    def __init__(self, idx: int, ln: int, col: int, fn: str, ftxt: str):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self, current_char=None):
        self.idx += 1
        self.col += 1

        if current_char == "\n":
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)


def string_with_arrows(text, pos_start, pos_end):
    result = ""

    # Calculate indices
    idx_start = max(text.rfind("\n", 0, pos_start.idx), 0)
    idx_end = text.find("\n", idx_start + 1)
    if idx_end < 0:
        idx_end = len(text)

    # Generate each line
    line_count = pos_end.ln - pos_start.ln + 1
    for i in range(line_count):
        # Calculate line columns
        line = text[idx_start:idx_end]
        col_start = pos_start.col if i == 0 else 0
        col_end = pos_end.col if i == line_count - 1 else len(line) - 1

        # Append to result
        result += line + "\n"
        result += " " * col_start + "^" * (col_end - col_start)

        # Re-calculate indices
        idx_start = idx_end
        idx_end = text.find("\n", idx_start + 1)
        if idx_end < 0:
            idx_end = len(text)

    return result.replace("\t", "")


class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent: dict = parent

    def get(self, name):
        value = self.symbols.get(name)
        if value is None and self.parent:
            return self.parent.get(name)
        return value

    def set(self, name: str, value):
        self.symbols[name] = value

    def remove(self, name):
        del self.symbols[name]


class Context:
    def __init__(self, display_name: str, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table: SymbolTable = None


class RTResult:
    def __init__(self):
        self.reset()

    def reset(self):
        self.value = None
        self.error = None
        self.function_return_value = None
        self.loop_should_continue = False
        self.loop_should_break = False

    def register(self, res):
        res: RTResult = res
        self.function_return_value = res.function_return_value
        self.loop_should_continue = res.loop_should_continue
        self.loop_should_break = res.loop_should_break
        if res.error:
            self.error = res.error
        return res.value

    def success(self, value):  # sourcery skip: class-extract-method
        self.reset()
        self.value = value
        return self

    def success_return(self, value):
        self.reset()
        self.function_return_value = value
        return self

    def success_continue(self):
        self.reset()
        self.loop_should_continue = True
        return self

    def success_break(self):
        self.reset()
        self.loop_should_break = True
        return self

    def faliure(self, error):
        self.reset()
        self.error = error
        return self

    def should_return(self):
        return (
            self.error
            or self.function_return_value
            or self.loop_should_continue
            or self.loop_should_break
        )


class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.advance_count = 0
        self.to_reverse_count = 0

    def register_advancement(self):
        self.advance_count += 1

    def register(self, res):
        self.advance_count += res.advance_count
        if res.error:
            self.error = res.error
        return res.node

    def try_register(self, res):
        if res.error:
            self.to_reverse_count = res.advance_count
            return None
        return self.register(res)

    def success(self, node):
        self.node = node
        return self

    def faliure(self, error):
        if not self.error or self.advance_count == 0:
            self.error = error
        return self
