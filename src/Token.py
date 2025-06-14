"""
Token module for the custom programming language lexer.
Defines token types and token representation for the language's syntax elements.
"""
from enum import Enum

from Position import Position


class TokenType(Enum):
    """Enumeration of all possible token types in the lexical analysis."""
    # Identifiers and literals
    IDENT = "IDENT"
    INT = "INT"
    FLOAT = "FLOAT"
    BOOL = "BOOL"
    STRING = "STRING"
    
    # Arithmetic Operators
    PLUS = "PLUS"
    MINUS = "MINUS"
    ASTERISK = "ASTERISK"
    SLASH = "SLASH"
    POW = "POW"
    MODULUS = "MODULUS"

    # Assignment Operators
    EQ = "EQ"
    PLUS_EQ = "PLUS_EQ"
    MINUS_EQ = "MINUS_EQ"
    MUL_EQ = "MUL_EQ"
    DIV_EQ = "DIV_EQ"
    POW_EQ = "POW_EQ"
    MOD_EQ = "MOD_EQ"
    
    # Delimiters
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    COLON = "COLON"
    COMMA = "COMMA"
    SEMICOLON = "SEMICOLON"
    
    # Keywords
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    VAR = "VAR"
    DEF = "DEF"
    RETURN = "RETURN"
    IF = "IF"
    ELIF = "ELIF"
    ELSE = "ELSE"
    TRUE = "TRUE"
    FALSE = "FALSE"
    WHILE = "WHILE"
    CONTINUE = "CONTINUE"
    BREAK = "BREAK"
    IMPORT = "IMPORT"
    END = "END"

    # Typing
    TYPE = "TYPE"
    
    # Special characters and operators
    ARROW = "ARROW"
    EOF = "EOF"
    ILLEGAL = "ILLEGAL"
    
    # Comparison operators
    GT = ">"
    LT = "<"
    GT_EQ = ">="
    LT_EQ = "<="
    NOT_EQ = "!="
    EQ_EQ = "=="


class Token:
    """
    Represents a token in the language with its type, literal value, and position.
    Tokens are the basic building blocks produced during lexical analysis.
    """
    def __init__(self, type_: TokenType, literal=None, pos_start: Position=None, pos_end: Position=None):
        """
        Initialize a token with type, literal value, and position information.
        
        Args:
            type_: The token type from TokenType enum
            literal: The literal string value of the token (optional)
            pos_start: Starting position of token in source code
            pos_end: Ending position of token in source code
        """
        self.type = type_
        self.literal = literal
        
        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()  # end position is exclusive
        
        if pos_end:
            self.pos_end = pos_end.copy()

    def __str__(self):
        """
        String representation of the token, including position information.
        
        Returns:
            String with token type, literal (if available), and position info
        """
        return (f"{self.type}" + 
                (f": {self.literal}" if self.literal else "") + 
                f" [line no: {self.pos_start.ln}, col no: {self.pos_start.col}]")


# Dictionary mapping keyword strings to their corresponding token types
KEYWORDS = {
    "and": TokenType.AND,
    "or": TokenType.OR,
    "not": TokenType.NOT,
    "var": TokenType.VAR,
    "def": TokenType.DEF,
    "return": TokenType.RETURN,
    "if": TokenType.IF,
    "elif": TokenType.ELIF,
    "else": TokenType.ELSE,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "while": TokenType.WHILE,
    "continue": TokenType.CONTINUE,
    "break": TokenType.BREAK,
    "import": TokenType.IMPORT,
    "end": TokenType.END
}

# List of supported data types in the language
TYPE_KEYWORDS = ["int", "float", "bool", "str", "void"]


def lookup_ident(ident: str) -> TokenType:
    """
    Look up an identifier to determine if it's a keyword or a regular identifier.
    
    Args:
        ident: The identifier string to look up
        
    Returns:
        The appropriate TokenType (keyword type or IDENT)
    """
    # Check if it's a keyword
    tt = KEYWORDS.get(ident)
    if tt is not None:
        return tt
    
    # Check if it's a type
    if ident in TYPE_KEYWORDS:
        return TokenType.TYPE
    
    # Default to identifier
    return TokenType.IDENT