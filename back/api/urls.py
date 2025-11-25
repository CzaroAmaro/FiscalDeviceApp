from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views_chat import MessageViewSet

router = DefaultRouter()

router.register(r'technicians', views.TechnicianViewSet, basename='technician')
router.register(r'clients', views.ClientViewSet, basename='client')
router.register(r'manufacturers', views.ManufacturerViewSet, basename='manufacturer')
router.register(r'certifications', views.CertificationViewSet, basename='certification')
router.register(r'devices', views.FiscalDeviceViewSet, basename='fiscaldevice')
router.register(r'tickets', views.ServiceTicketViewSet, basename='serviceticket')
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'activation-codes', views.ActivationCodeViewSet, basename='activationcode')
router.register(r'messages', MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),
    path('users/me/', views.UserProfileView.as_view(), name='user-profile'),
    path('company/me/', views.ManageCompanyView.as_view(), name='manage-company'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('external/company-data/<str:nip>/', views.fetch_company_data, name='fetch-company-data'),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

# Stripe endpoints:
    path('create-checkout-session/', views.create_checkout_session, name='create-checkout-session'),
    path('handle-payment-success/', views.handle_payment_success, name='handle-payment-success'),
    path('stripe/webhook/', views.stripe_webhook, name='stripe-webhook'),
    path('redeem-activation-code/', views.redeem_activation_code, name='redeem-activation-code'),
    path('my-activation-codes/', views.my_activation_codes, name='my-activation-codes'),

    path('devices/<int:device_id>/export-pdf/', views.export_device_pdf, name='export-device-pdf'),
    path('charts/', views.ChartView.as_view(), name='charts-data'),

    path('reports/generate/', views.GenerateReportView.as_view(), name='generate-report'),
    path('reports/filter-options/', views.ReportFilterOptionsView.as_view(), name='report-filter-options'),
]