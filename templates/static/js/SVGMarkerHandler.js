(function() {
  var __indexOf = Array.prototype.indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  this.SVGMarkerHandler = (function() {

    function SVGMarkerHandler(paper, set, map, ownPaper) {
      var lyr, _i, _len, _ref,
        _this = this;
      this.paper = paper;
      this.set = set;
      this.map = map;
      this.ownPaper = ownPaper;
      this.markerList = new Array();
      this.mapIsBeingDragged = false;
      this.mousePosition = {
        x: 0,
        y: 0
      };
      this.dragStartPosition;
      this.dragEndPosition;
      this.mouseDownPosition = {
        x: 0,
        y: 0
      };
      this.mouseUpPosition = {
        x: 0,
        y: 0
      };
      this.activeLayers = [];
      this.lastShowInfoWindow;
      _ref = layers.getActiveLayers();
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        lyr = _ref[_i];
        this.activeLayers.push(lyr.lyrId);
      }
      this.inactiveLayers = [];
      if (this.paper === null) {
        this.embedCanvas = false;
      } else {
        this.set = this.paper.set();
        console.log('Using an embedded canvas');
        this.embedCanvas = true;
      }
      if (this.map) {
        $(document).mousemove(function(evt) {
          return _this.mousePosition = {
            x: evt.pageX,
            y: evt.pageY
          };
        });
        google.maps.event.addListener(this.map, 'dragstart', function() {
          _this.dragStartPosition = {
            x: _this.mousePosition.x,
            y: _this.mousePosition.y
          };
          return _this.mapIsBeingDragged = true;
        });
        google.maps.event.addListener(this.map, 'idle', function() {
          _this.dragEndPosition = {
            x: _this.mousePosition.x,
            y: _this.mousePosition.y
          };
          if (!_this.ownPaper) _this.recenterPaper();
          return _this.mapIsBeingDragged = false;
        });
      }
    }

    SVGMarkerHandler.prototype.createMarker = function(mapInfo) {
      var marker;
      marker = new SVGMarker(mapInfo, this);
      this.markerList.push(marker);
      return marker;
    };

    SVGMarkerHandler.prototype.redrawClippedMarkers = function() {
      return console.log("try redrawing markers that were clipped by moving them into place");
    };

    SVGMarkerHandler.prototype.toggleLayerActive = function(layerId) {
      console.log("Toggling layer " + layerId);
      console.log($.inArray(layerId, this.activeLayers));
      if (__indexOf.call(this.activeLayers, layerId) >= 0) {
        return this.setLayerInactive(layerId);
      } else {
        return this.setLayerActive(layerId);
      }
    };

    SVGMarkerHandler.prototype.setLayerInactive = function(layerId) {
      var layerIndex, marker, _i, _len, _ref, _results;
      if (__indexOf.call(this.activeLayers, layerId) >= 0) {
        layerIndex = $.inArray(layerId, this.activeLayers);
        this.activeLayers.splice(layerIndex, 1);
        this.inactiveLayers.push(layerId);
        _ref = this.markerList;
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          marker = _ref[_i];
          console.log("redrawing the marker");
          _results.push(marker.redrawPie());
        }
        return _results;
      }
    };

    SVGMarkerHandler.prototype.setLayerActive = function(layerId) {
      var layerIndex, marker, _i, _len, _ref, _results;
      if (__indexOf.call(this.inactiveLayers, layerId) >= 0) {
        layerIndex = $.inArray(layerId, this.inactiveLayers);
        this.inactiveLayers.splice(layerIndex, 1);
        this.activeLayers.push(layerId);
        _ref = this.markerList;
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          marker = _ref[_i];
          _results.push(marker.redrawPie());
        }
        return _results;
      }
    };

    SVGMarkerHandler.prototype.isLayerActive = function(layerId) {
      return __indexOf.call(this.activeLayers, layerId) >= 0;
    };

    SVGMarkerHandler.prototype.recenterPaper = function() {
      var dX, dY, grapic, newLeft, newTop, _i, _len, _ref, _results;
      try {
        dX = this.dragEndPosition.x - this.dragStartPosition.x;
        dY = this.dragEndPosition.y - this.dragStartPosition.y;
        if (this.embedCanvas === true) {
          console.log("dX: " + dX + ", dY: " + dY);
          console.log("Current canvas position. Top: " + ($(this.paper.canvas).css('top')) + " left: " + ($(this.paper.canvas).css('left')));
          newTop = parseFloat($(this.paper.canvas).css("top")) - dY;
          newLeft = parseFloat($(this.paper.canvas).css("left")) - dX;
          console.log("The new position will be: Top: " + newTop + " left: " + newLeft);
          $(this.paper.canvas).css("top", newTop);
          $(this.paper.canvas).css("left", newLeft);
        }
        _ref = markerClusterer.getMarkers();
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          grapic = _ref[_i];
          _results.push(grapic.redrawGraphic(dX, dY));
        }
        return _results;
      } catch (error) {
        return console.log("Error: not ready yet :(");
      }
    };

    return SVGMarkerHandler;

  })();

}).call(this);
