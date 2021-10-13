from ..utils import Position
from ..errors import RTError


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

    @property
    def is_float(self):
        return "." in str(self.value)

    def __add__(self, other):
        if isinstance(other, (Number, Bool)):
            return Number(self.value + other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(other)

    def __sub__(self, other):
        if isinstance(other, (Number, Bool)):
            return Number(self.value - other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(other)

    def __mul__(self, other):
        if isinstance(other, (Number, Bool)):
            return Number(self.value * other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(other)

    def __truediv__(self, other):
        if not isinstance(other, (Number, Bool)):
            return None, DataType.illegal_operation(other)

        if other.value == 0:
            return None, RTError(
                other.pos_start, other.pos_end, "Division by zero", self.context
            )
        return Number(self.value / other.value).set_context(self.context), None

    def __floordiv__(self, other):
        if not isinstance(other, (Number, Bool)):
            return None, DataType.illegal_operation(other)

        if other.value == 0:
            return None, RTError(
                other.pos_start, other.pos_end, "Division by zero", self.context
            )
        return Number(self.value // other.value).set_context(self.context), None

    def __mod__(self, other):
        if not isinstance(other, (Number, Bool)):
            return None, DataType.illegal_operation(other)

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
            return None, DataType.illegal_operation(other)

    def __eq__(self, other):
        if isinstance(other, (Number, Bool)):
            return (
                Bool(self.value == other.value).set_context(self.context),
                None,
            )
        else:
            return None, DataType.illegal_operation(other)

    def __ne__(self, other):
        if isinstance(other, (Number, Bool)):
            return (
                Bool(self.value != other.value).set_context(self.context),
                None,
            )
        else:
            return None, DataType.illegal_operation(other)

    def __lt__(self, other):
        if isinstance(other, (Number, Bool)):
            return Bool(self.value < other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(other)

    def __le__(self, other):
        if isinstance(other, (Number, Bool)):
            return (
                Bool(self.value <= other.value).set_context(self.context),
                None,
            )
        else:
            return None, DataType.illegal_operation(other)

    def __gt__(self, other):
        if isinstance(other, (Number, Bool)):
            return Bool(self.value > other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(other)

    def __ge__(self, other):
        if isinstance(other, (Number, Bool)):
            return (
                Bool(self.value >= other.value).set_context(self.context),
                None,
            )
        else:
            return None, DataType.illegal_operation(other)

    def __and__(self, other):
        if isinstance(other, (Number, Bool)):
            return (
                Bool(self.value and other.value).set_context(self.context),
                None,
            )
        else:
            return None, DataType.illegal_operation(other)

    def __or__(self, other):
        if isinstance(other, (Number, Bool)):
            return (
                bool(self.value or other.value).set_context(self.context),
                None,
            )
        else:
            return None, DataType.illegal_operation(other)

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
            return None, DataType.illegal_operation(other)

    def __sub__(self, other):
        if isinstance(other, (Number, Bool)):
            return Number(self.value - other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(other)

    def __mul__(self, other):
        if isinstance(other, (Number, Bool)):
            return Number(self.value * other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(other)

    def __truediv__(self, other):
        if not isinstance(other, (Number, Bool)):
            return None, DataType.illegal_operation(other)

        if other.value == 0:
            return None, RTError(
                other.pos_start, other.pos_end, "Division by zero", self.context
            )
        return Number(self.value / other.value).set_context(self.context), None

    def __floordiv__(self, other):
        if not isinstance(other, (Number, Bool)):
            return None, DataType.illegal_operation(other)

        if other.value == 0:
            return None, RTError(
                other.pos_start, other.pos_end, "Division by zero", self.context
            )
        return Number(self.value // other.value).set_context(self.context), None

    def __mod__(self, other):
        if not isinstance(other, (Number, Bool)):
            return None, DataType.illegal_operation(other)

        if other.value == 0:
            return None, RTError(
                other.pos_start, other.pos_end, "Modulo by zero", self.context
            )
        return Number(self.value % other.value).set_context(self.context), None

    def __neg__(self):
        return Number(-self.value)

    def __pow__(self, other):
        return None, DataType.illegal_operation(other)

    def __eq__(self, other):
        if isinstance(other, (Number, Bool)):
            return (
                Bool(self.value == other.value).set_context(self.context),
                None,
            )
        else:
            return None, DataType.illegal_operation(other)

    def __ne__(self, other):
        if isinstance(other, (Number, Bool)):
            return (
                Bool(self.value != other.value).set_context(self.context),
                None,
            )
        else:
            return None, DataType.illegal_operation(other)

    def __lt__(self, other):
        if isinstance(other, (Number, Bool)):
            return Bool(self.value < other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(other)

    def __le__(self, other):
        if isinstance(other, (Number, Bool)):
            return (
                Bool(self.value <= other.value).set_context(self.context),
                None,
            )
        else:
            return None, DataType.illegal_operation(other)

    def __gt__(self, other):
        if isinstance(other, (Number, Bool)):
            return Bool(self.value > other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(other)

    def __ge__(self, other):
        if isinstance(other, (Number, Bool)):
            return (
                Bool(self.value >= other.value).set_context(self.context),
                None,
            )
        else:
            return None, DataType.illegal_operation(other)

    def __and__(self, other):
        if isinstance(other, (Number, Bool)):
            return (
                Bool(self.value and other.value).set_context(self.context),
                None,
            )
        else:
            return None, DataType.illegal_operation(other)

    def __or__(self, other):
        if isinstance(other, (Number, Bool)):
            return (
                bool(self.value or other.value).set_context(self.context),
                None,
            )
        else:
            return None, DataType.illegal_operation(other)

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
            return None, DataType.illegal_operation(other)

    def __mul__(self, other):
        if isinstance(other, Number):
            return String(self.value * other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(other)

    def copy(self):
        return (
            String(self.value)
            .set_context(self.context)
            .set_pos(self.pos_start, self.pos_end)
        )

    def is_index(self, idx: Number):
        return -len(self.value) <= idx.value < len(self.value)

    def __getitem__(self, idx: Number):
        val = self.copy()
        val.value = self.value[idx.value]
        return val

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
            return None, DataType.illegal_operation(other)

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
            return None, DataType.illegal_operation(other)

        new_list = self.copy()
        new_list.elements.extend(other.elements)
        return new_list, None

    def __truediv__(self, other):
        if not isinstance(other, Number):
            return None, DataType.illegal_operation(other)
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

    def is_index(self, idx: Number):
        return -len(self.elements) <= idx.value < len(self.elements)

    def __getitem__(self, idx: Number):
        return self.elements[idx.value]

    def __repr__(self):
        return f"{self.elements!r}"

