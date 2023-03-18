from django.shortcuts import render
from django.template import Context
from django.http import HttpResponse, HttpResponseNotFound
from django.views.generic import TemplateView



class IndexView(TemplateView):
    template_name = "registration/index.html"


class Page2View(TemplateView):
    template_name = 'registration/page2.html'