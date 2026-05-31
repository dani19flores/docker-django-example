from django.contrib import messages

from django import template
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect

from .forms import ProductModelForm
from .models import ProductModel

# Create your views here.
@login_required
def product_model_Create_view(request):
    form = ProductModelForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(request, "Producto creado con exito")
        return HttpResponseRedirect("/ecommerce/{product_id}/".format(product_id=instance.id))
    context = {"form": form}
    template = "ecommerce/create-view.html"
    return render(request, template, context)

@login_required
def product_model_detail_view(request,product_id):
    instance = get_object_or_404(ProductModel, id=product_id)
    context = {"product": instance}
    template = "ecommerce/detail-view.html"
    return render(request, template, context)

@login_required
def product_model_list_view(request):
    queryset = ProductModel.objects.all()
    template= "ecommerce/list-view.html"
    context = {"products": queryset}

    return render(request, template, context)

@login_required
def login_required_view(request):
    queryset = ProductModel.objects.all()
    template= "ecommerce/list-view.html"
    context = {"products": queryset}

    return render(request, template, context)