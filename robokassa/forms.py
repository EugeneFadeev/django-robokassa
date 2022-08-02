# coding: utf-8
from __future__ import unicode_literals
import json

from hashlib import md5
from decimal import Decimal
from urllib.parse import urlencode, quote_plus
from django import forms

from robokassa.conf import LOGIN, PASSWORD1, PASSWORD2, TEST_MODE, STRICT_CHECK, FORM_TARGET, RECUR_FORM_TARGET, EXTRA_PARAMS
from robokassa.models import SuccessNotification


class BaseRobokassaForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(BaseRobokassaForm, self).__init__(*args, **kwargs)
        # создаем дополнительные поля
        for key in EXTRA_PARAMS:
            self.fields['shp'+key] = forms.CharField(required=False)
            if 'initial' in kwargs:
                self.fields['shp'+key].initial = kwargs['initial'].get(key, 'None')

    def _append_extra_part(self, standard_part, value_func):
        extra_part = ":".join(["%s=%s" % ('shp'+key, value_func('shp' + key)) for key in EXTRA_PARAMS])
        if extra_part:
            return ':'.join([standard_part, extra_part])
        return standard_part

    def extra_params(self):
        extra = {}
        for param in EXTRA_PARAMS:
            if ('shp'+param) in self.cleaned_data:
                extra[param] = self.cleaned_data['shp'+param]
        return extra

    def _get_signature(self):
        return md5(self._get_signature_string().encode('utf-8')).hexdigest().upper()

    def _get_signature_string(self):
        raise NotImplementedError


class RobokassaForm(BaseRobokassaForm):
    # Идентификатор магазина
    MerchantLogin = forms.CharField(max_length=20, initial=LOGIN)
    # требуемая к получению сумма
    OutSum = forms.DecimalField(min_value=0, max_digits=20, decimal_places=2, required=False)
    # Номер счета в магазине. Необязательный параметр, но мы настоятельно рекомендуем его использовать. Значение этого параметра должно быть уникальным для каждой оплаты.
    InvId = forms.IntegerField(min_value=0, required=False)
    # описание покупки
    Description = forms.CharField(max_length=1000, required=False)
    # контрольная сумма MD5
    SignatureValue = forms.CharField(max_length=32)
    # предлагаемая валюта платежа
    IncCurrLabel = forms.CharField(max_length=10, required=False)
    # язык общения с клиентом (en или ru)
    Culture = forms.CharField(max_length=10, required=False)
    # e-mail пользователя
    Email = forms.CharField(max_length=100, required=False)
    # Рекуррентный платеж
    Recurring = forms.CharField(max_length=10, required=False)
    # Товарные позиции
    Receipt = forms.CharField(max_length=2000, required=False)
    # Параметр с URL'ом, на который форма должны быть отправлена.
    # Может пригодиться для использования в шаблоне.
    target = FORM_TARGET

    def __init__(self, *args, **kwargs):

        super(RobokassaForm, self).__init__(*args, **kwargs)

        if TEST_MODE is True:
            self.fields['isTest'] = forms.BooleanField(required=False)
            self.fields['isTest'].initial = 1

        # скрытый виджет по умолчанию
        for field in self.fields:
            self.fields[field].widget = forms.HiddenInput()

        self.fields['SignatureValue'].initial = self._get_signature()

    def get_target_url(self):
        return self.target

    def get_post_data(self):
        """ Получить Data для POST запроса, соответствующими значениям полей в
        форме.
        """

        def _initial(name, field):
            val = self.initial.get(name, field.initial)
            if not val:
                return val
            if isinstance(val, Decimal):
                return str(val.quantize(Decimal("1.00")))
            return str(val)

        fields = {name: _initial(name, field) for name, field in list(self.fields.items()) if _initial(name, field) }
        return fields
    
    def get_redirect_url(self):
        """ Получить URL с GET-параметрами, соответствующими значениям полей в
        форме. Редирект на адрес, возвращаемый этим методом, эквивалентен
        ручной отправке формы методом GET.
        """

        def _initial(name, field):
            val = self.initial.get(name, field.initial)
            if not val:
                return val
            return str(val).encode('1251')

        fields = [(name, _initial(name, field))
                  for name, field in list(self.fields.items())
                  if _initial(name, field)
                  ]
        params = urlencode(fields)
        return self.target + '?' + params

    def _get_signature_string(self):
        def _val(name):
            value = self.initial[name] if name in self.initial else self.fields[name].initial
            if value is None:
                return ''
            return str(value)

        hash_string_array = [_val('MerchantLogin'), _val('OutSum'), _val('InvId')]

#         if _val('UserIP'):
#             hash_string_array.append(_val('UserIP'))
        if _val('Receipt'):
            hash_string_array.append(_val('Receipt'))

        hash_string_array.append(PASSWORD1)

        for key in EXTRA_PARAMS:
            hash_string_array.append(f"shp{key}={_val(key)}")

        return ':'.join(hash_string_array)


class RobokassaRecurringForm(BaseRobokassaForm):
    # login магазина в обменном пункте
    MerchantLogin = forms.CharField(max_length=20, initial=LOGIN)
    # требуемая к получению сумма
    OutSum = forms.DecimalField(min_value=0, max_digits=20, decimal_places=2, required=False)
    # номер счета в магазине (должен быть уникальным для магазина)
    InvoiceID = forms.IntegerField(min_value=0, required=True)
    # номер счета в магазине (должен быть уникальным для магазина)
    PreviousInvoiceID = forms.IntegerField(min_value=0, required=False)

    # описание покупки
    Description = forms.CharField(max_length=100, required=False)
    # контрольная сумма MD5
    SignatureValue = forms.CharField(max_length=32)
    # e-mail пользователя
    Email = forms.CharField(max_length=100, required=False)
    # язык общения с клиентом (en или ru)
    Culture = forms.CharField(max_length=10, required=False)
    # Товарные позиции
    Receipt = forms.CharField(max_length=2000, required=False)

    # Параметр с URL'ом, на который форма должны быть отправлена.
    # Может пригодиться для использования в шаблоне.
    target = RECUR_FORM_TARGET

    def __init__(self, *args, **kwargs):

        super(RobokassaRecurringForm, self).__init__(*args, **kwargs)

        if TEST_MODE is True:
            self.fields['isTest'] = forms.BooleanField(required=False)
            self.fields['isTest'].initial = 1

        # скрытый виджет по умолчанию
        for field in self.fields:
            self.fields[field].widget = forms.HiddenInput()

        self.fields['SignatureValue'].initial = self._get_signature()

    def get_target_url(self):
        return self.target

    def get_post_data(self):
        """ Получить Data для POST запроса, соответствующими значениям полей в
        форме.
        """

        def _initial(name, field):
            val = self.initial.get(name, field.initial)
            if not val:
                return val
            if isinstance(val, Decimal):
                return str(val.quantize(Decimal("1.00")))
            return str(val)

        fields = {name: _initial(name, field) for name, field in list(self.fields.items()) if _initial(name, field) }
        return fields
    
    def get_redirect_url(self):
        """ Получить URL с GET-параметрами, соответствующими значениям полей в
        форме. Редирект на адрес, возвращаемый этим методом, эквивалентен
        ручной отправке формы методом GET.
        """

        def _initial(name, field):
            val = self.initial.get(name, field.initial)
            if not val:
                return val
            return str(val).encode('1251')

        fields = [(name, _initial(name, field))
                  for name, field in list(self.fields.items())
                  if _initial(name, field)
                  ]
        params = urlencode(fields)
        return self.target + '?' + params

    def _get_signature_string(self):
        def _val(name):
            value = self.initial[name] if name in self.initial else self.fields[name].initial
            if value is None:
                return ''
            return str(value)

        hash_string_array = [_val('MerchantLogin'), _val('OutSum'), _val('InvoiceID')]

#         if _val('UserIP'):
#             hash_string_array.append(_val('UserIP'))
        if _val('Receipt'):
            hash_string_array.append(_val('Receipt'))

        hash_string_array.append(PASSWORD1)

        for key in EXTRA_PARAMS:
            hash_string_array.append(f"shp{key}={_val(key)}")

        return ':'.join(hash_string_array)


class ResultURLForm(BaseRobokassaForm):
    """Форма для приема результатов и проверки контрольной суммы"""
    OutSum = forms.CharField(max_length=15)
    InvId = forms.IntegerField(min_value=0)
    SignatureValue = forms.CharField(max_length=32)

    def clean(self):
        try:
            signature = self.cleaned_data['SignatureValue'].upper()
            if signature != self._get_signature():
                raise forms.ValidationError('Ошибка в контрольной сумме')
        except KeyError:
            raise forms.ValidationError('Пришли не все необходимые параметры')

        return self.cleaned_data

    def _get_signature_string(self):
        _val = lambda name: str(self.cleaned_data[name])

        hash_string_array = [_val('OutSum'), _val('InvId')]
        hash_string_array.append(PASSWORD2)

        for key in EXTRA_PARAMS:
            hash_string_array.append(f"shp{key}={_val(key)}")

        return ':'.join(hash_string_array)


class _RedirectPageForm(ResultURLForm):
    """Форма для проверки контрольной суммы на странице Success"""

    Culture = forms.CharField(max_length=10)

    def _get_signature_string(self):
        _val = lambda name: str(self.cleaned_data[name])

        hash_string_array = [_val('OutSum'), _val('InvId')]
        hash_string_array.append(PASSWORD1)

        for key in EXTRA_PARAMS:
            hash_string_array.append(f"shp{key}={_val(key)}")

        return ':'.join(hash_string_array)


class SuccessRedirectForm(_RedirectPageForm):
    """Форма для обработки страницы Success с дополнительной защитой. Она
    проверяет, что ROBOKASSA предварительно уведомила систему о платеже,
    отправив запрос на ResultURL."""

    def clean(self):
        data = super(SuccessRedirectForm, self).clean()
        if STRICT_CHECK:
            if not SuccessNotification.objects.filter(InvId=data['InvId']):
                raise forms.ValidationError('От ROBOKASSA не было предварительного уведомления')
        return data


class FailRedirectForm(BaseRobokassaForm):
    """Форма приема результатов для перенаправления на страницу Fail"""
    OutSum = forms.CharField(max_length=15)
    InvId = forms.IntegerField(min_value=0)
    Culture = forms.CharField(max_length=10)
