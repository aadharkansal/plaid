from django.contrib import admin
from bankaccount.models import *

# Register your models here.

admin.site.register(PlaidInstitution)
admin.site.register(UserPlaidLink)
admin.site.register(PlaidLinkAccount)
admin.site.register(PlaidAccountTransaction)
