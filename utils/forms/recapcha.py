from recaptcha.client import captcha
from django.conf import settings
from django import forms
from django.utils.safestring import mark_safe

class ReCaptcha(forms.Widget):
    input_type = None # Subclasses must define this.

    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        html = u"<script>var RecaptchaOptions = {theme : '%s'};</script>" % (
            final_attrs.get('theme', 'white'))
        html += captcha.displayhtml(settings.RECAPTCHA_PUBLIC)
        return mark_safe(html)

    def value_from_datadict(self, data, files, name):
        return {
            'recaptcha_challenge_field': data.get('recaptcha_challenge_field', None),
            'recaptcha_response_field': data.get('recaptcha_response_field', None),
        }

# hack: Inherit from FileField so a hack in Django passes us the
# initial value for our field, which should be set to the IP
class ReCaptchaField(forms.FileField):
    widget = ReCaptcha
    default_error_messages = {
        'invalid-site-public-key': u"Invalid public key",
        'invalid-site-private-key': u"Invalid private key",
        'invalid-request-cookie': u"Invalid cookie",
        'incorrect-captcha-sol': u"Invalid entry, please try again.",
        'verify-params-incorrect': u"The parameters to verify were incorrect, make sure you are passing all the required parameters.",
        'invalid-referrer': u"Invalid referrer domain",
        'recaptcha-not-reachable': u"Could not contact reCAPTCHA server",
    }

    def clean(self, data, initial):
        if initial is None or initial == '':
            raise Exception("ReCaptchaField requires the client's IP be set to the initial value")
        ip = initial
        resp = captcha.submit(data.get("recaptcha_challenge_field", None),
                              data.get("recaptcha_response_field", None),
                              settings.RECAPTCHA_SECRET, ip)
        if not resp.is_valid:
            raise forms.ValidationError(self.default_error_messages.get(
                    resp.error_code, "Unknown error: %s" % (resp.error_code)))    
