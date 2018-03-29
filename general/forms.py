from django import forms
from django.template import loader
from django.utils.safestring import mark_safe

# *** HACK ALERT ***
# Monkeypatch some form things so the defaults are nicer:
# Import this module from somewhere like models to be sure the patch is loaded.

# Monkeypatch forms.CharField so it strips off leading/trailing whitespace
# on input to clean() before it is processed.  (Validation will fail if only
# whitespace is input into required fields.)
def strip_input(func):
    def decorated_func(self, value):
        if isinstance(value, basestring):
            value = value.strip()
        return func(self, value)
    decorated_func.__name__ = func.__name__
    decorated_func.__module__ == func.__module__
    return decorated_func

forms.CharField.clean = strip_input(forms.CharField.clean)

# Set required rows to class="required".
forms.BaseForm.required_css_class = "required"


class PhotoInput(forms.FileInput):
    template_name = 'new_templates/photo_widget.html'

    def get_context(self, name, value, attrs=None):
        return {'widget': {'name': name, 'value': value, 'attrs': attrs}}

    def render(self, name, value, attrs=None):
        rendered = super(PhotoInput, self).render(name, None, attrs=attrs)
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(rendered+template)
