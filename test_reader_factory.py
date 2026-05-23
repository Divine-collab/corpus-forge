"""
Tests for ReaderFactory class.

Tests verify that ReaderFactory correctly:
- Instantiates readers for supported file types
- Handles unsupported file types with clear error messages
- Handles missing files appropriately
- Validates file extensions
"""

import os
import tempfile
from reader_factory import ReaderFactory
from Code_reader import CodeReader
from Pdf_reader import PdfReader
from Text_reader import TextReader


print("=" * 60)
print("READERFACTORY TESTS")
print("=" * 60)

# ============================================================
# TEST 1: Instantiate TextReader for .txt files
# ============================================================
print("\nTEST 1: Create TextReader for .txt file")
print("-" * 60)

try:
    # Create a temporary text file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is a test text file.")
        txt_path = f.name
    
    reader = ReaderFactory.create_reader(txt_path)
    
    if isinstance(reader, TextReader):
        print(f"✅ TextReader created successfully")
        print(f"   File path: {txt_path}")
        print(f"   Reader type: {type(reader).__name__}")
    else:
        print(f"❌ Wrong reader type: {type(reader).__name__}")
    
    os.remove(txt_path)

except Exception as e:
    print(f"❌ Error: {str(e)}")


# ============================================================
# TEST 2: Instantiate TextReader for .md files
# ============================================================
print("\nTEST 2: Create TextReader for .md file")
print("-" * 60)

try:
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("# Markdown Title\n\nThis is markdown content.")
        md_path = f.name
    
    reader = ReaderFactory.create_reader(md_path)
    
    if isinstance(reader, TextReader):
        print(f"✅ TextReader created successfully for markdown")
        print(f"   File path: {md_path}")
        print(f"   Reader type: {type(reader).__name__}")
    else:
        print(f"❌ Wrong reader type: {type(reader).__name__}")
    
    os.remove(md_path)

except Exception as e:
    print(f"❌ Error: {str(e)}")


# ============================================================
# TEST 3: Instantiate CodeReader for .py files
# ============================================================
print("\nTEST 3: Create CodeReader for .py file")
print("-" * 60)

try:
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("def hello():\n    print('Hello, World!')\n")
        py_path = f.name
    
    reader = ReaderFactory.create_reader(py_path)
    
    if isinstance(reader, CodeReader):
        print(f"✅ CodeReader created successfully for Python")
        print(f"   File path: {py_path}")
        print(f"   Reader type: {type(reader).__name__}")
    else:
        print(f"❌ Wrong reader type: {type(reader).__name__}")
    
    os.remove(py_path)

except Exception as e:
    print(f"❌ Error: {str(e)}")


# ============================================================
# TEST 4: Instantiate CodeReader for .js files
# ============================================================
print("\nTEST 4: Create CodeReader for .js file")
print("-" * 60)

try:
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write("function hello() {\n  console.log('Hello');\n}\n")
        js_path = f.name
    
    reader = ReaderFactory.create_reader(js_path)
    
    if isinstance(reader, CodeReader):
        print(f"✅ CodeReader created successfully for JavaScript")
        print(f"   File path: {js_path}")
        print(f"   Reader type: {type(reader).__name__}")
    else:
        print(f"❌ Wrong reader type: {type(reader).__name__}")
    
    os.remove(js_path)

except Exception as e:
    print(f"❌ Error: {str(e)}")


# ============================================================
# TEST 5: Unsupported file type error
# ============================================================
print("\nTEST 5: Handle unsupported file type")
print("-" * 60)

try:
    with tempfile.NamedTemporaryFile(mode='w', suffix='.docx', delete=False) as f:
        f.write("This is a Word document.")
        docx_path = f.name
    
    reader = ReaderFactory.create_reader(docx_path)
    print(f"❌ Should have raised ValueError for unsupported type")
    os.remove(docx_path)

except ValueError as e:
    print(f"✅ Correct error raised for unsupported type")
    print(f"   Error message: {str(e)}")
    os.remove(docx_path)

except Exception as e:
    print(f"❌ Wrong exception type: {type(e).__name__}: {str(e)}")
    os.remove(docx_path)


# ============================================================
# TEST 6: File not found error
# ============================================================
print("\nTEST 6: Handle file not found")
print("-" * 60)

try:
    reader = ReaderFactory.create_reader("/nonexistent/path/file.txt")
    print(f"❌ Should have raised FileNotFoundError")

except FileNotFoundError as e:
    print(f"✅ Correct error raised for missing file")
    print(f"   Error message: {str(e)}")

except Exception as e:
    print(f"❌ Wrong exception type: {type(e).__name__}: {str(e)}")


# ============================================================
# TEST 7: File with no extension error
# ============================================================
print("\nTEST 7: Handle file with no extension")
print("-" * 60)

try:
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("This file has no extension.")
        no_ext_path = f.name
    
    reader = ReaderFactory.create_reader(no_ext_path)
    print(f"❌ Should have raised ValueError for missing extension")
    os.remove(no_ext_path)

except ValueError as e:
    print(f"✅ Correct error raised for missing extension")
    print(f"   Error message: {str(e)}")
    os.remove(no_ext_path)

except Exception as e:
    print(f"❌ Wrong exception type: {type(e).__name__}: {str(e)}")
    os.remove(no_ext_path)


# ============================================================
# TEST 8: is_supported() method
# ============================================================
print("\nTEST 8: is_supported() method")
print("-" * 60)

try:
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("test")
        py_path = f.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xyz', delete=False) as f:
        f.write("test")
        xyz_path = f.name
    
    is_py_supported = ReaderFactory.is_supported(py_path)
    is_xyz_supported = ReaderFactory.is_supported(xyz_path)
    
    if is_py_supported and not is_xyz_supported:
        print(f"✅ is_supported() works correctly")
        print(f"   .py supported: {is_py_supported}")
        print(f"   .xyz supported: {is_xyz_supported}")
    else:
        print(f"❌ is_supported() returned incorrect results")
    
    os.remove(py_path)
    os.remove(xyz_path)

except Exception as e:
    print(f"❌ Error: {str(e)}")


# ============================================================
# TEST 9: get_extension() method
# ============================================================
print("\nTEST 9: get_extension() method")
print("-" * 60)

try:
    tests = [
        ("document.pdf", ".pdf"),
        ("script.py", ".py"),
        ("README.md", ".md"),
        ("file.txt", ".txt"),
        ("archive", ""),
        ("UPPERCASE.PDF", ".pdf"),
    ]
    
    all_passed = True
    for filename, expected_ext in tests:
        actual_ext = ReaderFactory.get_extension(filename)
        if actual_ext == expected_ext:
            print(f"   ✅ {filename} -> {actual_ext}")
        else:
            print(f"   ❌ {filename} -> {actual_ext} (expected {expected_ext})")
            all_passed = False
    
    if all_passed:
        print(f"\n✅ All get_extension() tests passed")

except Exception as e:
    print(f"❌ Error: {str(e)}")


# ============================================================
# TEST 10: Supported extensions list
# ============================================================
print("\nTEST 10: Supported extensions list")
print("-" * 60)

try:
    supported = sorted(ReaderFactory.SUPPORTED_EXTENSIONS)
    print(f"✅ Supported extensions: {supported}")
    
    expected = {".txt", ".md", ".pdf", ".py", ".js"}
    if ReaderFactory.SUPPORTED_EXTENSIONS == expected:
        print(f"✅ All expected extensions are supported")
    else:
        print(f"⚠️  Supported extensions: {supported}")

except Exception as e:
    print(f"❌ Error: {str(e)}")


print("\n" + "=" * 60)
print("ALL TESTS COMPLETED!")
print("=" * 60)
