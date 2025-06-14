from enum import Enum


class NodeType(Enum):
    """Enumeration of all possible node types in the AST."""
    Program = "Program"

    # Statements
    ExpressionStatement = "ExpressionStatement"
    VarStatement = "VarStatement"
    FunctionStatement = "FunctionStatement"
    ReturnStatement = "ReturnStatement"
    AssignStatement = "AssignStatement"
    IfStatement = "IfStatement"
    WhileStatement = "WhileStatement"
    BreakStatement = "BreakStatement"
    ContinueStatement = "ContinueStatement"
    ImportStatement = "ImportStatement"

    # Expressions
    InfixExpression = "InfixExpression"
    CallExpression = "CallExpression"
    PrefixExpression = "PrefixExpression"

    # Literals
    IntegerLiteral = "IntegerLiteral"
    FloatLiteral = "FloatLiteral"
    IdentifierLiteral = "IdentifierLiteral"
    BooleanLiteral = "BooleanLiteral"
    StringLiteral = "StringLiteral"

    # Helper
    FunctionParameter = "FunctionParameter"


class Node:
    """Base abstract class for all AST nodes."""
    
    def type(self):
        """Return the type of this node."""
        pass

    def json(self):
        """Convert the node to a JSON-serializable dictionary."""
        pass


class Statement(Node):
    """Base class for all statement nodes."""
    pass


class Expression(Node):
    """Base class for all expression nodes."""
    pass


class Program(Node):
    """Root node of the AST representing an entire program."""
    
    def __init__(self):
        self.statements = []
    
    def type(self):
        return NodeType.Program
    
    def json(self):
        return {
            "type": self.type().value,
            "statements": [{stmt.type().value: stmt.json()} for stmt in self.statements]
        }


class FunctionParameter(Expression):
    """Represents a parameter in a function definition."""
    
    def __init__(self, name: str, value_type: str = None):
        self.name = name
        self.value_type = value_type

    def type(self):
        return NodeType.FunctionParameter

    def json(self):
        return {
            "type": self.type().value,
            "name": self.name,
            "value_type": self.value_type
        }


class ExpressionStatement(Statement):
    """A statement consisting of a single expression."""
    
    def __init__(self, expr: Expression = None):
        self.expr = expr

    def type(self):
        return NodeType.ExpressionStatement

    def json(self):
        return {
            "type": self.type().value,
            "expr": self.expr.json()
        }


class AssignStatement(Statement):
    """An assignment statement (e.g., x = value)."""
    
    def __init__(self, ident: Expression = None, operator: str = "", right_value: Expression = None):
        self.ident = ident
        self.operator = operator
        self.right_value = right_value
    
    def type(self):
        return NodeType.AssignStatement
    
    def json(self):
        return {
            "type": self.type().value,
            "ident": self.ident.json(),
            "right_value": self.right_value.json()
        }


class IfStatement(Statement):
    """A conditional statement with optional else clause."""
    
    def __init__(self, condition: Expression = None, body: list = None, else_body: list = None):
        self.condition = condition
        self.body = body or []
        self.else_body = else_body or []
    
    def type(self):
        return NodeType.IfStatement
    
    def json(self):
        return {
            "type": self.type().value,
            "condition": self.condition.json(),
            "body": [stmt.json() for stmt in self.body],
            "else_body": [stmt.json() for stmt in self.else_body]
        }


class WhileStatement(Statement):
    """A while loop statement."""
    
    def __init__(self, condition: Expression, body: list = None):
        self.condition = condition
        self.body = body if body is not None else []

    def type(self):
        return NodeType.WhileStatement
    
    def json(self):
        return {
            "type": self.type().value,
            "condition": self.condition.json(),
            "body": [stmt.json() for stmt in self.body]
        }


class BreakStatement(Statement):
    """A break statement to exit a loop."""
    def __init__(self):
        pass
    
    def type(self):
        return NodeType.BreakStatement
    
    def json(self):
        return {
            "type": self.type().value
        }


class ContinueStatement(Statement):
    """A continue statement to exit a loop."""
    def __init__(self):
        pass
    
    def type(self):
        return NodeType.ContinueStatement
    
    def json(self):
        return {
            "type": self.type().value
        }


class ImportStatement(Statement):
    """A import statement to import external library written in this language"""
    def __init__(self, file_path: str):
        self.file_path = file_path

    def type(self):
        return NodeType.ImportStatement
    
    def json(self):
        return {
            "type": self.type().value,
            "file_path": self.file_path
        }


class FunctionStatement(Statement):
    """A function definition statement."""
    
    def __init__(self, parameters: list[FunctionParameter] = None, body=None, 
                name=None, return_type: str = None):
        self.parameters = parameters or []
        self.body = body or []
        self.name = name
        self.return_type = return_type

    def type(self):
        return NodeType.FunctionStatement
    
    def json(self):
        return {
            "type": self.type().value,
            "name": self.name.json(),
            "return_type": self.return_type,
            "parameters": [p.json() for p in self.parameters],
            "body": [stmt.json() for stmt in self.body]
        }


class ReturnStatement(Statement):
    """A return statement within a function."""
    
    def __init__(self, return_value: Expression = None):
        self.return_value = return_value
    
    def type(self):
        return NodeType.ReturnStatement
    
    def json(self):
        return {
            "type": self.type().value,
            "return_value": self.return_value.json()
        }


class VarStatement(Statement):
    """A variable declaration statement."""
    
    def __init__(self, name: Expression = None, value: Expression = None, value_type: str = None):
        self.name = name
        self.value = value
        self.value_type = value_type
    
    def type(self):
        return NodeType.VarStatement
    
    def json(self):
        return {
            "type": self.type().value,
            "name": self.name.json(),
            "value": self.value.json(),
            "value_type": self.value_type
        }


class InfixExpression(Expression):
    """An expression with an operator between two operands (e.g., a + b)."""
    
    def __init__(self, left_node: Expression, operator: str, right_node: Expression = None):
        self.left_node = left_node
        self.operator = operator
        self.right_node = right_node

    def type(self):
        return NodeType.InfixExpression

    def json(self):
        return {
            "type": self.type().value,
            "left_node": self.left_node.json(),
            "operator": self.operator,
            "right_node": self.right_node.json()
        }


class CallExpression(Expression):
    """A function call expression."""
    
    def __init__(self, function: Expression = None, args: list[Expression] = None):
        self.function = function  # Expected to be an IdentifierLiteral
        self.args = args or []

    def type(self):
        return NodeType.CallExpression
    
    def json(self):
        return {
            "type": self.type().value,
            "function": self.function.json(),
            "args": [arg.json() for arg in self.args]
        }


class PrefixExpression(Expression):
    """An expression with an operator before its operand (e.g., -a)."""
    
    def __init__(self, operator: str, right_node: Expression = None):
        self.operator = operator
        self.right_node = right_node

    def type(self):
        return NodeType.PrefixExpression
    
    def json(self):
        return {
            "type": self.type().value,
            "operator": self.operator,
            "right_node": self.right_node.json()
        }


class IntegerLiteral(Expression):
    """An integer literal value."""
    
    def __init__(self, value):
        self.value = value
    
    def type(self):
        return NodeType.IntegerLiteral
    
    def json(self):
        return {
            "type": self.type().value,
            "value": self.value
        }


class FloatLiteral(Expression):
    """A floating-point literal value."""
    
    def __init__(self, value):
        self.value = value
    
    def type(self):
        return NodeType.FloatLiteral
    
    def json(self):
        return {
            "type": self.type().value,
            "value": self.value
        }


class IdentifierLiteral(Expression):
    """An identifier (variable or function name)."""
    
    def __init__(self, value):
        self.value = value
    
    def type(self):
        return NodeType.IdentifierLiteral
    
    def json(self):
        return {
            "type": self.type().value,
            "value": self.value
        }


class BooleanLiteral(Expression):
    """A boolean literal (True or False)."""
    
    def __init__(self, value):
        self.value = value
    
    def type(self):
        return NodeType.BooleanLiteral
    
    def json(self):
        return {
            "type": self.type().value,
            "value": self.value
        }


class StringLiteral(Expression):
    """A string literal value."""
    
    def __init__(self, value):
        self.value = value
    
    def type(self):
        return NodeType.StringLiteral
    
    def json(self):
        return {
            "type": self.type().value,
            "value": self.value
        }