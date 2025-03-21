from django.db import models

class User(models.Model):
    nickname = models.CharField(max_length=100,unique=True)
    name = models.CharField(max_length=100)
    identity = models.CharField(max_length=50)
    sex = models.CharField(max_length=10)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.name
