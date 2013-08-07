
# -*- coding: utf-8 -*-

from django.views.generic.edit import FormView
from django.utils.translation import ugettext_lazy as _, ugettext
from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from invoices.models import CompanyInfo
from valueladder.models import Thing
from creditservices.signals import processCredit
from django.template.loader import render_to_string
from django.contrib.sites.models import Site

from .bill_processing import data_processing
from .bill_processing.billparser import TMobileCSVBillParser
from .forms import BillUploadForm, PricesSelectForm


DATA_SK = 'dataInfo'
PARSED_SK = 'parsedInfo'
DAY_SK = 'day'


class UploadBillView(FormView):
    """
    Form for input actual operator invoice content and invoice PDF.
    """
    template_name = 'vpnadmin/uploaddata.html'
    form_class = BillUploadForm

    @method_decorator(login_required)
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, request, *args, **kwargs):
        return FormView.dispatch(self, request, *args, **kwargs)

    def form_valid(self, form):
        parser = TMobileCSVBillParser(form.cleaned_data['bill'])

        self.request.session[DAY_SK] = form.cleaned_data['day']
        self.request.session[PARSED_SK] = parser.parsed

        return HttpResponseRedirect(reverse('verifyForm'))
    
    
class PriceTunningView(FormView):
    """
    Shows parsed operator invoice content in table along with
    expected invoice price.
    """
    template_name = 'vpnadmin/dataProcessed.html'
    form_class = PricesSelectForm
    initial_prices = {'call': 1, 'sms': 1, 'mms': 3}

    @method_decorator(login_required)
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, request, *args, **kwargs):
        return FormView.dispatch(self, request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        if self.request.method == 'GET':
            self.recalc(self.initial_prices)
        ctx_data = FormView.get_context_data(self, **kwargs)
        ctx_data.update(self.request.session.get(DATA_SK))
        return ctx_data
    
    def get_initial(self):
        return self.initial_prices

    def form_valid(self, form):
        try:
            prices = {
                'call': form.cleaned_data['call'],
                'sms': form.cleaned_data['sms'],
                'mms': form.cleaned_data['mms'],
            }
            self.recalc(prices)
            ctx = self.get_context_data(form=form)
        except data_processing.DataProcessingError, e:
            ctx = {'error': str(e)}
        return self.render_to_response(ctx)
        
    def recalc(self, prices):
        parsed = self.request.session.get(PARSED_SK)
        data, total = data_processing.calculate_charging(parsed, prices)
        self.request.session[DATA_SK] = {'data': data, 'totals': total}

class ProcessBillView(TemplateView):
    """
    Shows parsed operator invoice content in table along with
    expected invoice price.
    """
    template_name = 'vpnadmin/dataProcessed.html'

    @method_decorator(login_required)
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, request, *args, **kwargs):
        return TemplateView.dispatch(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = request.session.get(DATA_SK)['data']
        day = request.session.get(DAY_SK)
        
        invoices = self.process_charging(data, day)

        message = _('%(count)i records processed OK.') % {
            'count': len(invoices)
        }
        del(request.session[DATA_SK])
        del(request.session[DAY_SK])
        del(request.session[PARSED_SK])
        return self.render_to_response({'message': message})
    
    def process_charging(self, chargings, chargeday):
        """
        Subtracts credit and generates charging info mails. 
        """
        for (cInfo, _), chargeinfo in chargings.items():
            if cInfo.user_id == settings.OUR_COMPANY_ID:
                return # do not charge myself
                
            price = chargeinfo.pop('totalprice')
            currency = Thing.objects.get_default()
            contractor = CompanyInfo.objects.get_our_company_info()
            details = '\n'.join(['%s:%s' % (k, v) for k, v in chargeinfo.items()])
            
            # subtract credit
            currCredit = processCredit(cInfo, -price, currency, details,
                                       contractor.bankaccount)
        
            # send info mail
            mailContent = render_to_string('vpnadmin/infoMail.html', {
                'invoice': chargeinfo,
                'state': currCredit,
                'price': price,
                'cinfo': cInfo,
                'domain': Site.objects.get_current(),
            })
            subject = ugettext('phone service info')
            cInfo.user.email_user(subject, mailContent)
