from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from .models import ProductModel

# Create your views here.
def product_model_list_view(request):
    queryset = ProductModel.objects.all()
    template= "ecommerce/list-view.html"
    context = {"products": queryset}
    return render(request, template, context)