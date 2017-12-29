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

@app.route('/mailing-list/join', methods=['POST'])
def join_mailing_list():
    email = request.form['email']
    feedback = mailing_list.send_welcome(email)
    return jsonify(feedback)

@app.route('/presale/join', methods=['POST'])
def join_presale():
    email = request.form['email']
    accredited = request.form["accredited"]
    entity_type = request.form["entity_type"]
    desired_allocation = request.form["desired_allocation"]
    desired_allocation_currency = request.form["desired_allocation_currency"]
    citizenship = request.form["citizenship"]
    sending_addr = request.form["sending_addr"]
    note = request.form["note"]
    if not email:
        return jsonify("Please enter your email")
    if not accredited or not entity_type or not citizenship or not desired_allocation_currency:
        return jsonify("An error occured")
    if not desired_allocation:
        return jsonify("Please enter your desired allocation")
    if "confirm" not in request.form:
        return jsonify("Please agree to the important notice")
    feedback = mailing_list.presale(email, accredited, entity_type, desired_allocation, desired_allocation_currency, citizenship, sending_addr, note)
    flash(feedback)
    return jsonify("OK")

@app.route('/mailing-list/unsubscribe', methods=['GET'])
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