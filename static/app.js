const ACTIVE_STORAGE_KEY = 'corpusForgeActiveDocuments';

const uploadForm = document.getElementById('uploadForm');
const fileInput = document.getElementById('fileInput');
const uploadStatus = document.getElementById('uploadStatus');
const documentsList = document.getElementById('documentsList');
const activeDocuments = document.getElementById('activeDocuments');
const activeCount = document.getElementById('activeCount');
const selectionHint = document.getElementById('selectionHint');
const refreshDocs = document.getElementById('refreshDocs');
const queryForm = document.getElementById('queryForm');
const queryDocument = document.getElementById('queryDocument');
const queryInput = document.getElementById('queryInput');
const queryStatus = document.getElementById('queryStatus');
const answerBox = document.getElementById('answerBox');
const answerContent = document.getElementById('answerContent');
const tokenInfo = document.getElementById('tokenInfo');
const refreshStats = document.getElementById('refreshStats');
const totalRequests = document.getElementById('totalRequests');
const totalTokens = document.getElementById('totalTokens');
const inputTokens = document.getElementById('inputTokens');
const outputTokens = document.getElementById('outputTokens');

let documentsCache = [];

// Load and display API statistics
async function loadStats() {
	try {
		const response = await fetch('/stats');
		const data = await response.json();

		if (response.ok && data.success) {
			totalRequests.textContent = data.total_api_requests || 0;
			totalTokens.textContent = (data.total_tokens_overall || 0).toLocaleString();
			inputTokens.textContent = (data.total_input_tokens || 0).toLocaleString();
			outputTokens.textContent = (data.total_output_tokens || 0).toLocaleString();
		}
	} catch (error) {
		console.error('Failed to load stats:', error);
	}
}

function getActiveIds() {
	try {
		return JSON.parse(localStorage.getItem(ACTIVE_STORAGE_KEY) || '[]').map(String);
	} catch (error) {
		return [];
	}
}

function setActiveIds(ids) {
	localStorage.setItem(ACTIVE_STORAGE_KEY, JSON.stringify(ids.map(String)));
}

function formatBytes(bytes) {
	if (!bytes && bytes !== 0) return '—';
	const units = ['B', 'KB', 'MB', 'GB'];
	let value = Number(bytes);
	let unitIndex = 0;
	while (value >= 1024 && unitIndex < units.length - 1) {
		value /= 1024;
		unitIndex += 1;
	}
	return `${value.toFixed(value < 10 && unitIndex > 0 ? 1 : 0)} ${units[unitIndex]}`;
}

function setStatus(element, message, type = '') {
	element.textContent = message;
	element.className = `status ${type}`.trim();
}

function syncActiveUI() {
	const activeIds = getActiveIds();
	activeCount.textContent = activeIds.length;
	selectionHint.textContent = activeIds.length
		? `${activeIds.length} document${activeIds.length === 1 ? '' : 's'} selected.`
		: 'Select documents from the list below.';

	activeDocuments.innerHTML = '';
	const activeDocs = documentsCache.filter(doc => activeIds.includes(String(doc.file_id)));

	if (!activeDocs.length) {
		activeDocuments.innerHTML = '<p class="muted">No active documents selected yet.</p>';
	} else {
		activeDocs.forEach(doc => {
			const tag = document.createElement('div');
			tag.className = 'chip';
			tag.textContent = `${doc.file_name} (#${doc.file_id})`;
			activeDocuments.appendChild(tag);
		});
	}

	queryDocument.innerHTML = '<option value="">Select an active document</option>';
	activeDocs.forEach(doc => {
		const option = document.createElement('option');
		option.value = doc.file_id;
		option.textContent = `${doc.file_name} (#${doc.file_id})`;
		queryDocument.appendChild(option);
	});

	if (queryDocument.options.length === 1) {
		queryDocument.disabled = true;
	} else {
		queryDocument.disabled = false;
	}
}

function renderDocuments(documents) {
	documentsList.innerHTML = '';
	documentsCache = documents;

	if (!documents.length) {
		documentsList.innerHTML = '<p class="muted">No documents found yet. Upload one to get started.</p>';
		syncActiveUI();
		return;
	}

	const activeIds = new Set(getActiveIds());

	documents.forEach(doc => {
		const isActive = activeIds.has(String(doc.file_id));
		const card = document.createElement('article');
		card.className = 'doc-card';
		card.innerHTML = `
			<div class="doc-top">
				<div>
					<h3 class="doc-title">${doc.file_name}</h3>
					<div class="doc-meta">
						<span>ID: ${doc.file_id}</span>
						<span>Type: ${doc.file_type || '—'}</span>
						<span>Size: ${formatBytes(doc.file_size)}</span>
						<span>Words: ${doc.word_count ?? '—'}</span>
						<span>Uploaded: ${doc.upload_date || '—'}</span>
					</div>
				</div>
				<span class="chip">${isActive ? 'Active' : 'Inactive'}</span>
			</div>
			<p class="muted">${doc.cleaned_text_preview || 'No preview available.'}</p>
			<div class="doc-actions">
				<button type="button" class="secondary" data-action="toggle-active" data-id="${doc.file_id}">${isActive ? 'Unselect' : 'Select active'}</button>
				<button type="button" class="danger" data-action="delete" data-id="${doc.file_id}">Delete</button>
			</div>
		`;
		documentsList.appendChild(card);
	});

	syncActiveUI();
}

async function loadDocuments() {
	try {
		setStatus(uploadStatus, 'Loading documents...');
		const response = await fetch('/list-documents?limit=200');
		const data = await response.json();

		if (!response.ok || !data.success) {
			throw new Error(data.error || 'Failed to load documents');
		}

		renderDocuments(data.results || []);
		setStatus(uploadStatus, `${(data.results || []).length} document(s) loaded.`, 'success');
	} catch (error) {
		setStatus(uploadStatus, error.message, 'error');
		documentsList.innerHTML = `<p class="muted">${error.message}</p>`;
	}
}

uploadForm.addEventListener('submit', async event => {
	event.preventDefault();
	const file = fileInput.files[0];

	if (!file) {
		setStatus(uploadStatus, 'Please choose a file first.', 'error');
		return;
	}

	const formData = new FormData();
	formData.append('file', file);

	try {
		setStatus(uploadStatus, 'Uploading file...');
		const response = await fetch('/upload', {
			method: 'POST',
			body: formData
		});
		const data = await response.json();

		if (!response.ok || !data.success) {
			throw new Error(data.error || 'Upload failed');
		}

		uploadForm.reset();
		setStatus(uploadStatus, `Uploaded ${data.result?.file_name || file.name} successfully.`, 'success');
		await loadDocuments();
	} catch (error) {
		setStatus(uploadStatus, error.message, 'error');
	}
});

refreshDocs.addEventListener('click', loadDocuments);

documentsList.addEventListener('click', async event => {
	const button = event.target.closest('button[data-action]');
	if (!button) return;

	const documentId = button.dataset.id;
	const action = button.dataset.action;
	const activeIds = getActiveIds();

	if (action === 'toggle-active') {
		const updated = activeIds.includes(documentId)
			? activeIds.filter(id => id !== documentId)
			: [...activeIds, documentId];
		setActiveIds(updated);
		syncActiveUI();
		renderDocuments(documentsCache);
		return;
	}

	if (action === 'delete') {
		const confirmed = window.confirm('Delete this document permanently?');
		if (!confirmed) return;

		try {
			setStatus(uploadStatus, 'Deleting document...');
			const response = await fetch(`/documents/${documentId}`, { method: 'DELETE' });
			const data = await response.json();

			if (!response.ok || !data.success) {
				throw new Error(data.error || 'Delete failed');
			}

			setActiveIds(activeIds.filter(id => id !== documentId));
			setStatus(uploadStatus, `Document #${documentId} deleted.`, 'success');
			await loadDocuments();
		} catch (error) {
			setStatus(uploadStatus, error.message, 'error');
		}
	}
});

queryForm.addEventListener('submit', async event => {
	event.preventDefault();
	const documentId = queryDocument.value;
	const question = queryInput.value.trim();

	if (!documentId) {
		setStatus(queryStatus, 'Select an active document first.', 'error');
		return;
	}

	if (!question) {
		setStatus(queryStatus, 'Type a question first.', 'error');
		return;
	}

	try {
		setStatus(queryStatus, 'Waiting for Gemini...');
		answerBox.classList.add('hidden');
		tokenInfo.classList.add('hidden');

		// Extract steering parameters from dropdowns
		const steeringParams = {
			audience_level: document.getElementById('audienceLevel').value,
			tone: document.getElementById('tone').value,
			output_format: document.getElementById('outputFormat').value,
			creativity: document.getElementById('creativity').value
		};

		const response = await fetch('/query', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				query: question,
				document_id: Number(documentId),
				steering: steeringParams
			})
		});
		const data = await response.json();

		if (!response.ok || !data.success) {
			throw new Error(data.error || 'AI query failed');
		}

		// Display answer
		answerContent.textContent = data.answer;
		answerBox.classList.remove('hidden');

		// Display token usage if available
		if (data.input_token_count !== undefined || data.output_token_count !== undefined) {
			const inTokens = data.input_token_count || 0;
			const outTokens = data.output_token_count || 0;
			const totalTokensUsed = inTokens + outTokens;

			tokenInfo.innerHTML = `
				<div class="token-stat">
					<span class="token-stat-label">Input Tokens:</span>
					<span>${inTokens.toLocaleString()}</span>
				</div>
				<div class="token-stat">
					<span class="token-stat-label">Output Tokens:</span>
					<span>${outTokens.toLocaleString()}</span>
				</div>
				<div class="token-stat">
					<span class="token-stat-label">Total Tokens:</span>
					<span>${totalTokensUsed.toLocaleString()}</span>
				</div>
			`;
			tokenInfo.classList.remove('hidden');

			// Refresh stats after query
			await loadStats();
		}

		setStatus(queryStatus, 'Answer ready.', 'success');
	} catch (error) {
		setStatus(queryStatus, error.message, 'error');
	}
});

refreshStats.addEventListener('click', loadStats);

// Quiz functionality
const quizForm = document.getElementById('quizForm');
const quizDocument = document.getElementById('quizDocument');
const numQuestions = document.getElementById('numQuestions');
const quizStatus = document.getElementById('quizStatus');
const quizBox = document.getElementById('quizBox');
const quizTitle = document.getElementById('quizTitle');
const quizQuestionsContainer = document.getElementById('quizQuestionsContainer');
const quizSubmitBtn = document.getElementById('quizSubmitBtn');
const quizResults = document.getElementById('quizResults');

let currentQuiz = null;

quizForm.addEventListener('submit', async event => {
	event.preventDefault();
	const documentId = quizDocument.value;
	const questionCount = parseInt(numQuestions.value);

	if (!documentId) {
		setStatus(quizStatus, 'Select a document first.', 'error');
		return;
	}

	try {
		setStatus(quizStatus, 'Generating quiz...');
		quizBox.classList.add('hidden');

		const response = await fetch('/generate_quiz', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				document_id: Number(documentId),
				num_questions: questionCount
			})
		});
		const data = await response.json();

		if (!response.ok || !data.success) {
			throw new Error(data.error || 'Quiz generation failed');
		}

		currentQuiz = {
			id: data.quiz_id,
			questions: data.questions
		};

		displayQuiz(data.questions);
		quizBox.classList.remove('hidden');
		setStatus(quizStatus, 'Quiz ready!', 'success');
	} catch (error) {
		setStatus(quizStatus, error.message, 'error');
	}
});

function displayQuiz(questions) {
	quizTitle.textContent = `Quiz - ${questions.length} Questions`;
	quizQuestionsContainer.innerHTML = '';

	questions.forEach((q, idx) => {
		const questionDiv = document.createElement('div');
		questionDiv.className = 'quiz-question';

		const questionText = document.createElement('div');
		questionText.className = 'quiz-question-text';
		questionText.textContent = `${idx + 1}. ${q.question}`;
		questionDiv.appendChild(questionText);

		// Create options
		const options = q.options || {};
		['A', 'B', 'C', 'D'].forEach(optionKey => {
			if (options[optionKey]) {
				const optionDiv = document.createElement('div');
				optionDiv.className = 'quiz-option';

				const radioId = `q${idx}_${optionKey}`;
				const radio = document.createElement('input');
				radio.type = 'radio';
				radio.id = radioId;
				radio.name = `question_${idx}`;
				radio.value = optionKey;

				const label = document.createElement('label');
				label.htmlFor = radioId;
				label.textContent = `${optionKey}) ${options[optionKey]}`;

				optionDiv.appendChild(radio);
				optionDiv.appendChild(label);
				questionDiv.appendChild(optionDiv);
			}
		});

		quizQuestionsContainer.appendChild(questionDiv);
	});

	quizResults.classList.add('hidden');
}

quizSubmitBtn.addEventListener('click', async () => {
	const answers = {};
	const formElements = quizQuestionsContainer.querySelectorAll('input[type="radio"]:checked');

	formElements.forEach(element => {
		const questionIndex = element.name.split('_')[1];
		answers[questionIndex] = element.value;
	});

	// Score the quiz
	let score = 0;
	const results = [];

	currentQuiz.questions.forEach((q, idx) => {
		const userAnswer = answers[idx];
		const isCorrect = userAnswer === q.correct_answer;
		if (isCorrect) score++;

		results.push({
			question: q.question,
			userAnswer: userAnswer || 'Not answered',
			correctAnswer: q.correct_answer,
			isCorrect: isCorrect
		});
	});

	// Display results
	displayResults(results, score, currentQuiz.questions.length);
});

function displayResults(results, score, total) {
	quizResults.innerHTML = `<h4>Results: ${score}/${total} (${Math.round((score/total)*100)}%)</h4>`;

	results.forEach(result => {
		const resultDiv = document.createElement('div');
		resultDiv.className = `quiz-result-item ${result.isCorrect ? 'quiz-result-correct' : 'quiz-result-incorrect'}`;
		
		const statusText = result.isCorrect ? '✓ Correct' : '✗ Incorrect';
		resultDiv.innerHTML = `
			<strong>${result.question}</strong><br/>
			${statusText}<br/>
			Your answer: ${result.userAnswer} | Correct: ${result.correctAnswer}
		`;

		quizResults.appendChild(resultDiv);
	});

	quizResults.classList.remove('hidden');
	window.scrollTo(0, quizResults.offsetTop - 100);
}

// Update quiz document select when documents load
function syncQuizDocumentSelect() {
	const activeIds = getActiveIds();
	const quizDocSelect = document.getElementById('quizDocument');
	quizDocSelect.innerHTML = '<option value="">Select a document</option>';
	
	const activeDocs = documentsCache.filter(doc => activeIds.includes(String(doc.file_id)));
	activeDocs.forEach(doc => {
		const option = document.createElement('option');
		option.value = doc.file_id;
		option.textContent = `${doc.file_name} (#${doc.file_id})`;
		quizDocSelect.appendChild(option);
	});
}

// ─────────────────────────────────────────
// FLASHCARD FUNCTIONALITY
// ─────────────────────────────────────────

const flashcardForm = document.getElementById('flashcardForm');
const flashcardDocument = document.getElementById('flashcardDocument');
const numCards = document.getElementById('numCards');
const flashcardTitle = document.getElementById('flashcardTitle');
const flashcardStatus = document.getElementById('flashcardStatus');
const flashcardBox = document.getElementById('flashcardBox');
const flashcardSetTitle = document.getElementById('flashcardSetTitle');
const flashcardListContainer = document.getElementById('flashcardListContainer');
const flashcardStudyMode = document.getElementById('flashcardStudyMode');

let currentFlashcards = [];
let currentCardIndex = 0;

flashcardForm.addEventListener('submit', async (e) => {
	e.preventDefault();
	flashcardStatus.textContent = 'Generating flashcards...';
	flashcardStatus.className = 'status loading';

	const docId = flashcardDocument.value;
	const cardCount = parseInt(numCards.value) || 10;
	const setTitle = flashcardTitle.value || `Flashcard Set #${docId}`;

	try {
		const response = await fetch('/generate_flashcards', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				document_id: parseInt(docId),
				num_cards: cardCount,
				set_title: setTitle
			})
		});

		const data = await response.json();

		if (!response.ok || !data.success) {
			throw new Error(data.error || 'Failed to generate flashcards');
		}

		currentFlashcards = data.flashcards;
		currentCardIndex = 0;

		flashcardSetTitle.textContent = setTitle;
		displayFlashcardList(data.flashcards);
		displayFlashcard(0);
		
		flashcardBox.classList.remove('hidden');
		flashcardStatus.textContent = 'Flashcards generated!';
		flashcardStatus.className = 'status success';
	} catch (error) {
		flashcardStatus.textContent = `Error: ${error.message}`;
		flashcardStatus.className = 'status error';
		console.error(error);
	}
});

function displayFlashcardList(flashcards) {
	flashcardListContainer.innerHTML = '';
	
	flashcards.forEach((card, idx) => {
		const cardPreview = document.createElement('div');
		cardPreview.className = 'flashcard-item-preview';
		cardPreview.innerHTML = `
			<div class="flashcard-item-front">${card.front}</div>
			<div style="font-size: 0.85rem; opacity: 0.9; margin-top: 0.5rem;">Card ${idx + 1}/${flashcards.length}</div>
		`;
		cardPreview.addEventListener('click', () => {
			currentCardIndex = idx;
			displayFlashcard(idx);
		});
		flashcardListContainer.appendChild(cardPreview);
	});
}

function displayFlashcard(index) {
	if (index < 0 || index >= currentFlashcards.length) return;

	currentCardIndex = index;
	const card = currentFlashcards[index];

	// Reset flip state
	const flipContainer = document.getElementById('flashcardFlipContainer');
	flipContainer.classList.remove('flipped');

	// Update content
	document.getElementById('flashcardFrontText').textContent = card.front;
	document.getElementById('flashcardBackText').textContent = card.back;
	document.getElementById('cardProgress').textContent = `${index + 1} / ${currentFlashcards.length}`;

	// Show study mode
	flashcardStudyMode.classList.remove('hidden');

	// Update button states
	document.getElementById('prevCardBtn').disabled = index === 0;
	document.getElementById('nextCardBtn').disabled = index === currentFlashcards.length - 1;
}

// Flip card on click
document.addEventListener('click', (e) => {
	const flipContainer = document.getElementById('flashcardFlipContainer');
	if (flipContainer && flipContainer.contains(e.target) && !e.target.classList.contains('btn')) {
		flipContainer.classList.toggle('flipped');
	}
});

// Navigation buttons
document.getElementById('prevCardBtn')?.addEventListener('click', () => {
	if (currentCardIndex > 0) {
		displayFlashcard(currentCardIndex - 1);
	}
});

document.getElementById('nextCardBtn')?.addEventListener('click', () => {
	if (currentCardIndex < currentFlashcards.length - 1) {
		displayFlashcard(currentCardIndex + 1);
	}
});

// Sync flashcard document select with main document list
function syncFlashcardDocumentSelect() {
	const flashcardDocSelect = document.getElementById('flashcardDocument');
	flashcardDocSelect.innerHTML = '<option value="">Select a document</option>';
	
	documentsCache.forEach(doc => {
		const option = document.createElement('option');
		option.value = doc.file_id;
		option.textContent = `${doc.file_name} (#${doc.file_id})`;
		flashcardDocSelect.appendChild(option);
	});
}

document.addEventListener('DOMContentLoaded', async () => {
	await loadDocuments();
	await loadStats();
	syncQuizDocumentSelect();
	syncFlashcardDocumentSelect();
	createVizPanel();
	syncVizDocumentSelect();
});


// -----------------------------
// Word Cloud Visualization
// -----------------------------
function createVizPanel() {
	const grid = document.querySelector('.grid');
	if (!grid) return;

	// Avoid duplicate panel
	if (document.getElementById('vizPanel')) return;

	const panel = document.createElement('section');
	panel.className = 'panel';
	panel.id = 'vizPanel';
	panel.innerHTML = `
		<div class="panel-header">
			<h2>Visualize: Word Cloud</h2>
			<p>Generate a simple word cloud from a selected document's cleaned text.</p>
		</div>
		<div class="viz-controls">
			<select id="vizDocumentSelect"><option value="">Select a document</option></select>
			<label for="vizTopN">Top N:</label>
			<input id="vizTopN" type="number" value="50" min="5" max="500" style="width:70px" />
			<button id="vizGenerateBtn" class="primary">Generate Cloud</button>
		</div>
		<div id="vizStatus" class="status"></div>
		<div id="wordCloudContainer" class="word-cloud-container"></div>
		<div id="wordInfo" class="word-info hidden"></div>
	`;

	// Insert near the end of the grid
	grid.appendChild(panel);

	// Wire up controls
	document.getElementById('vizGenerateBtn').addEventListener('click', async () => {
		const docId = document.getElementById('vizDocumentSelect').value;
		const topN = parseInt(document.getElementById('vizTopN').value) || 50;
		if (!docId) {
			setStatus(document.getElementById('vizStatus'), 'Select a document first.', 'error');
			return;
		}

		setStatus(document.getElementById('vizStatus'), 'Generating word cloud...');
		try {
			const resp = await fetch(`/visualize/word-cloud?document_id=${encodeURIComponent(docId)}&top_n=${topN}`);
			const data = await resp.json();
			if (!resp.ok || !data.success) throw new Error(data.error || 'Visualization failed');
			renderWordCloud(data.word_counts || []);
			setStatus(document.getElementById('vizStatus'), `Top ${data.word_counts.length} words shown.`, 'success');
		} catch (err) {
			setStatus(document.getElementById('vizStatus'), err.message, 'error');
			console.error(err);
		}
	});

	// Click-to-copy or info panel
	document.getElementById('wordCloudContainer').addEventListener('click', (e) => {
		const target = e.target.closest('.wc-word');
		if (!target) return;
		const word = target.dataset.word;
		const count = target.dataset.count;
		// show quick info and copy to clipboard
		const info = document.getElementById('wordInfo');
		info.innerHTML = `<strong>${word}</strong> — ${count} occurrences — <button id="copyWordBtn">Copy</button>`;
		info.classList.remove('hidden');
		const copyBtn = document.getElementById('copyWordBtn');
		copyBtn.addEventListener('click', () => {
			navigator.clipboard?.writeText(word).then(() => {
				setStatus(document.getElementById('vizStatus'), `Copied "${word}" to clipboard.`, 'success');
			}).catch(() => setStatus(document.getElementById('vizStatus'), 'Copy failed', 'error'));
		});
	});
}

function syncVizDocumentSelect() {
	const select = document.getElementById('vizDocumentSelect');
	if (!select) return;
	select.innerHTML = '<option value="">Select a document</option>';

	// Prefer active documents
	const activeIds = getActiveIds();
	const activeDocs = documentsCache.filter(doc => activeIds.includes(String(doc.file_id)));
	const docsToShow = activeDocs.length ? activeDocs : documentsCache;

	docsToShow.forEach(doc => {
		const opt = document.createElement('option');
		opt.value = doc.file_id;
		opt.textContent = `${doc.file_name} (#${doc.file_id})`;
		select.appendChild(opt);
	});

	// If no active document exists in storage, auto-select the first available document
	// to improve discoverability for new users. This will also update the global active list.
	const currentlyActive = getActiveIds();
	if ((!currentlyActive || currentlyActive.length === 0) && docsToShow.length > 0) {
		const firstId = String(docsToShow[0].file_id);
		setActiveIds([firstId]);
		syncActiveUI();
		// select the first option
		select.value = firstId;
	}
}

function renderWordCloud(wordCounts) {
	const container = document.getElementById('wordCloudContainer');
	container.innerHTML = '';
	if (!wordCounts.length) {
		container.innerHTML = '<p class="muted">No words to display.</p>';
		return;
	}

	// Determine font-size scale
	const counts = wordCounts.map(w => w.count);
	const max = Math.max(...counts);
	const min = Math.min(...counts);

	wordCounts.forEach(({word, count}) => {
		const span = document.createElement('span');
		span.className = 'wc-word';
		span.textContent = word;
		span.dataset.word = word;
		span.dataset.count = String(count);

		// Normalize font-size between 14px and 48px
		const size = min === max ? 20 : Math.round(14 + (count - min) / (max - min) * (48 - 14));
		span.style.fontSize = `${size}px`;
		span.style.margin = '6px';
		span.style.display = 'inline-block';
		span.style.cursor = 'pointer';
		span.title = `${count} occurrences`;

		container.appendChild(span);
	});
}

