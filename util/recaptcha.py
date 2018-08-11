"""Flask extension that adds a context processor for adding Google's reCAPTCHA
to a form."""

from flask import request
from jinja2 import Markup
import requests


class DEFAULTS(object):
    # Default reCAPTCHA settings
    IS_ENABLED = True
    THEME = "light"
    TYPE = "image"
    SIZE = "normal"
    TABINDEX = 0
    INVISIBLE = "invisible"
    ELEMENT_ID = "id_captcha"


class ReCaptcha(object):

    VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"

    def __init__(self, app=None, site_key=None, secret_key=None,
                 is_enabled=True, **kwargs):
        if app:
            self.init_app(app=app)
        else:
            self.site_key = site_key
            self.secret_key = secret_key
            self.is_enabled = is_enabled
            self.theme = kwargs.get('theme', DEFAULTS.THEME)
            self.type = kwargs.get('type', DEFAULTS.TYPE)
            self.size = kwargs.get('size', DEFAULTS.SIZE)
            self.tabindex = kwargs.get('tabindex', DEFAULTS.TABINDEX)
            self.element_id = kwargs.get('element_id', DEFAULTS.ELEMENT_ID)

    def init_app(self, app=None):
        self.__init__(
            site_key=app.config.get("RECAPTCHA_SITE_KEY"),
            secret_key=app.config.get("RECAPTCHA_SECRET_KEY"),
            is_enabled=app.config.get("RECAPTCHA_ENABLED", DEFAULTS.IS_ENABLED),
            theme=app.config.get("RECAPTCHA_THEME", DEFAULTS.THEME),
            type=app.config.get("RECAPTCHA_TYPE", DEFAULTS.TYPE),
            size=app.config.get("RECAPTCHA_SIZE", DEFAULTS.SIZE),
            tabindex=app.config.get("RECAPTCHA_TABINDEX", DEFAULTS.TABINDEX),
            element_id=app.config.get(
                "RECAPTCHA_ELEMENT_ID",
                DEFAULTS.ELEMENT_ID
            )
        )

        @app.context_processor
        def inject_recaptcha_processor():
            # Jinja2 context processor to add the recaptcha function to the
            # template context
            def _inject_recaptcha(form_id=None, callback=None):
                return Markup(
                    self.inject_recaptcha(form_id=form_id, callback=callback)
                )
            return dict(recaptcha=_inject_recaptcha)

    def inject_recaptcha(self, form_id=None, callback=None):
        """Returns the markup required for adding a reCAPTCHA challenge to an
        existing form.

        Args:
            form_id: The ID of the form to add the reCAPTCHA to.
            callback: A JavaScript function to execute after the reCAPTCHA
                challenge has been executed.

        Returns:
            str: HTML/JS markup to be injected into the form.
        """
        if not self.is_enabled:
            # reCAPTCHA not enabled in settings, don't inject anything
            return ""

        if self.size == DEFAULTS.INVISIBLE:
            # Invisible reCAPTCHA
            return """
                <div id="{ELEMENT_ID}"></div>
                <script>
                  var recaptchaCallback = function(token) {{
                    // reCAPTCHA has been processed
                    var captcha = document.getElementById("{ELEMENT_ID}"),
                        fields = captcha.getElementsByTagName('textarea');
                    if(!fields.length) return;
                    // Add the reCAPTCHA token to the form
                    fields[0].value = grecaptcha.getResponse(recaptchaId);
                    if({CALLBACK}) {{
                      {CALLBACK}();
                    }}
                    // Reset the reCAPTCHA in case form submission was not
                    // successful, e.g. server side validation failure
                    grecaptcha.reset();
                  }};

                  var recaptchaOnloadCallback = function() {{
                     var el = document.getElementById("{ELEMENT_ID}"),
                         widget_id,
                         opts = [];
                     opts['sitekey'] = "{SITE_KEY}";
                     opts['callback'] = 'recaptchaCallback';
                     opts['size'] = "{SIZE}";
                     recaptchaId = grecaptcha.render(el, opts);
                  }};

                  var formElement = document.getElementById("{FORM_ID}")
                  formElement.addEventListener("submit", function(event) {{
                    event.preventDefault();
                    grecaptcha.execute(recaptchaId);
                  }});
                </script>

                <script src="https://www.google.com/recaptcha/api.js?onload=recaptchaOnloadCallback&render=explicit" async defer></script>
                """.format(
                    SITE_KEY=self.site_key,
                    SIZE=self.size,
                    ELEMENT_ID=self.element_id,
                    CALLBACK=callback,
                    FORM_ID=form_id
                )
        else:
            # Non-invisible reCAPTCHA
            return """
                <script src='//www.google.com/recaptcha/api.js'></script>
                <div class="g-recaptcha"
                    data-sitekey="{SITE_KEY}"
                    data-theme="{THEME}"
                    data-type="{TYPE}"
                    data-size="{SIZE}"
                    data-tabindex="{TABINDEX}">
                </div>
            """.format(
                SITE_KEY=self.site_key,
                THEME=self.theme,
                TYPE=self.type,
                SIZE=self.size,
                TABINDEX=self.tabindex
            )


    def verify(self, response=None, remote_ip=None):
        """Verifies that a reCAPTCHA response is valid.

        Args:
            response: The response token from the completed reCAPTCHA.
            remote_ip: The IP address of client who completed the reCAPTCHA.

        Returns:
            bool: True if response was valid, False otherwise.
        """
        if not self.is_enabled:
            return True

        data = {
            "secret": self.secret_key,
            "response": response or request.form.get('g-recaptcha-response'),
            "remoteip": remote_ip or request.environ.get('REMOTE_ADDR')
        }

        response = requests.get(self.VERIFY_URL, params=data)
        if response.status_code == 200:
            return response.json()["success"]

        return False
