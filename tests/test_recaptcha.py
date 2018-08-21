from flask import Flask
from util.recaptcha import ReCaptcha


def test_recaptcha_enabled(app):
    recaptcha = ReCaptcha(site_key="SITE_KEY", secret_key="SECRET_KEY")
    assert isinstance(recaptcha, ReCaptcha)
    assert recaptcha.is_enabled == True
    assert "script" in recaptcha.inject_recaptcha()
    assert recaptcha.verify(response="None", remote_ip="0.0.0.0") == False


def test_recaptcha_enabled_flask(app):
    recaptcha = ReCaptcha(app=app)
    assert isinstance(recaptcha, ReCaptcha)
    assert recaptcha.is_enabled == True
    assert "script" in recaptcha.inject_recaptcha()
    assert recaptcha.verify(response="None", remote_ip="0.0.0.0") == False


def test_recaptcha_disabled(app):
    recaptcha = ReCaptcha(site_key="SITE_KEY", secret_key="SECRET_KEY", is_enabled=False)
    assert recaptcha.is_enabled == False
    assert recaptcha.inject_recaptcha() == ""
    assert recaptcha.verify(response="None", remote_ip="0.0.0.0") == True


def test_recaptcha_disabled_flask(app):
    app.config.update({
        "RECAPTCHA_ENABLED": False
    })
    recaptcha = ReCaptcha(app=app)
    assert recaptcha.is_enabled == False
    assert recaptcha.inject_recaptcha() == ""
    assert recaptcha.verify(response="None", remote_ip="0.0.0.0") == True
