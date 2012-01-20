from django.contrib import admin
from django.contrib.gis import admin as geo_admin
import models

class WordAdmin(admin.ModelAdmin):
    list_display = ['root','finite_forms_description','similar_words_description']

class WordTypeAdmin(admin.ModelAdmin):
    list_display = ['name','description']


admin.site.register(models.Word, WordAdmin)
admin.site.register(models.WordType, WordTypeAdmin)
