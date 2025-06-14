from llvmlite import ir
import os
import sys

from AST import Node, NodeType, Program, Expression
from AST import ExpressionStatement, VarStatement, FunctionStatement, ReturnStatement, AssignStatement, IfStatement
from AST import WhileStatement, BreakStatement, ContinueStatement, ImportStatement
from AST import InfixExpression, CallExpression, PrefixExpression
from AST import IntegerLiteral, FloatLiteral, IdentifierLiteral, BooleanLiteral, StringLiteral
from AST import FunctionParameter

from Environment import Environment

from Lexer import Lexer
from Parser import Parser

class Compiler:
    def __init__(self):
        # Type mapping from language types to LLVM IR types
        self.type_map: dict[str, ir.Type] = {
            "int": ir.IntType(64),
            "float": ir.DoubleType(),
            "bool": ir.IntType(1),
            "str": ir.PointerType(ir.IntType(8)),
            "void": ir.VoidType()
        }

        self.module: ir.Module = ir.Module("main")
        self.builder: ir.IRBuilder = ir.IRBuilder()
        self.env: Environment = Environment()
        
        # Counter for unique block and identifier names
        self.counter: int = 0

        self.initialize_builtins()

        self.breakpoints: list[ir.Block] = []
        self.continues: list[ir.Block] = []

        self.global_parsed_pallets: dict[str, Program] = {}
    
    def increment_counter(self) -> int:
        """Generate a unique counter value for naming."""
        self.counter += 1
        return self.counter

    def initialize_builtins(self):
        """Set up built-in functions and constants."""
        def init_print(self) -> ir.Function:
            """Initialize the print function."""
            fnty: ir.FunctionType = ir.FunctionType(
                self.type_map["int"], 
                [ir.IntType(8).as_pointer()], 
                var_arg=True
            )
            return ir.Function(self.module, fnty, name="printf")
        
        def init_alloc(self) -> ir.Function:
            """Initialize the myalloc function."""
            fnty: ir.FunctionType = ir.FunctionType(
                ir.IntType(8).as_pointer(),
                [ir.IntType(64)]
            )
            return ir.Function(self.module, fnty, name="alloc")
        
        def init_memcpy(self) -> ir.Function:
            """Initialize the memcpy function."""
            fnty: ir.FunctionType = ir.FunctionType(
                ir.IntType(8).as_pointer(),
                [ir.IntType(8).as_pointer(), ir.IntType(8).as_pointer(), ir.IntType(64)]
            )
            return ir.Function(self.module, fnty, name="memcpy")
        
        def init_strcat(self) -> ir.Function:
            """Initialize the string concatenation function."""
            char_ptr = ir.IntType(8).as_pointer()

            fnty: ir.FunctionType  = ir.FunctionType(
                char_ptr, 
                [char_ptr, char_ptr]
            )
            return ir.Function(self.module, fnty, name="_strcat")
        
        def init_len(self) -> ir.Function:
            """Initialize the len function."""
            char_ptr = ir.IntType(8).as_pointer()
            int_type = ir.IntType(64)

            fnty: ir.FunctionType  = ir.FunctionType(
                int_type, 
                [char_ptr]
            )
            return ir.Function(self.module, fnty, name="strlen")
        
        def init_pow(self) -> ir.Function:
            """Initialize the power function."""
            fnty: ir.FunctionType = ir.FunctionType(
                self.type_map["float"], 
                [self.type_map["float"], self.type_map["float"]]
            )
            return ir.Function(self.module, fnty, name="pow")

        def init_booleans(self) -> tuple[ir.GlobalVariable, ir.GlobalVariable]:
            """Create global constants for true and false."""
            bool_type: ir.Type = self.type_map["bool"]

            true_var = ir.GlobalVariable(self.module, bool_type, "true")
            true_var.initializer = ir.Constant(bool_type, 1)
            true_var.global_constant = True

            false_var = ir.GlobalVariable(self.module, bool_type, "false")
            false_var.initializer = ir.Constant(bool_type, 0)
            false_var.global_constant = True

            return true_var, false_var
        
        # Register built-in functions and constants
        self.env.define("print", init_print(self), self.type_map["int"])
        self.env.define("_alloc", init_alloc(self), ir.IntType(8).as_pointer())
        self.env.define("_memcpy", init_memcpy(self), ir.IntType(8).as_pointer())
        self.env.define("_strcat", init_strcat(self), self.type_map["str"])
        self.env.define("pow", init_pow(self), self.type_map["float"])
        self.env.define("len", init_len(self), ir.IntType(64))

        true_var, false_var = init_booleans(self)
        self.env.define("true", true_var, true_var.type)
        self.env.define("false", false_var, true_var.type)
    
    def compile(self, node: Node):
        """Compile an AST node into LLVM IR."""
        match node.type():
            case NodeType.Program:
                self.visit_program(node)
            case NodeType.ExpressionStatement:
                self.visit_expression_statement(node)
            case NodeType.VarStatement:
                self.visit_var_statement(node)
            case NodeType.FunctionStatement:
                self.visit_function_statement(node)
            case NodeType.ReturnStatement:
                self.visit_return_statement(node)
            case NodeType.AssignStatement:
                self.visit_assign_statement(node)
            case NodeType.IfStatement:
                self.visit_if_statement(node)
            case NodeType.WhileStatement:
                self.visit_while_statement(node)
            case NodeType.BreakStatement:
                self.visit_break_statement(node)
            case NodeType.ContinueStatement:
                self.visit_continue_statement(node)
            case NodeType.ImportStatement:
                self.visit_import_statement(node)
            case NodeType.InfixExpression:
                self.visit_infix_expression(node)
            case NodeType.CallExpression:
                self.visit_call_expression(node)
            case NodeType.PrefixExpression:
                self.visit_prefix_expression(node)

    def visit_program(self, node: Program):
        """Create the main function and compile program statements."""
        func_name = ".main"
        param_types: list[ir.Type] = []
        return_type: ir.Type = self.type_map["int"]

        fnty = ir.FunctionType(return_type, param_types)
        func = ir.Function(self.module, fnty, name=func_name)

        block = func.append_basic_block(f"{func_name}_entry")
        self.builder = ir.IRBuilder(block)

        for stmt in node.statements:
            self.compile(stmt)
        
        # Default return value for main
        return_value: ir.Constant = ir.Constant(self.type_map["int"], 0)
        self.builder.ret(return_value)
    
    def visit_expression_statement(self, node: ExpressionStatement):
        """Compile an expression statement."""
        self.compile(node.expr)
    
    def visit_if_statement(self, node: IfStatement):
        """Compile an if statement with optional else block."""
        condition = node.condition
        test, _ = self.resolve_value(condition)

        if node.else_body is None:
            with self.builder.if_then(test):
                for stmt in node.body:
                    self.compile(stmt)
        else:
            with self.builder.if_else(test) as (then, otherwise):
                with then:
                    for stmt in node.body:
                        self.compile(stmt)
                with otherwise:
                    for stmt in node.else_body:
                        self.compile(stmt)
    
    def visit_while_statement(self, node: WhileStatement):
        """Compile a while statement."""
        condition: Expression = node.condition
        body: list = node.body

        test, _ = self.resolve_value(condition)

        while_loop_entry = self.builder.append_basic_block(f"while_loop_entry_{self.increment_counter()}") 
        while_loop_otherwise = self.builder.append_basic_block(f"while_loop_otherwise_{self.counter}")

        self.breakpoints.append(while_loop_otherwise)
        self.continues.append(while_loop_entry)

        self.builder.cbranch(test, while_loop_entry, while_loop_otherwise)

        self.builder.position_at_start(while_loop_entry)

        for stmt in body:
            self.compile(stmt)

        test, _ = self.resolve_value(condition)

        self.builder.cbranch(test, while_loop_entry, while_loop_otherwise)
        self.builder.position_at_start(while_loop_otherwise)

        self.breakpoints.pop()
        self.continues.pop()

    def visit_break_statement(self, node: BreakStatement):
        """Compile a break statement."""
        if self.breakpoints:
            self.builder.branch(self.breakpoints[-1])
        else:
            raise RuntimeError("Break statement outside of loop.")
    
    def visit_continue_statement(self, node: ContinueStatement):
        """Compile a continue statement."""
        if self.continues:
            self.builder.branch(self.continues[-1])
        else:
            raise RuntimeError("Continue statement outside of loop.")
    
    def visit_import_statement(self, node: ImportStatement):
        """Compile an import statement."""
        file_path: str = node.file_path

        if self.global_parsed_pallets.get(file_path) is not None:
            print(f"[Warning]: `{file_path}` is already imported globally\n")
            return
        
        with open(os.path.abspath(file_path), "r") as f:
            pallet_code: str = f.read()
        
        l: Lexer = Lexer(source_code=pallet_code)
        tokens = l.tokenize()

        if l.error_handler.has_error:
            print(f"Error with imported pallet: {file_path}")
            l.error_handler.report()
            sys.exit(1)

        p: Parser = Parser(tokens=tokens)

        program: Program = p.parse_program()
        if p.error_handler.has_error:
            print(f"Error with imported pallet: {file_path}")
            p.error_handler.report()
            sys.exit(1)
        
        for stmt in program.statements:
            self.compile(stmt)

        self.global_parsed_pallets[file_path] = program

    def visit_var_statement(self, node: VarStatement):
        """Compile a variable declaration statement."""
        name = node.name.value
        value = node.value
        value_type = node.value_type  # For future type checking

        default_values = {
            'int': IntegerLiteral(0),
            'float': FloatLiteral(0.0),
            'bool': BooleanLiteral(False),
            'str': StringLiteral("")
        }

        if value is None:
            if value_type not in default_values:
                raise TypeError(f"Unsupported type for variable '{name}': {value_type}")
            value = default_values[value_type]

        value, type_info = self.resolve_value(node=value)

        if self.env.lookup(name) is None:
            # Define and allocate a new variable
            ptr = self.builder.alloca(type_info)
            self.builder.store(value, ptr)
            self.env.define(name, ptr, type_info)
        else:
            # Update an existing variable
            ptr, _ = self.env.lookup(name)
            self.builder.store(value, ptr)

    def visit_function_statement(self, node: FunctionStatement):
        """Compile a function declaration."""
        name: str = node.name.value
        params: list[FunctionParameter] = node.parameters

        # Extract parameter names and types
        param_names: list[str] = [p.name for p in params]
        param_types: list[ir.Type] = [self.type_map[p.value_type] for p in params]
        return_type: ir.Type = self.type_map[node.return_type]

        # Create the function
        fnty: ir.FunctionType = ir.FunctionType(return_type, param_types)
        func: ir.Function = ir.Function(self.module, fnty, name=name)
        block: ir.Block = func.append_basic_block(f'{name}_entry')

        # Save current builder and environment
        previous_builder = self.builder
        previous_env = self.env

        # Set up new builder for this function
        self.builder = ir.IRBuilder(block)
        
        # Create a new environment for function scope
        self.env = Environment(parent=previous_env)
        
        # Allocate and store function parameters
        params_ptr = []
        for i, typ in enumerate(param_types):
            ptr = self.builder.alloca(typ)
            self.builder.store(func.args[i], ptr)
            params_ptr.append(ptr)

        # Define parameters in the function environment
        for i, param_name in enumerate(param_names):
            typ = param_types[i]
            ptr = params_ptr[i]
            self.env.define(param_name, ptr, typ)

        # Make the function visible inside itself for recursion
        self.env.define(name, func, return_type)

        # Compile function body
        for stmt in node.body:
            self.compile(stmt)

        # Restore previous environment and builder
        self.env = previous_env
        self.env.define(name, func, return_type)
        self.builder = previous_builder

    def visit_return_statement(self, node: ReturnStatement):
        """Compile a return statement."""
        value: Expression = node.return_value
        value, _ = self.resolve_value(value)
        self.builder.ret(value)
    
    def visit_assign_statement(self, node: AssignStatement):
        """Compile an assignment statement."""
        name: str = node.ident.value
        operator: str = node.operator
        value: Expression = node.right_value

        if self.env.lookup(name) is None:
            raise NameError(f"Variable '{name}' not defined.")

        right_value, right_type = self.resolve_value(value)

        var_ptr, _ = self.env.lookup(name)
        orig_value = self.builder.load(var_ptr)

        if isinstance(orig_value.type, ir.IntType) and isinstance(right_type, ir.DoubleType):
            # Convert int to float
            orig_value = self.builder.sitofp(orig_value, self.type_map["float"])
        
        if isinstance(orig_value.type, ir.DoubleType) and isinstance(right_type, ir.IntType):
            # Convert int to float
            right_value = self.builder.sitofp(right_value, self.type_map["float"])
        
        value = None
        Type = None
        match operator:
            case '=':
                value = right_value
            case '+=':
                if isinstance(orig_value.type, ir.IntType) and isinstance(right_type, ir.IntType):
                    value = self.builder.add(orig_value, right_value)
                elif isinstance(orig_value.type, ir.PointerType) and isinstance(right_type, ir.PointerType):
                    value, _ = self.handle_string_concatenation(orig_value, right_value)
                else:
                    value = self.builder.fadd(orig_value, right_value)
            case '-=':
                if isinstance(orig_value.type, ir.IntType) and isinstance(right_type, ir.IntType):
                    value = self.builder.sub(orig_value, right_value)
                else:
                    value = self.builder.fsub(orig_value, right_value)
            case '*=':
                if isinstance(orig_value.type, ir.IntType) and isinstance(right_type, ir.IntType):
                    value = self.builder.mul(orig_value, right_value)
                else:
                    value = self.builder.fmul(orig_value, right_value)
            case '/=':
                if isinstance(orig_value.type, ir.IntType) and isinstance(right_type, ir.IntType):
                    value = self.builder.sdiv(orig_value, right_value)
                else:
                    value = self.builder.fdiv(orig_value, right_value)
            case '%=':
                if isinstance(orig_value.type, ir.IntType) and isinstance(right_type, ir.IntType):
                    value = self.builder.srem(orig_value, right_value)
                else:
                    value = self.builder.frem(orig_value, right_value)
            case '**=':
                if isinstance(orig_value.type, ir.IntType) and isinstance(right_type, ir.IntType):
                    value = self.builtin_pow(orig_value, right_value)
                else:
                    value = self.builtin_pow(orig_value, right_value)
            case _:
                raise NotImplementedError(f"Unsupported assignment operator: {operator}")
        
        ptr, _ = self.env.lookup(name)
        self.builder.store(value, ptr)

    def visit_call_expression(self, node: CallExpression) -> tuple[ir.Instruction, ir.Type]:
        """Compile a function call expression."""
        name: str = node.function.value
        params: list[Expression] = node.args

        # Evaluate all arguments
        args = []
        types = []
        if len(params) > 0:
            for x in params:
                p_val, p_type = self.resolve_value(x)
                args.append(p_val)
                types.append(p_type)

        # Handle built-in or user-defined functions
        match name:
            case 'print':
                ret = self.builtin_print(params=args, return_type=types[0])
                ret_type = self.type_map['int']
            case 'pow':
                ret = self.builtin_pow(args[0], args[1])
                ret_type = self.type_map['float']
            case 'len':
                ret = self.builtin_len(args[0])
                ret_type = self.type_map['int']
            case _:
                func, ret_type = self.env.lookup(name)
                ret = self.builder.call(func, args)
        
        return ret, ret_type
    
    def visit_prefix_expression(self, node: PrefixExpression) ->tuple[ir.Value, ir.Type]:
        """Compile a prefix expression (op a)."""
        operator: str = node.operator
        right_node: Expression = node.right_node

        right_value, right_type = self.resolve_value(right_node)

        Type = None
        value = None
        if isinstance(right_type, ir.DoubleType):
            Type = self.type_map["float"]
            match operator:
                case '-':
                    value = self.builder.fmul(right_value, ir.Constant(Type, -1.0))
                case 'not':
                    value = self.builder.fcmp_ordered("==", right_value, ir.Constant(ir.DoubleType(), 0.0))
        
        elif isinstance(right_type, ir.IntType):
            Type = self.type_map["int"]
            match operator:
                case '-':
                    value = self.builder.mul(right_value, ir.Constant(Type, -1))
                case 'not':
                    value = self.builder.icmp_signed("==", right_value, ir.Constant(ir.IntType(64), 0))
        
        return value, Type

    def visit_infix_expression(self, node: InfixExpression):
        """Compile an infix expression (a op b)."""
        operator: str = node.operator
        left_value, left_type = self.resolve_value(node.left_node)
        right_value, right_type = self.resolve_value(node.right_node)
    
        value = None
        result_type = None

        # Both operands are integers
        if isinstance(left_type, ir.IntType) and isinstance(right_type, ir.IntType):
            result_type = self.type_map["int"]
            value = self.handle_int_operations(operator, left_value, right_value)
            if operator in ["<", ">", "<=", ">=", "==", "!="]:
                result_type = self.type_map["bool"]  # Boolean result
        
        # Both operands are floats
        elif isinstance(left_type, ir.DoubleType) and isinstance(right_type, ir.DoubleType):
            result_type = self.type_map["float"]
            value = self.handle_float_operations(operator, left_value, right_value)
            if operator in ["<", ">", "<=", ">=", "==", "!="]:
                result_type = self.type_map["bool"]  # Boolean result
        
        # Mixed int/float - convert int to float
        elif isinstance(left_type, ir.IntType) and isinstance(right_type, ir.DoubleType):
            left_value = self.builder.sitofp(left_value, self.type_map["float"])
            result_type = self.type_map["float"]
            value = self.handle_float_operations(operator, left_value, right_value)
            if operator in ["<", ">", "<=", ">=", "==", "!="]:
                result_type = self.type_map["bool"]  # Boolean result
                
        elif isinstance(left_type, ir.DoubleType) and isinstance(right_type, ir.IntType):
            right_value = self.builder.sitofp(right_value, self.type_map["float"])
            result_type = self.type_map["float"]
            value = self.handle_float_operations(operator, left_value, right_value)
            if operator in ["<", ">", "<=", ">=", "==", "!="]:
                result_type = self.type_map["bool"]  # Boolean result
        
        # String concatenation
        elif (isinstance(left_type, ir.PointerType) and 
              isinstance(right_type, ir.PointerType) and 
              operator == '+'):
            value, result_type = self.handle_string_concatenation(left_value, right_value)

        return value, result_type
    
    def handle_int_operations(self, operator, left_value, right_value):
        """Handle operations between two integer operands."""
        match operator:
            case '+':
                return self.builder.add(left_value, right_value)
            case '-':
                return self.builder.sub(left_value, right_value)
            case '*':
                return self.builder.mul(left_value, right_value)
            case '/':
                return self.builder.sdiv(left_value, right_value)
            case '%':
                return self.builder.srem(left_value, right_value)
            case '**':
                result = self.builtin_pow(left_value, right_value)
                # return self.builder.fptosi(result, self.type_map["int"])
                return result
            case "<" | "<=" | ">" | ">=" | "==" | "!=":
                return self.builder.icmp_signed(operator, left_value, right_value)
    
    def handle_float_operations(self, operator, left_value, right_value):
        """Handle operations between two floating point operands."""
        match operator:
            case '+':
                return self.builder.fadd(left_value, right_value)
            case '-':
                return self.builder.fsub(left_value, right_value)
            case '*':
                return self.builder.fmul(left_value, right_value)
            case '/':
                return self.builder.fdiv(left_value, right_value)
            case '%':
                return self.builder.frem(left_value, right_value)
            case '**':
                return self.builtin_pow(left_value, right_value)
            case "<" | "<=" | ">" | ">=" | "==" | "!=":
                return self.builder.fcmp_ordered(operator, left_value, right_value)
    
    def handle_string_concatenation(self, left_value, right_value):
        """Handle string concatenation operation."""
        # Get the function and call it
        void_ptr = ir.IntType(8).as_pointer()

        fn, ret_type = self.env.lookup("_strcat")

        str1_char_ptr = self.builder.bitcast(left_value, void_ptr)
        str2_char_ptr = self.builder.bitcast(right_value, void_ptr)

        result = self.builder.call(fn, [str1_char_ptr, str2_char_ptr])

        return result, ret_type

    def resolve_value(self, node: Expression, value_type: str = None) -> tuple[ir.Value, ir.Type]:
        """Resolve an expression to its LLVM IR value and type."""
        match node.type():
            case NodeType.IntegerLiteral:
                node: IntegerLiteral = node
                typ = self.type_map["int" if value_type is None else value_type]
                return ir.Constant(typ, node.value), typ
                
            case NodeType.FloatLiteral:
                node: FloatLiteral = node
                typ = self.type_map["float" if value_type is None else value_type]
                return ir.Constant(typ, node.value), typ
                
            case NodeType.IdentifierLiteral:
                node: IdentifierLiteral = node
                ptr, typ = self.env.lookup(node.value)
                return self.builder.load(ptr), typ
                
            case NodeType.BooleanLiteral:
                node: BooleanLiteral = node
                bool_type = self.type_map["bool"]
                return ir.Constant(bool_type, 1 if node.value else 0), bool_type
                
            case NodeType.StringLiteral:
                node: StringLiteral = node
                string, typ = self.convert_string(node.value)
                return string, typ
            
            case NodeType.InfixExpression:
                return self.visit_infix_expression(node)
                
            case NodeType.CallExpression:
                return self.visit_call_expression(node)
            
            case NodeType.PrefixExpression:
                return self.visit_prefix_expression(node)

    def convert_string(self, string: str) -> tuple[ir.Constant, ir.Type]:
        """Convert a string literal to an LLVM IR global string variable."""
        # string = string.replace('\\n', '\n\0')
        # More escape sequences can be added here
        string = string.replace('\\n', '\n')
        string = string.replace('\\t', '\t')
        string = string.replace('\\r', '\r')
        string = string.replace('\\\\', '\\')
        string = string.replace('\\"', '"')
        string = string.replace("\\'", "'")
        string = string.replace('\\0', '\0')
        string = string.replace('\\b', '\b')  # Backspace
        string = string.replace('\\f', '\f')  # Form feed
        string = string.replace('\\v', '\v')  # Vertical tab
        
        # Add null terminator without duplicating it if we replaced \0 above
        if not string.endswith('\0'):
            fmt: str = f"{string}\0"
        else:
            fmt: str = string
        
        # Get the byte array of the string
        byte_array = bytearray(fmt.encode("utf8"))
        str_len = len(byte_array)
        
        alloc_fn, _ = self.env.lookup("_alloc")
        
        # Allocate memory for the string
        size = ir.Constant(ir.IntType(64), str_len)
        ptr = self.builder.call(alloc_fn, [size])
        
        # Create an array constant for the string
        c_fmt = ir.Constant(ir.ArrayType(ir.IntType(8), str_len), byte_array)
        
        # Create a temporary alloca for the string constant
        temp = self.builder.alloca(c_fmt.type)
        self.builder.store(c_fmt, temp)
        
        # Cast to i8* for memcpy
        temp_cast = self.builder.bitcast(temp, ir.IntType(8).as_pointer())
        ptr_cast = self.builder.bitcast(ptr, ir.IntType(8).as_pointer())
        
        memcpy_fn, _ = self.env.lookup("_memcpy")

        # Copy the string data to the heap
        self.builder.call(memcpy_fn, [ptr_cast, temp_cast, size])
        
        return ptr, ir.PointerType(ir.IntType(8))

    def builtin_print(self, params: list[ir.Instruction], return_type: ir.Type) -> None:
        """Handle built-in print function."""
        func, _ = self.env.lookup('print')
        c_str = self.builder.alloca(return_type)
        self.builder.store(params[0], c_str)
        rest_params = params[1:]

        if isinstance(params[0], ir.LoadInstr):
            # Printing from a variable (e.g., var a: str = "hello"; print(a))
            c_fmt: ir.LoadInstr = params[0]
            g_var_ptr = c_fmt.operands[0]
            string_val = self.builder.load(g_var_ptr)
            fmt_arg = self.builder.bitcast(string_val, ir.IntType(8).as_pointer())
            return self.builder.call(func, [fmt_arg, *rest_params])
        else:
            # Printing from a string literal (e.g., print("hello %i", 23))
            fmt_arg = self.builder.bitcast(
                # self.module.get_global(f"__str_{self.counter}"), 
                params[0],  # Use the first parameter as the format string
                ir.IntType(8).as_pointer()
            )
            return self.builder.call(func, [fmt_arg, *rest_params])
    
    def builtin_pow(self, left_value: ir.Value, right_value: ir.Value) -> ir.Instruction:
        """Handle built-in power function."""
        func, ret_type = self.env.lookup("pow")

        if isinstance(left_value.type, ir.IntType):
            left_value = self.builder.sitofp(left_value, self.type_map["float"])
        if isinstance(right_value.type, ir.IntType):
            right_value = self.builder.sitofp(right_value, self.type_map["float"])

        return self.builder.call(func, [left_value, right_value])
    
    def builtin_len(self, string: ir.Value) -> ir.Instruction:
        """Handle built-in len function."""
        func, ret_type = self.env.lookup("len")
        return self.builder.call(func, [string])