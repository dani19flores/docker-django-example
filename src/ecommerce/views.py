from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

# Create your views here.
# def home(request):
#     html_content = """
#     <!DOCTYPE html>
#     <html lang="en">
#         <head>
#             <meta charset="UTF-8">
#             <meta name="viewport" content="width=device-width, initial-scale=1.0">
#             <title>E-commerce Home</title>
#             <style>
#                 body {
#                     font-family: Arial, sans-serif;
#                     background-color: #f4f4f4;
#                     margin: 0;
#                     padding: 20px;
#                 }
#                 h1 {
#                     color: #333;
#                 }
#             </style>   
#         </head>
#         <body>
#             <h1>Welcome to the E-commerce Home Page!</h1>
#         </body>
#     </html>
#         """
#     return HttpResponse(html_content)

def home(request):
    response = HttpResponse()
    response.content = "Algún contenido de prueba"
    response.write("<h1>Welcome to the E-commerce Home Page!</h1>")
    return response

def redirect_to_test(request):
    return HttpResponseRedirect("/ecommerce")