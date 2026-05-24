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

let documentsCache = [];

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

		const response = await fetch('/query', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ query: question, document_id: Number(documentId) })
		});
		const data = await response.json();

		if (!response.ok || !data.success) {
			throw new Error(data.error || 'AI query failed');
		}

		answerBox.textContent = data.answer;
		answerBox.classList.remove('hidden');
		setStatus(queryStatus, 'Answer ready.', 'success');
	} catch (error) {
		setStatus(queryStatus, error.message, 'error');
	}
});

document.addEventListener('DOMContentLoaded', async () => {
	await loadDocuments();
});