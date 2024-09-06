from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, Flask11111"

@app.route("/path1")
def path():
    return "path1"


if __name__ == '__main__':
    app.run(debug=True,port=5000)