from django.http import HttpResponse
from django.core import serializers
from mapstream2.listener.models import DataSource

def list_data(request, objectType, objectId):
	default = HttpResponse("Unknown object type requested")
	result = {
		"datasource": list_data_source(request, objectId),
	}
	return result.get(objectType, default)


def list_data_source(request, objectId):
	pretty = 'pretty' in request.GET
	if objectId:
		try:
			cleanId = int(objectId)
			data_source_json = serializers.serialize('json', [DataSource.objects.get(id=cleanId)], indent=4 if pretty else None, sort_keys=pretty)
		except DataSource.DoesNotExist:
			data_source_json = 'No data source exists with id: %s' % objectId
		except ValueError:
			data_source_json = 'The id "%s" is not a valid number' % objectId
		return HttpResponse(data_source_json, content_type='application/json')
	else:
		data_source_json = serializers.serialize('json', DataSource.objects.all(), indent=4 if pretty else None, sort_keys=pretty)
		return HttpResponse(data_source_json, content_type='application/json')
