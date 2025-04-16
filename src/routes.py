from flask import render_template
from src.app import app

@app.route('/')
@app.route('/index')
def index():
    return render_template(
        'index.html', title='home'
    )