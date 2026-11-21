# -*- coding: utf-8 -*-
"""
Script.py - Motor de LeviScript
Lexer + Parser + Interpreter para lenguaje JS-like de instaladores
"""

import json
import struct
import pickle
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Union
from pathlib import Path


# ============================================================
# TOKEN TYPES
# ============================================================
class TokenType(Enum):
    # Literals
    STRING = auto()
    NUMBER = auto()
    BOOL = auto()
    NULL = auto()
    
    # Identifiers
    IDENTIFIER = auto()
    
    # Keywords
    SETUP = auto()
    META = auto()
    REQUIRES = auto()
    IMPORT = auto()
    FROM = auto()
    LET = auto()
    CONST = auto()
    FUNCTION = auto()
    IF = auto()
    ELSE = auto()
    FOR = auto()
    WHILE = auto()
    RETURN = auto()
    TRUE = auto()
    FALSE = auto()
    NULL_KW = auto()
    
    # Page types
    WELCOME = auto()
    LICENSE = auto()
    OPTIONS = auto()
    INSTALL = auto()
    FINISH = auto()
    PAGES = auto()
    
    # Hooks
    BEFORE_DISPLAY = auto()
    AFTER_DISPLAY = auto()
    BEFORE_INSTALL = auto()
    ON_INSTALL = auto()
    AFTER_INSTALL = auto()
    ON_ERROR = auto()
    ON_CANCEL = auto()
    
    # Operators
    ASSIGN = auto()          # =
    PLUS = auto()            # +
    MINUS = auto()           # -
    MULT = auto()            # *
    DIV = auto()             # /
    MOD = auto()             # %
    EQ = auto()              # ==
    NEQ = auto()             # !=
    LT = auto()              # <
    GT = auto()              # >
    LTE = auto()             # <=
    GTE = auto()             # >=
    AND = auto()             # &&
    OR = auto()              # ||
    NOT = auto()             # !
    
    # Delimiters
    LBRACE = auto()          # {
    RBRACE = auto()          # }
    LBRACKET = auto()        # [
    RBRACKET = auto()        # ]
    LPAREN = auto()          # (
    RPAREN = auto()          # )
    COLON = auto()           # :
    SEMICOLON = auto()       # ;
    COMMA = auto()           # ,
    DOT = auto()             # .
    ARROW = auto()           # =>
    DOLLAR = auto()          # $
    AT = auto()              # @
    
    # Special
    NEWLINE = auto()
    EOF = auto()
    COMMENT = auto()
    TEMPLATE_START = auto()  # ${
    TEMPLATE_END = auto()    # }


# ============================================================
# KEYWORDS MAPPING
# ============================================================
KEYWORDS = {
    'setup': TokenType.SETUP,
    'meta': TokenType.META,
    'requires': TokenType.REQUIRES,
    'import': TokenType.IMPORT,
    'from': TokenType.FROM,
    'let': TokenType.LET,
    'const': TokenType.CONST,
    'function': TokenType.FUNCTION,
    'if': TokenType.IF,
    'else': TokenType.ELSE,
    'for': TokenType.FOR,
    'while': TokenType.WHILE,
    'return': TokenType.RETURN,
    'true': TokenType.TRUE,
    'false': TokenType.FALSE,
    'null': TokenType.NULL_KW,
    'Welcome': TokenType.WELCOME,
    'License': TokenType.LICENSE,
    'Options': TokenType.OPTIONS,
    'Install': TokenType.INSTALL,
    'Finish': TokenType.FINISH,
    'pages': TokenType.PAGES,
    'beforeDisplay': TokenType.BEFORE_DISPLAY,
    'afterDisplay': TokenType.AFTER_DISPLAY,
    'beforeInstall': TokenType.BEFORE_INSTALL,
    'onInstall': TokenType.ON_INSTALL,
    'afterInstall': TokenType.AFTER_INSTALL,
    'onError': TokenType.ON_ERROR,
    'onCancel': TokenType.ON_CANCEL,
}


# ============================================================
# TOKEN CLASS
# ============================================================
@dataclass
class Token:
    type: TokenType
    value: Any
    line: int
    column: int
    
    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, L{self.line}:C{self.column})"


# ============================================================
# LEXER
# ============================================================
class LeviLexer:
    """Tokenizador de LeviScript"""
    
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        
    def error(self, msg: str):
        raise SyntaxError(f"[{self.line}:{self.column}] {msg}")
    
    def peek(self, offset: int = 0) -> str:
        pos = self.pos + offset
        if pos >= len(self.source):
            return '\0'
        return self.source[pos]
    
    def advance(self) -> str:
        char = self.peek()
        self.pos += 1
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char
    
    def skip_whitespace(self):
        while self.peek() in ' \t\r':
            self.advance()
    
    def skip_comment(self):
        if self.peek() == '/' and self.peek(1) == '/':
            while self.peek() != '\n' and self.peek() != '\0':
                self.advance()
        elif self.peek() == '/' and self.peek(1) == '*':
            self.advance()  # /
            self.advance()  # *
            while not (self.peek() == '*' and self.peek(1) == '/'):
                if self.peek() == '\0':
                    self.error("Comentario multilinea no cerrado")
                self.advance()
            self.advance()  # *
            self.advance()  # /
    
    def read_string(self, quote: str) -> str:
        self.advance()  # opening quote
        result = ""
        while self.peek() != quote:
            if self.peek() == '\0':
                self.error("String no cerrado")
            if self.peek() == '\\':
                self.advance()
                escape = self.advance()
                result += {'n': '\n', 't': '\t', 'r': '\r', '"': '"', "'": "'", '\\': '\\'}.get(escape, escape)
            else:
                result += self.advance()
        self.advance()  # closing quote
        return result
    
    def read_number(self) -> Union[int, float]:
        start = self.pos
        has_dot = False
        while self.peek().isdigit() or (self.peek() == '.' and not has_dot):
            if self.peek() == '.':
                has_dot = True
            self.advance()
        num_str = self.source[start:self.pos]
        return float(num_str) if has_dot else int(num_str)
    
    def read_identifier(self) -> str:
        start = self.pos
        while self.peek().isalnum() or self.peek() in '_$':
            self.advance()
        return self.source[start:self.pos]
    
    def tokenize(self) -> List[Token]:
        while self.peek() != '\0':
            start_col = self.column
            
            # Whitespace
            if self.peek() in ' \t\r':
                self.skip_whitespace()
                continue
            
            # Newlines
            if self.peek() == '\n':
                self.advance()
                self.tokens.append(Token(TokenType.NEWLINE, '\n', self.line - 1, start_col))
                continue
            
            # Comments
            if self.peek() == '/' and self.peek(1) in '/*':
                self.skip_comment()
                continue
            
            # Strings
            if self.peek() in '"\'':
                quote = self.advance()
                value = self.read_string(quote)
                self.tokens.append(Token(TokenType.STRING, value, self.line, start_col))
                continue
            
            # Numbers
            if self.peek().isdigit():
                value = self.read_number()
                self.tokens.append(Token(TokenType.NUMBER, value, self.line, start_col))
                continue
            
            # Template literals ${...}
            if self.peek() == '$' and self.peek(1) == '{':
                self.advance()  # $
                self.advance()  # {
                self.tokens.append(Token(TokenType.TEMPLATE_START, '${', self.line, start_col))
                continue
            
            # Identifiers and keywords
            if self.peek().isalpha() or self.peek() == '_':
                name = self.read_identifier()
                token_type = KEYWORDS.get(name, TokenType.IDENTIFIER)
                self.tokens.append(Token(token_type, name, self.line, start_col))
                continue
            
            # Multi-char operators
            two_char = self.peek() + self.peek(1)
            if two_char == '=>':
                self.advance(); self.advance()
                self.tokens.append(Token(TokenType.ARROW, '=>', self.line, start_col))
                continue
            if two_char == '==':
                self.advance(); self.advance()
                self.tokens.append(Token(TokenType.EQ, '==', self.line, start_col))
                continue
            if two_char == '!=':
                self.advance(); self.advance()
                self.tokens.append(Token(TokenType.NEQ, '!=', self.line, start_col))
                continue
            if two_char == '<=':
                self.advance(); self.advance()
                self.tokens.append(Token(TokenType.LTE, '<=', self.line, start_col))
                continue
            if two_char == '>=':
                self.advance(); self.advance()
                self.tokens.append(Token(TokenType.GTE, '>=', self.line, start_col))
                continue
            if two_char == '&&':
                self.advance(); self.advance()
                self.tokens.append(Token(TokenType.AND, '&&', self.line, start_col))
                continue
            if two_char == '||':
                self.advance(); self.advance()
                self.tokens.append(Token(TokenType.OR, '||', self.line, start_col))
                continue
            
            # Single-char operators and delimiters
            single_char_ops = {
                '+': TokenType.PLUS,
                '-': TokenType.MINUS,
                '*': TokenType.MULT,
                '/': TokenType.DIV,
                '%': TokenType.MOD,
                '=': TokenType.ASSIGN,
                '<': TokenType.LT,
                '>': TokenType.GT,
                '!': TokenType.NOT,
                '{': TokenType.LBRACE,
                '}': TokenType.RBRACE,
                '[': TokenType.LBRACKET,
                ']': TokenType.RBRACKET,
                '(': TokenType.LPAREN,
                ')': TokenType.RPAREN,
                ':': TokenType.COLON,
                ';': TokenType.SEMICOLON,
                ',': TokenType.COMMA,
                '.': TokenType.DOT,
                '$': TokenType.DOLLAR,
                '@': TokenType.AT,
            }
            
            if self.peek() in single_char_ops:
                char = self.advance()
                self.tokens.append(Token(single_char_ops[char], char, self.line, start_col))
                continue
            
            # Unknown character
            self.error(f"Carácter inesperado: '{self.peek()}'")
        
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens


# ============================================================
# AST NODES
# ============================================================
@dataclass
class ASTNode:
    pass

@dataclass
class Program(ASTNode):
    body: List[ASTNode]

@dataclass
class SetupDecl(ASTNode):
    name: str
    body: List[ASTNode]

@dataclass
class MetaBlock(ASTNode):
    fields: Dict[str, Any]

@dataclass
class RequiresBlock(ASTNode):
    deps: List[str]

@dataclass
class ImportStmt(ASTNode):
    items: List[str]
    source: str

@dataclass
class VarDecl(ASTNode):
    kind: str  # 'let' or 'const'
    name: str
    value: ASTNode

@dataclass
class FunctionDecl(ASTNode):
    name: str
    params: List[str]
    body: List[ASTNode]

@dataclass
class HookDecl(ASTNode):
    hook_type: str
    body: List[ASTNode]

@dataclass
class PageDecl(ASTNode):
    page_type: str
    config: Dict[str, Any]

@dataclass
class PagesBlock(ASTNode):
    pages: List[PageDecl]

@dataclass
class BinaryOp(ASTNode):
    left: ASTNode
    op: str
    right: ASTNode

@dataclass
class UnaryOp(ASTNode):
    op: str
    operand: ASTNode

@dataclass
class Literal(ASTNode):
    value: Any
    literal_type: str

@dataclass
class Identifier(ASTNode):
    name: str

@dataclass
class MemberAccess(ASTNode):
    obj: ASTNode
    member: str

@dataclass
class ArrayLiteral(ASTNode):
    elements: List[ASTNode]

@dataclass
class ObjectLiteral(ASTNode):
    pairs: Dict[str, ASTNode]

@dataclass
class CallExpr(ASTNode):
    func: ASTNode
    args: List[ASTNode]

@dataclass
class IfStmt(ASTNode):
    condition: ASTNode
    then_body: List[ASTNode]
    else_body: Optional[List[ASTNode]]

@dataclass
class ForStmt(ASTNode):
    var: str
    iterable: ASTNode
    body: List[ASTNode]

@dataclass
class WhileStmt(ASTNode):
    condition: ASTNode
    body: List[ASTNode]

@dataclass
class ReturnStmt(ASTNode):
    value: Optional[ASTNode]

@dataclass
class TemplateExpr(ASTNode):
    parts: List[Union[str, ASTNode]]


# ============================================================
# PARSER
# ============================================================
class LeviParser:
    """Parser de LeviScript a AST"""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        
    def error(self, msg: str):
        token = self.current()
        raise SyntaxError(f"[{token.line}:{token.column}] {msg}")
    
    def current(self) -> Token:
        if self.pos >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.pos]
    
    def peek(self, offset: int = 0) -> Token:
        pos = self.pos + offset
        if pos >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[pos]
    
    def advance(self) -> Token:
        token = self.current()
        self.pos += 1
        return token
    
    def expect(self, token_type: TokenType, msg: str = None) -> Token:
        if self.current().type != token_type:
            self.error(msg or f"Se esperaba {token_type.name}, se encontró {self.current().type.name}")
        return self.advance()
    
    def match(self, *types: TokenType) -> bool:
        return self.current().type in types
    
    def skip_newlines(self):
        while self.match(TokenType.NEWLINE):
            self.advance()
    
    def parse(self) -> Program:
        body = []
        self.skip_newlines()
        while not self.match(TokenType.EOF):
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
            self.skip_newlines()
        return Program(body)
    
    def parse_statement(self) -> Optional[ASTNode]:
        self.skip_newlines()
        
        if self.match(TokenType.SETUP):
            return self.parse_setup()
        if self.match(TokenType.META):
            return self.parse_meta()
        if self.match(TokenType.REQUIRES):
            return self.parse_requires()
        if self.match(TokenType.IMPORT):
            return self.parse_import()
        if self.match(TokenType.LET, TokenType.CONST):
            return self.parse_var_decl()
        if self.match(TokenType.FUNCTION):
            return self.parse_function()
        if self.match(TokenType.PAGES):
            return self.parse_pages()
        if self.match(TokenType.BEFORE_DISPLAY, TokenType.AFTER_DISPLAY, 
                       TokenType.BEFORE_INSTALL, TokenType.ON_INSTALL,
                       TokenType.AFTER_INSTALL, TokenType.ON_ERROR, TokenType.ON_CANCEL):
            return self.parse_hook()
        if self.match(TokenType.IF):
            return self.parse_if()
        if self.match(TokenType.FOR):
            return self.parse_for()
        if self.match(TokenType.WHILE):
            return self.parse_while()
        if self.match(TokenType.RETURN):
            return self.parse_return()
        
        return self.parse_expression_statement()
    
    def parse_setup(self) -> SetupDecl:
        self.advance()  # setup
        name = self.expect(TokenType.IDENTIFIER, "Se esperaba nombre del setup").value
        self.expect(TokenType.LBRACE)
        self.skip_newlines()
        
        body = []
        while not self.match(TokenType.RBRACE):
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
            self.skip_newlines()
        
        self.expect(TokenType.RBRACE)
        return SetupDecl(name, body)
    
    def parse_meta(self) -> MetaBlock:
        self.advance()  # meta
        self.expect(TokenType.LBRACE)
        self.skip_newlines()
        
        fields = {}
        while not self.match(TokenType.RBRACE):
            key = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.COLON)
            value = self.parse_expression()
            fields[key] = value
            
            if self.match(TokenType.COMMA):
                self.advance()
            self.skip_newlines()
        
        self.expect(TokenType.RBRACE)
        return MetaBlock(fields)
    
    def parse_requires(self) -> RequiresBlock:
        self.advance()  # requires
        deps = []
        
        if self.match(TokenType.LBRACKET):
            self.advance()
            self.skip_newlines()
            while not self.match(TokenType.RBRACKET):
                dep = self.expect(TokenType.STRING).value
                deps.append(dep)
                if self.match(TokenType.COMMA):
                    self.advance()
                self.skip_newlines()
            self.expect(TokenType.RBRACKET)
        else:
            dep = self.expect(TokenType.STRING).value
            deps.append(dep)
        
        return RequiresBlock(deps)
    
    def parse_import(self) -> ImportStmt:
        self.advance()  # import
        self.expect(TokenType.LBRACE)
        items = []
        while not self.match(TokenType.RBRACE):
            item = self.expect(TokenType.IDENTIFIER).value
            items.append(item)
            if self.match(TokenType.COMMA):
                self.advance()
        self.expect(TokenType.RBRACE)
        self.expect(TokenType.FROM)
        source = self.expect(TokenType.STRING).value
        return ImportStmt(items, source)
    
    def parse_var_decl(self) -> VarDecl:
        kind = 'let' if self.match(TokenType.LET) else 'const'
        self.advance()
        name = self.expect(TokenType.IDENTIFIER).value
        value = None
        if self.match(TokenType.ASSIGN):
            self.advance()
            value = self.parse_expression()
        return VarDecl(kind, name, value)
    
    def parse_function(self) -> FunctionDecl:
        self.advance()  # function
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.LPAREN)
        params = []
        while not self.match(TokenType.RPAREN):
            param = self.expect(TokenType.IDENTIFIER).value
            params.append(param)
            if self.match(TokenType.COMMA):
                self.advance()
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.LBRACE)
        body = self.parse_block()
        self.expect(TokenType.RBRACE)
        return FunctionDecl(name, params, body)
    
    def parse_pages(self) -> PagesBlock:
        self.advance()  # pages
        self.expect(TokenType.LBRACKET)
        pages = []
        self.skip_newlines()
        
        while not self.match(TokenType.RBRACKET):
            page = self.parse_page()
            if page:
                pages.append(page)
            if self.match(TokenType.COMMA):
                self.advance()
            self.skip_newlines()
        
        self.expect(TokenType.RBRACKET)
        return PagesBlock(pages)
    
    def parse_page(self) -> PageDecl:
        page_types = {
            TokenType.WELCOME: 'Welcome',
            TokenType.LICENSE: 'License',
            TokenType.OPTIONS: 'Options',
            TokenType.INSTALL: 'Install',
            TokenType.FINISH: 'Finish',
        }
        
        if self.current().type not in page_types:
            self.error(f"Tipo de página no válido: {self.current().type.name}")
        
        page_type = page_types[self.current().type]
        self.advance()
        self.expect(TokenType.LBRACE)
        
        config = {}
        self.skip_newlines()
        while not self.match(TokenType.RBRACE):
            key = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.COLON)
            value = self.parse_expression()
            config[key] = value
            
            if self.match(TokenType.COMMA):
                self.advance()
            self.skip_newlines()
        
        self.expect(TokenType.RBRACE)
        return PageDecl(page_type, config)
    
    def parse_hook(self) -> HookDecl:
        hook_types = {
            TokenType.BEFORE_DISPLAY: 'beforeDisplay',
            TokenType.AFTER_DISPLAY: 'afterDisplay',
            TokenType.BEFORE_INSTALL: 'beforeInstall',
            TokenType.ON_INSTALL: 'onInstall',
            TokenType.AFTER_INSTALL: 'afterInstall',
            TokenType.ON_ERROR: 'onError',
            TokenType.ON_CANCEL: 'onCancel',
        }
        
        hook_type = hook_types[self.current().type]
        self.advance()
        self.expect(TokenType.LBRACE)
        body = self.parse_block()
        self.expect(TokenType.RBRACE)
        return HookDecl(hook_type, body)
    
    def parse_block(self) -> List[ASTNode]:
        body = []
        self.skip_newlines()
        while not self.match(TokenType.RBRACE, TokenType.EOF):
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
            self.skip_newlines()
        return body
    
    def parse_if(self) -> IfStmt:
        self.advance()  # if
        self.expect(TokenType.LPAREN)
        condition = self.parse_expression()
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.LBRACE)
        then_body = self.parse_block()
        self.expect(TokenType.RBRACE)
        
        else_body = None
        if self.match(TokenType.ELSE):
            self.advance()
            if self.match(TokenType.IF):
                else_body = [self.parse_if()]
            else:
                self.expect(TokenType.LBRACE)
                else_body = self.parse_block()
                self.expect(TokenType.RBRACE)
        
        return IfStmt(condition, then_body, else_body)
    
    def parse_for(self) -> ForStmt:
        self.advance()  # for
        self.expect(TokenType.LPAREN)
        var = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.IDENTIFIER)  # in
        iterable = self.parse_expression()
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.LBRACE)
        body = self.parse_block()
        self.expect(TokenType.RBRACE)
        return ForStmt(var, iterable, body)
    
    def parse_while(self) -> WhileStmt:
        self.advance()  # while
        self.expect(TokenType.LPAREN)
        condition = self.parse_expression()
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.LBRACE)
        body = self.parse_block()
        self.expect(TokenType.RBRACE)
        return WhileStmt(condition, body)
    
    def parse_return(self) -> ReturnStmt:
        self.advance()  # return
        value = None
        if not self.match(TokenType.SEMICOLON, TokenType.NEWLINE, TokenType.RBRACE):
            value = self.parse_expression()
        return ReturnStmt(value)
    
    def parse_expression_statement(self) -> ASTNode:
        expr = self.parse_expression()
        if self.match(TokenType.SEMICOLON):
            self.advance()
        return expr
    
    def parse_expression(self) -> ASTNode:
        return self.parse_assignment()
    
    def parse_assignment(self) -> ASTNode:
        left = self.parse_or()
        if self.match(TokenType.ASSIGN):
            self.advance()
            right = self.parse_assignment()
            # For simplicity, we don't support complex assignments in AST
            # Just return the right side for now
            return right
        return left
    
    def parse_or(self) -> ASTNode:
        left = self.parse_and()
        while self.match(TokenType.OR):
            op = self.advance().value
            right = self.parse_and()
            left = BinaryOp(left, op, right)
        return left
    
    def parse_and(self) -> ASTNode:
        left = self.parse_equality()
        while self.match(TokenType.AND):
            op = self.advance().value
            right = self.parse_equality()
            left = BinaryOp(left, op, right)
        return left
    
    def parse_equality(self) -> ASTNode:
        left = self.parse_comparison()
        while self.match(TokenType.EQ, TokenType.NEQ):
            op = self.advance().value
            right = self.parse_comparison()
            left = BinaryOp(left, op, right)
        return left
    
    def parse_comparison(self) -> ASTNode:
        left = self.parse_additive()
        while self.match(TokenType.LT, TokenType.GT, TokenType.LTE, TokenType.GTE):
            op = self.advance().value
            right = self.parse_additive()
            left = BinaryOp(left, op, right)
        return left
    
    def parse_additive(self) -> ASTNode:
        left = self.parse_multiplicative()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op = self.advance().value
            right = self.parse_multiplicative()
            left = BinaryOp(left, op, right)
        return left
    
    def parse_multiplicative(self) -> ASTNode:
        left = self.parse_unary()
        while self.match(TokenType.MULT, TokenType.DIV, TokenType.MOD):
            op = self.advance().value
            right = self.parse_unary()
            left = BinaryOp(left, op, right)
        return left
    
    def parse_unary(self) -> ASTNode:
        if self.match(TokenType.NOT, TokenType.MINUS):
            op = self.advance().value
            operand = self.parse_unary()
            return UnaryOp(op, operand)
        return self.parse_call()
    
    def parse_call(self) -> ASTNode:
        expr = self.parse_primary()
        while self.match(TokenType.LPAREN, TokenType.DOT):
            if self.match(TokenType.LPAREN):
                self.advance()
                args = []
                while not self.match(TokenType.RPAREN):
                    args.append(self.parse_expression())
                    if self.match(TokenType.COMMA):
                        self.advance()
                self.expect(TokenType.RPAREN)
                expr = CallExpr(expr, args)
            elif self.match(TokenType.DOT):
                self.advance()
                member = self.expect(TokenType.IDENTIFIER).value
                expr = MemberAccess(expr, member)
        return expr
    
    def parse_primary(self) -> ASTNode:
        if self.match(TokenType.TRUE):
            self.advance()
            return Literal(True, 'bool')
        if self.match(TokenType.FALSE):
            self.advance()
            return Literal(False, 'bool')
        if self.match(TokenType.NULL_KW):
            self.advance()
            return Literal(None, 'null')
        if self.match(TokenType.NUMBER):
            return Literal(self.advance().value, 'number')
        if self.match(TokenType.STRING):
            return Literal(self.advance().value, 'string')
        if self.match(TokenType.IDENTIFIER):
            return Identifier(self.advance().value)
        if self.match(TokenType.LPAREN):
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr
        if self.match(TokenType.LBRACKET):
            return self.parse_array()
        if self.match(TokenType.LBRACE):
            return self.parse_object()
        if self.match(TokenType.TEMPLATE_START):
            return self.parse_template()
        
        self.error(f"Expresión inesperada: {self.current().type.name}")
    
    def parse_array(self) -> ArrayLiteral:
        self.expect(TokenType.LBRACKET)
        elements = []
        self.skip_newlines()
        while not self.match(TokenType.RBRACKET):
            elements.append(self.parse_expression())
            if self.match(TokenType.COMMA):
                self.advance()
            self.skip_newlines()
        self.expect(TokenType.RBRACKET)
        return ArrayLiteral(elements)
    
    def parse_object(self) -> ObjectLiteral:
        self.expect(TokenType.LBRACE)
        pairs = {}
        self.skip_newlines()
        while not self.match(TokenType.RBRACE):
            if self.match(TokenType.IDENTIFIER):
                key = self.advance().value
            elif self.match(TokenType.STRING):
                key = self.advance().value
            else:
                self.error("Se esperaba identificador o string como clave de objeto")
            
            self.expect(TokenType.COLON)
            value = self.parse_expression()
            pairs[key] = value
            
            if self.match(TokenType.COMMA):
                self.advance()
            self.skip_newlines()
        self.expect(TokenType.RBRACE)
        return ObjectLiteral(pairs)
    
    def parse_template(self) -> TemplateExpr:
        self.expect(TokenType.TEMPLATE_START)
        parts = []
        
        while not self.match(TokenType.RBRACE):
            if self.match(TokenType.STRING):
                parts.append(self.advance().value)
            elif self.match(TokenType.IDENTIFIER):
                parts.append(Identifier(self.advance().value))
            elif self.match(TokenType.DOT):
                self.advance()
                # Member access in template
            else:
                break
        
        self.expect(TokenType.RBRACE)
        return TemplateExpr(parts)


# ============================================================
# AST SERIALIZER (for .lsx files)
# ============================================================
class ASTSerializer:
    """Serializa AST a formato binario .lsx"""
    
    MAGIC = b'LSX\x01'  # Version 1.0
    
    @staticmethod
    def serialize(ast: Program) -> bytes:
        """Convierte AST a bytes para archivo .lsx"""
        # Use pickle for now, can be replaced with custom binary format
        data = pickle.dumps(ast, protocol=pickle.HIGHEST_PROTOCOL)
        
        # Add header with magic and length
        header = ASTSerializer.MAGIC + struct.pack('<I', len(data))
        return header + data
    
    @staticmethod
    def deserialize(data: bytes) -> Program:
        """Convierte bytes de .lsx a AST"""
        if not data.startswith(ASTSerializer.MAGIC):
            raise ValueError("Archivo .lsx inválido o corrupto")
        
        # Skip magic (4 bytes) and read length (4 bytes)
        length = struct.unpack('<I', data[4:8])[0]
        payload = data[8:8+length]
        
        return pickle.loads(payload)


# ============================================================
# PYTHON CODE GENERATOR
# ============================================================
class PythonGenerator:
    """Genera código Python a partir del AST"""
    
    def __init__(self):
        self.indent = 0
        self.output = []
        self.imports = set()
        
    def generate(self, ast: Program) -> str:
        """Genera código Python completo"""
        # Add standard imports
        self.imports.add('import sys')
        self.imports.add('from pathlib import Path')
        self.imports.add('from PyQt6.QtWidgets import *')
        self.imports.add('from PyQt6.QtCore import *')
        self.imports.add('from PyQt6.QtGui import *')
        self.imports.add('from leviathan_ui import *')
        
        # Generate body
        for node in ast.body:
            self.visit(node)
        
        # Combine imports and body
        result = '\n'.join(sorted(self.imports)) + '\n\n'
        result += '\n'.join(self.output)
        return result
    
    def emit(self, code: str):
        self.output.append('    ' * self.indent + code)
    
    def visit(self, node: ASTNode):
        method = f'visit_{type(node).__name__}'
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node: ASTNode):
        raise NotImplementedError(f"No hay visitor para {type(node).__name__}")
    
    def visit_Program(self, node: Program):
        for stmt in node.body:
            self.visit(stmt)
    
    def visit_SetupDecl(self, node: SetupDecl):
        self.emit(f'class {node.name}Installer:')
        self.indent += 1
        self.emit('def __init__(self):')
        self.indent += 1
        self.emit('self.app = QApplication(sys.argv)')
        self.emit('self.window = None')
        self.indent -= 1
        
        for stmt in node.body:
            self.visit(stmt)
        
        self.indent -= 1
    
    def visit_MetaBlock(self, node: MetaBlock):
        self.emit('# Meta configuration')
        for key, value in node.fields.items():
            py_value = self.expr_to_python(value)
            self.emit(f'self.meta_{key} = {py_value}')
    
    def visit_RequiresBlock(self, node: RequiresBlock):
        self.emit('# Dependencies')
        deps = [f'"{dep}"' for dep in node.deps]
        self.emit(f'self.requires = [{', '.join(deps)}]')
    
    def visit_PagesBlock(self, node: PagesBlock):
        self.emit('self.pages = []')
        for page in node.pages:
            self.visit(page)
    
    def visit_PageDecl(self, node: PageDecl):
        config = ', '.join([f'{k}={self.expr_to_python(v)}' for k, v in node.config.items()])
        self.emit(f'self.pages.append({node.page_type}({config}))')
    
    def visit_HookDecl(self, node: HookDecl):
        self.emit(f'def {node.hook_type}(self):')
        self.indent += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent -= 1
    
    def visit_VarDecl(self, node: VarDecl):
        value = self.expr_to_python(node.value)
        self.emit(f'self.{node.name} = {value}')
    
    def visit_FunctionDecl(self, node: FunctionDecl):
        params = ', '.join(node.params)
        self.emit(f'def {node.name}(self, {params}):')
        self.indent += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent -= 1
    
    def visit_CallExpr(self, node: CallExpr):
        func_name = self.expr_to_python(node.func)
        args = ', '.join([self.expr_to_python(arg) for arg in node.args])
        self.emit(f'{func_name}({args})')
    
    def visit_Identifier(self, node: Identifier):
        return node.name
    
    def visit_Literal(self, node: Literal):
        if node.literal_type == 'string':
            return repr(node.value)
        elif node.literal_type == 'bool':
            return 'True' if node.value else 'False'
        elif node.literal_type == 'null':
            return 'None'
        return str(node.value)
    
    def expr_to_python(self, expr: ASTNode) -> str:
        if isinstance(expr, Literal):
            if expr.literal_type == 'string':
                return repr(expr.value)
            elif expr.literal_type == 'bool':
                return 'True' if expr.value else 'False'
            elif expr.literal_type == 'null':
                return 'None'
            return str(expr.value)
        elif isinstance(expr, Identifier):
            return expr.name
        elif isinstance(expr, ArrayLiteral):
            elements = [self.expr_to_python(e) for e in expr.elements]
            return f'[{', '.join(elements)}]'
        elif isinstance(expr, ObjectLiteral):
            pairs = [f'{repr(k)}: {self.expr_to_python(v)}' for k, v in expr.pairs.items()]
            return f'{{{', '.join(pairs)}}}'
        elif isinstance(expr, BinaryOp):
            left = self.expr_to_python(expr.left)
            right = self.expr_to_python(expr.right)
            op_map = {'&&': 'and', '||': 'or', '!': 'not'}
            py_op = op_map.get(expr.op, expr.op)
            return f'({left} {py_op} {right})'
        return str(expr)


# ============================================================
# MAIN API
# ============================================================
class LeviScript:
    """API principal para compilar LeviScript"""
    
    @staticmethod
    def compile(source: str) -> Program:
        """Compila código fuente a AST"""
        lexer = LeviLexer(source)
        tokens = lexer.tokenize()
        parser = LeviParser(tokens)
        return parser.parse()
    
    @staticmethod
    def to_python(ast: Program) -> str:
        """Convierte AST a código Python"""
        generator = PythonGenerator()
        return generator.generate(ast)
    
    @staticmethod
    def save_lsx(ast: Program, path: str):
        """Guarda AST como archivo .lsx binario"""
        data = ASTSerializer.serialize(ast)
        Path(path).write_bytes(data)
    
    @staticmethod
    def load_lsx(path: str) -> Program:
        """Carga AST desde archivo .lsx"""
        data = Path(path).read_bytes()
        return ASTSerializer.deserialize(data)


# ============================================================
# CLI ENTRY POINT
# ============================================================
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='LeviScript Compiler v1.0.5')
    subparsers = parser.add_subparsers(dest='command')
    
    # Parse command
    parse_parser = subparsers.add_parser('parse', help='Parse .ls file and show AST')
    parse_parser.add_argument('file', help='Source .ls file')
    
    # Precompile command
    precompile_parser = subparsers.add_parser('precompile', help='Compile .ls to .lsx')
    precompile_parser.add_argument('file', help='Source .ls file')
    precompile_parser.add_argument('-o', '--output', help='Output .lsx file')
    
    # Generate Python command
    gen_parser = subparsers.add_parser('generate', help='Generate Python from .ls')
    gen_parser.add_argument('file', help='Source .ls or .lsx file')
    gen_parser.add_argument('-o', '--output', help='Output .py file')
    
    args = parser.parse_args()
    
    if args.command == 'parse':
        source = Path(args.file).read_text(encoding='utf-8')
        ast = LeviScript.compile(source)
        print(json.dumps(ast, indent=2, default=lambda o: o.__dict__))
    
    elif args.command == 'precompile':
        source = Path(args.file).read_text(encoding='utf-8')
        ast = LeviScript.compile(source)
        output = args.output or args.file.replace('.ls', '.lsx')
        LeviScript.save_lsx(ast, output)
        print(f'✓ Precompiled: {args.file} → {output}')
    
    elif args.command == 'generate':
        if args.file.endswith('.lsx'):
            ast = LeviScript.load_lsx(args.file)
        else:
            source = Path(args.file).read_text(encoding='utf-8')
            ast = LeviScript.compile(source)
        
        python_code = LeviScript.to_python(ast)
        output = args.output or args.file.replace('.ls', '.py')
        Path(output).write_text(python_code, encoding='utf-8')
        print(f'✓ Generated: {output}')
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
