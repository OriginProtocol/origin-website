from flask import redirect
from flask import render_template
from flask import request

from app import app
from config import constants
from logic.emails import send_emails

# force https on prod
@app.before_request
def beforeRequest():
    if constants.HTTPS:
        print 'yes'
        if not request.url.startswith('https'):
            return redirect(request.url.replace('http', 'https', 1))

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

@app.route('/signup', methods=['POST','GET'])
def signup():
    email = request.args.get("email")
    send_result = send_emails.send_welcome(email)
    return send_result