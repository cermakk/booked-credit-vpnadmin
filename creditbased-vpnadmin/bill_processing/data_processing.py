# -*- coding: utf-8 -*-
import logging
import datetime
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.utils.translation import ugettext, ugettext_lazy as _
from creditservices.models import CompanyInfo
from creditservices.signals import processCredit
from vpnadmin.models import PhoneServiceInfo
from valueladder.models import Thing


PROCESSING_FEE = getattr(settings, 'PROCESSING_FEE', 0)


class DataProcessingError(Exception):
    pass


def calculate_user(cInfo, phoneInfo, parsed):
    """
    TODO: calculate how much will given user pay for what.
    """

def calculate_charging(parsed_data):
    """
    Creates set of dicts {'service': price, ...}
    They already contains what is a user charged for in VPN manner.
    This is data for summary view. If all is right, submit triggers processing.
    """
    data = {}
#    total = {
#        'inVPN': datetime.timedelta(),
#        'outVPN': datetime.timedelta(),
#        'sms': 0,
#        'extra': 0
#    }
    for num, pinfo in parsed_data.items():
        try:
            cInfo = CompanyInfo.objects.get(phone=num)
            phoneInfo = PhoneServiceInfo.objects.get(user=cInfo.user)
        except PhoneServiceInfo.DoesNotExist:
            m = 'Phone service info for %s not exists' % cInfo.user
            raise DataProcessingError(m)
        except CompanyInfo.DoesNotExist:
            raise DataProcessingError('Company (phone %s) not exists' % num)        
        
        data[phoneInfo] = calculate_user(cInfo, phoneInfo, pinfo)
        
#        total['inVPN'] += inVPN
#        total['outVPN'] += outVPN
#        total['sms'] += nonVPNSMS
#        total['extra'] += sum(extra.values())

    total['inVPNMins'] = _convertToMinutes(total['inVPN'])
    total['outVPNMins'] = _convertToMinutes(total['outVPN'])

    expectedInvoicePrice = total['extra'] + 5526
#    if total['outVPNMins'] > FREE_MINS_COUNT:
#        expectedInvoicePrice += \
#            ((total['outVPNMins'] - FREE_MINS_COUNT) * MINUTE_PRICE)
#    if total['sms'] > FREE_SMS_COUNT:
#        expectedInvoicePrice += \
#            ((total['sms'] - FREE_SMS_COUNT) * SMS_PRICE)

    return data, expectedInvoicePrice, total


def process_charging(charging):
    if cinfo.user_id == settings.OUR_COMPANY_ID:
        return # do not charge myself
        
    price = sum(charging.values())
    currency = Thing.objects.get_default()
    contractor = CompanyInfo.objects.get_our_company_info()
    details = '\n'.join(['%s:%s' % (k, v) for k, v in charging.items()])
    
    # subtract credit
    currCredit = processCredit(cinfo, -price, currency, details,
                               contractor.bankaccount)

    # send info mail
    mailContent = render_to_string('vpnadmin/infoMail.html', {
        'invoice': charging,
        'state': currCredit,
        'billURL': billURL,
        'price': price,
        'cinfo': cinfo,
        'domain': Site.objects.get_current(),
    })
    subject = ugettext('phone service info')
    cinfo.user.email_user(subject, mailContent)


def _convertToTimeDelta(time):
    parts = time.split(':')
    return datetime.timedelta(hours=int(parts[0]),
        minutes=int(parts[1]), seconds=int(parts[2]))


def _convertToMinutes(time):
    return (time.days * 24 * 60) + (time.seconds / 60)
