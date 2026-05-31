from django.urls import path

from ecommerce import views

urlpatterns = [
    path("", views.home, name="home"),
    path("redirect/", views.redirect_to_test, name="test"),
]
