from .utils import Position, TT, DIGITS, LETTERS, KEYWORDS
from .errors import Error, IllegalCharError, ExpectedCharError

LETTERS_DIGITS = LETTERS + DIGITS

class Token:
    def __init__(
        self,
        type: str,
        value=None,
        pos_start: Position = None,
        pos_end: Position = None,
    ):
        self.type = type
        self.value = value
        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end

    def matches(self, type, value):
        return self.type == type and self.value == value

    def __repr__(self):
        if self.value is not None:
            return f"{self.type}:{self.value}"
        return f"{self.type}"


class Lexer:
    def __init__(self, text: str, fn: str):
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.found_indent = False
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = (
            self.text[self.pos.idx] if self.pos.idx < len(self.text) else None
        )

    def make_tokens(self) -> tuple[list[Token], Error]:  # sourcery no-metrics
        tokens = []

        while self.current_char is not None:
            match self.current_char:
                case "#":
                    self.skip_comment()
                case char if char in {" ", "\t"}:
                    if not self.found_indent and (self.pos.idx == 0 or self.text[self.pos.idx - 1] == "\n"):
                        tokens.append(self.catch_indents())
                        self.found_indent = True
                    else:
                        self.advance()
                case "\n":
                    tokens.append(Token(TT.NEWLINE, "\n", self.pos.copy()))
                    self.found_indent = False
                    self.advance()
                case num if num in DIGITS:
                    self.found_indent = False
                    tokens.append(self.make_number())
                    self.found_indent = False
                case letter if letter in LETTERS:
                    tokens.append(self.make_identifier())
                case ("'"|'"') as quote:
                    self.found_indent = False
                    string, error = self.make_string(quote)
                    if error:
                        return [], error 
                    tokens.append(string)
                case "!":
                    self.found_indent = False
                    token, error = self.make_not_equals()
                    if error:
                        return [], error
                    tokens.append(token)
                case char if char in TT.SINGLE_CHAR_TOK:
                    self.found_indent = False
                    tokens.append(Token(TT.SINGLE_CHAR_TOK[char], char, pos_start=self.pos.copy()))
                    self.advance()
                case "*":
                    self.found_indent = False
                    tokens.append(self.make_double_char_token(TT.MULT, TT.POW, "*"))
                case "/":
                    self.found_indent = False
                    tokens.append(self.make_double_char_token(TT.DIV, TT.FDIV, "/"))
                case "=":
                    self.found_indent = False
                    tokens.append(self.make_double_char_token(TT.EQ, TT.EE, "="))
                case "=":
                    self.found_indent = False
                    tokens.append(self.make_double_char_token(TT.EQ, TT.EE, "="))
                case "<":
                    self.found_indent = False
                    tokens.append(self.make_double_char_token(TT.LT, TT.LTE, "="))
                case ">":
                    self.found_indent = False
                    tokens.append(self.make_double_char_token(TT.GT, TT.GTE, "="))
                case _:
                    self.found_indent = False
                    pos_start = self.pos.copy()
                    char = self.current_char
                    self.advance()
                    return [], IllegalCharError(pos_start, self.pos, f'"{char}"')

        tokens.append(Token(TT.EOF, pos_start=self.pos))
        return tokens, None

    def make_number(self) -> Token:
        num_str = ""
        dot_count = 0
        pos_start = self.pos.copy()

        while self.current_char is not None and self.current_char in DIGITS + ".":
            if self.current_char == ".":
                if dot_count == 1:
                    break
                dot_count += 1
            num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(TT.INT, int(num_str), pos_start, self.pos)
        else:
            return Token(TT.FLOAT, float(num_str), pos_start, self.pos)

    def make_identifier(self):
        id_str = ""
        pos_start = self.pos.copy()

        while self.current_char is not None and self.current_char in LETTERS_DIGITS:
            id_str += self.current_char
            self.advance()

        if id_str in KEYWORDS:
            tok_type = TT.KEYWORD
        elif id_str in {"true", "false"}:
            tok_type = TT.BOOL
            id_str = id_str == "true"
        else:
            tok_type = TT.IDENTIFIER

        return Token(tok_type, id_str, pos_start, self.pos)

    def make_not_equals(self) -> tuple[Token, Error]:
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == "=":
            self.advance()
            return Token(TT.NE, pos_start=pos_start, pos_end=self.pos), None

        self.advance()
        return None, ExpectedCharError(pos_start, self.pos, "'=' (after '!')")

    def make_double_char_token(self, default_type, new_type, second_char):
        pos_start = self.pos.copy()
        self.advance()
        tok_type = default_type

        if self.current_char == second_char:
            self.advance()
            tok_type = new_type

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_string(self, quote:str):
        string = ""
        pos_start = self.pos.copy()
        self.advance()

        escape_characters = {
            "n": "\n",
            "t": "\t",
            "'": "\'",
            "\"": "\"",
            "\\": "\\"
        }

        while self.current_char != "\"" and self.current_char is not None:
            if self.current_char == "\\":
                self.advance()
                string += escape_characters.get(self.current_char, self.current_char)
            else:
                string += self.current_char
            self.advance()

            if self.current_char == quote:
                break
        else:
            if self.current_char != "\"":
                return [], ExpectedCharError(pos_start, self.pos, f"'{quote}'")

        self.advance()
        return Token(TT.STRING, string, pos_start, self.pos.copy()), None

    def skip_comment(self):
        self.advance()

        while self.current_char not in {"\n", None}:
            self.advance()

        self.advance()

    def catch_indents(self):
        count = 0
        pos_start = self.pos.copy()
        while self.current_char in {" ", "\t"}:
            count += 4 if self.current_char == "\t" else 1
            self.advance()
        return Token(TT.SPACE, count, pos_start, self.pos.copy())