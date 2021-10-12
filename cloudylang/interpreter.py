import os

from .utils import Position, TT
from .errors import RTError, IndexError
from .lexer import Lexer, Token
from .parser import (
    Parser,
    BreakNode,
    CallNode,
    ContinueNode,
    FuncDefNode,
    ListNode,
    NumberNode,
    BinOpNode,
    ReturnNode,
    StringNode,
    UnaryOpNode,
    VarAccessNode,
    VarAssignNode,
    IfNode,
    ForNode,
    WhileNode,
)


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


class DataType:
    def __init__(self):
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
        raise Exception("NO COPIES")

    def get_type_from_value(self):
        str_value = str(self.value)
        if str_value.isnumeric():
            return Number(self.value)
        elif str_value in {"True", "False"}:
            return Bool(self.value)

    def is_true(self):
        return False

    def illegal_operation(self, other=None):
        if not other:
            other = self
        return RTError(self.pos_start, other.pos_end, "Illegal operation", self.context)


class Number(DataType):
    def __init__(self, value: int):
        self.value = value
        super().__init__()

    def copy(self):
        return (
            Number(self.value)
            .set_context(self.context)
            .set_pos(self.pos_start, self.pos_end)
        )

    def __add__(self, other):
        if isinstance(other, (Number, Bool)):
            return Number(self.value + other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __sub__(self, other):
        if isinstance(other, (Number, Bool)):
            return Number(self.value - other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __mul__(self, other):
        if isinstance(other, (Number, Bool)):
            return Number(self.value * other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __truediv__(self, other):
        if not isinstance(other, (Number, Bool)):
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

        if other.value == 0:
            return None, RTError(
                other.pos_start, other.pos_end, "Division by zero", self.context
            )
        return Number(self.value / other.value).set_context(self.context), None

    def __floordiv__(self, other):
        if not isinstance(other, (Number, Bool)):
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

        if other.value == 0:
            return None, RTError(
                other.pos_start, other.pos_end, "Division by zero", self.context
            )
        return Number(self.value // other.value).set_context(self.context), None

    def __mod__(self, other):
        if not isinstance(other, (Number, Bool)):
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

        if other.value == 0:
            return None, RTError(
                other.pos_start, other.pos_end, "Modulo by zero", self.context
            )
        return Number(self.value % other.value).set_context(self.context), None

    def __neg__(self):
        return Number(-self.value)

    def __pow__(self, other):
        if isinstance(other, (Number, Bool)):
            return Number(self.value ** other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __eq__(self, other):
        if isinstance(other, (Number, Bool)):
            return (
                Bool(self.value == other.value).set_context(self.context),
                None,
            )
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __ne__(self, other):
        if isinstance(other, (Number, Bool)):
            return (
                Bool(self.value != other.value).set_context(self.context),
                None,
            )
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __lt__(self, other):
        if isinstance(other, (Number, Bool)):
            return Bool(self.value < other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __le__(self, other):
        if isinstance(other, (Number, Bool)):
            return (
                Bool(self.value <= other.value).set_context(self.context),
                None,
            )
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __gt__(self, other):
        if isinstance(other, (Number, Bool)):
            return Bool(self.value > other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __ge__(self, other):
        if isinstance(other, (Number, Bool)):
            return (
                Bool(self.value >= other.value).set_context(self.context),
                None,
            )
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __and__(self, other):
        if isinstance(other, (Number, Bool)):
            return (
                Bool(self.value and other.value).set_context(self.context),
                None,
            )
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __or__(self, other):
        if isinstance(other, (Number, Bool)):
            return (
                bool(self.value or other.value).set_context(self.context),
                None,
            )
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __not__(self):
        return Bool(not self.value).set_context(self.context), None

    def __repr__(self):
        return str(self.value)


class Null(DataType):
    def __init__(self):
        super().__init__()

    def copy(self):
        return Null()


class Bool(DataType):
    def __init__(self, value: bool):
        self.value = value
        super().__init__()

    def __add__(self, other):
        if isinstance(other, (Number, Bool)):
            return Number(self.value + other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __sub__(self, other):
        if isinstance(other, (Number, Bool)):
            return Number(self.value - other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __mul__(self, other):
        if isinstance(other, (Number, Bool)):
            return Number(self.value * other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __truediv__(self, other):
        if not isinstance(other, (Number, Bool)):
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

        if other.value == 0:
            return None, RTError(
                other.pos_start, other.pos_end, "Division by zero", self.context
            )
        return Number(self.value / other.value).set_context(self.context), None

    def __floordiv__(self, other):
        if not isinstance(other, (Number, Bool)):
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

        if other.value == 0:
            return None, RTError(
                other.pos_start, other.pos_end, "Division by zero", self.context
            )
        return Number(self.value // other.value).set_context(self.context), None

    def __mod__(self, other):
        if not isinstance(other, (Number, Bool)):
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

        if other.value == 0:
            return None, RTError(
                other.pos_start, other.pos_end, "Modulo by zero", self.context
            )
        return Number(self.value % other.value).set_context(self.context), None

    def __neg__(self):
        return Number(-self.value)

    def __pow__(self, other):
        return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __eq__(self, other):
        if isinstance(other, (Number, Bool)):
            return (
                Bool(self.value == other.value).set_context(self.context),
                None,
            )
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __ne__(self, other):
        if isinstance(other, (Number, Bool)):
            return (
                Bool(self.value != other.value).set_context(self.context),
                None,
            )
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __lt__(self, other):
        if isinstance(other, (Number, Bool)):
            return Bool(self.value < other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __le__(self, other):
        if isinstance(other, (Number, Bool)):
            return (
                Bool(self.value <= other.value).set_context(self.context),
                None,
            )
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __gt__(self, other):
        if isinstance(other, (Number, Bool)):
            return Bool(self.value > other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __ge__(self, other):
        if isinstance(other, (Number, Bool)):
            return (
                Bool(self.value >= other.value).set_context(self.context),
                None,
            )
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __and__(self, other):
        if isinstance(other, (Number, Bool)):
            return (
                Bool(self.value and other.value).set_context(self.context),
                None,
            )
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __or__(self, other):
        if isinstance(other, (Number, Bool)):
            return (
                bool(self.value or other.value).set_context(self.context),
                None,
            )
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __not__(self):
        return Bool(not self.value).set_context(self.context), None

    def is_true(self):
        return self.value

    def copy(self):
        return (
            Bool(self.value)
            .set_context(self.context)
            .set_pos(self.pos_start, self.pos_end)
        )

    def __repr__(self):
        return str(self.value).lower()


class String(DataType):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def __add__(self, other):
        if isinstance(other, String):
            return String(self.value + other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def __mul__(self, other):
        if isinstance(other, Number):
            return String(self.value * other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

    def copy(self):
        return (
            String(self.value)
            .set_context(self.context)
            .set_pos(self.pos_start, self.pos_end)
        )

    def __repr__(self) -> str:
        return f"{self.value!r}"

    def __str__(self) -> str:
        return self.value


class List(DataType):
    def __init__(self, elements: list):
        super().__init__()
        self.elements = elements

    def __add__(self, other):
        new_list = self.copy()
        new_list.elements.append(other)
        return new_list, None

    def __sub__(self, other):
        if not isinstance(other, Number):
            return None, DataType.illegal_operation(self, other)

        new_list = self.copy()
        try:
            new_list.elements.pop(other.value)
            return new_list, None
        except:
            return None, RTError(
                self.pos_start,
                self.pos_end,
                "Element at this index could not be removed because index is out of range.",
            )

    def __mul__(self, other):
        if not isinstance(other, List):
            return None, DataType.illegal_operation(self.pos_start, other.pos_end)

        new_list = self.copy()
        new_list.elements.extend(other.elements)
        return new_list, None

    def __truediv__(self, other):
        if not isinstance(other, Number):
            return None, DataType.illegal_operation(self, other)
        try:
            return self.elements[other.value], None
        except:
            return None, RTError(
                self.pos_start,
                self.pos_end,
                "Element at this index could not be retrieved because index is out of range.",
            )

    def copy(self):
        return (
            List(self.elements)
            .set_context(self.context)
            .set_pos(self.pos_start, self.pos_end)
        )

    def __repr__(self):
        return f"{self.elements!r}"


class BaseFunction(DataType):
    def __init__(self, name):
        super().__init__()
        self.name = name or "<anonymous>"

    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        return new_context

    def check_args(self, arg_names, args):
        res = RTResult()

        if len(args) != len(arg_names):
            return res.faliure(
                RTError(
                    self.pos_start,
                    self.pos_end,
                    f"Function {self.name} takes in {len(arg_names)} but {len(args)} passed instead.",
                )
            )

        return res.success(None)

    def populate_args(self, arg_names, args, exec_context):
        for i, arg in enumerate(args):
            arg_name = arg_names[i]
            arg_value = arg
            arg_value.set_context(exec_context)
            exec_context.symbol_table.set(arg_name, arg_value)

    def check_and_populate_args(self, arg_names, args, exec_context):
        res = RTResult()
        res.register(self.check_args(arg_names, args))
        if res.should_return():
            return res
        self.populate_args(arg_names, args, exec_context)
        return res.success(None)


class Function(BaseFunction):
    def __init__(
        self, name, body_node: BinOpNode, arg_names: list, should_auto_return: bool
    ):
        super().__init__(name)
        self.body_node = body_node
        self.arg_names = arg_names
        self.should_auto_return = should_auto_return

    def execute(self, args):
        res = RTResult()
        interpreter = Interpreter()
        exec_context = self.generate_new_context()

        res.register(self.check_and_populate_args(self.arg_names, args, exec_context))
        if res.should_return():
            return res

        value = res.register(interpreter.visit(self.body_node, exec_context))
        if res.should_return() and res.function_return_value is None:
            return res

        return_value = (
            (value if self.should_auto_return else None)
            or res.function_return_value
            or Null()
        )

        return res.success(return_value)

    def copy(self):
        copy = Function(
            self.name, self.body_node, self.arg_names, self.should_auto_return
        )
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return f"<function {self.name}>"


class BuiltInFunction(BaseFunction):
    def __init__(self, name):
        super().__init__(name)

    def execute(self, args):
        res = RTResult()
        exec_context = self.generate_new_context()

        method_name = f"execute_{self.name}"
        method = getattr(self, method_name, self.no_visit_method)

        res.register(self.check_and_populate_args(method.arg_names, args, exec_context))
        if res.should_return():
            return res

        return_value = res.register(method(exec_context))
        if res.should_return():
            return res
        return res.success(return_value)

    def copy(self):
        return (
            BuiltInFunction(self.name)
            .set_context(self.context)
            .set_pos(self.pos_start, self.pos_end)
        )

    def no_visit_method(self):
        raise Exception(f"No execute_{self.name} method defined.")

    # BUILT-INS

    def execute_print(self, exec_context):
        print(str(exec_context.symbol_table.get("value")))
        return RTResult().success(Null())

    execute_print.arg_names = ["value"]

    def execute_print_ret(self, exec_context):
        return RTResult().success(String(str(exec_context.symbol_table.get("value"))))

    execute_print_ret.arg_names = ["value"]

    def execute_input(self, exec_context):
        text = input("> ")
        return RTResult().success(String(text))

    execute_input.arg_names = []

    def execute_input_int(self, exec_context):
        while True:
            text = input()
            try:
                number = int(text)
                break
            except ValueError:
                print(f"'{text}' must be an integer. Try again!")
        return RTResult().success(Number(number))

    execute_input_int.arg_names = []

    def execute_clear(self, exec_context):
        os.system("cls|clear")
        return RTResult().success(Null())

    execute_clear.arg_names = []

    def execute_is_number(self, exec_context):
        return_value = isinstance(exec_context.symbol_table.get("value"), Number)
        return RTResult().success(Bool(return_value))

    execute_is_number.arg_names = ["value"]

    def execute_is_string(self, exec_context):
        return_value = isinstance(exec_context.symbol_table.get("value"), String)
        return RTResult().success(Bool(return_value))

    execute_is_string.arg_names = ["value"]

    def execute_is_bool(self, exec_context):
        return_value = isinstance(exec_context.symbol_table.get("value"), Bool)
        return RTResult().succegss(Bool(return_value))

    execute_is_bool.arg_names = ["value"]

    def execute_is_list(self, exec_context):
        return_value = isinstance(exec_context.symbol_table.get("value"), List)
        return RTResult().success(Bool(return_value))

    execute_is_list.arg_names = ["value"]

    def execute_is_function(self, exec_context):
        return_value = isinstance(exec_context.symbol_table.get("value"), BaseFunction)
        return RTResult().success(Bool(return_value))

    execute_is_function.arg_names = ["value"]

    def execute_append(self, exec_context):
        list_ = exec_context.symbol_table.get("list")
        value = exec_context.symbol_table.get("value")

        if not isinstance(list_, List):
            return RTResult().faliure(
                RTError(
                    self.pos_start,
                    self.pos_end,
                    "First argument must be a list.",
                    exec_context,
                )
            )

        list_.elements.append(value)
        return RTResult().success(Null())

    execute_append.arg_names = ["list", "value"]

    def execute_pop(self, exec_context):
        list_ = exec_context.symbol_table.get("list")
        index = exec_context.symbol_table.get("index")

        if not isinstance(list_, List):
            return RTResult().faliure(
                RTError(
                    self.pos_start,
                    self.pos_end,
                    "First argument must be a list.",
                    exec_context,
                )
            )

        if not isinstance(index, Number):
            return RTResult().faliure(
                RTError(
                    self.pos_start,
                    self.pos_end,
                    "Second argument must be an integer.",
                    exec_context,
                )
            )

        try:
            element = list_.elements.pop(index.value)
        except:
            return RTResult().faliure(
                RTError(self.pos_start, self.pos_end, "Index is out of range.")
            )
        return RTResult().success(Null())

    execute_pop.arg_names = ["list", "index"]

    def execute_extend(self, exec_context):
        list1 = exec_context.symbol_table.get("list1")
        list2 = exec_context.symbol_table.get("list2")

        if not (isinstance(list1, List) and isinstance(list2, List)):
            return RTResult().faliure(
                RTError(
                    self.pos_start,
                    self.pos_end,
                    "Both arguments must be lists",
                    exec_context,
                )
            )

        list1.elements.extend(list2.elements)
        return RTResult().success(Null())

    execute_extend.arg_names = ["list1", "list2"]

    def execute_len(self, exec_context):
        list_ = exec_context.symbol_table.get("list")
        if not isinstance(list_, List):
            return RTResult().faliure(
                RTError(
                    self.pos_start,
                    self.pos_end,
                    "Argument must be a list",
                    exec_context,
                )
            )

        return RTResult().success(Number(len(list_.elements)))
    execute_len.arg_names = ["list"]

    def execute_run(self, exec_context):
        fn = exec_context.symbol_table.get("fn")

        if not isinstance(fn, String):
            return RTResult().faliure(
                RTError(
                    self.pos_start,
                    self.pos_end,
                    "Argument must be string",
                    exec_context,
                )
            )

        fn = fn.value

        try:
            with open(fn, "r") as f:
                script = f.read()

        except Exception as e:
            return RTResult().faliure(
                RTError(
                    self.pos_start,
                    self.pos_end,
                    f'Failed to load scirpt "{fn}"\n{e}',
                    exec_context,
                )
            )

        _, error = run(fn, script)

        if error:
            return RTResult().faliure(
                RTError(
                    self.pos_start,
                    self.pos_end,
                    f'Failed to finish executing script "{fn}".\n{error}',
                    exec_context,
                )
            )

        return RTResult().success(Null())

    execute_run.arg_names = ["fn"]


BuiltInFunction.print = BuiltInFunction("print")
BuiltInFunction.print_ret = BuiltInFunction("print_ret")
BuiltInFunction.input = BuiltInFunction("input")
BuiltInFunction.input_int = BuiltInFunction("input_int")
BuiltInFunction.clear = BuiltInFunction("clear")
BuiltInFunction.is_number = BuiltInFunction("is_number")
BuiltInFunction.is_string = BuiltInFunction("is_string")
BuiltInFunction.is_list = BuiltInFunction("is_list")
BuiltInFunction.is_bool = BuiltInFunction("is_bool")
BuiltInFunction.is_function = BuiltInFunction("is_function")
BuiltInFunction.append = BuiltInFunction("append")
BuiltInFunction.pop = BuiltInFunction("pop")
BuiltInFunction.extend = BuiltInFunction("extend")
BuiltInFunction.run = BuiltInFunction("run")
BuiltInFunction.len = BuiltInFunction("len")


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


class Interpreter:
    def visit(self, node, context: Context) -> RTResult:
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node):
        raise Exception(f"No visit_{type(node).__name__}")

    def visit_NumberNode(self, node: NumberNode, context: Context):
        return RTResult().success(
            Number(node.tok.value)
            .set_context(context)
            .set_pos(node.pos_start, node.pos_end)
        )

    def visit_BoolNode(self, node: NumberNode, context: Context):
        return RTResult().success(
            Bool(node.tok.value)
            .set_context(context)
            .set_pos(node.pos_start, node.pos_end)
        )

    def visit_StringNode(self, node: StringNode, context: Context):
        return RTResult().success(
            String(node.tok.value)
            .set_context(context)
            .set_pos(node.pos_start, node.pos_end)
        )

    def visit_ListNode(self, node: ListNode, context: Context):
        res = RTResult()
        elements = []

        for element_node in node.element_nodes:
            elements.append(res.register(self.visit(element_node, context)))
            if res.should_return():
                return res

        return res.success(
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
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

        value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return res.success(value)

    def visit_VarAssignNode(self, node: VarAssignNode, context: Context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = res.register(self.visit(node.value_node, context))
        if res.should_return():
            return res

        context.symbol_table.set(var_name, value)
        return res.success(value)

    def visit_BinOpNode(
        self, node: BinOpNode, context: Context
    ) -> Number:  # sourcery no-metrics
        res = RTResult()
        left = res.register(self.visit(node.left_node, context))
        if res.should_return():
            return res
        right = res.register(self.visit(node.right_node, context))
        if res.should_return():
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
            result, error = left.__or__(right)

        if error:
            return res.faliure(error)

        return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node: UnaryOpNode, context: Context):
        res = RTResult()
        number = res.register(self.visit(node.node, context))
        if res.should_return():
            return res

        error = None

        if node.op_tok.type == TT.MINUS:
            number = -number
        elif node.op_tok.matches(TT.KEYWORD, "not"):
            number, error = number.__not__()

        if error:
            return res
        return res.success(number.set_pos(node.pos_start, node.pos_end))

    def visit_IfNode(self, node: IfNode, context=None):
        res = RTResult()

        for condition, expr, should_return_null in node.cases:
            condition_value = res.register(self.visit(condition, context))
            if res.should_return():
                return res

            if condition_value.is_true():
                expr_value = res.register(self.visit(expr, context))
                if res.should_return():
                    return res
                return res.success(Null() if should_return_null else expr_value)

        if node.else_case:
            expr, should_return_null = node.else_case
            else_value = res.register(self.visit(expr, context))
            if res.should_return():
                return res
            return res.success(Null() if should_return_null else else_value)

        return res.success(Null())

    def visit_ForNode(self, node: ForNode, context: Context):
        res = RTResult()
        elements = []

        start_value = res.register(self.visit(node.start_value_node, context))
        if res.should_return():
            return res

        end_value = res.register(self.visit(node.end_value_node, context))
        if res.should_return():
            return res

        if node.step_value_node:
            step_value = res.register(self.visit(node.step_value_node, context))
            if res.should_return():
                return res
        else:
            step_value = Number(1)

        i = start_value.value

        if step_value.value >= 0:
            condition = lambda: i < end_value.value
        else:
            condition = lambda: i > end_value.value

        while condition():
            context.symbol_table.set(node.var_name_tok.value, Number(i))
            i += step_value.value

            value = res.register(self.visit(node.body_node, context))
            if (
                res.should_return()
                and not res.loop_should_continue
                and not res.loop_should_break
            ):
                return res

            if res.loop_should_break:
                break

            if res.loop_should_continue:
                continue

            elements.append(value)

        return res.success(
            Null()
            if node.should_return_null
            else List(elements)
            .set_context(context)
            .set_pos(node.pos_start, node.pos_end)
        )

    def visit_WhileNode(self, node: WhileNode, context: Context):
        res = RTResult()
        elements = []

        while True:
            condition = res.register(self.visit(node.condition_node, context))
            if res.should_return():
                return res

            if not condition.is_true():
                break

            value = res.register(self.visit(node.body_node, context))
            if (
                res.should_return()
                and not res.loop_should_continue
                and not res.loop_should_break
            ):
                return res

            if res.loop_should_break:
                break

            if res.loop_should_continue:
                continue

            elements.append(value)

        return res.success(
            Null()
            if node.should_return_null
            else List(elements)
            .set_context(context)
            .set_pos(node.pos_start, node.pos_end)
        )

    def visit_FuncDefNode(self, node: FuncDefNode, context: Context):
        res = RTResult()

        func_name = node.var_name_tok.value if node.var_name_tok else None
        body_node = node.body_node
        arg_names = [arg_name.value for arg_name in node.arg_name_toks]
        func_value = (
            Function(func_name, body_node, arg_names, node.should_auto_return)
            .set_context(context)
            .set_pos(node.pos_start, node.pos_end)
        )

        if node.var_name_tok:
            context.symbol_table.set(func_name, func_value)

        return res.success(func_value)

    def visit_CallNode(self, node: CallNode, context: Context):
        res = RTResult()
        args = []

        value_to_call = res.register(self.visit(node.node_to_call, context))
        if res.should_return():
            return res
        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

        for arg_node in node.arg_nodes:
            args.append(res.register(self.visit(arg_node, context)))
            if res.should_return():
                return res

        return_value = res.register(value_to_call.execute(args))
        if res.should_return():
            return res
        return_value = (
            return_value.copy()
            .set_pos(node.pos_start, node.pos_end)
            .set_context(context)
        )
        return res.success(return_value)

    def visit_ReturnNode(self, node: ReturnNode, context):
        res = RTResult()

        if node.node_to_return:
            value = res.register(self.visit(node.node_to_return, context))
            if res.should_return():
                return res
        else:
            value = Null()

        return res.success_return(value)

    def visit_BreakNode(self, node: BreakNode, context: Context):
        return RTResult().success_break()

    def visit_ContinueNode(self, node: ContinueNode, context: Context):
        return RTResult().success_continue()


global_symbol_table = SymbolTable()
global_symbol_table.set("null", Null())
global_symbol_table.set("print", BuiltInFunction.print)
global_symbol_table.set("print_ret", BuiltInFunction.print_ret)
global_symbol_table.set("input", BuiltInFunction.input)
global_symbol_table.set("input_int", BuiltInFunction.input_int)
global_symbol_table.set("clear", BuiltInFunction.clear)
global_symbol_table.set("is_number", BuiltInFunction.is_number)
global_symbol_table.set("is_string", BuiltInFunction.is_string)
global_symbol_table.set("is_bool", BuiltInFunction.is_bool)
global_symbol_table.set("is_function", BuiltInFunction.is_function)
global_symbol_table.set("is_list", BuiltInFunction.is_list)
global_symbol_table.set("append", BuiltInFunction.append)
global_symbol_table.set("pop", BuiltInFunction.pop)
global_symbol_table.set("extend", BuiltInFunction.extend)
global_symbol_table.set("run", BuiltInFunction.run)
global_symbol_table.set("len", BuiltInFunction.len)


def run(fn: str, text: str):
    # Generate Tokens
    lexer = Lexer(text, fn)
    tokens, error = lexer.make_tokens()
    # return tokens, error
    if error:
        return None, error
    if not tokens:
        return None, error

    if len(tokens) == 1 and tokens[0].matches(TT.EOF, None):
        return "", error

    # Generate AST
    parser = Parser(tokens)
    ast = parser.parse()
    # return ast.node, ast.error
    if ast.error:
        return None, ast.error

    # Get Interpreter
    interpreter = Interpreter()
    context = Context("<program>")
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)

    if str(result.value) in {"True", "False"}:
        result.value = str(result.value).lower()

    return result.value, result.error
