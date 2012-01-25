from django.contrib import admin
from django.contrib.gis import admin as geo_admin
import models

class TagAdmin(admin.ModelAdmin):
	list_display = ('name',)

class EventAdmin(geo_admin.GeoModelAdmin):
	list_display = ('name', 'description', 'event_type' , 'time_created', 'status')
	list_filter = ('status',)

class EventTypeAdmin(admin.ModelAdmin):
	list_display = ('name', 'description',)

class EventStatusAdmin(admin.ModelAdmin):
	list_display = ('name', 'description',)

class SettlementGeoDataAdmin(geo_admin.GeoModelAdmin):
	list_display = ('community', 'parish', 'pop2001_field', 'area', 'area_sqkm')
	list_filter = ('parish',)
	search_fields = ('community',)
	ordering = ('community',)

class EventReportAdmin(geo_admin.GeoModelAdmin):
	list_display = ('title', 'made_by', 'time_of_report', 'location',)
	list_filter = ('time_of_report',)
	search_fields = ('title',)

class SecureViewAdmin(admin.ModelAdmin):
	list_display = ('key', 'url', 'view_parameters',)

class SecureViewParameterAdmin(admin.ModelAdmin):
	list_display = ('keyword', 'value',)

class GeoLocationAdmin(admin.ModelAdmin):
	list_display = ['classname','search_field']


admin.site.register(models.Tag, TagAdmin)
geo_admin.site.register(models.Event, EventAdmin)
admin.site.register(models.EventType, EventTypeAdmin)
admin.site.register(models.EventStatus, EventStatusAdmin)
admin.site.register(models.SecureView, SecureViewAdmin)
admin.site.register(models.SecureViewParameter, SecureViewParameterAdmin)
admin.site.register(models.GeoLocation,GeoLocationAdmin)
geo_admin.site.register(models.GeoObject, SettlementGeoDataAdmin)
geo_admin.site.register(models.EventReport, EventReportAdmin)
