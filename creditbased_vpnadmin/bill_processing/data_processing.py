# -*- coding: utf-8 -*-
import datetime
from django.conf import settings
from creditservices.models import CompanyInfo
from creditbased_vpnadmin.models import PhoneServiceInfo


PROCESSING_FEE = getattr(settings, 'PROCESSING_FEE', 0)


class DataProcessingError(Exception):
    pass


def create_service_classes(cInfo, phoneInfo, parsed):
    volani = 0
    sms = 0
    mms = 0
    other = {}
    for k, v in parsed.items():
        if k.startswith(unicode('Volání')):
            volani += (v['free'].seconds + v['paid'].seconds)
        elif k.startswith(unicode('SMS')):
            sms += (v['paid'] + v['free'])
        elif k.startswith(unicode('MMS')):
            mms += (v['paid'] + v['free'])
        else:
            other[k] = v
        
    # mam zakladni tridy a ted je nejak zpracuju
    return {
        'call': volani,
        'sms': sms, 'mms': mms,
        'other': other
    }
    
def calculate_price(phoneInfo, charging, prices):
    """
    calculate how much will given user pay for what.
    """
    charging['totalprice'] = (charging['call'] / 60 * prices['call']) + \
        charging['sms'] * prices['sms']
    return charging['totalprice']

def calculate_charging(parsed_data, prices):
    """
    Creates set of dicts {'service': price, ...}
    They already contains what is a user charged for in VPN manner.
    This is data for summary view. If all is right, submit triggers processing.
    """
    data = {}
    total = {
        'call': 0,
        'mms': 0,
        'sms': 0,
        'price': 0
    }
    for num, pinfo in parsed_data.items():        
        cInfo, phoneInfo = _getInfos(num)
        charging = create_service_classes(cInfo, phoneInfo, pinfo)
        data[(cInfo, phoneInfo)] = charging
        
        total['call'] += charging['call']
        total['sms'] += charging['sms']
        total['mms'] += charging['mms']

    for (cInfo, phoneInfo), charging in data.items():
        total['price'] += calculate_price(phoneInfo, charging, prices)

    return data, total

def _getInfos(num):
    try:
        cInfo = CompanyInfo.objects.get(phone=num)
        phoneInfo = PhoneServiceInfo.objects.get(user=cInfo.user)
    except PhoneServiceInfo.DoesNotExist:
        m = 'Phone service info for %s not exists' % cInfo.user
        raise DataProcessingError(m)
    except CompanyInfo.DoesNotExist:
        raise DataProcessingError('Company (phone %s) not exists' % num)
    return cInfo, phoneInfo

def _convertToTimeDelta(time):
    parts = time.split(':')
    return datetime.timedelta(hours=int(parts[0]),
        minutes=int(parts[1]), seconds=int(parts[2]))

def _convertToMinutes(time):
    return (time.days * 24 * 60) + (time.seconds / 60)

# -----------------------------------------------------------------------------
if __name__ == '__main__':
    from billparser import TMobileCSVBillParser
    with open('sumsheet_3673301813.csv', 'r') as f:
        p = TMobileCSVBillParser(f)
        
    chargings = calculate_charging(p.parsed)
    for ci, charging in chargings.items():
        print '%s:\n%s' % (ci, charging)
    