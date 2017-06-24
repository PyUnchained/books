"""opexa_accounting URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from books.views import*

urlpatterns = [
    url(r'^new_journal_entry/$',
        NewJournalEntry.as_view(),
        name = 'new_journal_entry'),
    url(r'^new_transaction/$',
        NewJournalEntryRule.as_view(),
        name = 'new_transaction'),

    url(r'^enter_transaction/(\w+)/$',
        EnterTransactionView.as_view(),
        name = 'enter_transaction'),

    url(r'^view_journal/(\w+)/$',
        JournalView.as_view(),
        name = 'view_journal'),

    
]
