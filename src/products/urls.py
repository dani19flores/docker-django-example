from django.urls import path
from django.views.generic import RedirectView, TemplateView

from products import views

app_name = "products"

urlpatterns = [
    path('about/', TemplateView.as_view(template_name='about.html')),
    path('about-us/', RedirectView.as_view(url='/products/about/')),  # CBV inline
    path('about-us-fbv/', views.about_us_redirect_view),               # FBV
    path('about-us-cbv/', views.AboutRedirectView.as_view()),          # CBV como clase aparte
    path('team/', TemplateView.as_view(template_name='team.html')),
    path('fbv/', views.product_list_view),
    path('cbv/', views.product_list_view_cbv),
    path('fbv/<slug:slug>/', views.product_detail_view),
    path('cbv/<slug:slug>/', views.product_detail_view_cbv),
    path('list/', views.ProductAutoListView.as_view(), name="product-list"),
    path('list/<slug:slug>/', views.ProductAutoDetailView.as_view(), name="product-detail"),
]
