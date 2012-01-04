@init = ->
  @geocoder = new google.maps.Geocoder()
  $('#report_submit_button').prop 'disabled', false
  # codeAddress 'Kingston, Jamaica'

@geocodeResults = []

@validateLocation = ->
  codeAddress $('#id_location').val(), () -> $('#report_form').submit()
  # alert 'and the results are .... '
 
@codeAddress = (address, callback) ->
  geocoder.geocode {'address': address}, (results, status) ->
    if status is google.maps.GeocoderStatus.OK
      # lat = results[0].geometry.location.lat()
      # long = results[0].geometry.location.long()
      # alert 'got results ' + location
      $('#report_submit_button').prop 'disabled', true
      $('#id_lat_long').val(results[0].geometry.location)
      callback()
    else
      alert 'Oh no!! We got status: ' + status
