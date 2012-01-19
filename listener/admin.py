from django.contrib import admin
# from django.contrib.gis import admin as geo_admin
import models

class DataTagAdmin(admin.ModelAdmin):
	list_display = ('name', 'description')

class DataSourceTypeAdmin(admin.ModelAdmin):
	list_display = ('name', 'description',)

class DataSourceStatusAdmin(admin.ModelAdmin):
	list_display = ('name', 'description',)

class DataSourceAdmin(admin.ModelAdmin):
	list_display = ('src_type', 'src_id', 'description', 'state', 'time_last_active')
	list_filter = ("src_type", "state")

class RawDataAdmin(admin.ModelAdmin):
	list_display = ('title', 'source', 'time_added')
	list_filter = ("source", "time_added", "tags")


class DataSourceParameterAdmin(admin.ModelAdmin):
	list_display = ('name','value',)

admin.site.register(models.DataTag, DataTagAdmin)
admin.site.register(models.DataSourceType, DataSourceTypeAdmin)
admin.site.register(models.DataSourceStatus, DataSourceStatusAdmin)
admin.site.register(models.DataSource, DataSourceAdmin)
admin.site.register(models.RawData, RawDataAdmin)
admin.site.register(models.DataSourceParameter,DataSourceParameterAdmin)
