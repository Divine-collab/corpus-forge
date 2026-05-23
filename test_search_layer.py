"""
Tests for Search Layer.

Tests verify search functionality including:
- Keyword searches
- Filtering by file type
- Filtering by date range
- Result ranking and scoring
- Error handling
"""

from search_layer import SearchQuery, SearchLayer, SearchLayerAPI


print("=" * 70)
print("SEARCH LAYER TESTS")
print("=" * 70)

# ============================================================
# TEST 1: SearchQuery creation and validation
# ============================================================
print("\nTEST 1: SearchQuery creation and validation")
print("-" * 70)

try:
    # Valid query with keyword
    q1 = SearchQuery(keyword="machine learning")
    if q1.is_valid() and q1.keyword == "machine learning":
        print("✅ Query with keyword: VALID")
    else:
        print("❌ Query with keyword: INVALID")
    
    # Valid query with date range
    q2 = SearchQuery(start_date="2026-05-01", end_date="2026-05-31")
    if q2.is_valid():
        print("✅ Query with date range: VALID")
    else:
        print("❌ Query with date range: INVALID")
    
    # Invalid query (empty)
    q3 = SearchQuery()
    if not q3.is_valid():
        print("✅ Empty query correctly marked INVALID")
    else:
        print("❌ Empty query should be INVALID")
    
    # Query with all filters
    q4 = SearchQuery(
        keyword="python",
        file_type=".py",
        start_date="2026-05-01",
        end_date="2026-05-31"
    )
    if q4.is_valid() and q4.file_type == ".py":
        print("✅ Query with all filters: VALID")
    else:
        print("❌ Query with all filters: INVALID")

except Exception as e:
    print(f"❌ Error: {str(e)}")


# ============================================================
# TEST 2: Preview creation (text truncation)
# ============================================================
print("\nTEST 2: Preview creation and text truncation")
print("-" * 70)

try:
    short_text = "Hello world"
    long_text = "a" * 300  # 300 characters
    
    short_preview = SearchLayer._create_preview(short_text, 200)
    long_preview = SearchLayer._create_preview(long_text, 200)
    
    if short_preview == short_text:
        print(f"✅ Short text not truncated: {len(short_preview)} chars")
    else:
        print(f"❌ Short text was truncated incorrectly")
    
    if len(long_preview) <= 210 and long_preview.endswith("..."):
        print(f"✅ Long text truncated with ellipsis: {len(long_preview)} chars")
    else:
        print(f"❌ Long text not truncated properly")
    
    # Test boundary case
    boundary_text = "Hello world. This is a test. " * 10
    boundary_preview = SearchLayer._create_preview(boundary_text, 50)
    if "..." in boundary_preview or len(boundary_preview) <= 60:
        print(f"✅ Boundary text handled correctly: {len(boundary_preview)} chars")
    else:
        print(f"❌ Boundary text not handled")

except Exception as e:
    print(f"❌ Error: {str(e)}")


# ============================================================
# TEST 3: Match score calculation
# ============================================================
print("\nTEST 3: Match score calculation")
print("-" * 70)

try:
    # Test with keyword appearing once
    text1 = "This document discusses machine learning applications"
    score1 = SearchLayer._calculate_match_score("machine learning", text1)
    if 0.0 <= score1 <= 1.0:
        print(f"✅ Single match score: {score1}")
    else:
        print(f"❌ Score out of range: {score1}")
    
    # Test with keyword appearing multiple times
    text2 = "machine learning machine learning machine learning"
    score2 = SearchLayer._calculate_match_score("machine learning", text2)
    if score2 >= score1:
        print(f"✅ Multiple matches score higher: {score2}")
    else:
        print(f"❌ Multiple matches should score higher")
    
    # Test with no matches
    score3 = SearchLayer._calculate_match_score("machine learning", "completely different text")
    if score3 == 0.5:
        print(f"✅ No match default score: {score3}")
    else:
        print(f"❌ No match score incorrect: {score3}")
    
    # Test case insensitivity
    score4 = SearchLayer._calculate_match_score("Machine Learning", "machine learning")
    if score4 > 0:
        print(f"✅ Case-insensitive matching: {score4}")
    else:
        print(f"❌ Case insensitivity failed")

except Exception as e:
    print(f"❌ Error: {str(e)}")


# ============================================================
# TEST 4: Query building
# ============================================================
print("\nTEST 4: SQL query building with filters")
print("-" * 70)

try:
    # Query with keyword only
    q1 = SearchQuery(keyword="python")
    sql1, params1 = SearchLayer._build_query(q1)
    if "cleaned_text LIKE %s" in sql1 and "%python%" in params1:
        print("✅ Keyword query built correctly")
    else:
        print("❌ Keyword query incorrect")
    
    # Query with file type filter
    q2 = SearchQuery(keyword="python", file_type=".py")
    sql2, params2 = SearchLayer._build_query(q2)
    if "file_type = %s" in sql2 and ".py" in params2:
        print("✅ File type filter added to query")
    else:
        print("❌ File type filter not in query")
    
    # Query with date range
    q3 = SearchQuery(start_date="2026-05-01", end_date="2026-05-31")
    sql3, params3 = SearchLayer._build_query(q3)
    if "DATE(upload_date) >=" in sql3 and "2026-05-01" in params3:
        print("✅ Date range filters added to query")
    else:
        print("❌ Date range filters not correct")
    
    # Query with all filters
    q4 = SearchQuery(
        keyword="data",
        file_type=".txt",
        start_date="2026-05-10",
        end_date="2026-05-20"
    )
    sql4, params4 = SearchLayer._build_query(q4)
    if len(params4) == 4:
        print(f"✅ All filters combined: {len(params4)} parameters")
    else:
        print(f"❌ Parameter count wrong: {len(params4)}")

except Exception as e:
    print(f"❌ Error: {str(e)}")


# ============================================================
# TEST 5: Search result object
# ============================================================
print("\nTEST 5: Search result object and serialization")
print("-" * 70)

try:
    from search_layer import SearchResult
    
    result = SearchResult(
        file_id=1,
        file_name="test.pdf",
        file_type=".pdf",
        file_size=1024,
        word_count=500,
        upload_date="2026-05-23",
        cleaned_text_preview="This is a preview...",
        match_score=0.85
    )
    
    # Test attributes
    if result.file_id == 1 and result.file_name == "test.pdf":
        print("✅ SearchResult attributes set correctly")
    else:
        print("❌ SearchResult attributes incorrect")
    
    # Test serialization
    result_dict = result.to_dict()
    if all(k in result_dict for k in ['file_id', 'file_name', 'match_score']):
        print("✅ SearchResult serializes to dict with all fields")
    else:
        print("❌ SearchResult dict missing fields")
    
    if result_dict['match_score'] == 0.85:
        print("✅ Match score properly rounded")
    else:
        print(f"❌ Match score rounding issue: {result_dict['match_score']}")

except Exception as e:
    print(f"❌ Error: {str(e)}")


# ============================================================
# TEST 6: SearchLayer.search with mock data (JSON format)
# ============================================================
print("\nTEST 6: SearchLayer.search return format validation")
print("-" * 70)

try:
    q = SearchQuery(keyword="test")
    result = SearchLayer.search(q)
    
    # Check return structure
    required_keys = ['success', 'total_found', 'query', 'results', 'error']
    if all(k in result for k in required_keys):
        print("✅ Search result has all required fields")
    else:
        print(f"❌ Missing fields in result")
    
    if isinstance(result['results'], list):
        print("✅ Results is a list")
    else:
        print("❌ Results should be a list")
    
    if isinstance(result['total_found'], int):
        print("✅ total_found is integer")
    else:
        print("❌ total_found should be integer")

except Exception as e:
    print(f"❌ Error: {str(e)}")


# ============================================================
# TEST 7: Invalid query handling
# ============================================================
print("\nTEST 7: Invalid query handling")
print("-" * 70)

try:
    q_invalid = SearchQuery()  # Empty query
    result = SearchLayer.search(q_invalid)
    
    if result['success'] == False and result['error'] is not None:
        print("✅ Invalid query returns error")
        print(f"   Error message: {result['error']}")
    else:
        print("❌ Invalid query should return error")

except Exception as e:
    print(f"❌ Error: {str(e)}")


# ============================================================
# TEST 8: SearchLayerAPI convenience methods
# ============================================================
print("\nTEST 8: SearchLayerAPI convenience methods")
print("-" * 70)

try:
    # Test search_keyword API
    result1 = SearchLayerAPI.search_keyword("python")
    if 'success' in result1 and isinstance(result1['results'], list):
        print("✅ search_keyword returns valid structure")
    else:
        print("❌ search_keyword return format incorrect")
    
    # Test with filters
    result2 = SearchLayerAPI.search_keyword("python", file_type=".py")
    if 'success' in result2:
        print("✅ search_keyword with filters works")
    else:
        print("❌ search_keyword with filters failed")
    
    # Test list_all_documents
    result3 = SearchLayerAPI.list_all_documents()
    if 'success' in result3 and isinstance(result3['results'], list):
        print("✅ list_all_documents returns valid structure")
    else:
        print("❌ list_all_documents return format incorrect")

except Exception as e:
    print(f"❌ Error: {str(e)}")


print("\n" + "=" * 70)
print("ALL TESTS COMPLETED!")
print("=" * 70)
