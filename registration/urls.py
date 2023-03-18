from django.urls import path
from .views import IndexView, Page2View


urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path("page/", Page2View.as_view(), name="page2")
]
