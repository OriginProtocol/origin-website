from flask import jsonify, redirect, render_template, request, flash, session

from app import app
from config import constants
from logic.emails import mailing_list
from datetime import datetime

# change path of messages.mo file
app.config['BABEL_TRANSLATION_DIRECTORIES'] = '../translations'

from flask.ext.babel import gettext, Babel

babel = Babel(app)

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
    return redirect('/static/docs/product_brief_v17.pdf', code=302)

@app.route('/mailing-list/join', methods=['POST'])
def join_mailing_list():
    email = request.form['email']
    feedback = mailing_list.send_welcome(email)
    return jsonify(feedback)

@app.route('/presale/join', methods=['POST'])
def join_presale():
    full_name = request.form['full_name']
    email = request.form['email']
    accredited = request.form["accredited"]
    entity_type = request.form["entity_type"]
    desired_allocation = request.form["desired_allocation"]
    desired_allocation_currency = request.form["desired_allocation_currency"]
    citizenship = request.form["citizenship"]
    sending_addr = request.form["sending_addr"]
    note = request.form["note"]
    if not full_name:
        return jsonify("Please enter your name")
    if not email:
        return jsonify("Please enter your email")
    if not accredited or not entity_type or not citizenship or not desired_allocation_currency:
        return jsonify("An error occured")
    if not desired_allocation:
        return jsonify("Please enter your desired allocation")
    if "confirm" not in request.form:
        return jsonify("Please agree to the important notice")
    feedback = mailing_list.presale(full_name, email, accredited, entity_type, desired_allocation, desired_allocation_currency, citizenship, sending_addr, note)
    flash(feedback)
    return jsonify("OK")

@app.route('/mailing-list/unsubscribe', methods=['GET'])
def unsubscribe():
    email = request.args.get("email")
    feedback = mailing_list.unsubscribe(email)
    flash(feedback)
    return redirect('/', code=302)

@app.route('/webhook/fullcontact', methods=['GET','POST'])
def fullcontact_webhook():
    print 'POSTED!!'
    print request.get_json()
    print request.json
    return redirect('/', code=302)

@app.route('/language/<language>')
def set_language(language=None):
    session['language'] = language
    print(2, language)
    return redirect('/')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@babel.localeselector
def get_locale():
    # if the user has set up the language manually it will be stored in the session,
    # so we use the locale from the user settings
    try:
        language = session['language']
    except KeyError:
        language = None
    if language is not None:
        print("get_locale() method")
        print(1, language)
        return language
    return request.accept_languages.best_match(constants.LANGUAGES.keys())

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

@app.context_processor
def inject_conf_var():
    print("@app.context_processor")
    print(constants.LANGUAGES)
    return dict(CURRENT_LANGUAGE=session.get('language', request.accept_languages.best_match(constants.LANGUAGES.keys())), AVAILABLE_LANGUAGES=constants.LANGUAGES)
