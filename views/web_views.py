import re

from app import app
from config import constants
from database import db, db_models, db_common
from flask import redirect
from flask import render_template
from flask import request
from flask import jsonify
from util import sendgrid_wrapper as sgw

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

    if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
        return jsonify("Please enter a valid email address")

    try:
        me = db_models.EmailList()
        me.email = email
        me.unsubscribed = False
        db.session.add(me)
        db.session.commit()
    except:
        return jsonify('You are already signed up!')

    # send welcome email
    to_email = sgw.Email(email, email)
    from_email = sgw.Email(constants.FROM_EMAIL, constants.FROM_EMAIL_NAME)
    html_body = constants.WELCOME_HTML_BODY
    text_body = html_body.replace("<br>","")
    sgw.send_message(from_email, [to_email], constants.WELCOME_SUBJECT, text_body, html_body)

    return jsonify('Thanks for signing up!')