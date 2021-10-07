from .utils import Position, TT
from .errors import RTError
from .lexer import Lexer
from .parser import Parser, NumberNode, BinOpNode, UnaryOpNode, VarAccessNode, VarAssignNode

# ------------------------------
# RUNTIME RESULT
# ------------------------------


class RTResult:
    def __init__(self):
        self.value = None
        self.error = None

    def register(self, res):
        if res.error:
            self.error = res.error
        return res.value

    def success(self, value):
        self.value = value
        return self

    def faliure(self, error):
        self.error = error
        return self


# ------------------------------
# VALUES
# ------------------------------


class Number:
    def __init__(self, value: int):
        self.value = value
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start: Position = None, pos_end: Position = None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self

    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __add__(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None

    def __sub__(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None

    def __mul__(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None

    def __truediv__(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(
                    other.pos_start, other.pos_end, "Division by zero", self.context
                )
            return Number(self.value / other.value).set_context(self.context), None

    def __floordiv__(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(
                    other.pos_start, other.pos_end, "Division by zero", self.context
                )
            return Number(self.value // other.value).set_context(self.context), None

    def __mod__(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(
                    other.pos_start, other.pos_end, "Modulo by zero", self.context
                )
            return Number(self.value % other.value).set_context(self.context), None

    def __neg__(self):
        return Number(-self.value)

    def __pow__(self, other):
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.context), None

    def __eq__(self, other):
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).set_context(self.context), None

    def __ne__(self, other):
        if isinstance(other, Number):
            return Number(int(self.value != other.value)).set_context(self.context), None

    def __lt__(self, other):
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).set_context(self.context), None

    def __le__(self, other):
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).set_context(self.context), None

    def __gt__(self, other):
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).set_context(self.context), None

    def __ge__(self, other):
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).set_context(self.context), None

    def __and__(self, other):
        if isinstance(other, Number):
            return Number(int(self.value and other.value)).set_context(self.context), None

    def __or__(self, other):
        if isinstance(other, Number):
            return Number(int(self.value or other.value)).set_context(self.context), None

    def __not__(self):
        return Number(int(not self.value)).set_context(self.context), None

    def __repr__(self):
        return str(self.value)


# ------------------------------
# SYMBOL TABLE
# ------------------------------


class SymbolTable:
    def __init__(self):
        self.symbols = {}
        self.parent: dict = None

    def get(self, name):
        value = self.symbols.get(name)
        if value is None and self.parent:
            return self.parent.get(name)
        return value

    def set(self, name: str, value):
        self.symbols[name] = value

    def remove(self, name):
        del self.symbols[name]


# ------------------------------
# CONTEXT
# ------------------------------


class Context:
    def __init__(self, display_name: str, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table: SymbolTable = None


# ------------------------------
# INTERPRETER
# ------------------------------


class Interpreter:
    def visit(self, node, context: Context) -> RTResult:
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node):
        raise Exception(f"No visit_{type(node).__name__}")

    # ------------------------------

    def visit_NumberNode(self, node: NumberNode, context: Context):
        return RTResult().success(
            Number(node.tok.value)
            .set_context(context)
            .set_pos(node.pos_start, node.pos_end)
        )

    def visit_VarAccessNode(self, node: VarAccessNode, context: Context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = context.symbol_table.get(var_name)

        if not value:
            return res.faliure(
                RTError(
                    node.pos_start,
                    node.pos_end,
                    f"'{var_name}' is not defined",
                    context,
                )
            )

        value = value.copy().set_pos(node.pos_start, node.pos_end)
        return res.success(value)

    def visit_VarAssignNode(self, node: VarAssignNode, context: Context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = res.register(self.visit(node.value_node, context))
        if res.error:
            return res

        context.symbol_table.set(var_name, value)
        return res.success(value)

    def visit_BinOpNode(self, node: BinOpNode, context: Context) -> Number: # sourcery no-metrics
        res = RTResult()
        left = res.register(self.visit(node.left_node, context))
        if res.error:
            return res
        right = res.register(self.visit(node.right_node, context))
        if res.error:
            return res

        if node.op_tok.type == TT.PLUS:
            result, error = left + right
        elif node.op_tok.type == TT.MINUS:
            result, error = left - right
        elif node.op_tok.type == TT.MULT:
            result, error = left * right
        elif node.op_tok.type == TT.DIV:
            result, error = left / right
        elif node.op_tok.type == TT.FDIV:
            result, error = left // right
        elif node.op_tok.type == TT.MODU:
            result, error = left % right
        elif node.op_tok.type == TT.POW:
            result, error = left ** right
        elif node.op_tok.type == TT.EE:
            result, error = left == right
        elif node.op_tok.type == TT.NE:
            result, error = left != right
        elif node.op_tok.type == TT.LT:
            result, error = left < right
        elif node.op_tok.type == TT.GT:
            result, error = left > right
        elif node.op_tok.type == TT.LTE:
            result, error = left <= right
        elif node.op_tok.type == TT.GTE:
            result, error = left >= right
        elif node.op_tok.matches(TT.KEYWORD, "and"):
            result, error = left.__and__(right)
        elif node.op_tok.matches(TT.KEYWORD, "or"):
            result, error = left.__or__

        if error:
            return res.faliure(error)

        return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node: UnaryOpNode, context: Context):
        res = RTResult()
        number = res.register(self.visit(node.node, context))
        if res.error:
            return res

        error = None

        if node.op_tok.type == TT.MINUS:
            number, error = -number
        elif node.op_tok.matches(TT.KEYWORD, "not"):
            number, error = number.__not__()

        if error:
            return res
        return res.success(number.set_pos(node.pos_start, node.pos_end))


global_symbol_table = SymbolTable()
global_symbol_table.set("null", Number(0))


def run(fn: str, text: str):
    # Generate Tokens
    lexer = Lexer(text, fn)
    tokens, error = lexer.make_tokens()
    if error:
        return None, error
    if not tokens:
        return None, error

    # Generate AST
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error:
        return None, ast.error

    # Get Interpreter
    interpreter = Interpreter()
    context = Context("<program>")
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)

    return result.value, result.error
