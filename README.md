# CodeAlpha Task 2 - FAQ Chatbot

This repository contains a small FAQ chatbot built with Flask and scikit-learn. It converts a set of FAQ questions into TF-IDF vectors and uses cosine similarity to find the best match for a user's question.

Features
- Small, self-contained Flask app that answers questions from a hard-coded FAQ list.
- TF-IDF vectorization + cosine similarity (scikit-learn).
- Minimal web UI to ask questions and view responses.

Quick start (local)

1. Install Python 3.10+.
2. Clone the repo and open a terminal in the project folder.

   git clone https://github.com/alihasnainsamo17/CodeAlpha_FAQChatbot.git
   cd CodeAlpha_FAQChatbot

3. (Recommended) Create and activate a virtual environment:

   python -m venv .venv
   source .venv/bin/activate   # macOS / Linux
   .venv\Scripts\activate    # Windows (PowerShell)

4. Install dependencies:

   pip install -r requirements.txt

5. Run the app in development (debugging enabled via env var):

   # Enable debug only for development
   export FLASK_DEBUG=1
   python app.py

6. Open your browser at: http://127.0.0.1:5000

Production (gunicorn)

For production, do not run the Flask development server with debug enabled. Use a production WSGI server such as gunicorn.

Install gunicorn:

   pip install gunicorn

Run with 4 workers:

   gunicorn -w 4 -b 0.0.0.0:5000 app:app

You can also use the provided Procfile (for platforms like Heroku):

   web: gunicorn -w 4 -b 0.0.0.0:$PORT app:app

Docker (optional)

Build the image:

  docker build -t codealpha-faqchatbot .

Run the container:

  docker run -p 5000:5000 codealpha-faqchatbot

Notes
- The application reads FLASK_DEBUG or DEBUG environment variables to enable debug mode. By default debug is OFF (production-safe).
- The FAQ knowledge is hard-coded in app.py (FAQS list). Edit that list to add/remove questions & answers.
- If you want a persistent knowledge base or improved matching (embeddings/annoy/faiss), I can help migrate.

Repository
- Name: CodeAlpha_FAQChatbot

License
MIT
