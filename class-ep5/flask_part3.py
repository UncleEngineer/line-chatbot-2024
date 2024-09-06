from flask import Flask, request
import requests as requests_lib
import json

app = Flask(__name__)
@app.route('/methods', methods=['POST', 'GET'])
def test():
    if request.method == "GET":
        return "GET method used", 200
    elif request.method == "POST":
        return "POST naja", 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)