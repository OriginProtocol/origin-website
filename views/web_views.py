from collections import OrderedDict
from datetime import datetime
import os
import re
import sys
import calendar

from app import app
from database import db, db_models

from config import constants, universal, partner_details
from flask import (jsonify, redirect, render_template,
                   request, flash, g, url_for, Response,
                   stream_with_context, session)
from flask_babel import gettext, Babel, Locale
from util.recaptcha import ReCaptcha
from logic.emails import mailing_list
from logic.scripts import update_token_insight as insight
from logic.views import social_stats
import requests

from util.misc import sort_language_constants, get_real_ip, concat_asset_files, log

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

import json

# Translation: change path of messages.mo files
app.config['BABEL_TRANSLATION_DIRECTORIES'] = '../translations'
babel = Babel(app)

recaptcha = ReCaptcha(app=app)
if not recaptcha.is_enabled:
    log("Warning: recaptcha is not is_enabled")

selected_lang = ""

@app.before_request
def beforeRequest():
    """ Processing of URL before any routing """
    # Force https on prod
    if constants.HTTPS:
        if not request.url.startswith('https') and 'ogn.dev' not in request.url_root:
            return redirect(request.url.replace('http', 'https', 1))

    selected_lang = None
    if request.view_args and 'lang_code' in request.view_args:
        selected_lang = request.view_args.pop('lang_code')
    elif request.args and 'lang_code' in request.args:
        selected_lang = request.args['lang_code']
    g.lang_code = selected_lang

    if selected_lang in constants.LANGUAGES:
        g.current_lang = selected_lang
    else:
        # Use Accept-Languages header for fallback
        g.current_lang = get_locale()

    g.metadata = {}
    g.metadata['image'] = 'https://www.originprotocol.com/static/img/fb-og-img.png'
    g.metadata['title'] = gettext('Origin Protocol')
    g.metadata['description'] = gettext('Origin Protocol is the blockchain platform for building decentralized marketplaces')
    g.metadata['url'] = 'https://www.originprotocol.com'

@app.route('/', strict_slashes=False)
def root():
    def filter_featured_videos(video):
        return video['landing_page_featured']

    all_videos = json.load(open('static/files/videos.json'))
    featured_videos = filter(filter_featured_videos, all_videos)
    return render_template('landing.html', featured_videos=featured_videos)

@app.route('/robots.txt', strict_slashes=False)
def robots():
    return app.send_static_file('files/robots.txt')

@app.route('/apple-app-site-association', strict_slashes=False)
def apple_app_site_association():
    return app.send_static_file('files/apple-app-site-association.json')

@app.route('/mobile', strict_slashes=False)
@app.route('/<lang_code>/mobile', strict_slashes=False)
def mobile():
    return render_template('mobile.html')

@app.route('/singles', strict_slashes=False)
@app.route('/<lang_code>/singles', strict_slashes=False)
def singles():
    return render_template('singles.html')

@app.route('/mobile/apk', strict_slashes=False)
@app.route('/<lang_code>/mobile/apk', strict_slashes=False)
def mobile_apk():
    req = requests.get(constants.APK_URL, stream = True)
    return Response(stream_with_context(req.iter_content(chunk_size=1024)),
                    headers={
                        'content-type': req.headers['content-type'],
                        'content-disposition': 'attachment;filename=origin-marketplace.apk'
                    })

@app.route('/<lang_code>', strict_slashes=False)
def index():
    def filter_featured_videos(video):
        return video['landing_page_featured']

    all_videos = json.load(open('static/files/videos.json'))
    featured_videos = filter(filter_featured_videos, all_videos)

    # check if it's a legit language code
    if g.lang_code in constants.LANGUAGES:
        return render_template('landing.html', featured_videos=featured_videos)
    # shortcut for nick
    elif 'ogn.dev' in request.url_root and g.lang_code == "tb":
        return redirect('https://originprotocol.github.io/test-builds', code=302)
    elif 'ogn.dev' in request.url_root:
        return redirect('https://faucet.originprotocol.com/eth?code=%s' % (g.lang_code), code=302)
    # nope, it's a 404
    else:
        return render_template('404.html'), 404

@app.route('/team', strict_slashes=False)
@app.route('/<lang_code>/team', strict_slashes=False)
def team():
    # fetch our list of contributors from the DB
    contributors = db_models.Contributor.query.all()    

    return render_template('team.html', contributors=contributors)

@app.route('/admin', strict_slashes=False)
@app.route('/<lang_code>/admin', strict_slashes=False)
def admin():
    return redirect('https://admin.staging.originprotocol.com', code=302)

@app.route('/presale', strict_slashes=False)
@app.route('/<lang_code>/presale', strict_slashes=False)
def presale():
    return redirect('/ogn-token', code=302)

@app.route('/tokens', strict_slashes=False)
@app.route('/<lang_code>/tokens', strict_slashes=False)
def tokens():
    return redirect('/ogn-token', code=302)

@app.route('/whitepaper', strict_slashes=False)
@app.route('/<lang_code>/whitepaper', strict_slashes=False)
def whitepaper():
    localized_filename = 'whitepaper_v18_%s.pdf' % g.current_lang.lower()
    whitepaper_path = (os.path.join(app.root_path, '..', 'static', 'docs', localized_filename))
    if os.path.isfile(whitepaper_path):
        return app.send_static_file('docs/%s' % localized_filename)
    else:
        # Default to English
        return app.send_static_file('docs/whitepaper_v19.pdf')

@app.route('/product-brief', strict_slashes=False)
@app.route('/<lang_code>/product-brief', strict_slashes=False)
def product_brief():
    localized_filename = 'whitepaper_v18_%s.pdf' % g.current_lang.lower()
    product_brief_path = (os.path.join(app.root_path, '..', 'static', 'docs', localized_filename))
    if os.path.isfile(product_brief_path):
        return app.send_static_file('docs/%s' % localized_filename)
    else:
        # Default to English
        return app.send_static_file('docs/whitepaper_v19.pdf')

@app.route('/mailing-list/join', methods=['POST'], strict_slashes=False)
def join_mailing_list():
    if not 'email' in request.form:
        return jsonify(success=False, message=gettext("Missing email"))
    email = request.form['email']
    if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
        return jsonify(success=False, message=gettext("Invalid email"))

    # optional fields
    eth_address = request.form.get('eth_address')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    full_name = request.form.get('name')
    if not full_name:
        full_name = ' '.join(filter(None, (first_name, last_name)))
    full_name = None if full_name == '' else full_name
    phone = request.form.get('phone')
    ip_addr = request.form.get('ip_addr')
    country_code = request.form.get('country_code')
    dapp_user = 1 if 'dapp_user' in request.form else 0
    investor = 1 if 'investor' in request.form else 0

    log('Updating mailing list. email: %s name: %s phone: %s eth_address: %s country: %s ip_addr=%s'
        % (email, full_name, phone, eth_address, country_code, ip_addr))

    try:
        # Add an entry to the eth_contact DB table.
        if 'eth_address':
            log('Adding to wallet insights')
            insight.add_contact(
                address=eth_address,
                dapp_user=dapp_user,
                investor=investor,
                name=full_name,
                email=email,
                phone=phone,
                country_code=country_code)

        # Add an entry to the email_list table.
        new_contact = mailing_list.add_contact(email, first_name, last_name, ip_addr, country_code)

        # If it is a new contact, send a welcome email and add it to the SendGrid contact list.
        if new_contact:
            mailing_list.send_welcome(email)
            mailing_list.add_sendgrid_contact(
                email=email,
                full_name=full_name,
                country_code=country_code,
                dapp_user=dapp_user)
    except Exception as err:
        log('Failure: %s' % err)
        return jsonify(success=False, message=str(err))

    return jsonify(success=True, message=gettext('Thanks for signing up!'))


@app.route('/presale/join', methods=['POST'], strict_slashes=False)
def join_presale():
    full_name = request.form['full_name']
    email = request.form['email']
    desired_allocation = request.form["desired_allocation"]
    desired_allocation_currency = request.form["desired_allocation_currency"]
    citizenship = request.form["citizenship"]
    sending_addr = request.form["sending_addr"]
    ip_addr = get_real_ip()
    if not full_name:
        return jsonify(success=False, message=gettext("Please enter your name"))
    if not email:
        return jsonify(success=False, message=gettext("Please enter your email"))
    if not citizenship:
        return jsonify(success=False, message=gettext("Select your country of citizenship"))
    if not desired_allocation:
        return jsonify(success=False, message=gettext("Please enter your desired allocation"))
    if not desired_allocation_currency:
        return jsonify(success=False, message=gettext("Select a currency"))
    if not recaptcha.verify():
        return jsonify(success=False, message=gettext("Please prove you are not a robot."))
    feedback = mailing_list.presale(full_name, email, desired_allocation, desired_allocation_currency, citizenship, sending_addr, request.remote_addr)
    mailing_list.add_sendgrid_contact(email, full_name, citizenship)
    insight.add_contact(sending_addr,name=full_name, email=email, presale_interest=1)
    flash(feedback)
    return jsonify(success=True, message=gettext("OK"))

@app.route('/mailing-list/unsubscribe', methods=['GET'], strict_slashes=False)
def unsubscribe():
    email = request.args.get("email")
    feedback = mailing_list.unsubscribe(email)
    mailing_list.unsubscribe_sendgrid_contact(email)
    flash(feedback)
    return redirect('/en/', code=302)

@app.route('/social-stats', methods=['GET'], strict_slashes=False)
@app.route('/<lang_code>/social-stats', methods=['GET'], strict_slashes=False)
def fetch_social_stats():
    stats = social_stats.get_social_stats(g.current_lang)
    return jsonify({'stats': stats})

@app.route('/build-on-origin', strict_slashes=False)
@app.route('/<lang_code>/build-on-origin', strict_slashes=False)
def build_on_origin():
    return render_template('404.html'), 410

@app.route('/developers', strict_slashes=False)
@app.route('/<lang_code>/developers', strict_slashes=False)
def developers():

    class DatetimeRange:
        def __init__(self, dt1, dt2):
            self._dt1 = dt1
            self._dt2 = dt2

        def __contains__(self, dt):
            return self._dt1 <= dt < self._dt2

    def validSundaysFilter(sunday):
        if(sunday != 0):
            return True
        else:
            return False

    def sundayInMonthToDay(year, month, sundayIndex):
        return filter(validSundaysFilter, (week[-1] for week in calendar.monthcalendar(year, month)))[sundayIndex]

    year = datetime.now().year
    month = datetime.now().month

    # see date range specs: https://docs.google.com/spreadsheets/d/1ACAH15qdfE8jrfMAHVjWzrGRBKo-gMaVmS-D7GnL6po/edit#gid=0
    dateRanges = [
        # first day of a year to second Sunday in March
        DatetimeRange(
            datetime(year=year, month=1, day=1),
            datetime(year=year, month=3, day=sundayInMonthToDay(year, 3, 1)),
        ),
        # second Sunday in March to last Sunday in March
        DatetimeRange(
            datetime(year=year, month=3, day=sundayInMonthToDay(year, 3, 1)),
            datetime(year=year, month=3, day=sundayInMonthToDay(year, 3, -1))
        ),
        # last Sunday in March to first Sunday in April
        DatetimeRange(
            datetime(year=year, month=3, day=sundayInMonthToDay(year, 3, -1)),
            datetime(year=year, month=4, day=sundayInMonthToDay(year, 4, 0))
        ),
        # first Sunday in April last Sunday in September
        DatetimeRange(  
            datetime(year=year, month=4, day=sundayInMonthToDay(year, 4, 0)),
            datetime(year=year, month=9, day=sundayInMonthToDay(year, 9, -1))
        ),
        # last Sunday in September to last Sunday in October
        DatetimeRange(
            datetime(year=year, month=9, day=sundayInMonthToDay(year, 9, -1)),
            datetime(year=year, month=10, day=sundayInMonthToDay(year, 10, -1))
        ),
        # last Sunday in October to first Sunday in November
        DatetimeRange(
            datetime(year=year, month=10, day=sundayInMonthToDay(year, 10, -1)),
            datetime(year=year, month=11, day=sundayInMonthToDay(year, 11, 0))
        ),
        # first Sunday in November to the end of the year
        DatetimeRange(
            datetime(year=year, month=11, day=sundayInMonthToDay(year, 11, 0)),
            datetime(year=year, month=12, day=31)
        )
    ]

    desktopImages = [
        '/static/img/developers/1-st-sun-nov.svg',
        '/static/img/developers/2-nd-sun-mar.svg',
        '/static/img/developers/last-sun-mar.svg',
        '/static/img/developers/1-st-sun-apr.svg',
        '/static/img/developers/last-sun-sep.svg',
        '/static/img/developers/last-sun-oct.svg',
        '/static/img/developers/1-st-sun-nov.svg'
    ]

    mobileTimes = [
        [ '12:30 PM', '1:30 PM', '3:30 PM', '5:30 PM', '8:30 PM', '9:30 PM', '10:30 PM', '11:30 PM', '2:00 AM', '4:30 AM', '4:30 AM', '5:30 AM', '5:30 AM', '9:30 AM'],
        [ '12:30 PM', '1:30 PM', '3:30 PM', '4:30 PM', '7:30 PM', '8:30 PM', '9:30 PM', '10:30 PM', '1:00 AM', '3:30 AM', '3:30 AM', '4:30 AM', '4:30 AM', '8:30 AM'],
        [ '12:30 PM', '1:30 PM', '3:30 PM', '4:30 PM', '8:30 PM', '9:30 PM', '9:30 PM', '10:30 PM', '1:00 AM', '3:30 AM', '3:30 AM', '4:30 AM', '4:30 AM', '8:30 AM'],
        [ '12:30 PM', '1:30 PM', '3:30 PM', '4:30 PM', '8:30 PM', '9:30 PM', '9:30 PM', '10:30 PM', '1:00 AM', '3:30 AM', '3:30 AM', '4:30 AM', '4:30 AM', '7:30 AM'],
        [ '12:30 PM', '1:30 PM', '3:30 PM', '4:30 PM', '8:30 PM', '9:30 PM', '9:30 PM', '10:30 PM', '1:00 AM', '3:30 AM', '3:30 AM', '4:30 AM', '4:30 AM', '8:30 AM'],
        [ '12:30 PM', '1:30 PM', '3:30 PM', '4:30 PM', '7:30 PM', '8:30 PM', '9:30 PM', '10:30 PM', '1:00 AM', '3:30 AM', '3:30 AM', '4:30 AM', '4:30 AM', '8:30 AM'],
        [ '12:30 PM', '1:30 PM', '3:30 PM', '5:30 PM', '8:30 PM', '9:30 PM', '10:30 PM', '11:30 PM', '2:00 AM', '4:30 AM', '4:30 AM', '5:30 AM', '5:30 AM', '9:30 AM']
    ]

    imageIndex = 0
    while imageIndex < len(dateRanges):
        if (datetime.now() in dateRanges[imageIndex]):
            break
        imageIndex += 1

    return render_template('developers.html', desktopBackground=desktopImages[imageIndex], mobileTimes=mobileTimes[imageIndex])

@app.route('/discord', strict_slashes=False)
@app.route('/<lang_code>/discord', strict_slashes=False)
def discord():
    return redirect(universal.DISCORD_URL, code=301)

@app.route('/ios', strict_slashes=False)
@app.route('/<lang_code>/ios', strict_slashes=False)
def ios():
    return redirect(universal.IOS_URL, code=301)

@app.route('/android', strict_slashes=False)
@app.route('/<lang_code>/android', strict_slashes=False)
def android():
    return redirect(universal.ANDROID_URL, code=301)

@app.route('/telegram', strict_slashes=False)
@app.route('/<lang_code>/telegram', strict_slashes=False)
def telegram():
    return redirect(universal.TELEGRAM_URL, code=301)

@app.route('/dapp', strict_slashes=False)
@app.route('/<lang_code>/dapp', strict_slashes=False)
def dapp():
    return redirect(universal.DAPP_URL, code=301)

@app.route('/rewards', strict_slashes=False)
@app.route('/<lang_code>/rewards', strict_slashes=False)
def rewards():
    return redirect(universal.REWARDS_URL, code=301)

@app.route('/partners', strict_slashes=False)
@app.route('/<lang_code>/partners', strict_slashes=False)
def partners():
    return render_template('404.html'), 410

@app.route('/about', strict_slashes=False)
@app.route('/<lang_code>/about', strict_slashes=False)
def about():
    return render_template('about.html')

@app.route('/investors', strict_slashes=False)
@app.route('/<lang_code>/investors', strict_slashes=False)
def investors():
    return render_template('investors.html')

@app.route('/product', strict_slashes=False)
@app.route('/<lang_code>/product', strict_slashes=False)
def product():
    return render_template('product.html')

@app.route('/ogn-token', strict_slashes=False)
@app.route('/<lang_code>/ogn-token', strict_slashes=False)
def ogn_token():
    return render_template('ogn-token.html')

@app.route('/video/<video_slug>', strict_slashes=False)
@app.route('/<lang_code>/video/<video_slug>', strict_slashes=False)
def video(video_slug):
    def remove_current_video(video):
        if(video['slug'] == video_slug):
            return False
        else:
            return True

    def find_current_video(video):
        if(video['slug'] == video_slug):
            return True
        else:
            return False

    def filter_featured_videos(video):
        return video['video_page_featured']


    all_videos = json.load(open('static/files/videos.json'))

    featured_videos = filter(remove_current_video, filter(filter_featured_videos, all_videos))

    videoList = filter(find_current_video, all_videos)
    if (len(videoList) == 0):
        return render_template('404.html'), 404

    video=videoList[0]
    g.metadata['image'] = 'https://www.originprotocol.com/static/img/videos/' + video['hash'] + '.jpg'
    g.metadata['title'] = video['title']
    g.metadata['url'] = 'https://www.originprotocol.com/video/' + video['slug']
    return render_template('video.html', featured_videos=featured_videos, video=video)

@app.route('/videos', strict_slashes=False)
@app.route('/<lang_code>/videos', strict_slashes=False)
def videos():
    data = json.load(open('static/files/videos.json'))
    return render_template('videos.html', videos=data)

@app.route('/privacy', strict_slashes=False)
@app.route('/<lang_code>/privacy', strict_slashes=False)
def privacy():
    return render_template('privacy.html')

@app.route('/tos', strict_slashes=False)
@app.route('/<lang_code>/tos', strict_slashes=False)
def tos():
    return render_template('tos.html')

@app.route('/aup', strict_slashes=False)
@app.route('/<lang_code>/aup', strict_slashes=False)
def aup():
    return render_template('aup.html')

@app.route('/creator', strict_slashes=False)
@app.route('/<lang_code>/creator', strict_slashes=False)
def creator():
    return render_template('creator.html')

# @app.route('/partners/interest', methods=['POST'], strict_slashes=False)
# def partners_interest():
#     name = request.form['name']
#     company_name = request.form['company_name']
#     email = request.form['email']
#     website = request.form["website"]
#     note = request.form["note"]
#     ip_addr = get_real_ip()
#     if not name:
#         return jsonify(gettext("Please enter your name"))
#     if not company_name:
#         return jsonify(gettext("Please enter your company name"))
#     if not email:
#         return jsonify(gettext("Please enter your email"))
#     if not recaptcha.verify():
#         return jsonify(gettext("Please prove you are not a robot."))
#     feedback = mailing_list.partners_interest(name, company_name, email,
#                                               website, note, ip_addr)
#     mailing_list.add_sendgrid_contact(email,name)
#     flash(feedback)
#     return jsonify("OK")

@app.route('/whitepaper-v2', strict_slashes=False)
@app.route('/<lang_code>/whitepaper-v2', strict_slashes=False)
def whitepaperv2():
    return render_template('whitepaper.html')

@app.route('/static/css/all_styles.css', strict_slashes=False)
def assets_all_styles():
    return Response(concat_asset_files([
        "static/css/vendor-bootstrap-4.0.0-beta2.css",
        "static/css/alertify.css",
        "static/css/animate.css",
        "static/css/style.css",
        "static/css/common.css",
        "static/css/footer.css",
        "static/css/components/countdown-timer.css",
        "static/css/components/countdown-bar.css",
        "static/css/pages/common.css",
        "static/css/pages/team.css",
        "static/css/pages/token.css",
        "static/css/pages/product.css",
        "static/css/pages/singles.css",
        "static/css/pages/mobile.css",
        "static/css/pages/about.css",
        "static/css/pages/landing.css",
        "static/css/pages/video.css",
        "static/css/pages/videos.css",
        "static/css/pages/investors.css",
        "static/css/pages/developers.css",
        "static/css/pages/presale.css",
        "static/css/pages/whitepaper.css"
    ]), mimetype="text/css")

@app.route('/static/js/all_javascript.js', strict_slashes=False)
def assets_all_javascript():
    return Response(concat_asset_files([
        "static/js/vendor-jquery-3.2.1.min.js",
        "static/js/vendor-popper.min.js",
        "static/js/vendor-bootstrap.min.js",
        "static/js/vendor-alertify.js",
        "static/js/vendor-d3.min.js",
        "static/js/vendor-wow.min.js",
        "static/js/script.js",
        "static/js/countdown-timer.js",
        "static/js/yt-player.js",
        "static/js/videos.js",
        "static/js/youkuPlayer.js",
        "static/js/scrollspy.js",
    ], True), mimetype="application/javascript")

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
