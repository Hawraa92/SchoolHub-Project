# predictor/models.py
from django.db import models

class PredictionConfig(models.Model):
    name = models.CharField(max_length=50, default="Config")

    def __str__(self):
        return self.name
