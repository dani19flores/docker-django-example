from django.contrib import messages
from django import template
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q

from .forms import ProductModelForm
from .models import ProductModel



# Delete your views here.
@login_required
def product_model_delete_view(request,product_id):
    instance = get_object_or_404(ProductModel, id=product_id)
    if request.method == "POST":
        instance.delete()
        messages.success(request, "Producto eliminado con exito")
        return HttpResponseRedirect("/ecommerce/")
    context = {"product": instance}
    template = "ecommerce/delete-view.html"
    return render(request, template, context)

# Update your views here.
@login_required
def product_model_Update_view(request, product_id):
    instance = get_object_or_404(ProductModel, id=product_id)
    form = ProductModelForm(request.POST or None, instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(request, "Producto creado con exito")
        return HttpResponseRedirect("/ecommerce/{product_id}/".format(product_id=instance.id))
    context = {"form": form}
    template = "ecommerce/update-view.html"
    return render(request, template, context)

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
    query = request.GET.get("q", None)
    queryset = ProductModel.objects.all()
    if query is not None:
        queryset = queryset.filter(
            Q(title__icontains=query) | 
            Q(price__icontains=query) |
            Q(description__icontains=query) |
            Q(seller__icontains=query) |
            Q(color__icontains=query) |
            Q(product_dimensions__icontains=query)
        )
    template= "ecommerce/list-view.html"
    context = {"products": queryset}

    return render(request, template, context)

@login_required
def login_required_view(request):
    queryset = ProductModel.objects.all()
    template= "ecommerce/list-view.html"
    context = {"products": queryset}

    return render(request, template, context)