"""
Simple test script to verify TextReader works correctly
"""

from Text_reader import TextReader
import os


def test_text_reader():
    """Test the TextReader class with sample files"""
    
    # Create sample test files
    print("Creating sample test files...")
    
    # Test 1: Simple text file
    with open("sample_text.txt", "w") as f:
        f.write("Hello world.\nThis is a test file.\nIt has multiple lines.")
    
    # Test 2: Markdown file
    with open("sample_markdown.md", "w") as f:
        f.write("# Hello World\n\nThis is **bold** text.\n\n- Item 1\n- Item 2\n\nMore *italic* text.")
    
    print("\n" + "="*60)
    print("TEST 1: Reading Text File")
    print("="*60)
    
    reader1 = TextReader("sample_text.txt")
    result1 = reader1.process()
    
    print(f"File Name: {result1['file_name']}")
    print(f"File Type: {result1['file_type']}")
    print(f"File Size: {result1['file_size']} bytes")
    print(f"Upload Date: {result1['upload_date']}")
    print(f"Raw Text Length: {len(result1['raw_text'])} characters")
    print(f"Cleaned Text Length: {len(result1['cleaned_text'])} characters")
    print(f"Word Count: {result1['word_count']}")
    print(f"Error: {result1['error']}")
    
    print("\n" + "="*60)
    print("TEST 2: Reading Markdown File")
    print("="*60)
    
    reader2 = TextReader("sample_markdown.md")
    result2 = reader2.process()
    
    print(f"File Name: {result2['file_name']}")
    print(f"File Type: {result2['file_type']}")
    print(f"File Size: {result2['file_size']} bytes")
    print(f"Upload Date: {result2['upload_date']}")
    print(f"Raw Text Length: {len(result2['raw_text'])} characters")
    print(f"Cleaned Text Length: {len(result2['cleaned_text'])} characters")
    print(f"Word Count: {result2['word_count']}")
    print(f"Error: {result2['error']}")
    print(f"\nCleaned Text:\n{result2['cleaned_text']}")
    
    print("\n" + "="*60)
    print("TEST 3: File Not Found Error")
    print("="*60)
    
    reader3 = TextReader("nonexistent_file.txt")
    result3 = reader3.process()
    print(f"Error: {result3['error']}")
    
    print("\n" + "="*60)
    print("TEST 4: Empty File Error")
    print("="*60)
    
    # Create empty file
    with open("empty_file.txt", "w") as f:
        f.write("")
    
    reader4 = TextReader("empty_file.txt")
    result4 = reader4.process()
    print(f"Error: {result4['error']}")
    
    # Cleanup test files
    print("\nCleaning up test files...")
    for file in ["sample_text.txt", "sample_markdown.md", "empty_file.txt"]:
        if os.path.exists(file):
            os.remove(file)
    
    print("\nAll tests completed!")


if __name__ == "__main__":
    test_text_reader()
