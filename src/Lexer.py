from Token import Token, TokenType, lookup_ident
from Position import Position
from Error import ErrorHandler
import string


class Lexer:
    """Lexical analyzer that converts source code into tokens."""

    # Class constants
    WHITESPACE = string.whitespace
    DIGITS = string.digits
    LETTERS = string.ascii_letters
    ALPHANUMERIC = LETTERS + DIGITS

    def __init__(self, source_code: str, file_path="<stdin>", error_handler=None):
        """Initialize the lexer with source code.

        Args:
            source_code: The source code to tokenize
            file_path: Path to the source file (for error reporting)
            error_handler: Optional custom error handler
        """
        self.source_code = source_code
        self.current_char = None
        self.position = Position(idx=-1, ln=1, col=0, fn=file_path, ftxt=source_code)
        self.error_handler = error_handler if error_handler else ErrorHandler()
        self.advance()

    def advance(self):
        """Move to the next character in the source code."""
        self.position.advance(self.current_char)
        self.current_char = (
            self.source_code[self.position.idx]
            if self.position.idx < len(self.source_code)
            else None
        )

    def tokenize(self):
        """Process the source code and return a list of tokens.

        Returns:
            list: The tokens from the source code
        """
        tokens = []

        while self.current_char is not None:
            if self.current_char in self.WHITESPACE:
                self._skip_whitespace()
            elif self.current_char == "#":
                self._skip_comment()
            elif self.current_char in self.LETTERS + "_":
                tokens.append(self._process_identifier())
            elif self.current_char in self.DIGITS + ".":
                if self._is_invalid_decimal_point():
                    self._report_invalid_decimal_point()
                    self.advance()
                    continue
                tokens.append(self._process_number())
            elif self.current_char == "\"":
                tokens.append(self._process_string())
            elif self.current_char == "+":
                tokens.append(self._process_plus_or_add_equals())
            elif self.current_char == "-":
                tokens.append(self._process_minus_or_arrow())
            elif self.current_char == "*":
                tokens.append(self._process_asterisks())
            elif self.current_char == "/":
                tokens.append(self._process_slash_or_div_equals())
            elif self.current_char == "%":
                tokens.append(self._process_modulus_or_mod_equals())
            elif self.current_char == "=":
                tokens.append(self._process_equals())
            elif self.current_char == ":":
                tokens.append(Token(TokenType.COLON, literal=self.current_char, pos_start=self.position))
                self.advance()
            elif self.current_char == "(":
                tokens.append(Token(TokenType.LPAREN, literal=self.current_char, pos_start=self.position))
                self.advance()
            elif self.current_char == ")":
                tokens.append(Token(TokenType.RPAREN, literal=self.current_char, pos_start=self.position))
                self.advance()
            elif self.current_char == ",":
                tokens.append(Token(TokenType.COMMA, literal=self.current_char, pos_start=self.position))
                self.advance()
            elif self.current_char == ";":
                tokens.append(Token(TokenType.SEMICOLON, literal=self.current_char, pos_start=self.position))
                self.advance()
            elif self.current_char == ">":
                tokens.append(self._process_greater_than())
            elif self.current_char == "<":
                tokens.append(self._process_less_than())
            elif self.current_char == "!":
                tokens.append(self._process_not_equals())
            else:
                tokens.append(self._process_illegal_character())

        tokens.append(Token(TokenType.EOF, pos_start=self.position))
        return tokens

    def _is_invalid_decimal_point(self):
        """Check if a decimal point is not followed by a digit."""
        return (
            self.current_char == "."
            and (self.position.idx + 1 >= len(self.source_code)
                 or self.source_code[self.position.idx + 1] not in DIGITS)
        )

    def _report_invalid_decimal_point(self):
        """Report an error for invalid decimal point usage."""
        start_pos = self.position.copy()
        end_pos = self.position.copy()
        end_pos.advance()

        self.error_handler.add_error(
            start_pos,
            end_pos,
            "Lexical Error",
            "Invalid token: decimal point must be followed by a digit"
        )

    def _report_multiple_decimal_points(self, number_str):
        """Report an error for multiple decimal points in a number."""
        start_pos = self.position.copy()
        end_pos = self.position.copy()
        end_pos.advance()

        self.error_handler.add_error(
            start_pos,
            end_pos,
            "Lexical Error",
            f"Invalid number format: multiple decimal points in '{number_str}.'"
        )

    def _report_unterminated_string(self, start_pos):
        """Report an error for an unterminated string literal."""
        end_pos = self.position.copy()
        end_pos.advance()

        self.error_handler.add_error(
            start_pos, 
            end_pos, 
            "Lexical Error", 
            "Unterminated string literal"
        )

    def _process_illegal_character(self):
        """Process an unrecognized character as an illegal token.

        Returns:
            Token: The illegal token
        """
        illegal_char = self.current_char
        start_pos = self.position.copy()
        end_pos = self.position.copy()
        end_pos.advance()

        self.error_handler.add_error(
            start_pos, 
            end_pos, 
            "Lexical Error", 
            f"Unrecognized character: '{illegal_char}'"
        )
        
        token = Token(TokenType.ILLEGAL, literal=illegal_char, pos_start=start_pos, pos_end=self.position)
        self.advance()
        return token

    def _skip_whitespace(self):
        """Skip whitespace characters."""
        while self.current_char and self.current_char in self.WHITESPACE:
            self.advance()

    def _skip_comment(self):
        """Skip a line comment."""
        while self.current_char is not None and self.current_char != "\n":
            self.advance()
        
        self.advance()  # Skip the newline character

    def _process_identifier(self):
        """Process an identifier or keyword token.

        Returns:
            Token: The identifier or keyword token
        """
        identifier = ""
        start_pos = self.position.copy()

        while self.current_char is not None and self.current_char in self.ALPHANUMERIC + "_":
            identifier += self.current_char
            self.advance()

        token_type = lookup_ident(identifier)
        return Token(token_type, identifier, start_pos, self.position)

    def _process_number(self):
        """Process a numeric token (integer or float).

        Returns:
            Token: The number token
        """
        decimal_count = 0
        number_str = ""
        start_pos = self.position.copy()

        while self.current_char is not None and self.current_char in self.DIGITS + ".":
            if self.current_char == ".":
                if decimal_count == 0:
                    decimal_count += 1
                else:
                    self._report_multiple_decimal_points(number_str)
                    break

            number_str += self.current_char
            self.advance()

        if decimal_count == 0:
            return Token(TokenType.INT, int(number_str), start_pos, self.position)
        else:
            return Token(TokenType.FLOAT, float(number_str), start_pos, self.position)

    def _process_string(self):
        """Process a string literal.

        Returns:
            Token: The string token
        """
        string_content = ""
        start_pos = self.position.copy()
        
        self.advance()  # Skip the opening quote

        while self.current_char is not None and self.current_char != "\"":
            string_content += self.current_char
            if self.current_char == "\\":
                self.advance()
                string_content += self.current_char
            self.advance()
        
        if self.current_char is None:
            self._report_unterminated_string(start_pos)
        else:
            self.advance()  # Skip the closing quote
            
        return Token(TokenType.STRING, string_content, start_pos, self.position)

    def _process_plus_or_add_equals(self):
        """Process a plus symbol or addition assignment operator.

        Returns:
            Token: The plus or addition assignment token
        """
        literal = self.current_char
        start_pos = self.position.copy()
        self.advance()

        if self.current_char == "=":
            literal += self.current_char
            self.advance()
            return Token(TokenType.PLUS_EQ, literal, start_pos, self.position)
        
        return Token(TokenType.PLUS, literal, pos_start=start_pos, pos_end=self.position)

    def _process_minus_or_arrow(self):
        """Process a minus symbol or arrow operator.

        Returns:
            Token: The minus or arrow token
        """
        literal = self.current_char
        start_pos = self.position.copy()
        self.advance()

        if self.current_char == '>':
            literal += self.current_char
            self.advance()
            return Token(TokenType.ARROW, literal, start_pos, self.position)
        elif self.current_char == "=":
            literal += self.current_char
            self.advance()
            return Token(TokenType.MINUS_EQ, literal, start_pos, self.position)
        
        return Token(TokenType.MINUS, literal, pos_start=start_pos, pos_end=self.position)

    def _process_asterisks(self):
        """Process a multiplication or power operator.

        Returns:
            Token: The multiplication or power token
        """
        literal = self.current_char
        start_pos = self.position.copy()
        self.advance()

        if self.current_char == "*":
            literal += self.current_char
            self.advance()

            if self.current_char == "=":
                literal += self.current_char
                self.advance()
                return Token(TokenType.POW_EQ, literal, start_pos, self.position)
            
            return Token(TokenType.POW, literal, start_pos, self.position)

        elif self.current_char == "=":
            literal += self.current_char
            self.advance()
            return Token(TokenType.MUL_EQ, literal, start_pos, self.position)
        
        return Token(TokenType.ASTERISK, literal, pos_start=start_pos, pos_end=self.position)

    def _process_slash_or_div_equals(self):
        """Process a division or division assignment operator.

        Returns:
            Token: The division or division assignment token
        """
        literal = self.current_char
        start_pos = self.position.copy()
        self.advance()

        if self.current_char == "=":
            literal += self.current_char
            self.advance()
            return Token(TokenType.DIV_EQ, literal, start_pos, self.position)
        
        return Token(TokenType.SLASH, literal, pos_start=start_pos, pos_end=self.position)

    def _process_modulus_or_mod_equals(self):
        """Process a modulus or modulus assignment operator.

        Returns:
            Token: The modulus or modulus assignment token
        """
        literal = self.current_char
        start_pos = self.position.copy()
        self.advance()

        if self.current_char == "=":
            literal += self.current_char
            self.advance()
            return Token(TokenType.MOD_EQ, literal, start_pos, self.position)
        
        return Token(TokenType.MODULUS, literal, pos_start=start_pos, pos_end=self.position)

    def _process_equals(self):
        """Process an equals or equality operator.

        Returns:
            Token: The equals or equality token
        """
        literal = self.current_char
        start_pos = self.position.copy()
        self.advance()

        if self.current_char == "=":
            literal += self.current_char
            self.advance()
            return Token(TokenType.EQ_EQ, literal, start_pos, self.position)
        
        return Token(TokenType.EQ, literal, pos_start=start_pos, pos_end=self.position)

    def _process_greater_than(self):
        """Process a greater than or greater than or equal operator.

        Returns:
            Token: The greater than or greater than or equal token
        """
        literal = self.current_char
        start_pos = self.position.copy()
        self.advance()

        if self.current_char == "=":
            literal += self.current_char
            self.advance()
            return Token(TokenType.GT_EQ, literal, start_pos, self.position)
        
        return Token(TokenType.GT, literal, pos_start=start_pos, pos_end=self.position)

    def _process_less_than(self):
        """Process a less than or less than or equal operator.

        Returns:
            Token: The less than or less than or equal token
        """
        literal = self.current_char
        start_pos = self.position.copy()
        self.advance()

        if self.current_char == "=":
            literal += self.current_char
            self.advance()
            return Token(TokenType.LT_EQ, literal, start_pos, self.position)
        
        return Token(TokenType.LT, literal, pos_start=start_pos, pos_end=self.position)

    def _process_not_equals(self):
        """Process a not equals operator.

        Returns:
            Token: The not equals token or illegal token if not followed by equals
        """
        literal = self.current_char
        start_pos = self.position.copy()
        self.advance()

        if self.current_char == "=":
            literal += self.current_char
            self.advance()
            return Token(TokenType.NOT_EQ, literal, start_pos, self.position)
        
        self.error_handler.add_error(
            start_pos, 
            self.position, 
            "Lexical error",
            "Invalid token: '!' must be followed by '='"
        )

        return Token(TokenType.ILLEGAL, literal, start_pos, self.position)
