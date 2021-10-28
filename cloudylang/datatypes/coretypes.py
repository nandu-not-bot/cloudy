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
            return NewNum(self.value)
        elif str_value in {"True", "False"}:
            return Bool(self.value)

    def is_true(self):
        return False

    def illegal_operation(self, other=None):
        if not other:
            other = self
        return RTError(self.pos_start, other.pos_end, "Illegal operation", self.context)

    def __add__(self, other):
        return None, self.illegal_operation(other)

    def __sub__(self, other):
        return None, self.illegal_operation(other)

    def __mul__(self, other):
        return None, self.illegal_operation(other)

    def __truediv__(self, other):
        return None, self.illegal_operation(other)

    def __floordiv__(self, other):
        return None, self.illegal_operation(other)

    def __mod__(self, other):
        return None, self.illegal_operation(other)

    def __pow__(self, other):
        return None, self.illegal_operation(other)

    def __eq__(self, other):
        return None, self.illegal_operation(other)

    def __ne__(self, other):
        return None, self.illegal_operation(other)

    def __lt__(self, other):
        return None, self.illegal_operation(other)

    def __lte__(self, other):
        return None, self.illegal_operation(other)

    def __gt__(self, other):
        return None, self.illegal_operation(other)

    def __gte__(self, other):
        return None, self.illegal_operation(other)
    
    def __and__(self, other):
        return None, self.illegal_operation(other)
    
    def __or__(self, other):
        return None, self.illegal_operation(other)

    def __not__(self):
        return None, self.illegal_operation()

    def __neg__(self):
        return None, self.illegal_operation()

class NewNum:
    def __new__(cls, value):
        if "." in str(value):
            return Float(value)
        else:
            return Int(value)

class Number(DataType):
    def __init__(self, value: int):
        self.value = value
        super().__init__()

    def copy(self):
        return (
            NewNum(self.value)
            .set_context(self.context)
            .set_pos(self.pos_start, self.pos_end)
        )

    @property
    def is_float(self):
        return "." in str(self.value)

    def __add__(self, other):
        if isinstance(other, (Number, Bool)):
            return NewNum(self.value + other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(other)

    def __sub__(self, other):
        if isinstance(other, (Number, Bool)):
            return NewNum(self.value - other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(other)

    def __mul__(self, other):
        if isinstance(other, (Number, Bool)):
            return NewNum(self.value * other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(other)

    def __truediv__(self, other):
        if not isinstance(other, (Number, Bool)):
            return None, DataType.illegal_operation(other)

        if other.value == 0:
            return None, RTError(
                other.pos_start, other.pos_end, "Division by zero", self.context
            )
        return NewNum(self.value / other.value).set_context(self.context), None

    def __floordiv__(self, other):
        if not isinstance(other, (Number, Bool)):
            return None, DataType.illegal_operation(other)

        if other.value == 0:
            return None, RTError(
                other.pos_start, other.pos_end, "Division by zero", self.context
            )
        return NewNum(self.value // other.value).set_context(self.context), None

    def __mod__(self, other):
        if not isinstance(other, (Number, Bool)):
            return None, DataType.illegal_operation(other)

        if other.value == 0:
            return None, RTError(
                other.pos_start, other.pos_end, "Modulo by zero", self.context
            )
        return NewNum(self.value % other.value).set_context(self.context), None

    def __neg__(self):
        return NewNum(-self.value)

    def __pow__(self, other):
        if isinstance(other, (Number, Bool)):
            return NewNum(self.value ** other.value).set_context(self.context), None
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
            return Bool(True).set_context(self.context), None

    def __lt__(self, other):
        if isinstance(other, (Number, Bool)):
            return Bool(self.value < other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(other)

    def __lte__(self, other):
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

    def __gte__(self, other):
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

class Float(Number):
    def __init__(self, value):
        super().__init__(value)

class Int(Number):
    def __init__(self, value):
        super().__init__(value)

class Null(DataType):
    def __init__(self):
        super().__init__()

    def copy(self):
        return Null()

    def __eq__(self, other):
        if isinstance(other, Null):
            return Bool(True).set_context(self.context), None
        else:
            return Bool(False).set_context(self.context), None

    def __ne__(self, other):
        if isinstance(other, Null):
            return Bool(False).set_context(self.context), None
        else:
            return Bool(True).set_context(self.context), None

    def __not__(self, other):
        return Bool(True).set_context(self.context), None

    def __repr__(self):
        return "null"


class Bool(DataType):
    def __init__(self, value: bool):
        self.value = value
        super().__init__()

    def __add__(self, other):
        if isinstance(other, (Number, Bool)):
            return NewNum(self.value + other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(other)

    def __sub__(self, other):
        if isinstance(other, (Number, Bool)):
            return NewNum(self.value - other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(other)

    def __mul__(self, other):
        if isinstance(other, (Number, Bool)):
            return NewNum(self.value * other.value).set_context(self.context), None
        else:
            return None, DataType.illegal_operation(other)

    def __truediv__(self, other):
        if not isinstance(other, (Number, Bool)):
            return None, DataType.illegal_operation(other)

        if other.value == 0:
            return None, RTError(
                other.pos_start, other.pos_end, "Division by zero", self.context
            )
        return NewNum(self.value / other.value).set_context(self.context), None

    def __floordiv__(self, other):
        if not isinstance(other, (Number, Bool)):
            return None, DataType.illegal_operation(other)

        if other.value == 0:
            return None, RTError(
                other.pos_start, other.pos_end, "Division by zero", self.context
            )
        return NewNum(self.value // other.value).set_context(self.context), None

    def __mod__(self, other):
        if not isinstance(other, (Number, Bool)):
            return None, DataType.illegal_operation(other)

        if other.value == 0:
            return None, RTError(
                other.pos_start, other.pos_end, "Modulo by zero", self.context
            )
        return NewNum(self.value % other.value).set_context(self.context), None

    def __neg__(self):
        return NewNum(-self.value)

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

    def __eq__(self, other):
        if isinstance(other, String):
            return Bool(self.value == other.value).set_context(self.context), None
        else:
            return Bool(False).set_context(self.context), None

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