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
    
    url(r'^new_transaction/$',
        NewJournalEntryRule.as_view(),
        name = 'new_transaction'),
    url(r'^enter_transaction/(\w+)/$',
        EnterTransactionView.as_view(),
        name = 'enter_transaction'),
    url(r'^enter_any_transaction/$',
        EnterAnyTransactionView.as_view(),
        name = 'enter_any_transaction'),

    url(r'^all_journals/$',
        JournalListView.as_view(),
        name = 'all_journals_list'),
    url(r'^view_journal/(.*)/$',
        JournalView.as_view(),
        name = 'view_journal'),
    url(r'^new_journal_entry/$',
        NewJournalEntry.as_view(),
        name = 'new_journal_entry'),

    #Stand Alone Site
    url(r'^$', landing, name = 'demo_landing'),

    #Admin URLS
    url(r'^single_entries/([a-zA-Z0-9-]*)/$',
        AdminSingleEntryView.as_view(),
        name = 'admin_single_entries'),
    # url(r'^admin_forms/(\w+)/$',
    #     AdminForms.as_view(), name = 'admin_forms'),


    
]
