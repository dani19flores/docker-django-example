from django.urls import path

from ecommerce import views

urlpatterns = [
    path("", views.product_model_list_view, name="list"),
]
