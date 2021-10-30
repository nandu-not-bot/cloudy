from .utils import Position
from ..lexer import Token

class NumberNode:
    def __init__(self, tok: Token):
        self.tok = tok

        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f"{self.tok}"


class BoolNode:
    def __init__(self, tok: Token):
        self.tok = tok

        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f"{self.tok}"


class StringNode:
    def __init__(self, tok: Token):
        self.tok = tok

        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f"{self.tok}"


class ListNode:
    def __init__(
        self, element_nodes: list[NumberNode], pos_start: Position, pos_end: Position
    ):
        self.element_nodes = element_nodes
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return str(self.element_nodes)


class DictNode:
    def __init__(self, key_value_nodes: list[tuple[StringNode]], pos_start: Position, pos_end: Position):
        self.key_value_nodes = key_value_nodes
        self.pos_start = pos_start
        self.pos_end = pos_end

class VarAccessNode:
    def __init__(self, var_name_tok: Token):
        self.var_name_tok = var_name_tok

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end

    def __repr__(self):
        return f"({self.var_name_tok})"


class VarAssignNode:
    def __init__(self, var_name_tok: Token, value_node: NumberNode):
        self.var_name_tok = var_name_tok
        self.value_node = value_node

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end

    def __repr__(self) -> str:
        return f"({self.var_name_tok} = {self.value_node})"


class BinOpNode:
    def __init__(self, left_node: NumberNode, op_tok: Token, right_node: NumberNode):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self):
        return f"({self.left_node} {self.op_tok} {self.right_node})"


class UnaryOpNode:
    def __init__(self, op_tok: Token, node: NumberNode):
        self.op_tok = op_tok
        self.node = node

        self.pos_start = self.op_tok.pos_start
        self.pos_end = node.pos_end

    def __repr__(self):
        return f"({self.op_tok} {self.node})"


class IfNode:
    def __init__(
        self,
        cases: tuple[list[tuple[BinOpNode]], bool],
        else_case: tuple[BinOpNode, bool],
    ):
        self.cases = cases
        self.else_case = else_case

        self.pos_start = self.cases[0][0].pos_start
        self.pos_end = (self.else_case or self.cases[-1])[0].pos_end

    def __repr__(self) -> str:
        return f"({self.cases=}, {self.else_case=})"


class ForNode:
    def __init__(
        self,
        var_name_tok: Token,
        start_value_node: BinOpNode,
        end_value_node: BinOpNode,
        step_value_node: BinOpNode,
        body_node: BinOpNode,
        should_return_null: bool,
    ):
        self.var_name_tok = var_name_tok
        self.start_value_node = start_value_node
        self.end_value_node = end_value_node
        self.step_value_node = step_value_node
        self.body_node = body_node
        self.should_return_null = should_return_null

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.body_node.pos_end

    def __repr__(self):
        return f"for {self.var_name_tok} = {self.start_value_node} ..."


class WhileNode:
    def __init__(
        self, condition_node: BinOpNode, body_node: BinOpNode, shoud_return_null: bool
    ):
        self.condition_node = condition_node
        self.body_node = body_node
        self.should_return_null = shoud_return_null

        self.pos_start = self.condition_node.pos_start
        self.pos_end = self.body_node.pos_end

    def __repr__(self) -> str:
        return f"(while {self.condition_node} ...)"


class FuncDefNode:
    def __init__(
        self,
        var_name_tok: Token,
        arg_name_toks: list[Token],
        body_node: BinOpNode,
        should_auto_return: bool,
    ):
        self.var_name_tok = var_name_tok
        self.arg_name_toks = arg_name_toks
        self.body_node = body_node
        self.should_auto_return = should_auto_return

        if var_name_tok:
            self.pos_start = self.var_name_tok.pos_start
        elif len(self.arg_name_toks) > 0:
            self.pos_start = self.arg_name_toks[0].pos_start
        else:
            self.pos_start = self.body_node.pos_start

        self.pos_end = self.body_node.pos_end

    def __repr__(self):
        return f"(func {self.var_name_tok}({self.arg_name_toks}) ...)"


class CallNode:
    def __init__(self, node_to_call: FuncDefNode, arg_nodes: list[BinOpNode]):
        self.node_to_call = node_to_call
        self.arg_nodes = arg_nodes

        self.pos_start = self.node_to_call.pos_start

        if self.arg_nodes:
            self.pos_end = self.arg_nodes[-1].pos_end
        else:
            self.pos_end = self.node_to_call.pos_end

    def __repr__(self) -> str:
        return f"({self.node_to_call}({self.arg_nodes}))"


class IndexNode:
    def __init__(self, data_node: VarAccessNode, index_node: NumberNode):
        self.data_node = data_node
        self.index_node = index_node

        self.pos_start = data_node.pos_start
        self.pos_end = index_node.pos_end

    def __repr__(self):
        return f"({self.data_node}[{self.index_node}])"


class IndexAssignNode:
    def __init__(self, var_name_tok: Token, index: NumberNode, value_node: NumberNode):
        self.var_name_tok = var_name_tok
        self.index = index
        self.value_node = value_node
        self.pos_start = index.pos_start
        self.pos_end = value_node.pos_end

    def __repr__(self):
        return f"({self.index} = {self.value_node})"


class ReturnNode:
    def __init__(
        self, node_to_return: NumberNode, pos_start: Position, pos_end: Position
    ):
        self.node_to_return = node_to_return
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f"(return {self.node_to_return})"


class ContinueNode:
    def __init__(self, pos_start: Position, pos_end: Position):
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self) -> str:
        return "(continue)"


class BreakNode:
    def __init__(self, pos_start: Position, pos_end: Position):
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return '(break)'

class DelNode:
    def __init__(self, atom: IndexNode, pos_start, pos_end):
        self.atom = atom
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f"(del {self.atom})"
