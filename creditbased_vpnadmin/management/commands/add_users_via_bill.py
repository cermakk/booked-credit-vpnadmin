'''
Created on Dec 29, 2011

@author: vencax
'''
import logging
from invoices.models import CompanyInfo
from django.core.management.base import BaseCommand
from optparse import make_option
from django.utils.translation import activate
from django.conf import settings
from creditbased_vpnadmin.models import PhoneServiceInfo
from creditbased_vpnadmin.bill_processing import billparser
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = '''creates users as they are missing while parsing a bill'''

    option_list = BaseCommand.option_list + (
        make_option('--town',
                    help='town to be set to new user'),
    )

    def handle(self, *args, **options):
        activate(settings.LANGUAGE_CODE)
        logging.basicConfig()
        
        town = getattr(options, 'town', 'plzen')
        
        with open(args[0]) as f:
            parsed_data = billparser.TMobileCSVBillParser(f).parsed
        
        for num, _ in parsed_data.items():
            try:
                cInfo = CompanyInfo.objects.get(phone=num)
            except CompanyInfo.DoesNotExist:
                u = User(username=str(num), first_name='new', last_name=str(num))
                u.save()
                cInfo = CompanyInfo(user=u, phone=num, town=town)
                cInfo.save()
                
            try:
                phoneInfo = PhoneServiceInfo.objects.get(user=cInfo.user)
            except PhoneServiceInfo.DoesNotExist:
                phoneInfo = PhoneServiceInfo(user=cInfo.user, bookedcredit=5)
                phoneInfo.save()
