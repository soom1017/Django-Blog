from django.db import models
from django.db.models.fields.related import create_many_to_many_intermediary_model

# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=30)
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now=True)
    #author: 추후 작성 예정

    def __str__(self):
        return f'[{self.pk}]{self.title}'
