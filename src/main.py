#!/usr/bin/env python3

import os
import sys
import json
import time
from ctypes import CFUNCTYPE, c_int, CDLL

from llvmlite import ir
import llvmlite.binding as llvm

from Lexer import Lexer
from Parser import Parser
from Compiler import Compiler

from Sanitizer import sanitize


def main():
    """Main entry point for the compiler."""
    # Configuration settings
    CONFIG = {
        "lexer_debug": False,
        "parser_debug": False,
        "compiler_debug": False,
        "run_code": True,
        "lib_path": "./src/libs.so"
    }
    
    # Validate command-line arguments
    if len(sys.argv) != 2:
        print("Usage: python /path/to/main.py <source_file>")
        sys.exit(1)

    filename = sys.argv[1]
    
    # Read source code
    try:
        with open(filename, 'r') as f:
            src = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading source file: {e}")
        sys.exit(1)

    # Run compilation pipeline
    try:
        tokens = run_lexical_analysis(src, filename, CONFIG["lexer_debug"])
        ast = run_parsing(tokens, CONFIG["parser_debug"])
        module = run_compilation(ast, CONFIG["compiler_debug"])
        
        if CONFIG["run_code"]:
            run_execution(module, CONFIG["lib_path"])
    except CompilationError:
        # Error details already reported by the respective stage
        pass


def run_lexical_analysis(src, filename, debug=False):
    """Run lexical analysis on the source code.
    
    Args:
        src: Source code string
        filename: Source file path for error reporting
        debug: Whether to print debug information
        
    Returns:
        List of tokens if successful
        
    Raises:
        CompilationError: If lexical analysis fails
    """
    lexer = Lexer(src, file_path=filename)
    tokens = lexer.tokenize()

    tokens = sanitize(tokens=tokens)

    if debug:
        print("===== SOURCE CODE =====")
        print(src, "\n")

        print("===== LEXER TOKENS =====")
        for token in tokens:
            print(token)
        print()

    if not lexer.error_handler.report():
        raise CompilationError("Lexical analysis failed")
        
    return tokens


def run_parsing(tokens, debug=False):
    """Parse tokens into an abstract syntax tree.
    
    Args:
        tokens: List of tokens from lexical analysis
        debug: Whether to print debug information
        
    Returns:
        AST if successful
        
    Raises:
        CompilationError: If parsing fails
    """
    parser = Parser(tokens)
    ast = parser.parse_program()

    if not parser.error_handler.report():
        raise CompilationError("Parsing failed")

    if debug:
        ensure_debug_dir_exists()
        with open("debug/ast.json", "w") as f:
            json.dump(ast.json(), f, indent=4)
            print("Successfully wrote AST to debug/ast.json")
            
    return ast


def run_compilation(ast, debug=False):
    """Compile AST to LLVM IR.
    
    Args:
        ast: Abstract syntax tree
        debug: Whether to print debug information
        
    Returns:
        LLVM module if successful
    """
    compiler = Compiler()
    compiler.compile(node=ast)

    module = compiler.module
    module.triple = llvm.get_default_triple()

    if debug:
        ensure_debug_dir_exists()
        with open("debug/ir.ll", "w") as f:
            f.write(str(module))
            print("Successfully wrote IR to debug/ir.ll")
            
    return module


def run_execution(module, lib_path):
    """Execute the compiled LLVM module.
    
    Args:
        module: LLVM module
        lib_path: Path to external library
    """
    # Initialize LLVM
    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()

    # Load external library
    try:
        external_lib = CDLL(lib_path)
    except OSError as e:
        print(f"Error loading external library: {e}")
        sys.exit(1)

    # Parse and verify the IR module
    try:
        llvm_ir_parsed = llvm.parse_assembly(str(module))
        llvm_ir_parsed.verify()
    except Exception as e:
        print(f"LLVM IR verification error: {e}")
        sys.exit(1)

    # Set up execution engine
    target = llvm.Target.from_default_triple()
    target_machine = target.create_target_machine(opt=3)
    engine = llvm.create_mcjit_compiler(llvm_ir_parsed, target_machine)

    # Map external functions
    alloc_func_addr = external_lib.alloc
    engine.add_global_mapping(llvm_ir_parsed.get_function("alloc"), alloc_func_addr)

    _strcat_func_addr = external_lib._strcat
    engine.add_global_mapping(llvm_ir_parsed.get_function("_strcat"), _strcat_func_addr)

    engine.finalize_object()

    # Get and run the main function
    try:
        entry = engine.get_function_address('.main')
        cfunc = CFUNCTYPE(c_int)(entry)
        
        start_time = time.time()
        result = cfunc()
        end_time = time.time()
        
        execution_time_ms = round((end_time - start_time) * 1000, 6)
        print(f'\n\nProgram returned: {result}\n=== Executed in {execution_time_ms} ms. ===')
    except Exception as e:
        print(f"Execution error: {e}")
        sys.exit(1)


def ensure_debug_dir_exists():
    """Ensure the debug directory exists."""
    if not os.path.exists("debug"):
        os.makedirs("debug")


class CompilationError(Exception):
    """Exception raised for compilation errors."""
    pass


if __name__ == "__main__":
    main()