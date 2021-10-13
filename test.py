class A:
    def __new__(cls, value):
        if value:
            return T(value)
        else:
            return F(value)

class T(A):
    def __init__(self, value):
        self.value = value

class F(A):
    def __new__(cls, value):
        return 

    def __init__(self, value):
        self.value = value

print(A(False))