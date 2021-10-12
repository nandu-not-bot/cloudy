from .utils import Position, string_with_arrows


class Error:
    def __init__(
        self, pos_start: Position, pos_end: Position, error_name: str, details: str
    ):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def __str__(self):
        string = f"{self.error_name}: {self.details}\n"
        string += f"File {self.pos_start.fn}, line {self.pos_start.ln + 1}"
        string += f"\n\n{string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)}"
        return string


class IllegalCharError(Error):
    def __init__(self, pos_start: Position, pos_end: Position, details: str):
        super().__init__(pos_start, pos_end, "Illegal Character", details)


class ExpectedCharError(Error):
    def __init__(self, pos_start: Position, pos_end: Position, details: str):
        super().__init__(pos_start, pos_end, "Expected Character", details)


class InvalidSyntaxError(Error):
    def __init__(self, pos_start: Position, pos_end: Position, details: str):
        super().__init__(pos_start, pos_end, "Invalid Syntax", details)


class RTError(Error):
    def __init__(self, pos_start: Position, pos_end: Position, details: str, context):
        super().__init__(pos_start, pos_end, "Runtime Error", details)
        self.context = context

    def __str__(self):
        string = self.generate_traceback()
        string += f"{self.error_name}: {self.details}"
        string += f"\n\n{string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)}"
        return string

    def generate_traceback(self):
        result = ""
        pos = self.pos_start
        ctx = self.context

        while ctx:
            result = (
                f"  File {pos.fn}, line {pos.ln + 1}, in {ctx.display_name}\n" + result
            )
            pos = ctx.parent_entry_pos
            ctx = ctx.parent

        return "Traceback (most recent call last):\n" + result


class ExpectedCharError(Error):
    def __init__(self, pos_start: Position, pos_end: Position, details: str):
        super().__init__(pos_start, pos_end, "Expected Character", details)


class IndexError(Error):
    def __init__(self, pos_start: Position, pos_end: Position, dtype: str):
        super().__init__(
            pos_start, pos_end, "Index Error", f"{dtype.lower()} index out of range"
        )
