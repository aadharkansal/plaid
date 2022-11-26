from django.db import models
from bankaccount.utils import EncryptedField
from django.utils.translation import gettext_lazy as _

from users.models import User


class PlaidInstitution(models.Model):
    """
    Model to store institution
    """
    plaid_institution_id = models.CharField(max_length=254, verbose_name="Plaid Institution ID", blank=False, null=False, unique=True)
    name = models.CharField(max_length=254, verbose_name="Institution Name", blank=False, null=False)
    url = models.CharField(max_length=254, verbose_name="Institution URL", blank=True)

    class Meta:
        verbose_name = _('Plaid Institution')
        verbose_name_plural = _('Plaid Instituions')
    
    def __str__(self):
        return self.name


class UserPlaidLink(models.Model):
    """
    Model to store access code and items of user in an institution
    """
    institution = models.ForeignKey(PlaidInstitution, on_delete=models.PROTECT, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    access_code = EncryptedField(max_length=254, verbose_name="Access Code", blank=False, null=False)
    item_id = models.CharField(max_length=254, verbose_name="Item ID", blank=True, null=True)

    class Meta:
        verbose_name = _('User Plaid Link')
        verbose_name_plural = _('User Plaid Links')
    
    def __str__(self):
        return self.name


class PlaidLinkAccount(models.Model):
    """
    Model to store accounts of user in an institution
    """
    user_plaid_link = models.ForeignKey(UserPlaidLink, on_delete=models.CASCADE)
    account_id = models.CharField(max_length=254)
    name = models.CharField(max_length=254)
    mask = models.CharField(max_length=254, null=True, blank=True)
    type = models.CharField(max_length=50)
    sub_type = models.CharField(max_length=50)
    balance = models.DecimalField(decimal_places=2, max_digits=19)
    currency = models.CharField(max_length=10)

    def __str__(self):
        return "{} - {} - {}".format(self.user_plaid_link, self.subtype, self.balance)


class PlaidAccountTransaction(models.Model):
    """
    Model to store all transactions happening across plaid of our users
    """
    plaid_link_account = models.ForeignKey(PlaidLinkAccount, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=254)
    name = models.CharField(max_length=254)
    merchant_name = models.CharField(max_length=254)
    transaction_type = models.CharField(max_length=10)
    amount = models.DecimalField(decimal_places=2, max_digits=19)
