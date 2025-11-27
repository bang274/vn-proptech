from django.urls import path
from . import views

urlpatterns = [
    path('', views.property_list, name='listings_index'),
    
    # This is the magic line. <int:pk> captures the ID (Primary Key) of the house.
    # Example: /property/1/ loads House #1. /property/5/ loads House #5.
    path('property/<int:pk>/', views.property_detail, name='property_detail'),

    path('property/<int:pk>/generate/', views.generate_pitch, name='generate_pitch'),
    path('inquiry', views.inquiry, name='inquiry'),
    path('dashboard/', views.dashboard, name='dashboard'),
]