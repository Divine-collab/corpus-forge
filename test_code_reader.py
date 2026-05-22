"""
Test script to verify CodeReader works correctly for Python and JavaScript files
"""

from Code_reader import CodeReader
import os


def test_code_reader():
    """Test the CodeReader class with sample code files"""
    
    # Create sample test files
    print("Creating sample test code files...")
    
    # Test 1: Python file
    with open("sample_python.py", "w") as f:
        f.write("""# This is a Python script
def calculate_sum(numbers):
    \"\"\"Calculate the sum of numbers\"\"\"
    total = 0
    for num in numbers:
        total += num  # Add number to total
    return total

user_data = [1, 2, 3, 4, 5]
result = calculate_sum(user_data)
""")
    
    # Test 2: JavaScript file
    with open("sample_code.js", "w") as f:
        f.write("""// JavaScript file for calculation
function calculateTotal(items) {
    /* Calculate the total of items */
    let total = 0;
    for (let item of items) {
        total += item; // Add item to total
    }
    return total;
}

const data = [10, 20, 30];
const sum = calculateTotal(data);
""")
    
    print("\n" + "="*60)
    print("TEST 1: Reading Python File")
    print("="*60)
    
    reader1 = CodeReader("sample_python.py")
    result1 = reader1.process()
    
    print(f"File Name: {result1['file_name']}")
    print(f"File Type: {result1['file_type']}")
    print(f"File Size: {result1['file_size']} bytes")
    print(f"Upload Date: {result1['upload_date']}")
    print(f"Word Count: {result1['word_count']}")
    print(f"Error: {result1['error']}")
    print(f"\nCleaned Text:\n{result1['cleaned_text']}")
    
    print("\n" + "="*60)
    print("TEST 2: Reading JavaScript File")
    print("="*60)
    
    reader2 = CodeReader("sample_code.js")
    result2 = reader2.process()
    
    print(f"File Name: {result2['file_name']}")
    print(f"File Type: {result2['file_type']}")
    print(f"File Size: {result2['file_size']} bytes")
    print(f"Upload Date: {result2['upload_date']}")
    print(f"Word Count: {result2['word_count']}")
    print(f"Error: {result2['error']}")
    print(f"\nCleaned Text:\n{result2['cleaned_text']}")
    
    print("\n" + "="*60)
    print("TEST 3: File Not Found Error")
    print("="*60)
    
    reader3 = CodeReader("nonexistent_code.py")
    result3 = reader3.process()
    print(f"Error: {result3['error']}")
    
    print("\n" + "="*60)
    print("TEST 4: Empty File Error")
    print("="*60)
    
    # Create empty file
    with open("empty_code.py", "w") as f:
        f.write("")
    
    reader4 = CodeReader("empty_code.py")
    result4 = reader4.process()
    print(f"Error: {result4['error']}")
    
    # Cleanup test files
    print("\nCleaning up test files...")
    for file in ["sample_python.py", "sample_code.js", "empty_code.py"]:
        if os.path.exists(file):
            os.remove(file)
    
    print("\nAll tests completed!")


if __name__ == "__main__":
    test_code_reader()
