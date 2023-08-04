from flask import Flask, render_template, request, redirect
import psycopg2
from pgvector.psycopg2 import register_vector
import openai
import numpy as np

# db 접속 함수
from connect_to_db import get_database_connection

app = Flask(__name__)

conn = get_database_connection()

cursor = conn.cursor()

topics = []

register_vector(cursor)

# db 값 읽어오는 함수
def check_data():
    cursor.execute("SELECT id, title, body FROM topics")
    topics = cursor.fetchall()
    return topics

# Main page
@app.route("/")
def init():
    return render_template('index.html', topics = check_data())

# Create Page
@app.route("/create")
def create():
    return render_template('create.html', topics = check_data())

# Create function
@app.route("/create_process", methods=['POST'])
def create_process():
    title = request.form["title"]
    body = request.form["body"]

    response = openai.Embedding.create(
        input=f'''title:{title}\n\nbody:{body}''',
        model="text-embedding-ada-002"
    )
    embeddings = np.array(response['data'][0]['embedding'])

    cursor.execute('INSERT INTO topics (title, body, embedding) VALUES(%s, %s, %s)', (title, body, embeddings))
    conn.commit()

    return redirect('/')

# Read Page
@app.route("/read/<int:id>")
def read(id):
    selected = None
    topics = check_data()

    for topic in topics:
        if topic[0] == id:
            selected = topic
            print(topic)
    
    return render_template('read.html', topics=topics, topic=selected)

# Debug On
app.run(debug=True)