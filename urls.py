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
from django.urls import path
from django.contrib import admin

from books.views import*


app_name = 'opexa_books'
urlpatterns = [

    # Account initialization views
    path('account_start/capital_sources', CapitalSourcesView.as_view(),
        name = 'capital_sources'),
    path('account_start/liability_sources', LiabilitySourcesView.as_view(),
        name = 'liability_sources'),
    path('account_start/asset_sources', AssetsSourcesView.as_view(),
        name = 'asset_sources'),
    path('account_start/end', end_declarations_view,
        name = 'end_declarations'),


    # Books Accounting Interface #
    ##############################
    path('dashboard', DashboardView.as_view(),
        name = 'dashboard')
    
]
