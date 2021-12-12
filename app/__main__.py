import secrets
import threading

from flask import Flask
from flask import render_template, request, redirect, url_for, session
import os
import json

from app.chat.handler import ChatHandler

app = Flask(__name__)
app.secret_key = 'Vale'
app.config['TEMPLATES_AUTO_RELOAD'] = True


chat = ChatHandler()


@app.route("/")
def index():
    template_base = session.get('id', 'index')
    template_path = f"{template_base}.html"
    return render_template(template_path)


@app.route('/', methods=['POST'])
def update_text():
    uploaded_file = request.files['file']
    content = uploaded_file.read()
    telegram_chat = json.loads(content)

    session['id'] = secrets.token_hex(nbytes=24)
    chat.generate_html_with_waiting_status(telegram_chat, session['id'])
    x = threading.Thread(target=chat.generate_html_with_scores, args=(telegram_chat, session['id']))
    x.start()
    return redirect(url_for("index"))
