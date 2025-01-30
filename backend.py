import os
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, send_file
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from pymongo import MongoClient
import logging
import re
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import requests

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Use a long, random, and secret string here
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# MongoDB configuration
client = MongoClient('mongodb://localhost:27017/')
db = client['user_database']
users_collection = db['users']

# Load Groq API key from environment variable
GROQ_API_KEY = "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"
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable not set")

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    user_data = users_collection.find_one({"_id": user_id})
    if user_data:
        return User(str(user_data["_id"]), user_data["username"])
    return None

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/chat")
@login_required
def chat():
    return render_template('index.html')

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        userid = request.form.get("userid")
        username = request.form.get("username")
        password = request.form.get("password")
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        if users_collection.find_one({"_id": userid}):
            flash("User ID already exists. Please log in.", "danger")
            return redirect(url_for("login"))

        user_id = users_collection.insert_one({
            "_id": userid,
            "username": username,
            "password": hashed_password
        }).inserted_id

        user = User(str(user_id), username)
        login_user(user)
        return redirect(url_for("chat"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        userid = request.form.get("userid")
        password = request.form.get("password")
        user_data = users_collection.find_one({"_id": userid})

        if user_data and bcrypt.check_password_hash(user_data["password"], password):
            user = User(str(user_data["_id"]), user_data["username"])
            login_user(user)
            return redirect(url_for("chat"))
        else:
            flash("Login failed. Check your User ID and password.", "danger")

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/query", methods=["POST"])
@login_required
def query():
    user_query = request.json.get("query")
    if not user_query:
        return jsonify({"error": "Query is required"}), 400

    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": f"Provide a detailed research and analysis on the topic: {user_query}. Include relevant information, key points, and resource names along with links also give the links to resources where the user can learn more on the {user_query}."
                }
            ],
            "model": "llama-3.3-70b-versatile",
            "temperature": 0.5,
            "max_tokens": 1024,
            "top_p": 1,
            "stop": None,
            "stream": False
        }

        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        response_data = response.json()
        response_text = response_data['choices'][0]['message']['content']
        logging.debug(f"Generated response: {response_text}")

        return jsonify({"response": response_text})
    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred while processing the request: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route("/generate_pdf", methods=["POST"])
@login_required
def generate_pdf():
    text = request.json.get("text")
    if not text:
        return jsonify({"error": "Text is required to generate PDF"}), 400

    try:
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        style_normal = styles['Normal']
        style_title = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=18,
            leading=22,
            spaceAfter=12,
            textColor='black',
            alignment=1,
            fontName='Helvetica-Bold'
        )
        style_link = ParagraphStyle(
            'Link',
            parent=styles['BodyText'],
            fontSize=12,
            textColor='blue',
            alignment=0,
            underline=True
        )

        text_lines = text.split('\n')
        title = text_lines[0] if text_lines else ""
        content = text_lines[1:] if text_lines else []

        story = []
        if title:
            story.append(Paragraph(title, style_title))
            story.append(Spacer(1, 12))

        for line in content:
            # Extract URLs and create clickable links without additional text
            parts = re.split(r'(http[s]?://\S+)', line)
            for part in parts:
                if re.match(r'http[s]?://\S+', part):
                    story.append(Paragraph(f'<a href="{part}">{part}</a>', style_link))
                elif part.strip():  # Add normal text parts only if they are not empty
                    story.append(Paragraph(part, style_normal))
            story.append(Spacer(1, 12))

        doc.build(story)
        pdf_buffer.seek(0)
        return send_file(pdf_buffer, as_attachment=True, download_name="response.pdf", mimetype='application/pdf')
    except Exception as e:
        logging.error(f"An error occurred while generating PDF: {str(e)}")
        return jsonify({"error": f"An error occurred while generating PDF: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)