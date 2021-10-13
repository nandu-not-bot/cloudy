from .coretypes import DataType, Int, Number
from ..errors import RTError
from ..utils import Context, RTResult, SymbolTable

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

class List(DataType):
    def __init__(self, elements: list):
        super().__init__()
        self.elements = elements

    def __add__(self, other):
        if not isinstance(other, List):
            return None, DataType.illegal_operation(other)
        
        new_list = self.copy()
        return List(new_list.elements + other.elements), None

    def __mul__(self, other):
        if not isinstance(other, Int):
            return None, DataType.illegal_operation(other)

        new_list = self.copy()
        new_list *= other
        return new_list, None

    def copy(self):
        return (
            List(self.elements)
            .set_context(self.context)
            .set_pos(self.pos_start, self.pos_end)
        )

    def is_index(self, idx: Number):
        return -len(self.elements) <= idx.value < len(self.elements)

    def __getitem__(self, idx: Number):
        return self.elements[idx.value]

    def __repr__(self):
        return f"{self.elements!r}"