"""
Flask entrypoint for Corpus Forge.

This file is intentionally left as a TODO scaffold so you can implement the
POST /upload endpoint step by step.
"""

import os
import tempfile

from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename

from Code_reader import CodeReader
from Pdf_reader import PdfReader
from Text_reader import TextReader


app = Flask(__name__)


# TODO: add upload configuration here.
# - choose an upload folder
# - define allowed extensions
# - decide whether temporary files should be deleted after processing

UPLOAD_FOLDER = tempfile.gettempdir()

ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf", ".py", ".js"}

# TODO: add a small helper that returns the file extension in lowercase.
# This will help you decide which reader to call.

def get_file_extension(filename):
		"""Return the extension including the leading dot, lowercased.

		Examples:
			'doc.md' -> '.md'
			'archive' -> ''
		"""
		return os.path.splitext(filename)[1].lower()


# TODO: add a small helper that maps extensions to readers.
# Suggested mapping:
# - .txt / .md -> TextReader
# - .pdf -> PdfReader
# - .py / .js -> CodeReader
def get_reader_for_extension(extension):
	"""Return the Reader class for a given extension (or None).

	Note: returns the class (not an instance) so the caller can
	instantiate it with the temporary filepath.
	"""
	if extension in {".txt", ".md"}:
		return TextReader
	if extension == ".pdf":
		return PdfReader
	if extension in {".py", ".js"}:
		return CodeReader
	return None



@app.route("/upload", methods=["POST"])
def upload_file():
	"""
	Handle an uploaded file and route it to the correct reader.

	TODO steps:
	1. Check whether 'file' exists in request.files.
	2. Reject empty filenames.
	3. Inspect the extension.
	4. Reject unsupported file types.
	5. Save the upload temporarily if your readers need a filepath.
	6. Call the appropriate reader.
	7. Return the reader result as JSON.
	8. Return clear JSON errors for invalid requests.
	"""
	# 1) Basic request validation
	if 'file' not in request.files:
		return jsonify({'success': False, 'error': 'No file part in the request'}), 400

	file = request.files['file']
	filename = secure_filename(file.filename or "")
	if filename == "":
		return jsonify({'success': False, 'error': 'No selected file'}), 400

	# 2) Determine extension and reader
	ext = get_file_extension(filename)
	if not ext or ext not in ALLOWED_EXTENSIONS:
		return jsonify({'success': False, 'error': f'Unsupported file type: {ext}'}), 400

	reader_cls = get_reader_for_extension(ext)
	if reader_cls is None:
		return jsonify({'success': False, 'error': 'No reader available for this file type'}), 400

	# 3) Save upload to a temporary file (reader implementations expect a filepath)
	temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext, dir=UPLOAD_FOLDER)
	temp_file.close()
	try:
		file.save(temp_file.name)

		# 4) Instantiate reader and process
		reader = reader_cls(temp_file.name)
		result = reader.process()

		# 5) If reader reported an error, surface it with 422 (unprocessable entity)
		if isinstance(result, dict) and result.get('error'):
			return jsonify({'success': False, 'error': result.get('error')}), 422

		# 6) Normal success response
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


# TODO: add error handlers for common upload problems.
# Examples:
# - missing file in request
# - unsupported extension
# - file read failure from a reader


if __name__ == "__main__":
	# TODO: decide whether debug=True should stay on while developing.
	app.run(debug=True)
