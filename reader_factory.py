"""
ReaderFactory: Factory pattern for instantiating the correct file reader.

This module provides a centralized way to create Reader instances based on file type.
It eliminates scattered routing logic and makes adding new file formats simple.
"""

import os
from Code_reader import CodeReader
from Pdf_reader import PdfReader
from Text_reader import TextReader


class ReaderFactory:
    """
    Factory class for creating the correct reader based on file extension.
    
    Maps file extensions to their corresponding Reader classes.
    Provides a single method to instantiate and return the appropriate reader.
    """
    
    # Mapping of file extensions to Reader classes
    READER_MAP = {
        ".txt": TextReader,
        ".md": TextReader,
        ".pdf": PdfReader,
        ".py": CodeReader,
        ".js": CodeReader,
    }
    
    # Set of supported extensions
    SUPPORTED_EXTENSIONS = set(READER_MAP.keys())
    
    @staticmethod
    def get_extension(file_path):
        """
        Extract file extension from path.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            str: File extension including dot, lowercased (e.g., '.pdf')
                 Returns empty string if file has no extension
        """
        return os.path.splitext(file_path)[1].lower()
    
    @staticmethod
    def is_supported(file_path):
        """
        Check if the file type is supported.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            bool: True if file extension is supported, False otherwise
        """
        ext = ReaderFactory.get_extension(file_path)
        return ext in ReaderFactory.SUPPORTED_EXTENSIONS
    
    @staticmethod
    def create_reader(file_path):
        """
        Create and return an initialized reader instance for the given file.
        
        Args:
            file_path (str): Path to the file to read
            
        Returns:
            Reader: An instance of the appropriate Reader class (TextReader, CodeReader, or PdfReader)
            
        Raises:
            ValueError: If file extension is not supported or file has no extension
            FileNotFoundError: If the file path doesn't exist
        """
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File does not exist: {file_path}")
        
        # Extract extension
        ext = ReaderFactory.get_extension(file_path)
        
        # Validate extension exists and is supported
        if not ext:
            raise ValueError(f"File has no extension: {file_path}")
        
        if ext not in ReaderFactory.READER_MAP:
            supported = ", ".join(sorted(ReaderFactory.SUPPORTED_EXTENSIONS))
            raise ValueError(
                f"Unsupported file type '{ext}'. Supported types: {supported}"
            )
        
        # Get the reader class and instantiate it
        reader_class = ReaderFactory.READER_MAP[ext]
        return reader_class(file_path)
    
    @staticmethod
    def add_reader(extension, reader_class):
        """
        Register a new file extension and its corresponding reader class.
        
        This allows extending ReaderFactory with new file types at runtime.
        
        Args:
            extension (str): File extension including dot (e.g., '.docx')
            reader_class: Reader class to use for this extension
            
        Raises:
            ValueError: If extension is already registered with a different reader
        """
        ext = extension.lower() if not extension.startswith('.') else extension
        
        if ext in ReaderFactory.READER_MAP:
            if ReaderFactory.READER_MAP[ext] != reader_class:
                raise ValueError(
                    f"Extension '{ext}' is already registered with a different reader"
                )
        
        ReaderFactory.READER_MAP[ext] = reader_class
        ReaderFactory.SUPPORTED_EXTENSIONS.add(ext)
