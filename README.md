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

5. Run the app:

   python app.py

6. Open your browser at: http://127.0.0.1:5000

Docker (optional)

Build the image:

  docker build -t codealpha-faqchatbot .

Run the container:

  docker run -p 5000:5000 codealpha-faqchatbot

Notes
- The application runs with debug=True for convenience in development. Do not enable debug mode in production — set debug=False or use a WSGI server such as gunicorn.
- To customize the knowledge base, open app.py and edit the FAQS list.

Repository
- Name: CodeAlpha_FAQChatbot

License
MIT
