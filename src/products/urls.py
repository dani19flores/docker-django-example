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
    path('publicados/', views.product_proxy_list_view, name="published-products"),
    path('digital-products/', views.DigitalProductListView.as_view(), name="digital-product-list"),
    path('protegido/', views.ProductProtectedListView.as_view(), name="protected-product-list"),
    path('crear/', views.product_create_view, name="product-create"),
    path('crear-cbv/', views.product_create_view_cbv, name="product-create-cbv"),

    # RedirectView basada en la instancia del modelo Product (local, ver
    # doc/mixin-instance-redirect-view.md): dos formas de llegar al mismo
    # destino, /products/list/<slug>/.
    path('id/<int:pk>/', views.ProductIDRedirectView.as_view(), name="product-id-redirect"),
    path('slug-redirect/<slug:slug>/', views.ProductRedirectView.as_view(), name="product-slug-redirect"),

    # estas dos van al final: <slug:slug>/ es un "catch-all" que matchea
    # cualquier texto simple, así que tiene que evaluarse después de todas
    # las rutas literales de arriba (si no, se las "come" a ellas).
    path('<int:pk>/', views.ProductInstanceRedirectView.as_view(), name="instance-redirect"),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name="detail"),
]
