"""
Flask entrypoint for Corpus Forge.

This file is intentionally left as a TODO scaffold so you can implement the
POST /upload endpoint step by step.
"""

import os
import tempfile

from flask import Flask, jsonify, render_template, request
from werkzeug.utils import secure_filename

from reader_factory import ReaderFactory
from search_layer import SearchQuery, SearchLayer, SearchLayerAPI
from query_layer import AIQueryLayer
from db import (
	insert_uploaded_file,
	get_document_text,
	insert_api_usage_log,
	get_api_stats,
	insert_quiz,
	insert_quiz_question,
	get_quiz,
	get_quizzes_by_document,
	delete_uploaded_file,
	insert_flashcard_set,
	insert_flashcard,
	get_flashcard_set,
	get_flashcard_sets_by_document
)


app = Flask(__name__)


UPLOAD_FOLDER = tempfile.gettempdir()


@app.route("/")
def index():
	"""Serve the main frontend page."""
	return render_template("index.html")



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


@app.route("/documents/<int:document_id>", methods=["DELETE"])
def delete_document(document_id):
	"""
	Delete a document from the database by ID.
	
	Returns:
	{
		"success": bool,
		"document_id": int,
		"message": string,
		"error": string (if error)
	}
	"""
	try:
		from db import delete_uploaded_file

		deleted = delete_uploaded_file(document_id)
		if deleted:
			return jsonify({
				'success': True,
				'document_id': document_id,
				'message': 'Document deleted successfully'
			}), 200

		return jsonify({
			'success': False,
			'document_id': document_id,
			'error': f'Document with ID {document_id} not found'
		}), 404

	except Exception as e:
		return jsonify({'success': False, 'error': f'Delete error: {str(e)}'}), 500


@app.route("/query", methods=["POST"])
def query():
	"""
	AI Query endpoint: Ask a question about a specific document.
	
	Request JSON parameters:
	{
		"query": "string" (required, the question to ask),
		"document_id": int (required, the document to query),
		"steering": dict (optional, prompt steering parameters)
	}
	
	Steering parameters (optional):
	{
		"audience_level": "beginner|intermediate|expert",
		"tone": "professional|casual|academic",
		"output_format": "summary|detailed|code",
		"creativity": "literal|balanced|creative"
	}
	
	Returns:
	{
		"success": bool,
		"answer": string (if success),
		"document_id": int,
		"query": string,
		"error": string (if error)
	}
	"""
	try:
		# Get JSON request data
		data = request.get_json()
		if not data:
			return jsonify({'success': False, 'error': 'Request must be JSON'}), 400
		
		# Extract parameters
		user_query = data.get('query', '').strip()
		document_id = data.get('document_id')
		steering = data.get('steering', {})
		
		# Validate inputs
		if not user_query:
			return jsonify({'success': False, 'error': 'Query cannot be empty'}), 400
		
		if document_id is None:
			return jsonify({'success': False, 'error': 'document_id is required'}), 400
		
		# Fetch document text from database
		document_text = get_document_text(document_id)
		if document_text is None:
			return jsonify({
				'success': False,
				'error': f'Document with ID {document_id} not found'
			}), 404
		
		# Initialize AI Query Layer
		ai_layer = AIQueryLayer()
		
		# Ask question about document with steering parameters
		result = ai_layer.query(user_query, document_text, steering=steering)
		input_token_count = result.get('input_token_count')
		output_token_count = result.get('output_token_count')

		# Log token usage for every successful Gemini call.
		if result.get('success'):
			total_token_count = (input_token_count or 0) + (output_token_count or 0)
			usage_log_id = insert_api_usage_log(
				document_id=document_id,
				query_text=user_query,
				input_tokens=input_token_count or 0,
				output_tokens=output_token_count or 0,
				total_tokens=total_token_count,
			)
			if usage_log_id is None:
				print(f"[DB] Failed to log token usage for document_id={document_id}")
		
		# Return result with document context
		if result['success']:
			return jsonify({
				'success': True,
				'answer': result['answer'],
				'document_id': document_id,
				'query': user_query,
				'input_token_count': input_token_count,
				'output_token_count': output_token_count,
				'total_token_count': (input_token_count or 0) + (output_token_count or 0)
			}), 200
		else:
			return jsonify({
				'success': False,
				'error': result['error'],
				'document_id': document_id,
				'query': user_query
			}), 400
	
	except Exception as e:
		return jsonify({'success': False, 'error': f'Query error: {str(e)}'}), 500


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


@app.route("/stats", methods=["GET"])
def stats():
	"""
	Return aggregate token usage statistics from api_usage_logs.

	Returns:
	{
		"success": bool,
		"total_api_requests": int,
		"total_input_tokens": int,
		"total_output_tokens": int,
		"total_tokens_overall": int,
		"error": string (if error)
	}
	"""
	try:
		stats_data = get_api_stats()
		if stats_data is None:
			return jsonify({
				'success': False,
				'error': 'Failed to retrieve API usage statistics'
			}), 500

		return jsonify({
			'success': True,
			**stats_data
		}), 200

	except Exception as e:
		return jsonify({'success': False, 'error': f'Stats error: {str(e)}'}), 500
	

@app.route("/generate_quiz", methods=["POST"])
def generate_quiz():
	"""
	Generate quiz questions from a document.
	
	Request JSON parameters:
	{
		"document_id": int (required),
		"num_questions": int (optional, default 5)
	}
	
	Returns:
	{
		"success": bool,
		"quiz_id": int (if success),
		"questions": list (if success),
		"error": string (if error)
	}
	"""
	try:
		data = request.get_json()
		if not data:
			return jsonify({'success': False, 'error': 'Request must be JSON'}), 400
		
		document_id = data.get('document_id')
		num_questions = data.get('num_questions', 5)
		
		if document_id is None:
			return jsonify({'success': False, 'error': 'document_id is required'}), 400
		
		if not isinstance(num_questions, int) or num_questions < 1 or num_questions > 20:
			return jsonify({'success': False, 'error': 'num_questions must be between 1 and 20'}), 400
		
		# Fetch document text
		document_text = get_document_text(document_id)
		if document_text is None:
			return jsonify({
				'success': False,
				'error': f'Document with ID {document_id} not found'
			}), 404
		
		# Generate quiz using AI layer
		ai_layer = AIQueryLayer()
		result = ai_layer.generate_quiz(document_text, num_questions)
		
		if not result['success']:
			return jsonify({
				'success': False,
				'error': result['error']
			}), 400
		
		# Save quiz to database
		quiz_title = f"Quiz for Document {document_id}"
		quiz_id = insert_quiz(document_id, quiz_title, len(result['questions']))
		
		if quiz_id is None:
			return jsonify({
				'success': False,
				'error': 'Failed to save quiz to database'
			}), 500
		
		# Save quiz questions
		for q in result['questions']:
			insert_quiz_question(
				quiz_id,
				q['question'],
				'multiple_choice',
				q['correct_answer']
			)
		
		return jsonify({
			'success': True,
			'quiz_id': quiz_id,
			'questions': result['questions']
		}), 200
	
	except Exception as e:
		return jsonify({
			'success': False,
			'error': f'Server error: {str(e)}'
		}), 500


@app.route("/get_quiz/<int:quiz_id>", methods=["GET"])
def get_quiz_endpoint(quiz_id):
	"""
	Retrieve a quiz by ID.
	
	Returns:
	{
		"success": bool,
		"quiz": {
			"id": int,
			"document_id": int,
			"quiz_title": string,
			"num_questions": int,
			"questions": list
		}
	}
	"""
	try:
		quiz = get_quiz(quiz_id)
		
		if not quiz:
			return jsonify({
				'success': False,
				'error': f'Quiz with ID {quiz_id} not found'
			}), 404
		
		return jsonify({
			'success': True,
			'quiz': quiz
		}), 200
	
	except Exception as e:
		return jsonify({
			'success': False,
			'error': f'Server error: {str(e)}'
		}), 500


@app.route("/list_quizzes/<int:document_id>", methods=["GET"])
def list_quizzes(document_id):
	"""
	List all quizzes for a document.
	
	Returns:
	{
		"success": bool,
		"quizzes": list
	}
	"""
	try:
		quizzes = get_quizzes_by_document(document_id)
		
		return jsonify({
			'success': True,
			'quizzes': quizzes
		}), 200
	
	except Exception as e:
		return jsonify({
			'success': False,
			'error': f'Server error: {str(e)}'
		}), 500


# ─────────────────────────────────────────
# FLASHCARD ENDPOINTS
# ─────────────────────────────────────────
@app.route("/generate_flashcards", methods=["POST"])
def generate_flashcards():
	"""
	Generate flashcards from a selected document.
	
	Request JSON:
	{
		"document_id": <id>,
		"num_cards": <int>,
		"set_title": <optional string>
	}
	
	Returns:
	{
		"success": bool,
		"flashcard_set_id": <id>,
		"flashcards": [{"front": str, "back": str}, ...],
		"error": str
	}
	"""
	try:
		data = request.get_json()
		if not data:
			return jsonify({'success': False, 'error': 'No JSON data'}), 400
		
		document_id = data.get('document_id')
		num_cards = data.get('num_cards', 10)
		set_title = data.get('set_title', f'Flashcard Set #{document_id}')
		
		if not document_id:
			return jsonify({'success': False, 'error': 'document_id required'}), 400
		
		# Get document text
		doc_result = get_document_text(document_id)
		if not doc_result:
			return jsonify({'success': False, 'error': 'Document not found'}), 404
		
		document_text = doc_result.get('cleaned_text', '')
		
		# Initialize AI layer and generate flashcards
		try:
			ai_layer = AIQueryLayer()
		except ValueError as e:
			return jsonify({'success': False, 'error': str(e)}), 500
		
		result = ai_layer.generate_flashcards(document_text, num_cards)
		
		if not result['success']:
			return jsonify(result), 400
		
		flashcards = result['flashcards']
		
		# Save flashcard set to database
		set_id = insert_flashcard_set(document_id, set_title, len(flashcards))
		if not set_id:
			return jsonify({'success': False, 'error': 'Failed to save flashcard set'}), 500
		
		# Save individual flashcards
		for idx, card in enumerate(flashcards):
			insert_flashcard(set_id, card['front'], card['back'], idx + 1)
		
		return jsonify({
			'success': True,
			'flashcard_set_id': set_id,
			'flashcards': flashcards
		}), 201
	
	except Exception as e:
		return jsonify({
			'success': False,
			'error': f'Server error: {str(e)}'
		}), 500


@app.route("/get_flashcard_set/<int:set_id>", methods=["GET"])
def get_flashcards(set_id):
	"""
	Retrieve a flashcard set with all its cards.
	
	Returns:
	{
		"success": bool,
		"flashcard_set": {
			"id": int,
			"document_id": int,
			"title": str,
			"num_cards": int,
			"cards": [{"id": int, "front": str, "back": str, "order": int}, ...],
			"created_at": str
		},
		"error": str
	}
	"""
	try:
		flashcard_set = get_flashcard_set(set_id)
		
		if not flashcard_set:
			return jsonify({'success': False, 'error': 'Flashcard set not found'}), 404
		
		return jsonify({
			'success': True,
			'flashcard_set': flashcard_set
		}), 200
	
	except Exception as e:
		return jsonify({
			'success': False,
			'error': f'Server error: {str(e)}'
		}), 500


@app.route("/list_flashcard_sets/<int:document_id>", methods=["GET"])
def list_flashcard_sets(document_id):
	"""
	List all flashcard sets for a document.
	
	Returns:
	{
		"success": bool,
		"flashcard_sets": [
			{
				"id": int,
				"document_id": int,
				"title": str,
				"num_cards": int,
				"created_at": str
			},
			...
		]
	}
	"""
	try:
		flashcard_sets = get_flashcard_sets_by_document(document_id)
		
		return jsonify({
			'success': True,
			'flashcard_sets': flashcard_sets
		}), 200
	
	except Exception as e:
		return jsonify({
			'success': False,
			'error': f'Server error: {str(e)}'
		}), 500


if __name__ == "__main__":
	# TODO: decide whether debug=True should stay on while developing.
	app.run(debug=True)

