"""
Test script to verify PdfReader works correctly
"""

from Pdf_reader import PdfReader
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


def create_sample_pdf():
    """Create a sample PDF file for testing"""
    pdf_path = "sample_test.pdf"
    
    c = canvas.Canvas(pdf_path, pagesize=letter)
    
    # Page 1
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, "Sample PDF Document")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, 720, "This is the first page of the PDF.")
    c.drawString(50, 700, "It contains sample text for testing the PdfReader.")
    c.drawString(50, 680, "We can extract this text for topic analysis.")
    
    c.drawString(50, 650, "Key Topics Mentioned:")
    c.drawString(70, 630, "- Machine Learning")
    c.drawString(70, 610, "- Data Processing")
    c.drawString(70, 590, "- Natural Language Processing")
    
    # Page 2
    c.showPage()
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, "Page 2: Advanced Topics")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, 720, "This is the second page.")
    c.drawString(50, 700, "It discusses more advanced concepts.")
    c.drawString(50, 680, "Database systems and cloud computing are important.")
    
    c.drawString(50, 650, "Technologies:")
    c.drawString(70, 630, "- PostgreSQL")
    c.drawString(70, 610, "- AWS")
    c.drawString(70, 590, "- Docker")
    
    c.save()
    return pdf_path


def test_pdf_reader():
    """Test the PdfReader class"""
    
    print("Creating sample PDF file...")
    pdf_file = create_sample_pdf()
    
    print("\n" + "="*60)
    print("TEST 1: Reading PDF File")
    print("="*60)
    
    reader = PdfReader(pdf_file)
    result = reader.process(extract_images=False)  # Skip images for this test
    
    if result['error'] is None:
        print(f"✅ File Name: {result['file_name']}")
        print(f"✅ File Type: {result['file_type']}")
        print(f"✅ File Size: {result['file_size']} bytes")
        print(f"✅ Page Count: {result['page_count']}")
        print(f"✅ Upload Date: {result['upload_date']}")
        print(f"✅ Word Count: {result['word_count']}")
        print(f"✅ Images Extracted: {result['image_count']}")
        print(f"\n📄 Extracted Text (first 200 chars):\n{result['cleaned_text'][:200]}...")
    else:
        print(f"❌ Error: {result['error']}")
    
    print("\n" + "="*60)
    print("TEST 2: File Not Found Error")
    print("="*60)
    
    reader2 = PdfReader("nonexistent.pdf")
    result2 = reader2.process()
    print(f"Error: {result2['error']}")
    
    print("\n" + "="*60)
    print("TEST 3: Empty PDF Error")
    print("="*60)
    
    # Create empty PDF
    empty_pdf = "empty_test.pdf"
    c = canvas.Canvas(empty_pdf, pagesize=letter)
    c.save()
    
    reader3 = PdfReader(empty_pdf)
    result3 = reader3.process()
    print(f"Error: {result3['error']}")
    
    # Cleanup
    print("\nCleaning up test files...")
    for file in [pdf_file, empty_pdf]:
        if os.path.exists(file):
            os.remove(file)
    
    print("\nAll tests completed!")


if __name__ == "__main__":
    test_pdf_reader()
