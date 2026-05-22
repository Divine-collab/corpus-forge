import os
from datetime import datetime


class TextReader:
    """
    A class to read and process text/markdown files.
    Extracts content, metadata, and calculates statistics.
    """
    
    def __init__(self, file_path):
        """
        Initialize the TextReader with a file path.
        
        Args:
            file_path (str): Path to the text/markdown file to read
        """
        self.file_path = file_path
        self.error_message = None
    
    def read_file(self):
        """
        Read the raw content from the file.
        
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
    
    def clean_content(self, text):
        """
        Clean the text by removing markdown formatting and extra whitespace.
        
        Args:
            text (str): The raw text to clean
            
        Returns:
            str: The cleaned text
        """
        import re
        
        if not text:
            return ""
        
        # Remove markdown bold formatting (**)
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        
        # Remove markdown italic formatting (*)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        
        # Remove markdown headers (#, ##, ###, etc.)
        text = re.sub(r'^#+\s', '', text, flags=re.MULTILINE)
        
        # Remove markdown list markers (-, *, +)
        text = re.sub(r'^[\-\*\+]\s', '', text, flags=re.MULTILINE)
        
        # Remove markdown links [text](url)
        text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
        
        # Remove code blocks (``` code ```)
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        
        # Remove inline code (backticks)
        text = re.sub(r'`(.*?)`', r'\1', text)
        
        # Remove extra whitespace and blank lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        cleaned_text = '\n'.join(lines)
        
        return cleaned_text
    
    def extract_metadata(self):
        """
        Extract metadata about the file.
        
        Returns:
            dict: Dictionary containing file metadata
                  Keys: file_name, file_type, file_size, upload_date
        """
        try:
            # Get file name from path
            file_name = os.path.basename(self.file_path)
            
            # Determine file type from extension
            file_extension = os.path.splitext(file_name)[1].lower()
            if file_extension == ".md":
                file_type = "markdown"
            elif file_extension == ".txt":
                file_type = "text"
            else:
                file_type = file_extension.replace(".", "")
            
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
        Count the number of words in the text.
        
        Args:
            text (str): The text to count words in
            
        Returns:
            int: The word count
        """
        if not text or text.strip() == "":
            return 0
        
        # Split text by whitespace and count non-empty words
        words = text.split()
        return len(words)
    
    def process(self):
        """
        Main method that orchestrates the entire text processing pipeline.
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