"""
Flask entrypoint for Corpus Forge.

This file is intentionally left as a TODO scaffold so you can implement the
POST /upload endpoint step by step.
"""

import os
import tempfile

from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename

from reader_factory import ReaderFactory
from search_layer import SearchQuery, SearchLayer, SearchLayerAPI
from db import insert_uploaded_file


app = Flask(__name__)


UPLOAD_FOLDER = tempfile.gettempdir()



@app.route("/upload", methods=["POST"])
def upload_file():
	"""
	Handle an uploaded file and route it to the correct reader using ReaderFactory.
	
	Steps:
	1. Check whether 'file' exists in request.files.
	2. Reject empty filenames.
	3. Save the upload temporarily.
	4. Use ReaderFactory to create the appropriate reader.
	5. Call process() on the reader.
	6. Store the result in the database.
	7. Return the reader result as JSON.
	"""
	# 1) Basic request validation
	if 'file' not in request.files:
		return jsonify({'success': False, 'error': 'No file part in the request'}), 400

	file = request.files['file']
	filename = secure_filename(file.filename or "")
	if filename == "":
		return jsonify({'success': False, 'error': 'No selected file'}), 400

	# 2) Save upload to a temporary file (reader implementations expect a filepath)
	ext = ReaderFactory.get_extension(filename)
	temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext, dir=UPLOAD_FOLDER)
	temp_file.close()
	
	try:
		file.save(temp_file.name)

		# 3) Use ReaderFactory to create the appropriate reader
		try:
			reader = ReaderFactory.create_reader(temp_file.name)
		except (ValueError, FileNotFoundError) as e:
			return jsonify({'success': False, 'error': str(e)}), 400

		# 4) Process the file
		result = reader.process()

		# 5) If reader reported an error, surface it with 422 (unprocessable entity)
		if isinstance(result, dict) and result.get('error'):
			return jsonify({'success': False, 'error': result.get('error')}), 422

		# 6) Store in database
		file_size = os.path.getsize(temp_file.name)
		db_id = insert_uploaded_file(
			filename=filename,
			file_type=result.get('file_type', ext),
			file_size=file_size,
			raw_text=result.get('raw_text', ''),
			cleaned_text=result.get('cleaned_text', ''),
			word_count=result.get('word_count', 0)
		)

		# If DB insert failed, surface an error to the client
		if db_id is None:
			return jsonify({'success': False, 'error': 'Failed to persist record to database'}), 500

		# 7) Return success response
		response = {
			'success': True,
			'reader': reader.__class__.__name__,
			'file_name': result.get('file_name'),
			'result': result,
		}
		return jsonify(response), 200

	except Exception as e:
		# Unexpected server error
		return jsonify({'success': False, 'error': str(e)}), 500

	finally:
		# Always try to remove the temporary file
		try:
			os.remove(temp_file.name)
		except Exception:
			pass


@app.route("/search", methods=["POST"])
def search():
	"""
	Search endpoint for finding documents by keyword and filters.
	
	Request JSON parameters:
	{
		"keyword": "string" (required if no date filters),
		"file_type": ".pdf" (optional),
		"start_date": "2026-05-01" (optional, YYYY-MM-DD),
		"end_date": "2026-05-31" (optional, YYYY-MM-DD)
	}
	
	Returns:
	{
		"success": bool,
		"total_found": int,
		"query": string,
		"results": [
			{
				"file_id": int,
				"file_name": string,
				"file_type": string,
				"file_size": int,
				"word_count": int,
				"upload_date": string,
				"cleaned_text_preview": string,
				"match_score": float
			}
		],
		"error": string (if error)
	}
	"""
	try:
		# Get JSON request data
		data = request.get_json()
		if not data:
			return jsonify({'success': False, 'error': 'Request must be JSON'}), 400
		
		# Extract search parameters
		keyword = data.get('keyword', '').strip()
		file_type = data.get('file_type')
		start_date = data.get('start_date')
		end_date = data.get('end_date')
		
		# Create search query
		query = SearchQuery(
			keyword=keyword,
			file_type=file_type,
			start_date=start_date,
			end_date=end_date
		)
		
		# Validate query
		if not query.is_valid():
			return jsonify({
				'success': False,
				'error': 'Query must include keyword and/or date range'
			}), 400
		
		# Execute search
		result = SearchLayer.search(query)
		
		# Return results with appropriate status code
		if result['success']:
			return jsonify(result), 200
		else:
			return jsonify(result), 400
	
	except Exception as e:
		return jsonify({'success': False, 'error': f'Search error: {str(e)}'}), 500


@app.route("/list-documents", methods=["GET"])
def list_documents():
	"""
	List all uploaded documents with optional file type filter.
	
	Query parameters:
	- file_type: optional filter by file type (e.g., '.pdf')
	- limit: max number of results (default 50)
	
	Returns list of documents with metadata.
	"""
	try:
		file_type = request.args.get('file_type')
		limit = request.args.get('limit', default=50, type=int)
		
		result = SearchLayerAPI.list_all_documents(file_type=file_type, limit=limit)
		
		if result['success']:
			return jsonify(result), 200
		else:
			return jsonify(result), 400
	
	except Exception as e:
		return jsonify({'success': False, 'error': f'Error: {str(e)}'}), 500


# TODO: add error handlers for common upload problems.
# Examples:
# - missing file in request
# - unsupported extension
# - file read failure from a reader


# I took this function from other AI. It basically tests whether the DB connection works. You can run it to verify your DB config is correct.
# personally i verified the connection by running main.py and curl.exe -X POST http://127.0.0.1:5000/upload -F "file=@notes.txt" and checking the DB for the new record.
@app.route("/test-db", methods=["GET"])
def test_db():
    from db import get_db_connection
    connection = get_db_connection()
    if connection and connection.is_connected():
        connection.close()
        return jsonify({"status": "✅ Connected to corpus_forge successfully"}), 200
    else:
        return jsonify({"status": "❌ Connection failed"}), 500
	

if __name__ == "__main__":
	# TODO: decide whether debug=True should stay on while developing.
	app.run(debug=True)
