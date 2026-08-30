from flask import Flask, render_template, request, jsonify, g, abort
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3
import os

# Configuration
DB_PATH = os.path.join(os.path.dirname(__file__), 'faqs.db')

app = Flask(__name__)
app.config['DATABASE'] = DB_PATH

# Default FAQS to populate the DB on first run
DEFAULT_FAQS = [
    {
        "question": "What is CodeAlpha?",
        "answer": "CodeAlpha is a software development and internship platform that provides practical project experience."
    },
    {
        "question": "How do I complete my internship tasks?",
        "answer": "Complete the required tasks, upload your source code to GitHub, and submit the project details using the provided submission form."
    },
    {
        "question": "How do I create a GitHub repository?",
        "answer": "Sign in to GitHub, click New repository, enter a repository name, choose the visibility, and create the repository."
    },
    {
        "question": "What should I include in my project?",
        "answer": "Include working source code, a README file explaining the project, setup instructions, and any required screenshots or demonstration."
    },
    {
        "question": "How can I submit my internship project?",
        "answer": "Use the submission form shared by your internship group and follow all instructions in that form."
    },
    {
        "question": "Can I use Python for AI projects?",
        "answer": "Yes. Python is widely used for AI and machine learning because it has libraries such as scikit-learn, NumPy, pandas, and many others."
    },
    {
        "question": "What is cosine similarity?",
        "answer": "Cosine similarity measures how similar two text vectors are. Here it is used to find the FAQ question most similar to the user's question."
    }
]

# Globals used by the matching logic. Rebuilt when the DB changes.
vectorizer = None
faq_matrix = None
questions = []
faqs_cache = []

# --- Database helpers ---

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    """Create the faqs table if it doesn't exist and populate with defaults when empty."""
    os.makedirs(os.path.dirname(app.config['DATABASE']) or '.', exist_ok=True)
    db = sqlite3.connect(app.config['DATABASE'])
    try:
        cur = db.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS faqs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL
            )
        ''')
        db.commit()

        cur.execute('SELECT COUNT(1) as cnt FROM faqs')
        cnt = cur.fetchone()[0]
        if cnt == 0:
            for item in DEFAULT_FAQS:
                cur.execute('INSERT INTO faqs (question, answer) VALUES (?, ?)', (item['question'], item['answer']))
            db.commit()
    finally:
        db.close()


def load_faqs_from_db():
    """Load FAQs from the database into memory and return a list of dicts."""
    db = get_db()
    cur = db.execute('SELECT id, question, answer FROM faqs ORDER BY id')
    rows = cur.fetchall()
    items = [{'id': r['id'], 'question': r['question'], 'answer': r['answer']} for r in rows]
    return items


def rebuild_vectorizer():
    """Rebuild the TF-IDF vectorizer and matrix from the current DB faqs."""
    global vectorizer, faq_matrix, questions, faqs_cache
    faqs_cache = load_faqs_from_db()
    questions = [f['question'] for f in faqs_cache]
    if len(questions) == 0:
        vectorizer = None
        faq_matrix = None
        return

    vectorizer = TfidfVectorizer(lowercase=True, stop_words='english')
    faq_matrix = vectorizer.fit_transform(questions)


# Initialize DB and vectorizer on startup
init_db()
with app.app_context():
    rebuild_vectorizer()


# --- Routes ---

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/admin')
def admin():
    return render_template('admin.html')


@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    user_question = (data.get('question') or '').strip()

    if not user_question:
        return jsonify({'error': 'Please type a question.'}), 400

    if vectorizer is None or faq_matrix is None:
        return jsonify({'error': 'No FAQs available to answer questions.'}), 500

    user_vector = vectorizer.transform([user_question])
    scores = cosine_similarity(user_vector, faq_matrix)[0]

    best_index = int(scores.argmax())
    best_score = float(scores[best_index])

    if best_score < 0.15:
        return jsonify({
            'answer': 'Sorry, I could not find a good match in my FAQ knowledge base. Please ask another question.',
            'score': round(best_score, 3)
        })

    matched = faqs_cache[best_index]
    return jsonify({
        'answer': matched['answer'],
        'matched_question': matched['question'],
        'score': round(best_score, 3)
    })


# --- Admin API for managing FAQs ---
@app.route('/faqs', methods=['GET'])
def list_faqs():
    items = load_faqs_from_db()
    return jsonify(items)


@app.route('/faqs', methods=['POST'])
def create_faq():
    data = request.get_json() or {}
    question = (data.get('question') or '').strip()
    answer = (data.get('answer') or '').strip()
    if not question or not answer:
        return jsonify({'error': 'Both question and answer are required.'}), 400

    db = get_db()
    cur = db.execute('INSERT INTO faqs (question, answer) VALUES (?, ?)', (question, answer))
    db.commit()
    faq_id = cur.lastrowid
    rebuild_vectorizer()
    return jsonify({'id': faq_id, 'question': question, 'answer': answer}), 201


@app.route('/faqs/<int:faq_id>', methods=['PUT'])
def update_faq(faq_id):
    data = request.get_json() or {}
    question = data.get('question')
    answer = data.get('answer')
    if question is None and answer is None:
        return jsonify({'error': 'question or answer required.'}), 400

    db = get_db()
    cur = db.execute('SELECT id FROM faqs WHERE id = ?', (faq_id,))
    if cur.fetchone() is None:
        return jsonify({'error': 'FAQ not found.'}), 404

    if question is not None:
        db.execute('UPDATE faqs SET question = ? WHERE id = ?', (question, faq_id))
    if answer is not None:
        db.execute('UPDATE faqs SET answer = ? WHERE id = ?', (answer, faq_id))
    db.commit()
    rebuild_vectorizer()
    return jsonify({'id': faq_id, 'question': question, 'answer': answer})


@app.route('/faqs/<int:faq_id>', methods=['DELETE'])
def delete_faq(faq_id):
    db = get_db()
    cur = db.execute('SELECT id FROM faqs WHERE id = ?', (faq_id,))
    if cur.fetchone() is None:
        return jsonify({'error': 'FAQ not found.'}), 404
    db.execute('DELETE FROM faqs WHERE id = ?', (faq_id,))
    db.commit()
    rebuild_vectorizer()
    return jsonify({'status': 'deleted'})


if __name__ == '__main__':
    import os
    debug_env = os.getenv('FLASK_DEBUG', os.getenv('DEBUG', '0'))
    debug = str(debug_env).lower() in ('1', 'true', 'yes')
    app.run(host='0.0.0.0', debug=debug)
