import os
import re
from datetime import datetime


class CodeReader:
    """
    A class to read and process code files (Python and JavaScript).
    Extracts comments, function/variable names, and calculates statistics.
    """
    
    def __init__(self, file_path):
        """
        Initialize the CodeReader with a file path.
        
        Args:
            file_path (str): Path to the Python (.py) or JavaScript (.js) file to read
        """
        self.file_path = file_path
        self.error_message = None
        
        # Determine language from file extension
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension == ".py":
            self.language = "python"
        elif file_extension == ".js":
            self.language = "javascript"
        else:
            self.language = "unknown"
    
    def read_file(self):
        """
        Read the raw content from the code file.
        
        Returns:
            str: The raw file content, or None if error occurs
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if file is empty
            if not content or content.strip() == "":
                self.error_message = "File is empty"
                return None
            
            return content
        
        except FileNotFoundError:
            self.error_message = "File does not exist"
            return None
        except PermissionError:
            self.error_message = "Permission denied: Cannot read file"
            return None
        except Exception as e:
            self.error_message = f"Error reading file: {str(e)}"
            return None
    
    def remove_strings(self, text):
        """
        Remove string literals from code to avoid noise in extraction.
        Handles both Python and JavaScript string formats.
        
        Args:
            text (str): The raw code to process
            
        Returns:
            str: Code with strings removed
        """
        if not text:
            return ""
        
        # Remove double-quoted strings
        text = re.sub(r'"[^"]*"', '""', text)
        
        # Remove single-quoted strings
        text = re.sub(r"'[^']*'", "''", text)
        
        # For Python: Remove triple-quoted strings (both """ and ''')
        text = re.sub(r'"""[^"]*"""', '""""""', text, flags=re.DOTALL)
        text = re.sub(r"'''[^']*'''", "''''''", text, flags=re.DOTALL)
        
        # For JavaScript: Remove template literals (backticks)
        text = re.sub(r'`[^`]*`', '``', text, flags=re.DOTALL)
        
        return text
    
    def extract_comments(self, text):
        """
        Extract all comments from the code.
        
        Args:
            text (str): The raw code to extract from
            
        Returns:
            str: All comments concatenated together
        """
        comments = []
        
        if self.language == "python":
            # Extract single-line comments (#)
            python_comments = re.findall(r'#(.+?)$', text, flags=re.MULTILINE)
            comments.extend(python_comments)
            
            # Extract docstrings (""" """ and ''' ''')
            docstrings_triple_double = re.findall(r'"""(.*?)"""', text, flags=re.DOTALL)
            docstrings_triple_single = re.findall(r"'''(.*?)'''", text, flags=re.DOTALL)
            comments.extend(docstrings_triple_double)
            comments.extend(docstrings_triple_single)
        
        elif self.language == "javascript":
            # Extract single-line comments (//)
            js_comments = re.findall(r'//(.+?)$', text, flags=re.MULTILINE)
            comments.extend(js_comments)
            
            # Extract multi-line comments (/* */)
            block_comments = re.findall(r'/\*(.*?)\*/', text, flags=re.DOTALL)
            comments.extend(block_comments)
        
        # Join all comments with spaces and clean whitespace
        return ' '.join(comments).strip()
    
    def extract_function_names(self, text):
        """
        Extract all function and method names from the code.
        
        Args:
            text (str): The raw code to extract from
            
        Returns:
            str: All function names separated by spaces
        """
        function_names = []
        
        if self.language == "python":
            # Find all function definitions: def function_name(
            python_functions = re.findall(r'def\s+(\w+)\s*\(', text)
            function_names.extend(python_functions)
        
        elif self.language == "javascript":
            # Find function declarations: function name()
            js_functions = re.findall(r'function\s+(\w+)\s*\(', text)
            function_names.extend(js_functions)
            
            # Find arrow functions and assignments: const name = () =>
            arrow_functions = re.findall(r'(?:const|let|var)\s+(\w+)\s*=\s*(?:\([^)]*\)|[^=]*)\s*=>?', text)
            function_names.extend(arrow_functions)
            
            # Find method definitions: method_name()
            method_names = re.findall(r'(\w+)\s*\([^)]*\)\s*{', text)
            function_names.extend(method_names)
        
        # Return function names joined with spaces
        return ' '.join(function_names)
    
    def extract_variable_names(self, text):
        """
        Extract meaningful variable names from the code.
        Skip generic single-letter variables like 'i', 'x', 'temp'.
        
        Args:
            text (str): The raw code to extract from
            
        Returns:
            str: All meaningful variable names separated by spaces
        """
        variable_names = []
        generic_names = {'i', 'j', 'k', 'x', 'y', 'z', 'temp', 'tmp', 't', 'a', 'b', 'c'}
        
        if self.language == "python":
            # Find variable assignments: var_name = value
            python_vars = re.findall(r'(\w+)\s*=(?!=)', text)
            for var in python_vars:
                if var.lower() not in generic_names and len(var) > 1:
                    variable_names.append(var)
        
        elif self.language == "javascript":
            # Find const declarations: const var_name = 
            const_vars = re.findall(r'const\s+(\w+)\s*=', text)
            variable_names.extend([v for v in const_vars if v.lower() not in generic_names])
            
            # Find let declarations: let var_name = 
            let_vars = re.findall(r'let\s+(\w+)\s*=', text)
            variable_names.extend([v for v in let_vars if v.lower() not in generic_names])
            
            # Find var declarations: var var_name = 
            var_vars = re.findall(r'var\s+(\w+)\s*=', text)
            variable_names.extend([v for v in var_vars if v.lower() not in generic_names])
        
        # Return variable names joined with spaces
        return ' '.join(variable_names)
    
    def clean_content(self, text):
        """
        Clean code by extracting meaningful content:
        combines comments + function names + variable names.
        Removes code syntax and string literals.
        
        Args:
            text (str): The raw code to clean
            
        Returns:
            str: The cleaned, meaningful content
        """
        # Remove string literals first
        text_no_strings = self.remove_strings(text)
        
        # Extract meaningful content
        comments = self.extract_comments(text_no_strings)
        functions = self.extract_function_names(text_no_strings)
        variables = self.extract_variable_names(text_no_strings)
        
        # Combine all extracted content
        combined = f"{comments} {functions} {variables}"
        
        # Remove code syntax characters: { } ( ) [ ] ; , . :
        cleaned = re.sub(r'[{}()\[\];,.:=<>!&|^~?]', ' ', combined)
        
        # Remove extra whitespace and normalize spacing
        cleaned = ' '.join(cleaned.split())
        
        return cleaned
    
    def extract_metadata(self):
        """
        Extract metadata about the code file.
        
        Returns:
            dict: Dictionary containing file metadata
                  Keys: file_name, file_type, file_size, upload_date
        """
        try:
            # Get file name from path
            file_name = os.path.basename(self.file_path)
            
            # Determine file type from extension
            file_type = self.language  # "python" or "javascript"
            
            # Get file size in bytes
            file_size = os.path.getsize(self.file_path)
            
            # Get current date/time as upload date
            upload_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            return {
                "file_name": file_name,
                "file_type": file_type,
                "file_size": file_size,
                "upload_date": upload_date
            }
        
        except Exception as e:
            self.error_message = f"Error extracting metadata: {str(e)}"
            return None
    
    def count_words(self, text):
        """
        Count the number of words in the cleaned content.
        
        Args:
            text (str): The text to count words in
            
        Returns:
            int: The word count
        """
        if not text or text.strip() == "":
            return 0
        
        # Split text into words (by whitespace)
        words = text.split()
        return len(words)
    
    def process(self):
        """
        Main method that orchestrates the entire code processing pipeline.
        Reads, cleans, extracts metadata, counts words, and returns everything.
        
        Returns:
            dict: A complete dictionary with all extracted information:
                  {
                      "file_name": str,
                      "file_type": str,
                      "file_size": int,
                      "upload_date": str,
                      "raw_text": str,
                      "cleaned_text": str,
                      "word_count": int,
                      "error": str (if error occurred, None otherwise)
                  }
        """
        # Step 1: Read the file
        raw_text = self.read_file()
        
        # Step 2: Check if there was an error reading the file
        if raw_text is None:
            return {
                "file_name": None,
                "file_type": None,
                "file_size": None,
                "upload_date": None,
                "raw_text": None,
                "cleaned_text": None,
                "word_count": None,
                "error": self.error_message
            }
        
        # Step 3: Clean the content
        cleaned_text = self.clean_content(raw_text)
        
        # Step 4: Extract metadata
        metadata = self.extract_metadata()
        if metadata is None:
            return {
                "file_name": None,
                "file_type": None,
                "file_size": None,
                "upload_date": None,
                "raw_text": None,
                "cleaned_text": None,
                "word_count": None,
                "error": self.error_message
            }
        
        # Step 5: Count words in cleaned text
        word_count = self.count_words(cleaned_text)
        
        # Step 6: Combine all information into a single dictionary
        result = {
            "file_name": metadata["file_name"],
            "file_type": metadata["file_type"],
            "file_size": metadata["file_size"],
            "upload_date": metadata["upload_date"],
            "raw_text": raw_text,
            "cleaned_text": cleaned_text,
            "word_count": word_count,
            "error": None
        }
        
        return result
