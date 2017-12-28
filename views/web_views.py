from flask import jsonify, redirect, render_template, request, flash

from app import app
from config import constants
from logic.emails import mailing_list
from datetime import datetime

# force https on prod
@app.before_request
def beforeRequest():
    if constants.HTTPS:
        if not request.url.startswith('https'):
            return redirect(request.url.replace('http', 'https', 1))

@app.route('/')
def index():
    flash('telegram')
    return render_template('index.html')

@app.route('/team')
def team():
    flash('slack')
    return render_template('team.html')

@app.route('/presale')
def presale():
    return render_template('presale.html')

@app.route('/whitepaper')
def whitepaper():
    return redirect('/static/docs/whitepaper_v3.pdf', code=302)

@app.route('/product-brief')
def product_brief():
    return redirect('/static/docs/product_brief_v15.pdf', code=302)

@app.route('/signup', methods=['POST','GET'])
def signup():
    email = request.args.get("email")
    accredited = request.args.get("accredited")
    entity_type = request.args.get("entity_type")
    desired_allocation = request.args.get("desired_allocation")
    desired_allocation_currency = request.args.get("desired_allocation_currency")
    citizenship = request.args.get("citizenship")
    sending_addr = request.args.get("sending_addr")
    note = request.args.get("note")

    feedback = mailing_list.send_welcome(email, accredited, entity_type, desired_allocation, desired_allocation_currency, citizenship, sending_addr, note)
    return jsonify(feedback)

@app.route('/unsubscribe', methods=['GET'])
def unsubscribe():
    email = request.args.get("email")
    feedback = mailing_list.unsubscribe(email)
    flash(feedback)
    return redirect('/', code=302)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}