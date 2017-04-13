from __future__ import unicode_literals

from django.db import models


class Docs(models.Model):
    """Create models here."""

    address = models.CharField(max_length=200)
