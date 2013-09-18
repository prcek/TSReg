# -*- coding: utf-8 -*-

import wtforms


class DisabledTextField(wtforms.fields.TextField):
    def __call__(self, *args, **kwargs):
        kwargs.setdefault('disabled', True)
        return super(DisabledTextField, self).__call__(*args, **kwargs)

class InputRequired(wtforms.validators.InputRequired):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('message',u'Prosím vyplň tuto položku')
        return super(InputRequired, self).__init__(*args, **kwargs)

class OptionalValue(wtforms.validators.Optional):
	pass

class YearRequired(wtforms.validators.NumberRange):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('message',u'Uveď platný rok')
        kwargs.setdefault('min',1900)
        kwargs.setdefault('max',2100)
        return super(YearRequired, self).__init__(*args, **kwargs)

class EmailRequired(wtforms.validators.Email):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('message',u'Uveď platný email')
        return super(EmailRequired, self).__init__(*args, **kwargs)

