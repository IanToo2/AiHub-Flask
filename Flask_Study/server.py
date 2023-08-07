from flask import Flask, render_template, request, redirect, jsonify

import psycopg2
from pgvector.psycopg2 import register_vector

import numpy as np
import json

# db 접속 함수
from connect_to_db import get_database_connection
print("import 끝")

app = Flask(__name__)

# DB conn 생성
conn = get_database_connection()
cursor = conn.cursor()

topics = []

register_vector(cursor)

print("서버 로딩 완료!!!")
# db 값 읽어오는 함수
def check_data():
    cursor.execute("SELECT id, title, body FROM topics")
    topics = cursor.fetchall()
    return topics

# Tensorflow로 데이터 벡터화 함수
def embed_text(title, body):

    # 전역 변수에 미리 로드한 모델을 가져오기
    embed = app.embed_model
    # 텍스트를 벡터화하여 embeddings 변수에 저장
    input_text = [f"title:{title}", f"body:{body}"]
    print(input_text)
    embeddings = embed(input_text)

    # Numpy 배열로 변환
    embeddings = np.array(embeddings)

    return embeddings

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
    # form으로부터 값 가져오기
    title = request.form["title"]
    body = request.form["body"]

    # DB에 저장
 
    cursor.execute('INSERT INTO topics (title, body) VALUES(%s, %s)', (title, body))
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