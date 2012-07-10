

function refreshMarkers() {
    var newMarkerArray = new Array();
    var newInactiveMarkerArray = new Array();
    var allMarkers = markerArray.concat(inactiveMarkerArray);
    for (var i=0; i < allMarkers.length; i++) {
        var marker = allMarkers[i];
        var total = marker.getTotal();
        if (total > 0) {
            newMarkerArray.push(marker);
        } else {
            newInactiveMarkerArray.push(marker);
        }
    }
    markerArray = newMarkerArray;
    inactiveMarkerArray = newInactiveMarkerArray;
    
    if (markerClusterer == null) {
        markerClusterer = new MarkerClusterer(map, markerArray, mcOptions);        
    } else {
        markerClusterer.markers_ = markerArray;
        markerClusterer.repaint();
    }
}