from django.contrib import admin

from .models import File, Report

# Register your models here.
class FileAdmin(admin.ModelAdmin):
    pass

admin.site.register(File, FileAdmin)

admin.site.register(Report, FileAdmin)
