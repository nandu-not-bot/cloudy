from .coretypes import Bool, DataType, Int, Number, String
from ..utils.errors import RTError
from ..utils.utils import Context, RTResult, SymbolTable


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
                    self.context,
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

    def add(self, other):
        if not isinstance(other, List):
            return None, DataType.illegal_operation(other)

        new_list = self.copy()
        return List(new_list.elements + other.elements), None

    def mul(self, other):
        if not isinstance(other, Int):
            return None, DataType.illegal_operation(other)

        new_list = self.copy()
        new_list *= other
        return new_list, None

    def in_(self, other):
        if isinstance(other, List):
            return Bool(other.elements in self.elements), None

        elif isinstance(other, String):
            for element in self.elements:
                if isinstance(element, String) and other.value == element.value:
                    return Bool(True).set_context(self.set_context), None
                
        elif isinstance(other, Number):
            for element in self.elements:
                if isinstance(element, Number) and other.value == element.value:
                    return Bool(True).set_context(self.set_context), None

        elif isinstance(other, Bool):
            for element in self.elements:
                if isinstance(element, Bool) and other.value == element.value:
                    return Bool(True).set_context(self.set_context), None
        
        elif isinstance(other, Dict):
            for element in self.elements:
                if isinstance(element, Dict) and other.pairs == element.pairs:
                    return Bool(True).set_context(self.set_context), None

        
        return Bool(False).set_context(self.set_context), None

    def not_in(self, other):
        if isinstance(other, List):
            return Bool(other.elements not in self.elements), None

        elif isinstance(other, String):
            for element in self.elements:
                if isinstance(element, String) and other.value == element.value:
                    return Bool(False).set_context(self.set_context), None

        elif isinstance(other, Number):
            for element in self.elements:
                if isinstance(element, Number) and other.value == element.value:
                    return Bool(False).set_context(self.set_context), None

        elif isinstance(other, Bool):
            for element in self.elements:
                if isinstance(element, Bool) and other.value == element.value:
                    return Bool(False).set_context(self.set_context), None

        elif isinstance(other, Dict):
            for element in self.elements:
                if isinstance(element, Dict) and other.pairs == element.pairs:
                    return Bool(False).set_context(self.set_context), None


        return Bool(True).set_context(self.set_context), None

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


class Dict(DataType):
    def __init__(self, pairs: dict):
        super().__init__()
        self.pairs = pairs

    def in_(self, other):
        if isinstance(other, String):
            return Bool(other.value in self.pairs), None
        return Bool(False).set_context(self.context), None

    def not_in(self, other):
        if isinstance(other, String):
            return Bool(other.value not in self.pairs), None
        return Bool(True).set_context(self.context), None

    def copy(self):
        return (
            Dict(self.pairs)
            .set_context(self.context)
            .set_pos(self.pos_start, self.pos_end)
        )

    def __repr__(self):
        return f"{self.pairs!r}"

class Range(DataType):
    def __init__(self, start: Number, end: Number, step: Number):
        super().__init__()
        self.start = start
        self.end = end
        self.step = step or Int(1)

    def __iter__(self):
        i = self.start.value
        while i < self.end.value:
            yield Number(i)
            i += self.step.value

    def copy(self):
        return Range(self.start, self.end, self.step).set_context(self.context)

    def __repr__(self):
        return f"<range {self.start}..{self.end}{f'!{self.step}' if self.step else ''}>"