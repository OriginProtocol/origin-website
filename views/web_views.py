from flask import jsonify, redirect, render_template, request, flash, session, g, url_for

from app import app
from config import constants
from logic.emails import mailing_list
from datetime import datetime
from flask_babel import gettext, Babel, Locale
from flask_recaptcha import ReCaptcha

# Translation: change path of messages.mo files
app.config['BABEL_TRANSLATION_DIRECTORIES'] = '../translations'
babel = Babel(app)

recaptcha = ReCaptcha(app=app)
if not recaptcha.is_enabled:
    print "Warning: recaptcha is not is_enabled"

@app.before_request
def beforeRequest():
    """ Processing of URL before any routing """
    # Force https on prod
    if constants.HTTPS:
        if not request.url.startswith('https'):
            return redirect(request.url.replace('http', 'https', 1))
    if request.view_args and 'lang_code' in request.view_args:
        if request.view_args['lang_code'] in constants.LANGUAGES:
            # Pull off current language from URL
            g.current_lang = request.view_args['lang_code']
            request.view_args.pop('lang_code')
        else:
            # Possible old style URL without language prefix
            # e.g. /blah --> /en/blah
            return redirect("/%s/%s" % (get_locale(), request.view_args['lang_code']), code=302)


@app.route('/')
def root():
    return redirect(url_for('index', lang_code=get_locale()))

@app.route('/<lang_code>')
def index():
    flash('telegram')
    return render_template('index.html')

@app.route('/<lang_code>/team')
def team():
    flash('slack')
    return render_template('team.html')

@app.route('/<lang_code>/presale')
def presale():
    return render_template('presale.html')

@app.route('/whitepaper')
def whitepaper():
    return redirect('/static/docs/whitepaper_v4.pdf', code=302)

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
    print("CHECK:", email, request.remote_addr) # Temp until we get IP recorded
    if not recaptcha.verify():
        return jsonify(gettext("Please prove you are not a robot."))
    if not full_name:
        return jsonify(gettext("Please enter your name"))
    if not email:
        return jsonify(gettext("Please enter your email"))
    if not accredited or not entity_type or not citizenship or not desired_allocation_currency:
        return jsonify(gettext("An error occured"))
    if not desired_allocation:
        return jsonify(gettext("Please enter your desired allocation"))
    if "confirm" not in request.form:
        return jsonify(gettext("Please agree to the important notice"))
    feedback = mailing_list.presale(full_name, email, accredited, entity_type, desired_allocation, desired_allocation_currency, citizenship, sending_addr, note, request.remote_addr)
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

@app.route('/<lang_code>/build-on-origin')
def build_on_origin():
    return render_template('build_on_origin.html')

@app.route('/build-on-origin/interest', methods=['POST'])
def build_on_origin_interest():
    name = request.form['name']
    company_name = request.form['comapny_name']
    email = request.form['email']
    website = request.form["website"]
    note = request.form["note"]
    print("CHECK:", email, request.remote_addr) # Temp until we get IP recorded
    if not recaptcha.verify():
        return jsonify(gettext("Please prove you are not a robot."))
    if not name:
        return jsonify(gettext("Please enter your name"))
    if not company_name:
        return jsonify(gettext("Please enter your company name"))
    if not email:
        return jsonify(gettext("Please enter your email"))
    feedback = mailing_list.build_interest(name, company_name, email, website, note)
    flash(feedback)
    return jsonify("OK")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@babel.localeselector
def get_locale():
    browser_language = request.accept_languages.best_match(constants.LANGUAGES) or 'en'
    return g.get('current_lang', browser_language)

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

@app.context_processor
def inject_conf_var():
    current_language = get_locale()
    try:
        current_language_direction = Locale(current_language).text_direction
    except:
        current_language_direction = 'ltr'
    try:
        available_languages = dict((l,Locale(l).get_language_name(l).capitalize()) for l in constants.LANGUAGES)
    except:
        available_languages = {'en':"English"}
    return dict(
        CURRENT_LANGUAGE=current_language,
        CURRENT_LANGUAGE_DIRECTION=current_language_direction,
        AVAILABLE_LANGUAGES=available_languages,
        URL_ROOT=request.url_root)
