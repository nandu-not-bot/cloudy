import json
import os

from .ast_json_generator import Generator
from .datatypes.coretypes import Int, NewNum, Null, Number, String, Bool
from .datatypes.derivedtypes import BaseFunction, Dict, List
from .utils import TT, Context, RTResult, SymbolTable
from .errors import RTError, OutOfRangeError
from .lexer import Lexer
from .parser import (
    DelNode,
    DictNode,
    IndexAssignNode,
    IndexNode,
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
        return RTResult().success(NewNum(number))

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

        return RTResult().success(NewNum(len(list_.elements)))

    execute_len.arg_names = ["list"]

    def execute_type(self, exec_context):
        obj = exec_context.symbol_table.get("obj")

        return RTResult().success(String(type(obj).__name__.lower()))

    execute_type.arg_names = ["obj"]

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


class Interpreter:
    def visit(self, node, context: Context) -> RTResult:
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node):
        raise Exception(f"No visit_{type(node).__name__}")

    def visit_NumberNode(self, node: NumberNode, context: Context):
        return RTResult().success(
            NewNum(node.tok.value)
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

    def visit_IndexNode(self, node: IndexNode, context: Context):
        res = RTResult()
        data = res.register(self.visit(node.data_node, context))
        if res.should_return():
            return res
        if not isinstance(data, (String, List, Dict)):
            return res.faliure(
                RTError(
                    node.pos_start,
                    node.pos_end,
                    f"Type '{type(data).__name__}' is not subscriptable",
                )
            )

        index: Number = res.register(self.visit(node.index_node, context))
        if res.should_return():
            return res

        if isinstance(data, (String, List)):
            if not isinstance(index, Int):
                return res.faliure(
                    RTError(
                        node.index_node.pos_start,
                        node.index_node.pos_end,
                        "Index can only be of type 'int'",
                        context,
                    )
                )

            if not data.is_index(index):
                return res.faliure(
                    OutOfRangeError(
                        node.index_node.pos_start,
                        node.index_node.pos_end,
                        type(data).__name__,
                    )
                )

            return_value = data[index]
            return res.success(return_value)

        elif isinstance(data, Dict):
            if not isinstance(index, String):
                return res.faliure(
                    RTError(
                        node.index_node.pos_start,
                        node.index_node.pos_end,
                        f"Key '{index.value}' not found",
                        context,
                    )
                )

            return_value = data.pairs.get(index.value)

            if not return_value:
                return res.faliure(
                    RTError(
                        node.index_node.pos_start,
                        node.index_node.pos_end,
                        f"Key '{index.value}' not found",
                        context,
                    )
                )

            return res.success(return_value)

    def visit_IndexAssignNode(self, node: IndexAssignNode, context: Context):
        res = RTResult()
        var_name = node.var_name_tok.value
        var = context.symbol_table.get(var_name)

        if not var:
            return res.faliure(
                RTError(
                    node.var_name_tok.pos_start,
                    node.var_name_tok.pos_end,
                    f"Undefined '{var_name}'",
                    context,
                )
            )

        if not isinstance(var, (List, Dict)):
            return res.faliure(
                RTError(
                    node.pos_start,
                    node.pos_end,
                    f"Type '{type(var).__name__}' is immutable.",
                    context,
                )
            )

        index = res.register(self.visit(node.index, context))
        if res.should_return():
            return res

        if isinstance(var, List):
            if not isinstance(index, Int):
                return res.faliure(
                    RTError(
                        node.index.pos_start,
                        node.index.pos_end,
                        "Index can only be of type 'int'",
                        context,
                    )
                )

            elements = var.elements

            if index.value >= len(elements):
                return res.faliure(
                    OutOfRangeError(
                        node.index.pos_start, node.index.pos_end, type(var).__name__
                    )
                )

            value = res.register(self.visit(node.value_node, context))
            if res.should_return():
                return res

            elements[index.value] = value
            context.symbol_table.set(
                var_name,
                List(elements)
                .set_context(var.context)
                .set_pos(var.pos_start, var.pos_end),
            )

            return res.success(value)

        elif isinstance(var, Dict):
            if not isinstance(index, String):
                return res.faliure(
                    RTError(
                        node.index.pos_start,
                        node.index.pos_end,
                        "Dict keys can only be of type 'string'",
                        context,
                    )
                )

            pairs = var.pairs

            pairs[index.value] = value = res.register(
                self.visit(node.value_node, context)
            )
            if res.should_return():
                return res

            context.symbol_table.set(
                var_name,
                Dict(pairs).set_context(context).set_pos(var.pos_start, var.pos_end),
            )

            return res.success(value)

    def visit_DelNode(self, node: DelNode, context: Context):  # sourcery no-metrics
        res = RTResult()
        atom = node.atom

        if not isinstance(atom, (VarAccessNode, IndexNode)):
            return res.faliure(
                RTError(
                    node.atom.pos_start,
                    node.atom.pos_end,
                    "Value must be a variable",
                    context,
                )
            )

        if isinstance(atom, VarAccessNode):
            var_name = atom.var_name_tok.value

            if not context.symbol_table.get(var_name):
                return res.faliure(
                    RTError(
                        atom.var_name_tok.pos_start,
                        atom.var_name_tok.pos_end,
                        f"Undefined variable '{var_name}'",
                        context,
                    )
                )

            del context.symbol_table.symbols[var_name]

            return res.success(Null())

        elif isinstance(atom, IndexNode):
            if not isinstance(atom.data_node, VarAccessNode):
                return res.faliure(
                    RTError(
                        node.atom.pos_start,
                        node.atom.pos_end,
                        "Value must be a variable",
                        context,
                    )
                )

            var_name = atom.data_node.var_name_tok.value

            if not context.symbol_table.get(var_name):
                return res.faliure(
                    RTError(
                        atom.data_node.var_name_tok.pos_start,
                        atom.data_node.var_name_tok.pos_end,
                        f"Undefined variable '{var_name}'",
                        context,
                    )
                )

            data_node_val = res.register(self.visit(atom.data_node, context))
            if res.should_return():
                return res

            index = res.register(self.visit(atom.index_node, context))

            if isinstance(data_node_val, List):
                if res.should_return():
                    return res

                if not isinstance(index, Int):
                    return res.faliure(
                        RTError(
                            atom.index_node.pos_start,
                            atom.index_node.pos_end,
                            "Index can only be of type 'int'",
                            context,
                        )
                    )

                elements = data_node_val.elements

                if index.value >= len(elements):
                    return res.faliure(
                        OutOfRangeError(
                            atom.index_node.pos_start,
                            atom.index_node.pos_end,
                            type(data_node_val).__name__,
                        )
                    )

                del elements[index.value]

                context.symbol_table.set(
                    var_name,
                    List(elements)
                    .set_context(context)
                    .set_pos(data_node_val.pos_start, data_node_val.pos_end),
                )

                return res.success(Null())

            elif isinstance(data_node_val, Dict):
                if not isinstance(index, String):
                    return res.faliure(
                        RTError(
                            atom.index_node.pos_start,
                            atom.index_node.pos_end,
                            "Dict keys can only be of type 'string'",
                            context,
                        )
                    )

                pairs = data_node_val.pairs

                if not pairs.get(index.value):
                    return res.faliure(
                        RTError(
                            atom.index_node.pos_start,
                            atom.index_node.pos_end,
                            f"Key '{index.value}' not found",
                            context,
                        )
                    )

                del pairs[index.value]

                context.symbol_table.set(
                    var_name,
                    Dict(pairs)
                    .set_context(context)
                    .set_pos(data_node_val.pos_start, data_node_val.pos_end),
                )

                return res.success(Null())

            else:
                return res.faliure(
                    RTError(
                        atom.data_node.pos_start,
                        atom.data_node.pos_end,
                        f"Value of type '{type(data_node_val).__name__}' cannot be deleted",
                    )
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

    def visit_DictNode(self, node: DictNode, context: Context):
        res = RTResult()
        dict_ = {}

        for key, value in node.key_value_nodes:
            key_val = res.register(self.visit(key, context))
            if res.should_return():
                return res

            if not isinstance(key_val, String):
                return res.faliure(
                    RTError(
                        key.pos_start,
                        key.pos_end,
                        f"Dictionary keys must be of type 'string' not '{type(key).__name__}'",
                    )
                )

            value_val = res.register(self.visit(value, context))
            if res.should_return():
                return res

            dict_[key_val.value] = value_val

        return res.success(
            Dict(dict_).set_context(context).set_pos(node.pos_start, node.pos_end)
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
            result, error = left.__add__(right)

        elif node.op_tok.type == TT.MINUS:
            result, error = left.__sub__(right)

        elif node.op_tok.type == TT.MULT:
            result, error = left.__mul__(right)

        elif node.op_tok.type == TT.DIV:
            result, error = left.__truediv__(right)

        elif node.op_tok.type == TT.FDIV:
            result, error = left.__floordiv__(right)

        elif node.op_tok.type == TT.MODU:
            result, error = left.__mod__(right)

        elif node.op_tok.type == TT.POW:
            result, error = left.__pow__(right)

        elif node.op_tok.type == TT.EE:
            result, error = left.__eq__(right)

        elif node.op_tok.type == TT.NE:
            result, error = left.__ne__(right)

        elif node.op_tok.type == TT.LT:
            result, error = left.__lt__(right)

        elif node.op_tok.type == TT.GT:
            result, error = left.__gt__(right)

        elif node.op_tok.type == TT.LTE:
            result, error = left.__lte__(right)

        elif node.op_tok.type == TT.GTE:
            result, error = left.__gte__(right)

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
            step_value = NewNum(1)

        i = start_value.value

        if step_value.value >= 0:
            condition = lambda: i < end_value.value
        else:
            condition = lambda: i > end_value.value

        while condition():
            context.symbol_table.set(node.var_name_tok.value, NewNum(i))
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

built_ins = [func[8:] for func in dir(BuiltInFunction) if func.startswith("execute_")]

for func_name in built_ins:
    global_symbol_table.set(func_name, BuiltInFunction(func_name))


def run(fn: str, text: str):
    # Generate Tokens
    text = text.rstrip()
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

    # AST json
    generator = Generator()
    with open("cloudylang/ast.json", "w") as f:
        json.dump(generator.gen(ast.node), f)

    # Get Interpreter
    interpreter = Interpreter()
    context = Context("<program>")
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)

    if str(result.value) in {"True", "False"}:
        result.value = str(result.value).lower()

    return result.value, result.error
