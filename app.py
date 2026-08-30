from flask import Flask, render_template, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

app = Flask(__name__)

# Example FAQ knowledge base. Replace/add questions for your chosen topic.
FAQS = [
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

questions = [item["question"] for item in FAQS]
vectorizer = TfidfVectorizer(lowercase=True, stop_words="english")
faq_matrix = vectorizer.fit_transform(questions)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    user_question = (data.get("question") or "").strip()

    if not user_question:
        return jsonify({"error": "Please type a question."}), 400

    user_vector = vectorizer.transform([user_question])
    scores = cosine_similarity(user_vector, faq_matrix)[0]

    best_index = scores.argmax()
    best_score = float(scores[best_index])

    # If similarity is too low, do not pretend to know the answer.
    if best_score < 0.15:
        return jsonify({
            "answer": "Sorry, I could not find a good match in my FAQ knowledge base. Please ask another question.",
            "score": round(best_score, 3)
        })

    return jsonify({
        "answer": FAQS[best_index]["answer"],
        "matched_question": FAQS[best_index]["question"],
        "score": round(best_score, 3)
    })

if __name__ == "__main__":
    # Production-ready: debug is disabled by default. Use the FLASK_DEBUG or DEBUG env var to enable for development.
    debug_env = os.getenv("FLASK_DEBUG", os.getenv("DEBUG", "0"))
    debug = str(debug_env).lower() in ("1", "true", "yes")

    # Listen on all interfaces so Docker and remote hosts can connect during development.
    app.run(host="0.0.0.0", debug=debug)
