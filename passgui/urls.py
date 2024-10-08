from django.urls import path
from . import views

app_name = 'passgui'

urlpatterns = [
    # Single path for both Pass 1 and Pass 2 logic
    path('', views.single_page_view, name='assembler'),
]
