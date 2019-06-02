from flask import render_template, request
import flask
app = flask.Flask(__name__)

@app.route('/')

def main():
    return render_template('GClient.html')

@app.route('/', methods=['POST'])
def my_form_post():
    text = request.form['text']
    processed_text = text.upper()
    return processed_text