from flask import render_template
from flask import redirect

from app import app

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/team')
def team():
    return render_template('team.html')

@app.route('/whitepaper')
def whitepaper():
    return redirect('/static/docs/whitepaper_v2.pdf', code=302)

@app.route('/product-brief')
def product_brief():
    return redirect('/static/docs/product_brief_v15.pdf', code=302)