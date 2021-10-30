from .utils.errors import InvalidSyntaxError
from .lexer import Token
from .utils.nodes import *
from .utils.utils import NON_VALUE_TOKS, TT, ParseResult, Token

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.tok_idx = -1
        self.indent_level = 0
        self.local_indent = 0
        self.advance()

    def advance(self):
        self.tok_idx += 1
        self.update_current_tok()
        return self.current_tok

    def reverse(self, amount=1):
        self.tok_idx -= amount
        self.update_current_tok()
        return self.current_tok

    def update_current_tok(self):
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]

    @property
    def peek(self) -> Token:
        return self.tokens[self.tok_idx + 1] if self.tok_idx+1 < len(self.tokens) else None

    # ---------------------------------------------------------------

    def parse(self):
        res = ParseResult()
        if self.current_tok.type == TT.SPACE:
            return res.faliure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Unexpected indent.",
                )
            )
        res = self.statements()
        if res.error and self.current_tok != TT.EOF:
            return res.faliure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    'Expected "+", "-", "*" or "/".',
                )
            )
        return res

    def statements(self):  # sourcery no-metrics
        res = ParseResult()
        statements = []
        pos_start = self.current_tok.pos_start.copy()
        self.local_indent = 0

        # Skip all newlines
        while self.current_tok.type == TT.NEWLINE:
            res.register_advancement()
            self.advance()

        # check for EOF
        if self.current_tok.type == TT.EOF:
            return res.success(
                ListNode([], self.current_tok.pos_start, self.current_tok.pos_end)
            )

        # Checks indents
        if self.current_tok.type != TT.SPACE and self.indent_level:
            return res.faliure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected indent",
                )
            )

        # Set indent if any
        if self.current_tok.type == TT.SPACE:
            self.local_indent = (self.current_tok.value - self.indent_level)
            self.indent_level += self.local_indent
            res.register_advancement()
            self.advance()

        # First statement
        statement = res.register(self.statement())
        if res.error:
            return res
        statements.append(statement)

        more_statements = True
        while True:
            newline_count = 0
            while self.current_tok.type == TT.NEWLINE:

                # Skip past the NEWLINE
                res.register_advancement()
                self.advance()

                if self.indent_level and self.current_tok.type == TT.SPACE:
                    if self.current_tok.value <= self.indent_level - self.local_indent:
                        break

                    elif self.current_tok.value != self.indent_level:
                        return res.faliure(
                            InvalidSyntaxError(
                                self.current_tok.pos_start,
                                self.current_tok.pos_end,
                                "Uneven indent.",
                            )
                        )

                    else:
                        newline_count += 1
                
                elif not self.indent_level:
                    newline_count += 1

            if not newline_count:
                more_statements = False

            if not more_statements:
                break

            # Skip if space
            if self.current_tok.type == TT.SPACE:
                res.register_advancement()
                self.advance()

            # Get statement, reverse if errors, append to statements if successful.
            statement = res.try_register(self.statement())
            if not statement:
                self.reverse(res.to_reverse_count)
                more_statements = True
                continue

            statements.append(statement)

        # Subtract local indent from global indent level after ending of statement set
        if self.indent_level > 0 and self.tokens[self.tok_idx - 1].type == TT.NEWLINE:
            self.reverse()

        self.indent_level -= self.local_indent
        return res.success(
            ListNode(statements, pos_start, self.current_tok.pos_end.copy())
        )

    def statement(self):
        res = ParseResult()
        pos_start = self.current_tok.pos_start.copy()

        if self.current_tok.type == TT.KEYWORD:
            ret_val = None

            match self.current_tok.value:
                case "return":
                    res.register_advancement()
                    self.advance()

                    expr = res.try_register(self.expr())
                    if not expr:
                        self.reverse(res.to_reverse_count)

                    ret_val = ReturnNode(expr, pos_start, self.current_tok.pos_start.copy())

                case "continue":
                    res.register_advancement()
                    self.advance()

                    ret_val = ContinueNode(pos_start, self.current_tok)

                case "break":
                    res.register_advancement()
                    self.advance()

                    ret_val = BreakNode(pos_start, self.current_tok)

                case "if":
                    ret_val = res.register(self.if_expr())

                case "for":
                    ret_val = res.register(self.for_expr())

                case "while":
                    ret_val = res.register(self.while_expr())

                case "func":
                    ret_val = res.register(self.func_def_expr())

                case "del":
                    pos_start = self.current_tok.pos_start.copy()

                    res.register_advancement()
                    self.advance()

                    value = res.register(self.index())
                    if res.error: return res

                    ret_val = DelNode(value, pos_start, value.pos_end)

            if ret_val:
                if res.error: return res
                return res.success(ret_val)

        # Default expr check
        expr = res.register(self.var_assign_statement())
        if res.error:
            return res

        return res.success(expr)

    def var_assign_statement(self):
        res = ParseResult()
        detected_var = False

        if self.current_tok.type == TT.IDENTIFIER: 
            var_name_tok = self.current_tok
            match self.peek.type:
                case TT.EQ:
                    res.register_advancement()
                    self.advance()
                    res.register_advancement()
                    self.advance()

                    expr = res.register(self.var_assign_statement())
                    if res.error: return res

                    return res.success(VarAssignNode(var_name_tok, expr))

                case TT.LSQUARE:
                    res.register_advancement()
                    self.advance()
                    res.register_advancement()
                    self.advance()

                    index = res.try_register(self.arith_expr())
                    if res.error: return res

                    if self.current_tok.type != TT.RSQUARE:
                        return res.faliure(
                            InvalidSyntaxError(
                                self.current_tok.pos_start, self.current_tok.pos_end, "Expected ']'"
                            )
                        )

                    if self.peek.type != TT.EQ:
                        self.reverse(res.advance_count)
                        detected_var = False
                    
                    else:
                        res.register_advancement()
                        self.advance()
                        res.register_advancement()
                        self.advance()

                        expr = res.register(self.var_assign_statement())
                        if res.error: return res

                        return res.success(IndexAssignNode(var_name_tok, index, expr))

        if not detected_var:
            expr = res.register(self.expr())
            if res.error: return res
            return res.success(expr)

    def expr(self):
        res = ParseResult()

        node = res.register(
            self.bin_op(self.comp_expr, ((TT.KEYWORD, "or"), (TT.KEYWORD, "and")))
        )

        if res.error:
            return res

        return res.success(node)

    def comp_expr(self):
        res = ParseResult()

        # Not operator
        if self.current_tok.matches(TT.KEYWORD, "not"):
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()

            node = res.register(self.comp_expr())
            if res.error:
                return res

            return res.success(UnaryOpNode(op_tok, node))

        # If no 'not' operator found, skip and look for arith_expr with all other comparison operators
        node = res.register(
            self.bin_op(self.arith_expr, (TT.EE, TT.NE, TT.LT, TT.GT, TT.LTE, TT.GTE))
        )

        if res.error:
            return res
        return res.success(node)

    def arith_expr(self):
        return self.bin_op(self.term, (TT.PLUS, TT.MINUS)) # Look for term with '+' or '-' operators

    def term(self):
        return self.bin_op(self.factor, (TT.MULT, TT.DIV, TT.FDIV, TT.MODU)) # Look for factor with "*", "/", "%" or "//" operators

    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        # Positive or negative numbers
        if tok.type in (TT.PLUS, TT.MINUS):
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            if res.error:
                return res
            return res.success(UnaryOpNode(tok, factor))

        return self.power()

    def power(self):
        return self.bin_op(self.call, (TT.POW,), self.factor) # Look for call with "**"

    def call(self):
        res = ParseResult()
        atom = res.register(self.index())
        if res.error: return res

        if self.current_tok.type == TT.LPAR:
            res.register_advancement()
            self.advance()
            arg_nodes = []

            if self.current_tok.type != TT.RPAR:
                arg_nodes.append(res.register(self.expr()))
                if res.error: return res.faliure(
                    InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end, "Expected expression"
                    )
                )
            
                while self.current_tok.type == TT.COMMA:
                    res.register_advancement()
                    self.advance()

                    arg_nodes.append(res.register(self.expr()))
                    if res.error: return res

            if self.current_tok.type != TT.RPAR:
                return res.faliure(
                    InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end, "Expected ')' or ','"
                    )
                )

            res.register_advancement()
            self.advance()

            return res.success(CallNode(atom, arg_nodes))
        return res.success(atom)

    def index(self):
        res = ParseResult()
        atom = res.register(self.atom())
        if res.error: return res

        if self.current_tok.type == TT.LSQUARE:
            iterations = 0
            while self.current_tok.type == TT.LSQUARE:
                res.register_advancement()
                self.advance()

                index = res.register(self.arith_expr())
                if res.error: return res

                if not iterations:
                    index_node = IndexNode(atom, index)
                else:
                    index_node = IndexNode(index_node, index)

                if self.current_tok.type != TT.RSQUARE:
                    return res.faliure(
                        InvalidSyntaxError(
                            self.current_tok.pos_start, self.current_tok.pos_end, "Expected ']'"
                        )
                    )

                res.register_advancement()
                self.advance()

                iterations += 1

            return res.success(index_node)

        return res.success(atom)

    def atom(self):
        res = ParseResult()

        match self.current_tok:

            # Number cases
            case tok if tok.type in (TT.INT, TT.FLOAT):
                res.register_advancement()
                self.advance()

                return res.success(NumberNode(tok))
            
            # String case
            case tok if tok.type == TT.STRING:
                res.register_advancement()
                self.advance()

                return res.success(StringNode(tok))

            # Bool case
            case tok if tok.type == TT.BOOL:
                res.register_advancement()
                self.advance()

                return res.success(BoolNode(tok))

            # Identifier case
            case tok if tok.type == TT.IDENTIFIER:
                res.register_advancement()
                self.advance()

                return res.success(VarAccessNode(tok))

            # Paranthesis case
            case tok if tok.type == TT.LPAR:
                res.register_advancement()
                self.advance()
                
                expr = res.register(self.expr())
                if res.error: return res

                if self.current_tok.type != TT.RPAR:
                    return res.faliure(
                        InvalidSyntaxError(
                            self.current_tok.pos_start, self.current_tok.pos_end, "Expected ')'"
                        )
                    )
                
                res.register_advancement()
                self.advance()

                return res.success(expr)

            # List case
            case tok if tok.type == TT.LSQUARE:
                list_expr = res.register(self.list_expr())
                if res.error: return res
                return res.success(list_expr)

            # Dict case
            case tok if tok.type == TT.LCURLY:
                dict_expr = res.register(self.dict_expr())
                if res.error: return res
                return res.success(dict_expr)

            case tok if not tok.value or tok.type == TT.SPACE:
                tok_char = (
                    NON_VALUE_TOKS[tok.type] 
                    if tok.type != TT.SPACE 
                    else " " * tok.value
                )

                return res.faliure(
                    InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end, f"Unexpected '{tok_char}'"
                    )
                )

            # Default case - 2 [value does exist (excluding spaces)]
            case tok:
                return res.faliure(
                    InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end, f"Unexpected '{tok.value}'"
                    )
                )

    def list_expr(self):
        res = ParseResult()
        element_nodes = []
        pos_start = self.current_tok.pos_start.copy()

        if self.current_tok.type != TT.LSQUARE:
            return res.faliure(
                InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, "Expected '['"
                )
            )

        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT.RSQUARE:
            element_nodes.append(res.register(self.expr()))

            if res.error: return res

            while self.current_tok.type == TT.COMMA:
                res.register_advancement()
                self.advance()

                element_nodes.append(res.register(self.expr()))
                if res.error: return res

        if self.current_tok.type != TT.RSQUARE:
            return res.faliure(
                InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, "Expected ']' or ','"
                )
            )

        res.register_advancement()
        self.advance()

        return res.success(ListNode(element_nodes, pos_start, self.current_tok.pos_start))

    def dict_expr(self):
        res = ParseResult()
        pos_start = self.current_tok.pos_start.copy()

        if self.current_tok.type != TT.LCURLY:
            return res.faliure(
                InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, "Expected '{'"
                )
            )

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT.RCURLY:
            pos_end = self.current_tok.pos_end.copy()

            res.register_advancement()
            self.advance()

            return res.success(
                DictNode([], pos_start, pos_end)
            )

        key_value_pairs = []

        while self.current_tok.type in (TT.NEWLINE, TT.SPACE):
            res.register_advancement()
            self.advance()

        key = res.register(self.expr())
        if res.error: return res

        if self.current_tok.type != TT.COLON:
            return res.failure(
                InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, "Expected ':'"
                )
            )

        res.register_advancement()
        self.advance()

        value = res.register(self.expr())
        if res.error: return res

        key_value_pairs.append((key, value))

        while self.current_tok.type in (TT.NEWLINE, TT.SPACE):
            res.register_advancement()
            self.advance()

        while self.current_tok.type == TT.COMMA:
            res.register_advancement()
            self.advance()

            while self.current_tok.type in (TT.NEWLINE, TT.SPACE):
                res.register_advancement()
                self.advance()

            key = res.register(self.expr())
            if res.error: return res

            if self.current_tok.type != TT.COLON:
                return res.failure(
                    InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end, "Expected ':'"
                    )
                )

            res.register_advancement()
            self.advance()

            value = res.register(self.expr())
            if res.error: return res

            key_value_pairs.append((key, value))

        while self.current_tok.type in (TT.NEWLINE, TT.SPACE):
            res.register_advancement()
            self.advance()

        if self.current_tok.type != TT.RCURLY:
            return res.faliure(
                InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, "Expected '}'"
                )
            )

        pos_end = self.current_tok.pos_end.copy()

        res.register_advancement()
        self.advance()

        return res.success(DictNode(key_value_pairs, pos_start, pos_end))

    def if_expr(self):
        res = ParseResult()
        all_cases = res.register(self.if_expr_cases("if"))
        if res.error: return res

        cases, else_case = all_cases
        return res.success(IfNode(cases, else_case))

    # Elif cases
    def if_expr_b(self):
        return self.if_expr_cases("elif")

    # Else case
    def if_expr_c(self):
        res = ParseResult()
        else_case = None

        if self.current_tok.matches(TT.KEYWORD, "else"):
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT.COLON:
                return res.faliure(
                    InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end, "Expected ':'"
                    )
                )

            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT.NEWLINE:
                statement = res.register(self.statement())
                if res.error: return res
                else_case = (statement, False)

            else:
                res.register_advancement()
                self.advance()

                statements = res.register(self.statements())
                if res.error: return res
                else_case = (statements, True)

        return res.success(else_case)


    # Determiner
    def if_expr_b_or_c(self):
        res = ParseResult()
        cases = []
        else_case = None

        if self.current_tok.matches(TT.KEYWORD, "elif"):
            all_cases = res.register(self.if_expr_b())
            if res.error:
                return res
            cases, else_case = all_cases
        else:
            else_case = res.register(self.if_expr_c())
            if res.error:
                return res

        return res.success((cases, else_case))

    # If and elif cases
    def if_expr_cases(self, case_keyword):  # sourcery no-metrics
        res = ParseResult()
        cases = []
        else_case = None

        if not self.current_tok.matches(TT.KEYWORD, case_keyword):
            return res.faliure(
                InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, f"Expected '{case_keyword}'"
                )
            )

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error:
            return res

        if self.current_tok.type != TT.COLON:
            return res.faliure(
                InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, "Expected ':'"
                )
            )

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT.NEWLINE:
            res.register_advancement()
            self.advance()

            statements = res.register(self.statements())
            if res.error: return res
            
            cases.append((condition, statements, True))

            while self.current_tok .type == TT. NEWLINE:
                res.register_advancement()
                self.advance()

            if (
                self.indent_level 
                and self.tok_idx + 1 < len(self.tokens) 
                and self.peek.type == TT.KEYWORD 
                and self.peek.value in {"else", "elif"}
            ):
                if self.current_tok.type != TT.SPACE:
                    return res.faliure(
                        InvalidSyntaxError(
                            self.current_tok.pos_start, self.current_tok.pos_end, "Expected indent"
                        )
                    )
                
                elif not self.current_tok.matches(TT.SPACE, self.local_indent):
                    return res.faliure(
                        InvalidSyntaxError(
                            self.current_tok.pos_start, self.current_tok.pos_end, "Uneven indent"
                        )
                    )

                else:
                    res.register_advancement()
                    self.advance()

            if self.current_tok.matches(TT.KEYWORD, "else") or self.current_tok.matches(TT.KEYWORD, "elif"):
                all_cases = res.register(self.if_expr_b_or_c())
                if res.error: return res
                new_cases, else_case = all_cases
                cases.extend(new_cases)

        else:
            expr = res.register(self.statement())
            if res.error:
                return res
            cases.append((condition, expr, False))

            all_cases = res.register(self.if_expr_b_or_c())
            if res.error:
                return res
            new_cases, else_case = all_cases
            cases.extend(new_cases)

        if not else_case:
            while self.current_tok.type != TT.NEWLINE:
                self.reverse()

        return res.success((cases, else_case))

    def for_expr(self):
        res = ParseResult()
        if not self.current_tok.matches(TT.KEYWORD, "for"):
            return res.faliure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected 'for'",
                )
            )

        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT.IDENTIFIER:
            return res.faliure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected identifier",
                )
            )

        var_name = self.current_tok
        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT.EQ:
            return res.faliure(
                InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, "Expected '='"
                )
            )

        res.register_advancement()
        self.advance()

        start_value = res.register(self.expr())
        if res.error:
            return res

        if not self.current_tok.matches(TT.KEYWORD, "to"):
            return res.faliure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected 'to'",
                )
            )

        res.register_advancement()
        self.advance()

        end_value = res.register(self.expr())
        if res.error:
            return res

        if self.current_tok.matches(TT.KEYWORD, "step"):
            res.register_advancement()
            self.advance()

            step_value = res.register(self.expr())
            if res.error:
                return res
        else:
            step_value = None

        if self.current_tok.type != TT.COLON:
            return res.faliure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected ':'",
                )
            )

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT.NEWLINE:
            res.register_advancement()
            self.advance()

            body = res.register(self.statements())
            if res.error:
                return res

            return res.success(
                ForNode(var_name, start_value, end_value, step_value, body, True)
            )

        body = res.register(self.statement())
        if res.error:
            return res

        return res.success(
            ForNode(var_name, start_value, end_value, step_value, body, False)
        )

    def while_expr(self):
        res = ParseResult()
        if not self.current_tok.matches(TT.KEYWORD, "while"):
            return res.faliure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected 'while'",
                )
            )

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error:
            return res

        if self.current_tok.type != TT.COLON:
            return res.faliure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected ':'",
                )
            )
        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT.NEWLINE:
            res.register_advancement()
            self.advance()

            body = res.register(self.statements())
            if res.error:
                return res

            return res.success(WhileNode(condition, body, True))

        body = res.register(self.statement())
        if res.error:
            return res

        return res.success(WhileNode(condition, body, False))

    def func_def_expr(self):
        res = ParseResult()

        if not self.current_tok.matches(TT.KEYWORD, "func"):
            return res.faliure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Excpected 'func'",
                )
            )

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT.IDENTIFIER:
            var_name_tok = self.current_tok
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT.LPAR:
                return res.faliure(
                    InvalidSyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "Expected '('",
                    )
                )
        else:
            var_name_tok = None
            if self.current_tok.type != TT.LPAR:
                return res.faliure(
                    InvalidSyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "Expected identifier or '('",
                    )
                )

        res.register_advancement()
        self.advance()

        arg_name_toks = []

        if self.current_tok.type == TT.IDENTIFIER:
            arg_name_toks.append(self.current_tok)
            res.register_advancement()
            self.advance()

            while self.current_tok.type == TT.COMMA:
                res.register_advancement()
                self.advance()

                if self.current_tok.type != TT.IDENTIFIER:
                    return res.faliure(
                        InvalidSyntaxError(
                            self.current_tok.pos_start,
                            self.current_tok.pos_end,
                            "Expected identifier",
                        )
                    )

                arg_name_toks.append(self.current_tok)
                res.register_advancement()
                self.advance()

            if self.current_tok.type != TT.RPAR:
                return res.faliure(
                    InvalidSyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "Expected ',' or  ')'",
                    )
                )

        elif self.current_tok.type != TT.RPAR:
            return res.faliure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Expected identifier or ')'",
                )
            )

        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT.COLON:
            return res.faliure(
                InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, "Expected ':'"
                )
            )

        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT.NEWLINE:
            node_to_return = res.register(self.expr())
            if res.error:
                return res

            return res.success(
                FuncDefNode(var_name_tok, arg_name_toks, node_to_return, True)
            )

        res.register_advancement()
        self.advance()

        body = res.register(self.statements())
        if res.error:
            return res

        return res.success(FuncDefNode(var_name_tok, arg_name_toks, body, False))

    def bin_op(self, func_a: callable, ops: tuple[Token], func_b=None):
        if func_b is None:
            func_b = func_a

        res = ParseResult()
        left = res.register(func_a())
        if res.error:
            return res

        while (
            self.current_tok.type in ops
            or (self.current_tok.type, self.current_tok.value) in ops
        ):
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            right = res.register(func_b())
            if res.error:
                return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)