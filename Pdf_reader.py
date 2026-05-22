import os
import pdfplumber
from datetime import datetime


class PdfReader:
    """
    A class to read and process PDF files.
    Extracts text content, images, and metadata from PDFs.
    """
    
    def __init__(self, file_path):
        """
        Initialize the PdfReader with a file path.
        
        Args:
            file_path (str): Path to the PDF file to read
        """
        self.file_path = file_path
        self.error_message = None
        self.extracted_images = []
        self.image_count = 0
    
    def read_file(self):
        """
        Open and read the PDF file.
        
        Returns:
            pdfplumber.PDF object or None if error occurs
        """
        try:
            pdf = pdfplumber.open(self.file_path)
            return pdf
        except FileNotFoundError:
            self.error_message = "File does not exist"
            return None
        except PermissionError:
            self.error_message = "Permission denied: Cannot read file"
            return None
        except Exception as e:
            self.error_message = f"Error reading PDF: {str(e)}"
            return None
    
    def extract_text_from_pages(self, pdf):
        """
        Extract text content from all pages in the PDF.
        
        Args:
            pdf: pdfplumber.PDF object
            
        Returns:
            str: All text from all pages concatenated
        """
        all_text = ""
        
        try:
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    all_text += page_text + "\n"
            
            return all_text.strip()
        
        except Exception as e:
            self.error_message = f"Error extracting text: {str(e)}"
            return ""
    
    def extract_images_from_pages(self, pdf, output_dir="extracted_images"):
        """
        Extract all images from PDF pages and save them.
        
        Args:
            pdf: pdfplumber.PDF object
            output_dir (str): Directory to save extracted images
            
        Returns:
            list: List of image file paths that were extracted
        """
        try:
            # Create output directory if it doesn't exist
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            image_paths = []
            
            # Loop through each page
            for page_num, page in enumerate(pdf.pages, 1):
                # Get all images on this page
                images = page.images
                
                for img_index, img in enumerate(images):
                    try:
                        # Get image from the page using crop
                        im = page.within_bbox([
                            img['x0'], img['top'], img['x1'], img['bottom']
                        ]).to_image()
                        
                        # Create unique filename
                        filename = f"page_{page_num}_image_{img_index}.png"
                        filepath = os.path.join(output_dir, filename)
                        
                        # Save image
                        im.save(filepath)
                        image_paths.append(filepath)
                    
                    except Exception as e:
                        # Continue with next image if this one fails
                        continue
            
            self.image_count = len(image_paths)
            return image_paths
        
        except Exception as e:
            self.error_message = f"Error extracting images: {str(e)}"
            return []
    
    def extract_metadata(self, pdf):
        """
        Extract metadata about the PDF file.
        
        Returns:
            dict: Dictionary containing file metadata
                  Keys: file_name, file_type, file_size, upload_date, page_count
        """
        try:
            file_name = os.path.basename(self.file_path)
            file_type = os.path.splitext(file_name)[1].lower()
            file_size = os.path.getsize(self.file_path)
            upload_date = datetime.fromtimestamp(
                os.path.getmtime(self.file_path)
            ).strftime("%Y-%m-%d %H:%M:%S")
            page_count = len(pdf.pages)
            
            return {
                "file_name": file_name,
                "file_type": file_type,
                "file_size": file_size,
                "upload_date": upload_date,
                "page_count": page_count
            }
        
        except Exception as e:
            self.error_message = f"Error extracting metadata: {str(e)}"
            return {}
    
    def clean_content(self, text):
        """
        Clean extracted text by removing extra whitespace and normalizing.
        
        Args:
            text (str): The raw extracted text
            
        Returns:
            str: The cleaned text
        """
        import re
        
        # Remove multiple consecutive newlines (replace with single space)
        text = re.sub(r'\n+', ' ', text)
        
        # Remove multiple spaces between words
        text = re.sub(r' +', ' ', text)
        
        # Remove control characters
        text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', text)
        
        # Strip leading and trailing whitespace
        text = text.strip()
        
        return text
    
    def count_words(self, text):
        """
        Count the number of words in the text.
        
        Args:
            text (str): The text to count words in
            
        Returns:
            int: The word count
        """
        if not text:
            return 0
        
        words = text.split()
        return len(words)
    
    def process(self, extract_images=True, image_output_dir="extracted_images"):
        """
        Main method that orchestrates the entire PDF processing pipeline.
        Reads, extracts text and images, extracts metadata, counts words.
        
        Args:
            extract_images (bool): Whether to extract and save images from PDF
            image_output_dir (str): Directory to save extracted images
        
        Returns:
            dict: A complete dictionary with all extracted information:
                  {
                      "file_name": str,
                      "file_type": str,
                      "file_size": int,
                      "upload_date": str,
                      "page_count": int,
                      "raw_text": str,
                      "cleaned_text": str,
                      "word_count": int,
                      "images_extracted": list (paths to extracted images),
                      "image_count": int,
                      "error": str (if error occurred, None otherwise)
                  }
        """
        # Read the PDF file
        pdf = self.read_file()
        
        # Check if file reading failed
        if pdf is None:
            return {
                "file_name": None,
                "file_type": None,
                "file_size": None,
                "upload_date": None,
                "page_count": None,
                "raw_text": None,
                "cleaned_text": None,
                "word_count": None,
                "images_extracted": [],
                "image_count": 0,
                "error": self.error_message
            }
        
        # Extract text from all pages
        raw_text = self.extract_text_from_pages(pdf)
        
        # Extract metadata
        metadata = self.extract_metadata(pdf)
        
        # Extract images if requested
        if extract_images:
            images_extracted = self.extract_images_from_pages(pdf, image_output_dir)
        else:
            images_extracted = []
        
        # Clean the text
        cleaned_text = self.clean_content(raw_text)
        
        # Count words
        word_count = self.count_words(cleaned_text)
        
        # Combine all information into result dictionary
        result = {
            "file_name": metadata.get("file_name"),
            "file_type": metadata.get("file_type"),
            "file_size": metadata.get("file_size"),
            "upload_date": metadata.get("upload_date"),
            "page_count": metadata.get("page_count"),
            "raw_text": raw_text,
            "cleaned_text": cleaned_text,
            "word_count": word_count,
            "images_extracted": images_extracted,
            "image_count": self.image_count,
            "error": self.error_message
        }
        
        # Close the PDF
        pdf.close()
        
        return result
