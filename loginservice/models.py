from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

class CustomUser(AbstractUser):

    #Simple validator for phone number. 
    phone_regex = RegexValidator(
        regex=r'^[0-9]{10}$',
        message="Ingrese un número telefónico válido de 10 dígitos"
        )

    phone_number = models.CharField(
            max_length = 10,
            validators = [phone_regex],
            help_text="Formato: 6561234567 (10 dígitos)"
            )
