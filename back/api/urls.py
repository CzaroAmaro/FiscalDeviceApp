from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

router.register(r'technicians', views.TechnicianViewSet, basename='technician')
router.register(r'clients', views.ClientViewSet, basename='client')
router.register(r'manufacturers', views.ManufacturerViewSet, basename='manufacturer')
router.register(r'certifications', views.CertificationViewSet, basename='certification')
router.register(r'devices', views.FiscalDeviceViewSet, basename='fiscaldevice')
router.register(r'tickets', views.ServiceTicketViewSet, basename='serviceticket')
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'activation-codes', views.ActivationCodeViewSet, basename='activationcode')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('external/company-data/<str:nip>/', views.fetch_company_data, name='fetch-company-data'),
]