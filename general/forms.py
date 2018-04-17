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
    template_name = 'new_templates/widget_photo_input.html'

    def get_context(self, name, value, attrs=None):
        return {'widget': {'name': name, 'value': value, 'attrs': attrs}}

    def render(self, name, value, attrs=None):
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)


class AmountInput(forms.NumberInput):
    template_name = 'new_templates/widget_currency_wrapper.html'

    def get_context(self, name, value, attrs=None):
        return {'widget': {'name': name, 'value': value, 'attrs': attrs}}

    def render(self, name, value, attrs=None):
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(super(AmountInput, self).render(name, value, attrs) + template)


class ReceiverInput(forms.TextInput):
    input_type = 'text'
    template_name = 'new_templates/widget_receiver.html'

    def get_context(self, name, value, attrs=None):
        return {'widget': {'name': name, 'value': value, 'attrs': attrs}}

    def render(self, name, value, attrs=None):
        attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(super(ReceiverInput, self).render(name, value, attrs) + template)


class ReceiverPayInput(ReceiverInput):
    template_name = 'new_templates/widget_receiver_pay.html'


class ToggleSwitch(forms.CheckboxInput):
    input_type = 'checkbox'
    template_name = 'new_templates/widget_toggle_switch.html'

    def get_context(self, name, value, attrs=None):
        return {'widget': {'name': name, 'value': value, 'attrs': attrs}}

    def render(self, name, value, attrs=None):
        attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)
