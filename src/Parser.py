from enum import Enum, auto
from typing import Optional, Dict, List, Callable, Any

from Token import Token, TokenType
from Error import ErrorHandler

from AST import (
    Statement, Expression, Program,
    ExpressionStatement, VarStatement, FunctionStatement,
    ReturnStatement, AssignStatement, IfStatement,
    WhileStatement, BreakStatement, ContinueStatement, ImportStatement,
    InfixExpression, CallExpression, PrefixExpression,
    IntegerLiteral, FloatLiteral, IdentifierLiteral,
    BooleanLiteral, StringLiteral, FunctionParameter
)


class PrecedenceType(Enum):
    """Enum representing operator precedence levels."""
    LOWEST = 0
    EQUALS = auto()
    LESSGREATER = auto()
    SUM = auto()
    PRODUCT = auto()
    EXPONENT = auto()
    PREFIX = auto()
    CALL = auto()


# Mapping of token types to their precedence
PRECEDENCES = {
    TokenType.PLUS: PrecedenceType.SUM,
    TokenType.MINUS: PrecedenceType.SUM,
    TokenType.ASTERISK: PrecedenceType.PRODUCT,
    TokenType.SLASH: PrecedenceType.PRODUCT,
    TokenType.MODULUS: PrecedenceType.PRODUCT,
    TokenType.POW: PrecedenceType.EXPONENT,
    TokenType.EQ_EQ: PrecedenceType.EQUALS,
    TokenType.NOT_EQ: PrecedenceType.EQUALS,
    TokenType.LT: PrecedenceType.LESSGREATER,
    TokenType.GT: PrecedenceType.LESSGREATER,
    TokenType.LT_EQ: PrecedenceType.LESSGREATER,
    TokenType.GT_EQ: PrecedenceType.LESSGREATER,
    TokenType.LPAREN: PrecedenceType.CALL
}


class Parser:
    """Parser for converting tokens into an abstract syntax tree."""
    
    def __init__(self, tokens: List[Token], error_handler=None):
        """
        Initialize the parser with a list of tokens.
        
        Args:
            tokens: List of tokens to parse
            error_handler: Optional error handler object
        """
        self.tokens = tokens
        self.pos = -1
        self.current_token = None
        self.exceptions = []
        self.error_handler = error_handler if error_handler else ErrorHandler()
        
        # Register prefix parsing functions
        self.prefix_parse_fns: Dict[TokenType, Callable] = {
            TokenType.IDENT: self.parse_identifier,
            TokenType.INT: self.parse_int_literal,
            TokenType.FLOAT: self.parse_float_literal,
            TokenType.STRING: self.parse_string_literal,
            TokenType.LPAREN: self.parse_grouped_expression,
            TokenType.TRUE: self.parse_boolean,
            TokenType.FALSE: self.parse_boolean,
            TokenType.MINUS: self.parse_prefix_expression,
            TokenType.NOT: self.parse_prefix_expression
        }

        # Register infix parsing functions
        self.infix_parse_fns: Dict[TokenType, Callable[[Expression], Expression]] = {
            TokenType.PLUS: self.parse_infix_expression,
            TokenType.MINUS: self.parse_infix_expression,
            TokenType.ASTERISK: self.parse_infix_expression,
            TokenType.SLASH: self.parse_infix_expression,
            TokenType.MODULUS: self.parse_infix_expression,
            TokenType.POW: self.parse_infix_expression,
            TokenType.EQ_EQ: self.parse_infix_expression,
            TokenType.NOT_EQ: self.parse_infix_expression,
            TokenType.LT: self.parse_infix_expression,
            TokenType.GT: self.parse_infix_expression,
            TokenType.LT_EQ: self.parse_infix_expression,
            TokenType.GT_EQ: self.parse_infix_expression,
            TokenType.LPAREN: self.parse_call_expression
        }

        self.advance()

    def advance(self) -> None:
        """Move to the next token."""
        self.pos += 1
        self.current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else None
    
    def synchronize(self, token_types: List[TokenType]) -> None:
        """
        Skip tokens until one of the specified token types is found.
        
        Args:
            token_types: List of token types to synchronize to
        """
        while (self.current_token and 
               self.current_token.type not in token_types and 
               self.current_token.type != TokenType.EOF):
            self.advance()

    def peek_token(self) -> Optional[Token]:
        """
        Look at the next token without advancing.
        
        Returns:
            The next token or None if at the end
        """
        return self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None

    def current_precedence(self) -> PrecedenceType:
        """
        Get precedence of current token.
        
        Returns:
            The precedence level of the current token
        """
        return PRECEDENCES.get(self.current_token.type, PrecedenceType.LOWEST)

    def peek_precedence(self) -> PrecedenceType:
        """
        Get precedence of next token.
        
        Returns:
            The precedence level of the next token
        """
        token = self.peek_token()
        return PRECEDENCES.get(token.type, PrecedenceType.LOWEST) if token else PrecedenceType.LOWEST

    def peek_token_is_assignment(self) -> bool:
        """
        Check if the next token is an assignment operator.

        Returns:
            True if the next token is an assignment operator, False otherwise
        """
        assignment_operators: list[TokenType] = [
            TokenType.EQ,
            TokenType.PLUS_EQ,
            TokenType.MINUS_EQ,
            TokenType.MUL_EQ,
            TokenType.DIV_EQ,
            TokenType.POW_EQ,
            TokenType.MOD_EQ
        ]
        return self.peek_token() and self.peek_token().type in assignment_operators

    def expect_token(
        self, 
        token_type: TokenType, 
        error_message: str, 
        do_advance: bool = True, 
        look_current: bool = False, 
        error_at_current: bool = False
    ) -> bool:
        """
        Check if next token is of expected type and advance, otherwise handle error.
        
        Args:
            token_type: Expected token type
            error_message: Error message to display if expectation fails
            do_advance: Whether to advance the token pointer
            look_current: Whether to check the current token instead of next token
            error_at_current: Whether to report error at current token position
            
        Returns:
            True if token matched expectation, False otherwise
        """
        if look_current:
            error_at_current = True

        token = self.current_token if look_current else self.peek_token()

        if token and token.type == token_type:
            if do_advance:
                self.advance()
            return True
        else:
            token = self.current_token if error_at_current else self.peek_token()
            self.report_error(token, error_message)
            return False

    def report_error(
        self, 
        token: Token, 
        message: str, 
        do_advance: bool = True, 
        sync_tokens: List[TokenType] = [TokenType.SEMICOLON]
    ) -> None:
        """
        Report an error and synchronize parser state.
        
        Args:
            token: Token where error occurred
            message: Error message
            do_advance: Whether to advance after reporting
            sync_tokens: Tokens to synchronize to
        
        Raises:
            Exception: Always raises to help with error recovery
        """
        self.error_handler.add_error(
            token.pos_start, 
            token.pos_end, 
            "Syntax Error",
            message
        )
        self.synchronize(sync_tokens)
        if do_advance:
            self.advance()
        raise Exception(message)

    def expect_semicolon(self) -> bool:
        """
        Check for required semicolon at end of statement.
        
        Returns:
            True if semicolon found, False otherwise
        """
        return self.expect_token(
            TokenType.SEMICOLON, 
            "Expected semicolon ';' after expression", 
            error_at_current=True
        )

    def parse_program(self) -> Program:
        """
        Parse the entire program.
        
        Returns:
            Program AST node containing all statements
        """
        program = Program()

        while self.current_token and self.current_token.type != TokenType.EOF:
            try:
                stmt = self.parse_statement()
                if stmt is not None:
                    program.statements.append(stmt)
                
                # Advance because the current token is ';'
                self.advance()
            except Exception as e:
                self.exceptions.append(f"Synchronizing after error: {e}")

        if self.exceptions:
            print("===== SYNCHRONIZATION =====")
            for exception in self.exceptions:
                print(exception)

        return program
    
    def parse_statement(self) -> Optional[Statement]:
        """
        Parse a statement based on the current token type.
        
        Returns:
            A Statement AST node or None if parsing failed
        """
        # Special case for assignment statements
        if (self.current_token.type == TokenType.IDENT and self.peek_token_is_assignment()):
            return self.parse_assignment_statement()

        # Handle different statement types
        if self.current_token.type == TokenType.VAR:
            return self.parse_var_statement()
        elif self.current_token.type == TokenType.DEF:
            return self.parse_function_statement()
        elif self.current_token.type == TokenType.RETURN:
            return self.parse_return_statement()
        elif self.current_token.type == TokenType.IF:
            return self.parse_if_statement()
        elif self.current_token.type == TokenType.WHILE:
            return self.parse_while_statement()
        elif self.current_token.type == TokenType.BREAK:
            return self.parse_break_statement()
        elif self.current_token.type == TokenType.CONTINUE:
            return self.parse_continue_statement()
        elif self.current_token.type == TokenType.IMPORT:
            return self.parse_import_statement()
        else:
            return self.parse_expression_statement()
    
    def parse_assignment_statement(self) -> Optional[AssignStatement]:
        """
        Parse an assignment statement.
        
        Returns:
            An AssignStatement AST node or None if parsing failed
        """
        stmt = AssignStatement()

        stmt.ident = self.parse_identifier()

        self.advance()  # skips the 'IDENT'
        
        stmt.operator = self.current_token.literal
        self.advance()

        stmt.right_value = self.parse_expression(PrecedenceType.LOWEST)

        if not self.expect_semicolon():
            return None

        return stmt

    def parse_var_statement(self) -> Optional[VarStatement]:
        """
        Parse a variable declaration statement.
        
        Returns:
            A VarStatement AST node or None if parsing failed
        """
        stmt = VarStatement()

        # Parse variable name
        if not self.expect_token(TokenType.IDENT, "Expected identifier after 'var'"):
            return None
        stmt.name = IdentifierLiteral(self.current_token.literal)
        
        # Parse colon
        if not self.expect_token(TokenType.COLON, "Expected colon ':' after identifier"):
            return None
        
        # Parse type
        if not self.expect_token(TokenType.TYPE, "Expected type after ':'"):
            return None
        stmt.value_type = self.current_token.literal

        # Parse optional initialization expression
        if self.peek_token() and self.peek_token().type == TokenType.SEMICOLON:
            self.advance()
            return stmt

        # Parse equals sign
        if not self.expect_token(TokenType.EQ, "Expected '=' or ';' after type"):
            return None
        
        # Parse initialization expression
        self.advance()
        stmt.value = self.parse_expression(PrecedenceType.LOWEST)

        # Parse semicolon
        if not self.expect_semicolon():
            return None

        return stmt

    def parse_if_statement(self) -> Optional[IfStatement]:
        """
        Parse an if statement with optional elif/else branches.
        
        Returns:
            An IfStatement AST node or None if parsing failed
        """
        stmt = IfStatement()

        self.advance()

        stmt.condition = self.parse_expression(PrecedenceType.LOWEST)

        if not self.expect_token(TokenType.COLON, "Expected colon ':' after condition"):
            return None
        
        self.advance()

        # Parse body statements
        while (self.current_token and 
               self.current_token.type not in [TokenType.ELIF, TokenType.ELSE, TokenType.END]):
            try:
                stmt.body.append(self.parse_statement())
                self.advance()
            except Exception as e:
                self.exceptions.append(f"Synchronizing after error: {e}")
        
        # Handle elif branch
        if self.current_token and self.current_token.type == TokenType.ELIF:
            stmt.else_body.append(self.parse_if_statement())
        # Handle else branch
        elif self.current_token and self.current_token.type == TokenType.ELSE:
            if not self.expect_token(TokenType.COLON, "Expected colon ':' after 'else'"):
                return None
            
            self.advance()

            while self.current_token and self.current_token.type != TokenType.END:
                try:
                    stmt.else_body.append(self.parse_statement())
                    self.advance()
                except Exception as e:
                    self.exceptions.append(f"Synchronizing after error: {e}")
        
        # Verify end of if statement
        if not self.expect_token(TokenType.END, "Expected 'end' after if block", look_current=True, do_advance=False):
            return None
            
        return stmt
    
    def parse_while_statement(self) -> Optional[WhileStatement]:
        """
        Parse a while statement.
        
        Returns:
            A WhileStatement AST node or None if parsing failed
        """
        condition: Expression = None
        body: List[Statement] = []

        self.advance()

        condition = self.parse_expression(PrecedenceType.LOWEST)

        if not self.expect_token(TokenType.COLON, "Expected colon ':' after condition"):
            return None
        
        self.advance()

        # Parse body statements
        while self.current_token and self.current_token.type != TokenType.END:
            try:
                body.append(self.parse_statement())
                self.advance()
            except Exception as e:
                self.exceptions.append(f"Synchronizing after error: {e}")
        
        # Verify end of while statement
        if not self.expect_token(TokenType.END, "Expected 'end' after while block", look_current=True, do_advance=False):
            return None
        
        return WhileStatement(condition=condition, body=body)

    def parse_break_statement(self) -> Optional[BreakStatement]:
        """
        Parse a break statement.
        
        Returns:
            A BreakStatement AST node or None if parsing failed
        """
        stmt = BreakStatement()
        
        if not self.expect_semicolon():
            return None

        return stmt

    def parse_continue_statement(self) -> Optional[ContinueStatement]:
        """
        Parse a continue statement.
        
        Returns:
            A ContinueStatement AST node or None if parsing failed
        """
        stmt = ContinueStatement()
        
        if not self.expect_semicolon():
            return None

        return stmt
    
    def parse_import_statement(self) -> Optional[ImportStatement]:
        """
        Parse a import statement.
        
        Returns:
            A ImportStatement AST node or None if parsing failed
        """
        if not self.expect_token(TokenType.STRING, "Expected a file path!"):
            return None
        
        stmt = ImportStatement(file_path=self.current_token.literal)
        
        if not self.expect_semicolon():
            return None

        return stmt


    def parse_function_statement(self) -> Optional[FunctionStatement]:
        """
        Parse a function declaration statement.
        
        Returns:
            A FunctionStatement AST node or None if parsing failed
        """
        func = FunctionStatement()

        # Parse function name
        if not self.expect_token(TokenType.IDENT, "Expected identifier after 'def'", error_at_current=True):
            return None

        func.name = IdentifierLiteral(self.current_token.literal)

        # Parse parameter list start
        if not self.expect_token(TokenType.LPAREN, "Expected left parenthesis '('", error_at_current=True):
            return None
        
        # Parse parameters
        func.parameters = self.parse_function_parameters()

        # Parse return type
        if not self.expect_token(TokenType.ARROW, "Expected an arrow '->'", error_at_current=True):
            return None

        if not self.expect_token(TokenType.TYPE, "Expected type after '->'", error_at_current=True):
            return None
        
        func.return_type = self.current_token.literal
        
        # Parse function body start
        if not self.expect_token(TokenType.COLON, "Expected colon ':' after type", error_at_current=True):
            return None
        
        self.advance()

        # Parse function body statements
        while (self.current_token and 
               self.current_token.type != TokenType.END and 
               self.current_token.type != TokenType.EOF):
            try:
                stmt = self.parse_statement()
                if stmt is not None:
                    func.body.append(stmt)
                self.advance()
            except Exception as e:
                self.exceptions.append(f"Synchronizing after error: {e}")

        # Verify end of function
        if not self.expect_token(TokenType.END, "Expected 'end' keyword after function body", look_current=True, do_advance=False):
            return None

        return func
    
    def parse_function_parameters(self) -> List[FunctionParameter]:
        """
        Parse function parameters.
        
        Returns:
            List of FunctionParameter AST nodes
        """
        params: List[FunctionParameter] = []

        # Handle empty parameter list
        if self.peek_token() and self.peek_token().type == TokenType.RPAREN:
            self.advance()
            return params
        
        # Parse first parameter
        if not self.expect_token(TokenType.IDENT, "Expected an identifier after '('", error_at_current=True):
            return []

        first_param = FunctionParameter(name=self.current_token.literal)

        if not self.expect_token(TokenType.COLON, "Expected colon ':' after identifier", error_at_current=True):
            return []
        
        if not self.expect_token(TokenType.TYPE, "Expected type after ':'", error_at_current=True):
            return []

        first_param.value_type = self.current_token.literal
        params.append(first_param)

        # Parse additional parameters
        while self.peek_token() and self.peek_token().type == TokenType.COMMA:
            self.advance()

            if not self.expect_token(TokenType.IDENT, "Expected identifier after ','", error_at_current=True):
                return []
            
            param = FunctionParameter(name=self.current_token.literal)

            if not self.expect_token(TokenType.COLON, "Expected colon ':' after identifier", error_at_current=True):
                return []
            
            if not self.expect_token(TokenType.TYPE, "Expected type after ':'", error_at_current=True):
                return []

            param.value_type = self.current_token.literal
            params.append(param)

        # Parse end of parameter list
        if not self.expect_token(TokenType.RPAREN, "Expected right parenthesis ')'", error_at_current=True):
            return []
        
        return params

    def parse_return_statement(self) -> Optional[ReturnStatement]:
        """
        Parse a return statement.
        
        Returns:
            A ReturnStatement AST node or None if parsing failed
        """
        stmt = ReturnStatement()

        self.advance()

        stmt.return_value = self.parse_expression(PrecedenceType.LOWEST)

        if not self.expect_semicolon():
            return None
        
        return stmt

    def parse_expression_statement(self) -> ExpressionStatement:
        """
        Parse an expression statement.
        
        Returns:
            An ExpressionStatement AST node
        """
        expr = self.parse_expression(PrecedenceType.LOWEST)
        
        # Parse semicolon
        if not self.expect_semicolon():
            return None

        return ExpressionStatement(expr)
    
    def parse_expression(self, precedence: PrecedenceType) -> Optional[Expression]:
        """
        Parse an expression with the given precedence.
        
        Args:
            precedence: Minimum precedence level to consider
            
        Returns:
            An Expression AST node or None if parsing failed
        """
        prefix_fn = self.prefix_parse_fns.get(self.current_token.type)
        if prefix_fn is None:
            token = self.current_token
            self.report_error(token, f"Expected expression, got {self.current_token.type}")
            return None
        
        left_expr = prefix_fn()

        # Parse infix expressions as long as they have higher precedence
        while (self.peek_token() and
               self.peek_token().type != TokenType.SEMICOLON and 
               precedence.value < self.peek_precedence().value):

            infix_fn = self.infix_parse_fns.get(self.peek_token().type)
            if infix_fn is None:
                return left_expr
            
            self.advance()
            left_expr = infix_fn(left_expr)

        return left_expr

    def parse_infix_expression(self, left_node: Expression) -> InfixExpression:
        """
        Parse an infix expression (e.g., a + b).
        
        Args:
            left_node: Left side of the expression
            
        Returns:
            An InfixExpression AST node
        """
        infix_expr = InfixExpression(left_node=left_node, operator=self.current_token.literal)

        precedence = self.current_precedence()

        # Handle right associativity for exponentiation
        if self.current_token.type == TokenType.POW:
            precedence = PrecedenceType(precedence.value - 1)

        self.advance()
        infix_expr.right_node = self.parse_expression(precedence)

        return infix_expr
    
    def parse_grouped_expression(self) -> Optional[Expression]:
        """
        Parse an expression within parentheses.
        
        Returns:
            An Expression AST node or None if parsing failed
        """
        self.advance()  # Skip the opening parenthesis
        expr = self.parse_expression(PrecedenceType.LOWEST)

        if not self.expect_token(TokenType.RPAREN, "Expected closing parenthesis ')' after expression", error_at_current=True):
            return None

        return expr
    
    def parse_call_expression(self, function: Expression) -> Optional[CallExpression]:
        """
        Parse a function call expression.
        
        Args:
            function: Function expression being called
            
        Returns:
            A CallExpression AST node or None if parsing failed
        """
        expr = CallExpression(function=function)
        expr.args = self.parse_expression_list(TokenType.RPAREN)
        
        return expr

    def parse_expression_list(self, end_token_type: TokenType) -> List[Expression]:
        """
        Parse a list of expressions separated by commas.
        
        Args:
            end_token_type: Token type that ends the expression list
            
        Returns:
            List of Expression AST nodes
        """
        args: List[Expression] = []

        # Handle empty list
        if self.peek_token() and self.peek_token().type == end_token_type:
            self.advance()
            return args

        self.advance()

        # Parse first argument
        args.append(self.parse_expression(PrecedenceType.LOWEST))

        # Parse additional arguments
        while self.peek_token() and self.peek_token().type == TokenType.COMMA:
            self.advance()
            self.advance()
            args.append(self.parse_expression(PrecedenceType.LOWEST))

        # Parse end of argument list
        if not self.expect_token(end_token_type, f"Expected closing token {end_token_type} after expression list", error_at_current=True):
            return []
        
        return args

    def parse_prefix_expression(self) -> PrefixExpression:
        """
        Parse a prefix expression (e.g., -a).

        Returns:
            A PrefixExpression AST node
        """
        prefix_expr: PrefixExpression = PrefixExpression(operator=self.current_token.literal)

        self.advance()
        prefix_expr.right_node = self.parse_expression(PrecedenceType.PREFIX)

        return prefix_expr

    def parse_identifier(self) -> IdentifierLiteral:
        """
        Parse an identifier.
        
        Returns:
            An IdentifierLiteral AST node
        """
        return IdentifierLiteral(self.current_token.literal)

    def parse_int_literal(self) -> IntegerLiteral:
        """
        Parse an integer literal.
        
        Returns:
            An IntegerLiteral AST node
        """
        return IntegerLiteral(self.current_token.literal)

    def parse_float_literal(self) -> FloatLiteral:
        """
        Parse a float literal.
        
        Returns:
            A FloatLiteral AST node
        """
        return FloatLiteral(self.current_token.literal)
    
    def parse_boolean(self) -> BooleanLiteral:
        """
        Parse a boolean literal.
        
        Returns:
            A BooleanLiteral AST node
        """
        return BooleanLiteral(self.current_token.literal == "true")
    
    def parse_string_literal(self) -> StringLiteral:
        """
        Parse a string literal.
        
        Returns:
            A StringLiteral AST node
        """
        return StringLiteral(self.current_token.literal)