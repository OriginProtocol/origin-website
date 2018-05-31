from collections import OrderedDict
from datetime import datetime
import os

from app import app
from config import constants, universal, partner_details
from flask import (jsonify, redirect, render_template,
                   request, flash, g, url_for, Response, stream_with_context)
from flask_babel import gettext, Babel, Locale
from flask_recaptcha import ReCaptcha
from logic.emails import mailing_list
import requests
from util.misc import sort_language_constants, get_real_ip, concat_asset_files


# Translation: change path of messages.mo files
app.config['BABEL_TRANSLATION_DIRECTORIES'] = '../translations'
babel = Babel(app)

recaptcha = ReCaptcha(app=app)
if not recaptcha.is_enabled:
    print("Warning: recaptcha is not is_enabled")

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

@app.route('/robots.txt')
def robots():
    return app.send_static_file('files/robots.txt')

@app.route('/apple-app-site-association')
def apple_app_site_association():
    return app.send_static_file('files/apple-app-site-association.json')

@app.route('/mobile/<link_code>')
@app.route('/mobile')
def mobile(link_code=None):
    return render_template('mobile.html', link_code=link_code)

@app.route('/<lang_code>')
def index():
    return render_template('index.html')

@app.route('/<lang_code>/team')
def team():
    return render_template('team.html')

@app.route('/<lang_code>/presale')
def presale():
    return render_template('presale.html')

@app.route('/<lang_code>/whitepaper')
def whitepaper():
    localized_filename = 'whitepaper_v4_%s.pdf' % g.current_lang.lower()
    whitepaper_path = (os.path.join(app.root_path, '..', 'static', 'docs', localized_filename))
    if os.path.isfile(whitepaper_path):
        return app.send_static_file('docs/%s' % localized_filename)
    else:
        # Default to English
        return app.send_static_file('docs/whitepaper_v4.pdf')

@app.route('/<lang_code>/product-brief')
def product_brief():
    localized_filename = 'product_brief_v17_%s.pdf' % g.current_lang.lower()
    product_brief_path = (os.path.join(app.root_path, '..', 'static', 'docs', localized_filename))
    if os.path.isfile(product_brief_path):
        return app.send_static_file('docs/%s' % localized_filename)
    else:
        # Default to English
        return app.send_static_file('docs/product_brief_v17.pdf')

@app.route('/mailing-list/join', methods=['POST'])
def join_mailing_list():
    email = request.form['email']
    ip_addr = get_real_ip()
    feedback = mailing_list.send_welcome(email, ip_addr)
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
    ip_addr = get_real_ip()
    print("CHECK:", email, request.remote_addr) # Temp until we get IP recorded
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
    if not recaptcha.verify():
        return jsonify(gettext("Please prove you are not a robot."))
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
    print('POSTED!!')
    print(request.get_json())
    print(request.json)
    return redirect('/', code=302)

@app.route('/<lang_code>/build-on-origin')
def build_on_origin():
    return redirect(url_for('partners', lang_code=g.current_lang), code=301)

@app.route('/<lang_code>/discord')
def discord():
    return redirect(universal.DISCORD_URL, code=301)

@app.route('/<lang_code>/telegram')
def telegram():
    return redirect(universal.TELEGRAM_URL, code=301)

@app.route('/<lang_code>/partners')
def partners():
    return render_template('partners.html')

@app.route('/<lang_code>/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/<lang_code>/tos')
def tos():
    return render_template('tos.html')

@app.route('/partners/interest', methods=['POST'])
def partners_interest():
    name = request.form['name']
    company_name = request.form['company_name']
    email = request.form['email']
    website = request.form["website"]
    note = request.form["note"]
    ip_addr = get_real_ip()
    if not name:
        return jsonify(gettext("Please enter your name"))
    if not company_name:
        return jsonify(gettext("Please enter your company name"))
    if not email:
        return jsonify(gettext("Please enter your email"))
    if not recaptcha.verify():
        return jsonify(gettext("Please prove you are not a robot."))
    feedback = mailing_list.partners_interest(name, company_name, email,
                                              website, note, ip_addr)
    flash(feedback)
    return jsonify("OK")

@app.route('/static/css/all_styles.css')
def assets_all_styles():
    return Response(concat_asset_files([
        "static/css/vendor-bootstrap-4.0.0-beta2.css",
        "static/css/style.css",
        "static/css/alertify.css",
        "static/css/animate.css"
    ]), mimetype="text/css")

@app.route('/static/js/all_javascript.js')
def assets_all_javascript():
    return Response(concat_asset_files([
        "static/js/vendor-jquery-3.2.1.min.js",
        "static/js/vendor-popper.min.js",
        "static/js/vendor-bootstrap.min.js",
        "static/js/vendor-alertify.js",
        "static/js/vendor-d3.min.js",
        "static/js/vendor-wow.min.js",
        "static/js/script.js"
    ]), mimetype="application/javascript")

@app.route('/origin-js/origin-v<version>.js', methods=['GET'])
def serve_origin_js(version):

    # temporary hack
    # should really do this w/ NGINX or serve from a proper CDN

    # serves up:
    # https://github.com/OriginProtocol/origin-js/releases/download/v0.5.10/origin.js
    # when you visit:
    # https://code.originprotocol.com/origin-js/origin-v0.5.10.js

    url = "https://github.com/OriginProtocol/origin-js/releases/download/v%s/origin.js" % version
    req = requests.get(url, stream=True)
    return Response(stream_with_context(req.iter_content(chunk_size=2048)), content_type="text/javascript")

@app.context_processor
def inject_partners():
    return dict(partners_dict = partner_details.PARTNERS)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@babel.localeselector
def get_locale():
    browser_language = request.accept_languages.best_match(constants.LANGUAGES) or 'en'
    return g.get('current_lang', browser_language)

@app.context_processor
def inject():
    return {'now': datetime.utcnow(), 'universal':universal}

@app.context_processor
def inject_conf_var():
    current_language = get_locale()
    try:
        current_language_direction = Locale(current_language).text_direction
    except:
        current_language_direction = 'ltr'
    try:
        available_languages =\
            OrderedDict([(lang,
                          Locale(lang).get_language_name(lang).capitalize())
                         for lang in sort_language_constants()])
    except:
        available_languages = {'en': "English"}
    return dict(
        CURRENT_LANGUAGE=current_language,
        CURRENT_LANGUAGE_DIRECTION=current_language_direction,
        AVAILABLE_LANGUAGES=available_languages,
        DOMAIN=request.headers['Host'])
