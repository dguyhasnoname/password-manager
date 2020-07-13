# server.py
from flask import Flask, render_template
import traceback

app = Flask(__name__, static_folder="../static", template_folder="../static")
@app.route("/")
def index():
    traceback.print_exc()
    return render_template("index.html")
@app.route("/hello")
def hello():
    return "Hello World!"
if __name__ == "__main__":
    app.run(debug=True)