from Token import Token, TokenType

# Automatic semicolon insertion
def sanitize(tokens: list[Token]) -> list[Token]:

    insert_positions = []
    semicolon_tokens = []
    new_tokens = []

    prev = None

    for i in range(len(tokens)):
        cur = tokens[i]

        if prev is not None and cur.type != TokenType.EOF and prev.pos_end.ln != cur.pos_start.ln:
            if prev.type in {
                TokenType.RPAREN, TokenType.IDENT, 
                TokenType.STRING, TokenType.INT, TokenType.FLOAT,
                TokenType.FALSE, TokenType.TRUE
            }:
                if cur.type in {
                    TokenType.LPAREN, TokenType.IDENT,
                    TokenType.STRING, TokenType.INT, TokenType.FLOAT,
                    TokenType.FALSE, TokenType.TRUE,
                    TokenType.DEF, TokenType.RETURN,
                    TokenType.IF, TokenType.ELIF, TokenType.ELSE, TokenType.END,
                    TokenType.VAR, TokenType.WHILE,
                    TokenType.BREAK, TokenType.CONTINUE
                }:
                    insert_positions.append(prev.pos_end.idx)

            elif prev.type in {TokenType.BREAK, TokenType.CONTINUE}:
                insert_positions.append(prev.pos_end.idx)
            
            elif prev.type == TokenType.RETURN:
                if cur.type in {
                    TokenType.BREAK, TokenType.CONTINUE, TokenType.DEF,
                    TokenType.ELIF, TokenType.ELSE, TokenType.END,
                    TokenType.IF, TokenType.RETURN,
                    TokenType.VAR, TokenType.WHILE
                }:
                    insert_positions.append(prev.pos_end.idx)
        elif cur.type == TokenType.EOF:
            # Final token check
            if prev and prev.type in {
                TokenType.RPAREN, TokenType.IDENT,
                TokenType.STRING, TokenType.INT, TokenType.FLOAT,
                TokenType.BREAK, TokenType.CONTINUE, TokenType.FALSE,
                TokenType.RETURN, TokenType.TRUE,
            }:
                insert_positions.append(prev.pos_end.idx)

        prev = cur
        
    # Reconstruct token list with semicolons inserted
    insert_positions = set(insert_positions)
    for token in tokens:
        new_tokens.append(token)
        if token.pos_end.idx in insert_positions:
            # Create a semicolon token just after the previous token
            pos_start = token.pos_end.copy()
            pos_end = token.pos_end.copy()
            pos_end.advance()

            semicolon_token = Token(
                TokenType.SEMICOLON,
                literal=";",
                pos_start=pos_start,
                pos_end=pos_end
            )
            new_tokens.append(semicolon_token)

    return new_tokens