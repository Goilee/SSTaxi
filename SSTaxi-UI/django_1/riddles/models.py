from django.db import models

from django.db import models


class Book(models.Model):
    cover = models.ImageField(upload_to='map_img.png')
    def __str__(self):
        return self.title
