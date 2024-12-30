from django.db import models

# Create your models here.


class NewsSchema(models.Model):
    title = models.TextField(null=True)
    content = models.TextField(null=True)
    img_url = models.TextField(null=True)
    url = models.TextField(null=True)
    date = models.DateTimeField(null=True)
    topic = models.TextField(null=True)


class QuerySchema(models.Model):
    query = models.TextField(null=True)
    num_results = models.IntegerField(default=10)
    topic = models.TextField(null=True)


class UserSchema(models.Model):
    user_name = models.TextField(null=True)
    topic = models.TextField(null=True)
