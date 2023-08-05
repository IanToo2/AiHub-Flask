from flask import Flask, render_template, request, redirect, jsonify

import psycopg2
from pgvector.psycopg2 import register_vector

import openai
import numpy as np

# tensorflow 
import tensorflow as tf
import tensorflow_hub as hub

# db 접속 함수
from connect_to_db import get_database_connection

app = Flask(__name__)

# TensorFlow Hub에서 사전 훈련된 USE(Universal Sentence Encoder) 모델 로드
embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")
app.embed_model = embed


conn = get_database_connection()
cursor = conn.cursor()

topics = []

register_vector(cursor)

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
    # 웹으로 부터 값 가져오기
    title = request.form["title"]
    body = request.form["body"]

    ## openai로 Embedding 처리
    ## 지금은 api key가 만료되어 사용 불가
    # response = openai.Embedding.create(
    #     input=f'''title:{title}\n\nbody:{body}''',
    #     model="text-embedding-ada-002"
    # )
    # embeddings = np.array(response['data'][0]['embedding'])
    embeddings = embed_text(title, body)
    # DB에 저장
    print("title = {}\n body = {}".format(title, body))
    print("embeddings data = {}".format(embeddings))
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