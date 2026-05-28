// Explorer page data injector
window.EXPLORE_DATA = (function(){
  // Basic project tree (generated from workspace)
  const tree = [
    "main.py",
    "db.py",
    "query_layer.py",
    "search_layer.py",
    "reader_factory.py",
    "Text_reader.py",
    "Code_reader.py",
    "Pdf_reader.py",
    "templates/index.html",
    "templates/explore.html",
    "static/app.js",
    "static/styles.css",
    "static/explore.css",
    "static/explore.js",
    "schema_flashcards.sql",
    "schema (SQL files)",
    "tests/*",
    "JOURNAL.md",
    "README.md"
  ];

  const endpoints = [
    {path: '/', methods:['GET'], description:'Main UI'},
    {path: '/upload', methods:['POST'], description:'Upload file'},
    {path: '/list-documents', methods:['GET'], description:'List uploaded docs'},
    {path: '/documents/<id>', methods:['DELETE'], description:'Delete document'},
    {path: '/query', methods:['POST'], description:'Ask AI about a document'},
    {path: '/test-db', methods:['GET'], description:'DB connectivity'},
    {path: '/stats', methods:['GET'], description:'API usage stats'},
    {path: '/visualize/word-cloud', methods:['GET'], description:'Word cloud data'},
    {path: '/generate_quiz', methods:['POST'], description:'Generate quiz via AI'},
    {path: '/generate_flashcards', methods:['POST'], description:'Generate flashcards via AI'},
    {path: '/get_quiz/<id>', methods:['GET'], description:'Retrieve quiz'},
    {path: '/get_flashcard_set/<id>', methods:['GET'], description:'Retrieve flashcard set'}
  ];

  const modules = {
    'main.py': ['flask', 'werkzeug.utils', 'reader_factory', 'search_layer', 'query_layer', 'db'],
    'query_layer.py': ['os', 'google.generativeai (optional)', 'dotenv (optional)'],
    'db.py': ['mysql.connector (optional)'],
    'search_layer.py': ['db.get_db_connection', 'datetime'],
    'reader_factory.py': ['Text_reader', 'Code_reader', 'Pdf_reader']
  };

  const db_models = {
    'uploaded_files': ['id','filename','file_type','file_size','raw_text','cleaned_text','word_count','upload_date'],
    'api_usage_logs': ['id','document_id','query_text','input_tokens','output_tokens','total_tokens','created_at'],
    'quizzes': ['id','document_id','quiz_title','num_questions','created_at'],
    'quiz_questions': ['id','quiz_id','question_text','question_type','correct_answer'],
    'flashcard_sets': ['id','document_id','set_title','num_cards','created_at'],
    'flashcards': ['id','flashcard_set_id','front_text','back_text','card_order','created_at']
  };

  const file_summaries = {
    'main.py':'Flask entrypoint: routes for upload, search, query, quizzes, flashcards, and word-cloud visualization.',
    'db.py':'Database access layer: mysql connector wrappers, CRUD for uploaded_files, quizzes, flashcards, and api_usage_logs.',
    'query_layer.py':'AI wrapper around Google Gemini; builds prompts for quiz/flashcards and returns structured results.',
    'search_layer.py':'Search utilities to query uploaded_files by keyword and filters; returns preview snippets.',
    'reader_factory.py':'Factory to construct appropriate reader (text, pdf, code) based on file extension.',
    'Text_reader.py':'Text/Markdown reader that returns raw and cleaned text plus metadata.',
    'Code_reader.py':'Code reader: extracts comments, function names, and variables for indexing.',
    'Pdf_reader.py':'PDF reader using PDF extraction libraries to retrieve text content.',
    'schema_flashcards.sql':'SQL DDL for flashcard tables.'
  };

  return {tree, endpoints, modules, db_models, file_summaries};
})();

// Rendering helpers
function el(tag, attrs={}, inner=''){
  const e = document.createElement(tag);
  Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,v));
  if(typeof inner === 'string') e.innerHTML = inner; else if(inner) e.appendChild(inner);
  return e;
}

function renderTree(){
  const elTree = document.getElementById('tree');
  const pre = el('pre',{}, window.EXPLORE_DATA.tree.join('\n'));
  elTree.appendChild(pre);
}

function renderModules(){
  const md = document.getElementById('modules-list');
  Object.entries(window.EXPLORE_DATA.modules).forEach(([k,v])=>{
    const p = el('div',{}, `<strong>${k}</strong>\n<pre>${v.join(', ')}</pre>`);
    md.appendChild(p);
  });
}

function renderEndpoints(){
  const md = document.getElementById('endpoints-list');
  window.EXPLORE_DATA.endpoints.forEach(e=>{
    const item = el('div',{}, `<strong>${e.path}</strong> <span class="small">${e.methods.join(', ')}</span>\n<pre>${e.description}</pre>`);
    md.appendChild(item);
  });

  // Mermaid sequence: client->main->query_layer->db
  const mermaid = `sequenceDiagram\n    participant Client\n    participant Main as main.py\n    participant AI as query_layer\n    participant DB as db.py\n\n    Client->>Main: POST /query or /generate_quiz\n    Main->>AI: build prompt & call model\n    AI-->>Main: answer/structured response\n    Main->>DB: insert usage logs / persist quiz/flashcards\n    DB-->>Main: OK\n    Main-->>Client: 200 JSON`;
  const mdia = el('div',{}, `<div class="mermaid">${mermaid}</div>`);
  const diag = document.getElementById('endpoints-diagram'); diag.appendChild(mdia);
}

function renderDB(){
  const md = document.getElementById('db-list');
  Object.entries(window.EXPLORE_DATA.db_models).forEach(([tbl,cols])=>{
    const item = el('div',{}, `<strong>${tbl}</strong>\n<pre>${cols.join(', ')}</pre>`);
    md.appendChild(item);
  });

  const dd = ['erDiagram', ...Object.keys(window.EXPLORE_DATA.db_models).map(t=>`  ${t} {\n    ${window.EXPLORE_DATA.db_models[t].slice(0,3).map(c=>"string "+c).join('\n    ')}\n  }`)].join('\n');
  const mer = `erDiagram\n${Object.keys(window.EXPLORE_DATA.db_models).map(t=>`${t} }|..|| uploaded_files : references`).join('\n')}`;
  // Simpler: create a basic mermaid flow for key tables
  const mermaid = `graph TD\n    UF[uploaded_files] --> AU[api_usage_logs]\n    UF --> QZ[quizzes] --> QQ[quiz_questions]\n    UF --> FS[flashcard_sets] --> FC[flashcards]`;
  const mdia = el('div',{}, `<div class="mermaid">${mermaid}</div>`);
  const diag = document.getElementById('db-diagram'); diag.appendChild(mdia);
}

function renderSummaries(){
  const md = document.getElementById('summaries');
  Object.entries(window.EXPLORE_DATA.file_summaries).forEach(([f,s])=>{
    const card = el('div',{}, `<strong>${f}</strong>\n<pre>${s}</pre>`);
    md.appendChild(card);
  });
}

function renderLinks(){
  const graph = `graph LR\n    main.py --> query_layer.py\n    main.py --> db.py\n    main.py --> search_layer.py\n    query_layer.py --> google_generativeai\n    db.py --> mysql_connector`;
  const mdia = el('div',{}, `<div class="mermaid">${graph}</div>`);
  document.getElementById('links-graph').appendChild(mdia);
}

// Wait for mermaid to be ready
document.addEventListener('DOMContentLoaded',()=>{
  renderTree(); renderModules(); renderEndpoints(); renderDB(); renderSummaries(); renderLinks();
  if(window.mermaid){ mermaid.initialize({startOnLoad:true,theme:'dark'}); }
});
