from strings_with_arrows import *

class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def __str__(self):
        result  = f'{self.error_name}: {self.details}\n'
        result += f'File {self.pos_start.fn}, line {self.pos_start.ln}, column {self.pos_start.col}\n'
        result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result


class ErrorHandler:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.has_error = False
    
    def add_error(self, pos_start, pos_end, error_name, details):
        error = Error(pos_start, pos_end, error_name, details)
        self.errors.append(error)
        self.has_error = True
        return error
    
    def add_warning(self, pos_start, pos_end, error_name, details):
        warning = Error(pos_start, pos_end, error_name, details)
        self.warnings.append(warning)
        return warning

    def report(self):
        if self.warnings:
            print("\nWarnings:")
            for warning in self.warnings:
                print(f" {warning}")

        if self.errors:
            print("\nErrors:")
            for error in self.errors:
                print(f" {error}")
            
            return False  # Compilation failed
        return True  # Compilation succeeded
