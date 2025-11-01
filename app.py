# Your main Flask application (backend logic, API routes)
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login')
def login():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True, port=3001, host='127.0.0.1')

