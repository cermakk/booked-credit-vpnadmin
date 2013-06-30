# -*- coding: utf-8 -*-
from django.utils.translation import ugettext
from django.conf import settings


def on_new_credit(sender, companyInfo, amount, currency, **kwargs):
    """
    Creates invoice with credit. 
    This is called when new_credit signal is generated (user send some money).
    """
    from invoices.models import Invoice, Item

    if companyInfo.id == settings.OUR_COMPANY_ID:
        return  # do not generate invoice to ourself

    invoice = Invoice(subscriber=companyInfo, paid=True)
    invoice.save()
    itemTitle = '%s (%i)' % (ugettext('Phone services credit'),
                             companyInfo.phone)
    invoice.items.add(Item(price=amount, name=itemTitle))
    invoice.send()
