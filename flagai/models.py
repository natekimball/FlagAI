from django.db import models
from django.contrib.auth.models import User


class File(models.Model):
    name = models.TextField()
    file = models.FileField()
    report = models.ForeignKey('Report', related_name='files', on_delete=models.CASCADE)

    def delete(self, *args, **kwargs):
        self.file.delete(save=False)
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.name


class Report(models.Model):
    description = models.TextField()
    offender_link = models.TextField(blank=True, null=True)
    people_involved = models.TextField(blank=True, null=True)
    contact_email = models.CharField(max_length=254)
    feedback = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=100)
    date_uploaded_or_edited = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # file = models.ForeignKey(File, on_delete=models.CASCADE, blank=True, null=True)
