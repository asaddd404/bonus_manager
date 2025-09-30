from django.db import models
from django.contrib.auth.models import AbstractUser

class Organization(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

class User(AbstractUser):
    organization = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.SET_NULL)

class Client(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    def __str__(self):
        return self.name

class BonusHistory(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='history')
    date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    balance_after = models.DecimalField(max_digits=10, decimal_places=2)

class MessageTemplate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    accrual_template = models.TextField(default="Здравствуйте, [имя]! Вам начислено [сумма] бонусов. Текущий баланс: [баланс].")
    deduction_template = models.TextField(default="Здравствуйте, [имя]! С вашего счета списано [сумма] бонусов. Текущий баланс: [баланс].")
    reset_template = models.TextField(default="Здравствуйте, [имя]! Ваш баланс обнулён. Текущий баланс: 0.")