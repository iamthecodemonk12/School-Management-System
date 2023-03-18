from django.urls import path
from . import views as v

app_name = "attendance" # namespacing urls


urlpatterns = [
    path('', v.Home.as_view(), name="home"),
]