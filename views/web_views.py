from collections import OrderedDict
from datetime import datetime
import os
import re
import sys
import calendar
import random

from flask_cors import CORS, cross_origin
from app import app
from database import db, db_models

from config import constants, universal, partner_details
from flask import (
    jsonify,
    redirect,
    render_template,
    request,
    flash,
    g,
    url_for,
    Response,
    make_response,
    stream_with_context,
    session,
)
from flask_babel import gettext, Babel, Locale
from util.recaptcha import ReCaptcha
from logic.emails import mailing_list
from logic.scripts import update_token_insight as insight
from logic.views import social_stats
import requests

from util.ip2geo import get_country
from util.misc import sort_language_constants, get_real_ip, concat_asset_files, log

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

import json

from logic.scripts import token_stats, drops

# Translation: change path of messages.mo files
app.config["BABEL_TRANSLATION_DIRECTORIES"] = "../translations"
babel = Babel(app)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

recaptcha = ReCaptcha(app=app)
if not recaptcha.is_enabled:
    log("Warning: recaptcha is not is_enabled")

selected_lang = ""


@app.before_request
def beforeRequest():
    """ Processing of URL before any routing """
    # Force https on prod
    if constants.HTTPS:
        if not request.url.startswith("https") and "ogn.dev" not in request.url_root:
            return redirect(request.url.replace("http", "https", 1))

    selected_lang = None
    if request.view_args and "lang_code" in request.view_args:
        selected_lang = request.view_args.pop("lang_code")
    elif request.args and "lang_code" in request.args:
        selected_lang = request.args["lang_code"]
    g.lang_code = selected_lang

    if selected_lang in constants.LANGUAGES:
        g.current_lang = selected_lang
    else:
        # Use Accept-Languages header for fallback
        g.current_lang = get_locale()

    g.metadata = {}
    g.metadata["image"] = "https://www.originprotocol.com/static/img/fb-og-img.png"
    g.metadata["title"] = gettext("Origin Protocol")
    g.metadata["description"] = gettext(
        "Origin Protocol is bringing NFTs and DeFi to the masses"
    )
    g.metadata["url"] = "https://www.originprotocol.com"

@app.after_request
def after_request(response):
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    return response

@app.route("/", strict_slashes=False)
def root():
    def filter_featured_videos(video):
        return video["landing_page_featured"]

    all_videos = json.load(open("static/files/videos.json"))
    featured_videos = filter(filter_featured_videos, all_videos)
    return render_template("landing.html", featured_videos=featured_videos)


@app.route("/robots.txt", strict_slashes=False)
def robots():
    return app.send_static_file("files/robots.txt")


@app.route("/apple-app-site-association", strict_slashes=False)
def apple_app_site_association():
    return app.send_static_file("files/apple-app-site-association.json")


@app.route("/mobile", strict_slashes=False)
@app.route("/<lang_code>/mobile", strict_slashes=False)
def mobile():
    return render_template("mobile.html")


@app.route("/singles", strict_slashes=False)
@app.route("/<lang_code>/singles", strict_slashes=False)
def singles():
    return render_template("singles.html")


@app.route("/mobile/apk", strict_slashes=False)
@app.route("/<lang_code>/mobile/apk", strict_slashes=False)
def mobile_apk():
    req = requests.get(constants.APK_URL, stream=True)
    return Response(
        stream_with_context(req.iter_content(chunk_size=1024)),
        headers={
            "content-type": req.headers["content-type"],
            "content-disposition": "attachment;filename=origin-marketplace.apk",
        },
    )


@app.route("/<lang_code>/", strict_slashes=False)
# @app.route("/", strict_slashes=False)
def index():
    def filter_featured_videos(video):
        return video["landing_page_featured"]

    all_videos = json.load(open("static/files/videos.json"))
    featured_videos = random.sample(json.load(open("static/files/videos.json")), k=3)
    # filter(filter_featured_videos, all_videos)

    # fetch the current yield for OUSD
    try:
        r = requests.get('https://analytics.ousd.com/api/v1/apr/trailing', timeout=2)
        apy = r.json()['apy']
    except:
        apy = "~20.0"

    # check if it's a legit language code
    if g.lang_code in constants.LANGUAGES:
        return render_template("landing.html", featured_videos=featured_videos, ousd_apy=apy)
    # nope, it's a 404
    else:
        return render_template("404.html"), 404


@app.route("/team", strict_slashes=False)
@app.route("/<lang_code>/team", strict_slashes=False)
def team():
    # fetch our list of contributors from the DB
    contributors = db_models.Contributor.query.all()

    return render_template("team.html", contributors=contributors)


@app.route("/admin", strict_slashes=False)
@app.route("/<lang_code>/admin", strict_slashes=False)
def admin():
    return redirect("https://admin.staging.originprotocol.com", code=302)


@app.route("/presale", strict_slashes=False)
@app.route("/<lang_code>/presale", strict_slashes=False)
def presale():
    return redirect("/ogn-token", code=302)


@app.route("/tokens", strict_slashes=False)
@app.route("/<lang_code>/tokens", strict_slashes=False)
def tokens():
    return redirect("/ogn-token", code=302)


@app.route("/whitepaper.pdf", strict_slashes=False)
@app.route("/<lang_code>/whitepaper.pdf", strict_slashes=False)
def whitepaper():
    localized_filename = "whitepaper_v18_%s.pdf" % g.current_lang.lower()
    whitepaper_path = os.path.join(
        app.root_path, "..", "static", "docs", localized_filename
    )
    if os.path.isfile(whitepaper_path):
        return app.send_static_file("docs/%s" % localized_filename)
    else:
        # Default to English
        return app.send_static_file("docs/whitepaper_v19.pdf")


@app.route("/product-brief", strict_slashes=False)
@app.route("/<lang_code>/product-brief", strict_slashes=False)
def product_brief():
    return redirect("/whitepaper", code=302)

@cross_origin()
@app.route("/mailing-list/join", methods=["POST"], strict_slashes=False)
def join_mailing_list():
    if not "email" in request.form:
        return jsonify(success=False, message=gettext("Missing email"))
    email = request.form["email"]
    if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
        return jsonify(success=False, message=gettext("Invalid email"))

    # optional fields
    source = request.form.get("source") or None
    eth_address = request.form.get("eth_address") or None
    first_name = request.form.get("first_name") or None
    last_name = request.form.get("last_name") or None
    full_name = request.form.get("name") or None
    if not full_name and (first_name or last_name):
        full_name = " ".join(filter(None, (first_name, last_name)))
    phone = request.form.get("phone") or None
    ip_addr = request.form.get("ip_addr") or get_real_ip()
    country_code = request.form.get("country_code") or get_country(ip_addr)
    dapp_user = 1 if "dapp_user" in request.form else 0
    investor = 1 if "investor" in request.form else 0
    backfill = (
        request.form.get("backfill") or None
    )  # Indicates the request was made from an internal backfill script.

    new_user = False

    log("Updating mailing list for", email, eth_address)
    try:
        # Add an entry to the eth_contact DB table.
        if eth_address:
            log("Adding to wallet insights")
            insight.add_contact(
                address=eth_address,
                dapp_user=dapp_user,
                investor=investor,
                name=full_name,
                email=email,
                phone=phone,
                country_code=country_code,
            )

        # Add an entry to the email_list table.
        log("Adding to mailing list")
        new_contact = mailing_list.add_contact(
            email, first_name, last_name, ip_addr, country_code
        )

        # If it is a new contact and not a backfill, send a welcome email.
        if new_contact and not backfill:
            log("Sending welcome email")
            mailing_list.send_welcome(email, source)

        # Add the entry to the Sendgrid contact list.
        if new_contact:
            new_user = True
            log("Adding to Sendgrid contact list")
            mailing_list.add_sendgrid_contact(
                email=email,
                full_name=full_name,
                country_code=country_code,
                dapp_user=dapp_user,
            )

    except Exception as err:
        log("Failure: %s" % err)
        return jsonify(success=False, message=str(err))

    if not new_user:
        return jsonify(success=True, message=gettext("You're already registered!"))

    return jsonify(success=True, message=gettext("Thanks for signing up!"))


@app.route("/presale/join", methods=["POST"], strict_slashes=False)
def join_presale():
    full_name = request.form["full_name"]
    email = request.form["email"]
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
        return jsonify(
            success=False, message=gettext("Select your country of citizenship")
        )
    if not desired_allocation:
        return jsonify(
            success=False, message=gettext("Please enter your desired allocation")
        )
    if not desired_allocation_currency:
        return jsonify(success=False, message=gettext("Select a currency"))
    if not recaptcha.verify():
        return jsonify(
            success=False, message=gettext("Please prove you are not a robot.")
        )
    feedback = mailing_list.presale(
        full_name,
        email,
        desired_allocation,
        desired_allocation_currency,
        citizenship,
        sending_addr,
        request.remote_addr,
    )
    mailing_list.add_sendgrid_contact(email, full_name, citizenship)
    insight.add_contact(sending_addr, name=full_name, email=email, presale_interest=1)
    flash(feedback)
    return jsonify(success=True, message=gettext("OK"))


@app.route("/mailing-list/unsubscribe", methods=["GET"], strict_slashes=False)
def unsubscribe():
    email = request.args.get("email")
    if not email or not re.match(
        r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email
    ):
        return gettext("Please enter a valid email address")

    try:
        mailing_list.unsubscribe(email)
        mailing_list.unsubscribe_sendgrid_contact(email)
        feedback = gettext("You have been unsubscribed")
    except Exception as err:
        log("Failure: %s" % err)
        feedback = gettext("Ooops, something went wrong")
    flash(feedback)
    return redirect("/en/", code=302)


# do not remove
# used by coinmarketcap.com to calculate total supply and circulating supply of OGN
@app.route("/total-ogn", methods=["GET"], strict_slashes=False)
@app.route("/<lang_code>/total-ogn", methods=["GET"], strict_slashes=False)
def total_ogn():
    return total_supply("0x8207c1ffc5b6804f6024322ccf34f29c3541ae26")

# do not remove
# used by coinmarketcap.com to calculate total supply and circulating supply of OUSD
@app.route("/total-ousd", methods=["GET"], strict_slashes=False)
@app.route("/<lang_code>/total-ousd", methods=["GET"], strict_slashes=False)
def total_ousd():
    return total_supply("0x2A8e1E676Ec238d8A992307B495b45B3fEAa5e86")

def total_supply(address):
    url = "https://api.etherscan.io/api?module=stats&action=tokensupply&contractaddress=%s&apikey=%s" % (address, constants.ETHERSCAN_KEY)
    response = requests.get(url)
    wei = response.json()["result"]
    return make_response(wei[:-18], 200)


@app.route("/social-stats", methods=["GET"], strict_slashes=False)
@app.route("/<lang_code>/social-stats", methods=["GET"], strict_slashes=False)
def fetch_social_stats():
    stats = social_stats.get_social_stats(g.current_lang)
    return jsonify({"stats": stats})


@app.route("/build-on-origin", strict_slashes=False)
@app.route("/<lang_code>/build-on-origin", strict_slashes=False)
def build_on_origin():
    return render_template("404.html"), 410


@app.route("/developers", strict_slashes=False)
@app.route("/<lang_code>/developers", strict_slashes=False)
def developers():
    return render_template("developers.html")


@app.route("/discord", strict_slashes=False)
@app.route("/<lang_code>/discord", strict_slashes=False)
def discord():
    return redirect(universal.DISCORD_URL, code=301)


@app.route("/ios", strict_slashes=False)
@app.route("/<lang_code>/ios", strict_slashes=False)
def ios():
    return redirect(universal.IOS_URL, code=301)


@app.route("/android", strict_slashes=False)
@app.route("/<lang_code>/android", strict_slashes=False)
def android():
    return redirect(universal.ANDROID_URL, code=301)


@app.route("/telegram", strict_slashes=False)
@app.route("/<lang_code>/telegram", strict_slashes=False)
def telegram():
    return redirect(universal.TELEGRAM_URL, code=301)

@app.route("/lupefiasco", strict_slashes=False)
@app.route("/<lang_code>/lupefiasco", strict_slashes=False)
def lupefiasco():
    return redirect(universal.LUPE_URL, code=301)

@app.route("/dapp", strict_slashes=False)
@app.route("/<lang_code>/dapp", strict_slashes=False)
def dapp():
    return redirect(universal.DAPP_URL, code=301)


@app.route("/rewards", strict_slashes=False)
@app.route("/<lang_code>/rewards", strict_slashes=False)
def rewards():
    return redirect(universal.REWARDS_URL, code=301)


@app.route("/reward/swag/fabruary_2020", strict_slashes=False)
@app.route("/<lang_code>/reward/swag/fabruary_2020", strict_slashes=False)
def swagRewards():
    return render_template("swagStore.html", hide_ogn_banner=True)


@app.route("/reward/stay_home_shop/april_2020", strict_slashes=False)
@app.route("/<lang_code>/reward/stay_home_shop/april_2020", strict_slashes=False)
def stayHomeRewards():
    return render_template("stayHomeStore.html", hide_ogn_banner=True)


@app.route("/reward/extension/march_2020", strict_slashes=False)
@app.route("/<lang_code>/reward/extension/march_2020", strict_slashes=False)
def extension_rewardsj():
    return render_template("extension-rewards.html", hide_ogn_banner=True)


@app.route("/partners", strict_slashes=False)
@app.route("/<lang_code>/partners", strict_slashes=False)
def partners():
    return render_template("404.html"), 410


@app.route("/about", strict_slashes=False)
@app.route("/<lang_code>/about", strict_slashes=False)
def about():
    return render_template("about.html")


@app.route("/investors", strict_slashes=False)
@app.route("/<lang_code>/investors", strict_slashes=False)
def investors():
    return render_template("investors.html")


@app.route("/product", strict_slashes=False)
@app.route("/<lang_code>/product", strict_slashes=False)
def product():
    return render_template("product.html")


@app.route("/ogn-token", strict_slashes=False)
@app.route("/<lang_code>/ogn-token", strict_slashes=False)
def ogn_token():
    data = token_stats.get_ogn_stats()
    binance_lang_code = constants.BINANCE_LOCALE_MAP[g.current_lang] or "en"

    return render_template(
        "ogn-token.html",
        binance_lang_code=binance_lang_code,
        ogn_stats=data["ogn_supply_stats"]
    )


@app.route("/video/<video_slug>", strict_slashes=False)
@app.route("/<lang_code>/video/<video_slug>", strict_slashes=False)
def video(video_slug):
    def remove_current_video(video):
        if video["slug"] == video_slug:
            return False
        else:
            return True

    def find_current_video(video):
        if video["slug"] == video_slug:
            return True
        else:
            return False

    def filter_featured_videos(video):
        return video["video_page_featured"]

    all_videos = json.load(open("static/files/videos.json"))

    featured_videos = filter(
        remove_current_video, filter(filter_featured_videos, all_videos)
    )

    videoList = list(filter(find_current_video, all_videos))
    if len(videoList) == 0:
        return render_template("404.html"), 404

    video = videoList[0]
    g.metadata["image"] = (
        "https://www.originprotocol.com/static/img/videos/" + video["hash"] + ".jpg"
    )
    g.metadata["title"] = video["title"]
    g.metadata["url"] = "https://www.originprotocol.com/video/" + video["slug"]
    return render_template("video.html", featured_videos=featured_videos, video=video)


@app.route("/videos", strict_slashes=False)
@app.route("/<lang_code>/videos", strict_slashes=False)
def videos():
    data = json.load(open("static/files/videos.json"))
    return render_template("videos.html", videos=data)


@app.route("/privacy", strict_slashes=False)
@app.route("/<lang_code>/privacy", strict_slashes=False)
def privacy():
    return render_template("privacy.html")


@app.route("/privacy/extension", strict_slashes=False)
@app.route("/<lang_code>/privacy/extension", strict_slashes=False)
def extension_privacy():
    return render_template("privacy-extension.html")


@app.route("/tos", strict_slashes=False)
@app.route("/<lang_code>/tos", strict_slashes=False)
def tos():
    return render_template("tos.html")

@app.route("/nft-terms", strict_slashes=False)
@app.route("/<lang_code>/nft-terms", strict_slashes=False)
def nft_terms():
    return render_template("nft-terms.html")


@app.route("/aup", strict_slashes=False)
@app.route("/<lang_code>/aup", strict_slashes=False)
def aup():
    return render_template("aup.html")


@app.route("/creator", strict_slashes=False)
@app.route("/<lang_code>/creator", strict_slashes=False)
def creator():
    return render_template("creator.html")

@app.route("/brave-customer-story", strict_slashes=False)
@app.route("/<lang_code>/brave-customer-story", strict_slashes=False)
def brave_dshop_pr():
    return render_template("brave-dshop-pr.html")

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


@app.route("/whitepaper", strict_slashes=False)
@app.route("/<lang_code>/whitepaper", strict_slashes=False)
def whitepaperv2():
    return render_template("whitepaper.html")

@app.route("/litepaper", strict_slashes=False)
@app.route("/<lang_code>/litepaper", strict_slashes=False)
def litepaper():
    return render_template("litepaper.html")


@app.route("/browser-extension", strict_slashes=False)
@app.route("/<lang_code>/browser-extension", strict_slashes=False)
def browser_extension():
    return render_template("browser-extension.html", hide_ogn_banner=False)


@app.route("/huobi-launch", strict_slashes=False)
@app.route("/<lang_code>/huobi-launch", strict_slashes=False)
def huobi_launch():
    return render_template("huobi-launch.html", hide_ogn_banner=True)


@app.route("/dshop", methods=["GET"], strict_slashes=False)
@app.route("/<lang_code>/dshop", strict_slashes=False)
def dshop():
    redirected = request.args.get("redirected")
    return render_template("dshop.html", hide_ogn_banner=True, redirected=redirected)


@app.route("/dashboard", strict_slashes=False)
@app.route("/<lang_code>/dashboard", strict_slashes=False)
def dashboard():
    data = token_stats.get_ogn_stats()

    # return render_template("dashboard.html")
    return render_template(
        "dashboard.html",
        hide_ogn_banner=True,
        ogn_stats=data["ogn_supply_stats"],
        supply_history=data["ogn_supply_history"],
        staked_data=data["ogn_staked_data"]
    )
    
@app.route("/nft", strict_slashes=False)
@app.route("/<lang_code>/nft", strict_slashes=False)
def nft():
    data = drops.get_drops()
    return render_template("nft.html", drops=data)

@app.route("/static/css/all_styles.css", strict_slashes=False)
def assets_all_styles():
    return Response(
        concat_asset_files(
            [
                "static/css/vendor-bootstrap-4.0.0-beta2.css",
                "static/css/vendor-owl.theme.default.min.css",
                "static/css/vendor-owl.carousel.min.css",
                "static/css/alertify.css",
                "static/css/animate.css",
                "static/css/style.css",
                "static/css/common.css",
                "static/css/footer.css",
                "static/css/components/countdown-timer.css",
                "static/css/components/countdown-bar.css",
                "static/css/components/countdown-hero-banner.css",
                "static/css/components/nft-banner.css",
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
                "static/css/pages/whitepaper.css",
                "static/css/pages/browser-extension.css",
                "static/css/pages/dshop.css",
                "static/css/pages/dashboard.css",
                "static/css/pages/nft.css",
                "static/css/components/nft-card.css",
            ]
        ),
        mimetype="text/css",
    )


@app.route("/static/js/all_javascript.js", strict_slashes=False)
def assets_all_javascript():
    return Response(
        concat_asset_files(
            [
                "static/js/vendor-jquery-3.2.1.min.js",
                "static/js/vendor-popper.min.js",
                "static/js/vendor-bootstrap.min.js",
                "static/js/vendor-alertify.js",
                "static/js/vendor-d3.min.js",
                "static/js/vendor-wow.min.js",
                "static/js/vendor-chart.min.js",
                "static/js/vendor-moment.min.js",
                "static/js/vendor-chartjs-adapter-moment.min.js",
                "static/js/vendor-owl.carousel.min.js",
                "static/js/script.js",
                "static/js/countdown-timer.js",
                "static/js/yt-player.js",
                "static/js/videos.js",
                "static/js/youkuPlayer.js",
                "static/js/scrollspy.js",
                "static/js/dashboard.js",
                "static/js/dshop.js",
            ],
            True,
        ),
        mimetype="application/javascript",
    )


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@babel.localeselector
def get_locale():
    browser_language = request.accept_languages.best_match(constants.LANGUAGES) or "en"
    return g.get("current_lang", browser_language)


@app.context_processor
def inject():
    return {"now": datetime.utcnow(), "universal": universal}


@app.context_processor
def inject_conf_var():
    current_language = get_locale()
    try:
        current_language_direction = Locale(current_language).text_direction
    except:
        current_language_direction = "ltr"
    try:
        available_languages = OrderedDict(
            [
                (lang, Locale(lang).get_language_name(lang).capitalize())
                for lang in sort_language_constants()
            ]
        )
    except:
        available_languages = {"en": "English"}

    # important (!) date needs to be in that exact format (along with minutes/seconds present).
    # also enter the date in UTC format -> greenwich mean time
    startDate = "2020/1/7 3:30:00 GMT"
    launchDate = "2020/1/9 3:00:00 GMT"

    return dict(
        CURRENT_LANGUAGE=current_language,
        CURRENT_LANGUAGE_DIRECTION=current_language_direction,
        AVAILABLE_LANGUAGES=available_languages,
        DOMAIN=request.headers["Host"],
        OGN_LAUNCH_START_DATE=startDate,
        OGN_LAUNCH_DATE=launchDate,
        OGN_ALREADY_LAUNCHED=datetime.strptime(launchDate, "%Y/%m/%d %H:%M:%S GMT")
        < datetime.utcnow(),
    )
