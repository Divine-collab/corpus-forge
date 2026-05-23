"""
Search Layer for Corpus Forge.

This module provides keyword-based search functionality for documents.
Users can search by keyword, file type, and date range.
Returns matching documents with metadata and text previews.
"""

from db import get_db_connection
from db import Error
from datetime import datetime


class SearchQuery:
    """
    Represents a search query with filters.
    
    Attributes:
        keyword (str): Text to search for in cleaned_text
        file_type (str): Filter by file extension (e.g., '.pdf', '.py')
        start_date (str): Filter by upload date range start (YYYY-MM-DD)
        end_date (str): Filter by upload date range end (YYYY-MM-DD)
    """
    
    def __init__(self, keyword="", file_type=None, start_date=None, end_date=None):
        """
        Initialize a search query.
        
        Args:
            keyword (str): Keywords to search for (required, can be empty for listing all)
            file_type (str): Optional file type filter (e.g., '.pdf')
            start_date (str): Optional start date in YYYY-MM-DD format
            end_date (str): Optional end date in YYYY-MM-DD format
        """
        self.keyword = keyword.strip() if keyword else ""
        self.file_type = file_type
        self.start_date = start_date
        self.end_date = end_date
    
    def is_valid(self):
        """Check if query is valid for searching."""
        # At least keyword or date range required
        return bool(self.keyword or self.start_date or self.end_date)


class SearchResult:
    """
    Represents a single search result (document metadata).
    """
    
    def __init__(self, file_id, file_name, file_type, file_size, word_count, 
                 upload_date, cleaned_text_preview, match_score=1.0):
        """
        Initialize a search result.
        
        Args:
            file_id (int): Database ID of the file
            file_name (str): Name of the file
            file_type (str): File extension
            file_size (int): File size in bytes
            word_count (int): Word count
            upload_date (str): Upload date as string
            cleaned_text_preview (str): First 200 chars of cleaned_text
            match_score (float): Relevance score 0-1
        """
        self.file_id = file_id
        self.file_name = file_name
        self.file_type = file_type
        self.file_size = file_size
        self.word_count = word_count
        self.upload_date = upload_date
        self.cleaned_text_preview = cleaned_text_preview
        self.match_score = match_score
    
    def to_dict(self):
        """Convert result to dictionary for JSON serialization."""
        return {
            'file_id': self.file_id,
            'file_name': self.file_name,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'word_count': self.word_count,
            'upload_date': self.upload_date,
            'cleaned_text_preview': self.cleaned_text_preview,
            'match_score': round(self.match_score, 2)
        }


class SearchLayer:
    """
    Core search layer for finding documents in the database.
    
    Handles keyword searches, filtering, and result ranking.
    """
    
    @staticmethod
    def search(query):
        """
        Execute a search query against the database.
        
        Args:
            query (SearchQuery): The search query with filters
            
        Returns:
            dict: Search results with metadata:
                  {
                      'success': bool,
                      'total_found': int,
                      'query': str (original keyword),
                      'results': list of SearchResult.to_dict(),
                      'error': str (if error occurred)
                  }
        """
        try:
            # Validate query
            if not query.is_valid():
                return {
                    'success': False,
                    'total_found': 0,
                    'results': [],
                    'error': 'Query must include keyword and/or date range'
                }
            
            # Build and execute SQL query
            sql, params = SearchLayer._build_query(query)
            
            connection = get_db_connection()
            if connection is None:
                return {
                    'success': False,
                    'total_found': 0,
                    'results': [],
                    'error': 'Database connection failed'
                }
            
            cursor = connection.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            cursor.close()
            connection.close()
            
            # Convert rows to SearchResult objects
            results = []
            for row in rows:
                # row: (file_id, filename, file_type, file_size, word_count, upload_date, cleaned_text)
                preview = SearchLayer._create_preview(row[6])
                match_score = SearchLayer._calculate_match_score(query.keyword, row[6])
                
                result = SearchResult(
                    file_id=row[0],
                    file_name=row[1],
                    file_type=row[2],
                    file_size=row[3],
                    word_count=row[4],
                    upload_date=row[5],
                    cleaned_text_preview=preview,
                    match_score=match_score
                )
                results.append(result)
            
            # Sort by match score (descending)
            results.sort(key=lambda r: r.match_score, reverse=True)
            
            return {
                'success': True,
                'total_found': len(results),
                'query': query.keyword,
                'results': [r.to_dict() for r in results],
                'error': None
            }
        
        except Exception as e:
            return {
                'success': False,
                'total_found': 0,
                'results': [],
                'error': f'Search error: {str(e)}'
            }
    
    @staticmethod
    def _build_query(query):
        """
        Build SQL query with filters from SearchQuery.
        
        Args:
            query (SearchQuery): The search query
            
        Returns:
            tuple: (sql_string, params_list)
        """
        conditions = []
        params = []
        
        # Keyword search on cleaned_text
        if query.keyword:
            conditions.append("cleaned_text LIKE %s")
            params.append(f"%{query.keyword}%")
        
        # File type filter
        if query.file_type:
            conditions.append("file_type = %s")
            params.append(query.file_type)
        
        # Date range filter
        if query.start_date:
            conditions.append("DATE(upload_date) >= %s")
            params.append(query.start_date)
        
        if query.end_date:
            conditions.append("DATE(upload_date) <= %s")
            params.append(query.end_date)
        
        # Build WHERE clause
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        # Complete SQL query
        sql = f"""
            SELECT 
                id, 
                filename, 
                file_type, 
                file_size, 
                word_count, 
                upload_date,
                cleaned_text
            FROM uploaded_files
            WHERE {where_clause}
            ORDER BY upload_date DESC
            LIMIT 100
        """
        
        return sql, params
    
    @staticmethod
    def _create_preview(text, length=200):
        """
        Create a preview snippet from full text.
        
        Args:
            text (str): Full text content
            length (int): Max length of preview
            
        Returns:
            str: Preview text truncated at word boundary
        """
        if not text or len(text) <= length:
            return text
        
        # Truncate to length and find last space for clean cutoff
        preview = text[:length]
        last_space = preview.rfind(' ')
        
        if last_space > 0:
            preview = preview[:last_space] + "..."
        else:
            preview = preview + "..."
        
        return preview
    
    @staticmethod
    def _calculate_match_score(keyword, text):
        """
        Calculate relevance score based on keyword match count.
        
        Args:
            keyword (str): Search keyword
            text (str): Document text to score
            
        Returns:
            float: Score between 0 and 1
        """
        if not keyword or not text:
            return 1.0
        
        text_lower = text.lower()
        keyword_lower = keyword.lower()
        
        # Count occurrences (case-insensitive)
        count = text_lower.count(keyword_lower)
        
        # Calculate score based on occurrence frequency
        # Cap at 100 occurrences for scoring
        score = min(count / 100.0, 1.0)
        
        return score if score > 0 else 0.5


class SearchLayerAPI:
    """
    High-level API for Search Layer.
    Useful for command-line or batch usage.
    """
    
    @staticmethod
    def search_keyword(keyword, file_type=None, start_date=None, end_date=None):
        """
        Simple keyword search API.
        
        Args:
            keyword (str): Text to search for
            file_type (str): Optional file type filter
            start_date (str): Optional start date
            end_date (str): Optional end date
            
        Returns:
            dict: Search results
        """
        query = SearchQuery(
            keyword=keyword,
            file_type=file_type,
            start_date=start_date,
            end_date=end_date
        )
        return SearchLayer.search(query)
    
    @staticmethod
    def list_all_documents(file_type=None, limit=50):
        """
        List all documents in database, optionally filtered by type.
        
        Args:
            file_type (str): Optional file type filter
            limit (int): Max number of results
            
        Returns:
            dict: List of documents
        """
        try:
            connection = get_db_connection()
            if connection is None:
                return {
                    'success': False,
                    'total': 0,
                    'results': [],
                    'error': 'Database connection failed'
                }
            
            cursor = connection.cursor()
            
            if file_type:
                sql = """
                    SELECT id, filename, file_type, file_size, word_count, upload_date
                    FROM uploaded_files
                    WHERE file_type = %s
                    ORDER BY upload_date DESC
                    LIMIT %s
                """
                cursor.execute(sql, (file_type, limit))
            else:
                sql = """
                    SELECT id, filename, file_type, file_size, word_count, upload_date
                    FROM uploaded_files
                    ORDER BY upload_date DESC
                    LIMIT %s
                """
                cursor.execute(sql, (limit,))
            
            rows = cursor.fetchall()
            cursor.close()
            connection.close()
            
            results = [
                {
                    'file_id': row[0],
                    'file_name': row[1],
                    'file_type': row[2],
                    'file_size': row[3],
                    'word_count': row[4],
                    'upload_date': row[5]
                }
                for row in rows
            ]
            
            return {
                'success': True,
                'total': len(results),
                'results': results,
                'error': None
            }
        
        except Exception as e:
            return {
                'success': False,
                'total': 0,
                'results': [],
                'error': f'Error listing documents: {str(e)}'
            }
