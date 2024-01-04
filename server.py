from flask import Flask, request
from analyze_last_commit import main

app = Flask(__name__)


@app.route("/analyze", methods=['POST'])
def analyze():
    repo = request.form['repo']
    res = main(repo)
    return res
