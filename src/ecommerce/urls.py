from django.urls import path

from ecommerce import views

urlpatterns = [
    path("", views.product_model_list_view, name="list"),
    path("<int:product_id>/", views.product_model_detail_view, name="detail"),
    path("create/", views.product_model_Create_view, name="create"),
    path("<int:product_id>/update/", views.product_model_Update_view, name="update"),
    path("<int:product_id>/delete/", views.product_model_delete_view, name="delete"),
]
