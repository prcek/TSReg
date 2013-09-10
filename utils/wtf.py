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

