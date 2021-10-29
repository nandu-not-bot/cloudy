from .utils import Context, Position, SymbolTable
from .parser import (
    IndexAssignNode,
    NumberNode,
    BoolNode,
    StringNode,
    ListNode,
    VarAccessNode,
    VarAssignNode,
    CallNode,
    IndexNode,
    FuncDefNode,
    IfNode,
    WhileNode,
    ForNode,
    ReturnNode,
    ContinueNode,
    BreakNode,
    BinOpNode,
    UnaryOpNode,
)

class Generator:

    def gen(self, node) -> dict:
        method_name = f"gen_{type(node).__name__}"
        method = getattr(self, method_name, self.no_gen_method)
        return method(node)

    def no_gen_method(self, node):
        raise NotImplementedError(f"We dont have a gen for this node! {type(node).__name__}")

    def gen_list(self, node):
        return [
            self.gen(e) for e in node
        ]
        
    def gen_NumberNode(self, node: NumberNode) -> dict:        
        return {
            "name": "NumberNode",
            "value": node.tok.value
        }

    def gen_BoolNode(self, node: BoolNode) -> dict:
        return {
            "name": "BoolNode",
            "value": node.tok.value
        }

    def gen_StringNode(self, node: StringNode) -> dict:
        return {
            "name": "StringNode",
            "value": node.tok.value
        }

    def gen_ListNode(self, node: ListNode) -> dict:
        return {
            "name": "ListNode",
            "elements": {
                str(i): self.gen(n) for i, n in enumerate(node.element_nodes)
            }
        }

    def gen_VarAssignNode(self, node: VarAssignNode) -> dict:
        return {
            "name": "VarAssignNode",
            "var_name": node.var_name_tok.value,
            "value": self.gen(node.value_node)
        }

    def gen_VarAccessNode(self, node: VarAccessNode) -> dict:
        return {
            "name": "VarAccessNode",
            "var_name": node.var_name_tok.value
        }

    def gen_CallNode(self, node: CallNode) -> dict:
        return {
            "name": "CallNode",
            "node_to_call": self.gen(node.node_to_call),
            "args": self.gen(node.arg_nodes)
        }
    
    def gen_IndexNode(self, node: IndexNode) -> dict:
        return {
            "name": "IndexNode",
            "data_node": self.gen(node.data_node),
            "index_node": self.gen(node.index_node)
        }

    def gen_IndexAssignNode(self, node: IndexAssignNode) -> dict:
        return {
            "name": "IndexAssignNode",
            "index_node": self.gen(node.index),
            "value_node": self.gen(node.value_node)
        }
    
    def gen_FuncDefNode(self, node: FuncDefNode) -> dict:
        return {
            "name": "FuncDefNode",
            "var_name": node.var_name_tok.value if node.var_name_tok else None,
            "arg_names": [
                arg_tok.value for arg_tok in node.arg_name_toks
            ],
            "body": self.gen(node.body_node),
            "should_auto_return": node.should_auto_return
        }

    def gen_IfNode(self, node: IfNode) -> dict:
        return {
            "name": "IfNode",
            "cases": [
                {
                    "condition": self.gen(condition),
                    "body": self.gen(body),
                    "should_auto_return": should_auto_return
                } for condition, body, should_auto_return in node.cases
            ],
            "else_case": {
                "body": self.gen(node.else_case[0]),
                "should_auto_return": node.else_case[1]
            } if node.else_case else None
        }

    def gen_WhileNode(self, node: WhileNode) -> dict:
        return {
            "name": "WhileNode",
            "condition": self.gen(node.condition_node),
            "body": self.gen(node.body_node),
            "should_return_null": node.should_return_null
        }

    def gen_ForNode(self, node: ForNode) -> dict:
        return {
            "name": "ForNode",
            "iterator_name": node.var_name_tok.value,
            "start_value": self.gen(node.start_value_node),
            "end_value": self.gen(node.end_value_node),
            "step_value": self.gen(node.step_value_node) if node.step_value_node else None,
            "body": self.gen(node.body_node),
            "should_return_null": node.should_return_null
        }

    def gen_ReturnNode(self, node: ReturnNode) -> dict:
        return {
            "name": "ReturnNode",
            "node_to_return": self.gen(node.node_to_return)
        }

    def gen_ContinueNode(self, node: ContinueNode) -> dict:
        return {
            "name": "ContinueNode"
        }

    def gen_BreakNode(self, node: BreakNode) -> dict:
        return {
            "name": "BreakNode"
        }

    def gen_BinOpNode(self, node: BinOpNode) -> dict:
        return {
            "name": "BinOpNode",
            "left_node": self.gen(node.left_node),
            "op": repr(node.op_tok),
            "right_node": self.gen(node.right_node)
        }

    def gen_UnaryOpNode(self, node: UnaryOpNode) -> dict:
        return {
            "name": "UnaryOpNode",
            "op": repr(node.op_tok),
            "node": self.gen(node.node)
        }
