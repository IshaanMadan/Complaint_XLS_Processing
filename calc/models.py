from django.db import models
from .validators import validate_file_extension
class Document(models.Model):
    file = models.FileField(upload_to="documents/%Y/%m/%d", validators=[validate_file_extension])
# Create your models here.
# class Document(models.Model):
    # docfile = models.FileField(null=True)