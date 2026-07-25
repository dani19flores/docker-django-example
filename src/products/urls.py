from django.urls import path
from django.views.generic import TemplateView

from products import views

urlpatterns = [
    path('about/', TemplateView.as_view(template_name='about.html')),
    path('team/', TemplateView.as_view(template_name='team.html')),
    path('fbv/', views.product_list_view),
    path('cbv/', views.product_list_view_cbv),
]