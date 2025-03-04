import os
import uuid

from django.db import models
from django.utils.text import slugify


def book_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/movies/", filename)


class Book(models.Model):

    class CoverChoices(models.TextChoices):
        HARD = "Hard"
        SOFT = "Soft"

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(max_length=10, choices=CoverChoices.choices)
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(decimal_places=2, max_digits=10)
    image = models.ImageField(null=True, blank=True, upload_to=book_image_file_path)

    def __str__(self):
        return f"{self.title} / {self.author}"
