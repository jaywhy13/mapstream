(function() {

  this.init = function() {
    this.geocoder = new google.maps.Geocoder();
    return $('#report_submit_button').prop('disabled', false);
  };

  this.geocodeResults = [];

  this.validateLocation = function() {
    return codeAddress($('#id_location').val(), function() {
      return $('#report_form').submit();
    });
  };

  this.codeAddress = function(address, callback) {
    return geocoder.geocode({
      'address': address
    }, function(results, status) {
      if (status === google.maps.GeocoderStatus.OK) {
        $('#report_submit_button').prop('disabled', true);
        $('#id_lat_long').val(results[0].geometry.location);
        return callback();
      } else {
        return alert('Oh no!! We got status: ' + status);
      }
    });
  };

}).call(this);
