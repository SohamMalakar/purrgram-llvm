from llvmlite import ir

class Environment:
    def __init__(self, records: dict[ir.Value, ir.Type] = None, parent = None, name: str = "global"):
        self.records = records if records else {}
        self.parent = parent
        self.name = name
    
    def define(self, name: str, value: ir.Value, _type: ir.Type) -> ir.Value:
        self.records[name] = (value, _type)
        return value
    
    def lookup(self, name: str) -> tuple[ir.Value, ir.Type]:
        return self.resolve(name)

    def resolve(self, name: str) -> tuple[ir.Value, ir.Type]:
        if name in self.records:
            return self.records[name]
        elif self.parent:
            return self.parent.resolve(name)
        else:
            return None