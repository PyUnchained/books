from decimal import Decimal
import mimetypes

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.generic.base import View
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib import messages


from books.models import Account, AccountGroup, DeclaredSource
from books.forms import NewSourceForm, SourceDeclarationForm
from books.utils import get_account_for_user
import books.financial_statements as financial_statements

class DashboardView(View):
    template_name = 'books/dashboard/home.html'
    def get(self, request, *args, **kwargs):
        ctx = {}
        return render(request, self.template_name, ctx)

class DownloadFinancialStatementView(View):
    document_name = None
    def create_file(self, request):
        raise RuntimeError('{} view failed to define create file function'.format(
            self.__class__))

    def get(self, request, *args, **kwargs):
        downloadable_file = self.create_file(request)
        with downloadable_file.open() as f:
            mime_type_guess = mimetypes.guess_type(self.document_name)
            response = HttpResponse(f, content_type=mime_type_guess[0])
            response['Content-Disposition'] = 'attachment; filename=' + self.document_name
            return response

class DownloadTrialBalanceView(DownloadFinancialStatementView):
    document_name = 'trial_balance.pdf'

    def create_file(self, request):
        acc = get_account_for_user(request.user)
        tb = financial_statements.TrialBalance(acc)
        return tb.as_pdf(file_name = 'tb_out.pdf')

class DownloadProfitAndLossView(DownloadFinancialStatementView):
    document_name = 'profit_and_loss.pdf'

    def create_file(self, request):
        acc = get_account_for_user(request.user)
        pl = financial_statements.ProfitAndLoss(acc)
        return pl.as_pdf(file_name = 'pl_out.pdf')

class DownloadBalanceSheetView(DownloadFinancialStatementView):
    document_name = 'balance_sheet.pdf'

    def create_file(self, request):
        acc = get_account_for_user(request.user)
        bs = financial_statements.BalanceSheet(acc)
        bs.as_dict()
        return bs.as_pdf(file_name = 'bs_out.pdf')
    