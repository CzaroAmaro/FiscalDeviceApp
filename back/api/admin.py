from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Client, FiscalDevice, ServiceRecord

admin.site.register(CustomUser, UserAdmin)
admin.site.register(Client)
admin.site.register(FiscalDevice)
admin.site.register(ServiceRecord)