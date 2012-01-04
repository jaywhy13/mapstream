from django.contrib import admin
from django.contrib.gis import admin as geo_admin
import models

class TagAdmin(admin.ModelAdmin):
	list_display = ('name',)

class EventTypeAdmin(admin.ModelAdmin):
	list_display = ('name', 'description',)

class EventStatusAdmin(admin.ModelAdmin):
	list_display = ('name', 'description',)

class SettlementGeoDataAdmin(geo_admin.GeoModelAdmin):
	list_display = ('community', 'parish', 'pop2001_field', 'area', 'area_sqkm', 'centroid')
	list_filter = ('parish',)
	search_fields = ('community',)
	ordering = ('community',)

class EventReportAdmin(geo_admin.GeoModelAdmin):
	list_display = ('title', 'made_by', 'time_of_report', 'location',)
	list_filter = ('time_of_report',)
	search_fields = ('title',)

admin.site.register(models.Tag, TagAdmin)
admin.site.register(models.EventType, EventTypeAdmin)
admin.site.register(models.EventStatus, EventStatusAdmin)
geo_admin.site.register(models.GeoObject, SettlementGeoDataAdmin)
geo_admin.site.register(models.EventReport, EventReportAdmin)