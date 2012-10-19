(function() {
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; },
    __indexOf = Array.prototype.indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  this.SVGMarker = (function(_super) {

    __extends(SVGMarker, _super);

    function SVGMarker(mapInfo, handler) {
      this.mapInfo = mapInfo;
      this.handler = handler;
      this.showInfoWindow = __bind(this.showInfoWindow, this);
      this.hoverOut = __bind(this.hoverOut, this);
      this.hoverIn = __bind(this.hoverIn, this);
      this.marker = new google.maps.Marker(mapInfo);
      this.map = mapInfo["map"];
      this.setMap(this.map);
      this.cachedProjection;
      this.graphic;
      this.myPaper;
      this.buffer = 20;
      this.radius1 = 12;
      this.radius2 = 25;
    }

    SVGMarker.prototype.getPosition = function() {
      return this.marker.getPosition();
    };

    SVGMarker.prototype.getDraggable = function() {
      return this.marker.getDraggable();
    };

    SVGMarker.prototype.getValues = function() {
      var info, result, _i, _len, _ref, _ref2;
      result = [];
      _ref = this.mapInfo.details.events;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        info = _ref[_i];
        if (_ref2 = info.type_id, __indexOf.call(this.handler.activeLayers, _ref2) >= 0) {
          result.push(1);
        }
      }
      return result;
    };

    SVGMarker.prototype.getColours = function() {
      var evt, lyr, result, _i, _len, _ref, _ref2;
      result = {
        colors: []
      };
      _ref = this.mapInfo.details.events;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        evt = _ref[_i];
        if (_ref2 = evt.type_id, __indexOf.call(this.handler.activeLayers, _ref2) >= 0) {
          lyr = layers.getLayerById(evt.type_id);
          result.colors.push(lyr.lyrColor);
        }
      }
      return result;
    };

    SVGMarker.prototype.getTotal = function() {
      var result, value, _i, _len, _ref;
      result = 0;
      _ref = this.getValues();
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        value = _ref[_i];
        result += value;
      }
      return result;
    };

    SVGMarker.prototype.onAdd = function() {
      var containerPosition, containerSize, map_container, map_container_id, panes, point, _ref;
      panes = this.getPanes();
      if (this.handler.ownPaper) {
        map_container_id = "#" + (this.map.getDiv().id);
        map_container = $(map_container_id);
        point = this.getProjection().fromLatLngToDivPixel(this.getPosition());
        containerPosition = {
          x: point.x - (this.radius2 + this.buffer),
          y: point.y - (this.radius2 + this.buffer)
        };
        containerSize = (this.radius2 + this.buffer) * 2;
        this.myPaper = Raphael(0, 0, containerSize, containerSize);
        $(this.myPaper.canvas).css("overflow", "visible");
        $(this.myPaper.canvas).css("pointer-events", "none");
        if (_ref = this.myPaper.canvas, __indexOf.call(panes.overlayImage.children, _ref) < 0) {
          return panes.overlayImage.appendChild(this.myPaper.canvas);
        } else {
          return console.log("canvas is already there!?");
        }
      }
    };

    SVGMarker.prototype.onRemove = function() {
      this.clearGraphic();
      $(this.myPaper.canvas).remove();
      return this.myPaper = null;
    };

    SVGMarker.prototype.hoverIn = function() {
      this.pie.stop();
      return this.pie.each(function(sector, cover, i) {
        var params;
        params = {
          transform: "s1.7 1.7 " + this.cx + " " + this.cy + " r180 " + this.cx + " " + this.cy
        };
        return this.sector.animate(params, 300, "easeOut");
      });
    };

    SVGMarker.prototype.showDetails = function() {
      console.log("Showing details for marker");
      this.pie.each(function(sector, cover, i) {
        var c, endPt, p;
        p = this.sector.paper.path("M" + this.cx + ", " + this.cy + " L" + this.cx + ", " + (this.cy + 28));
        p.transform("r" + (90 - this.mangle) + " " + this.cx + " " + this.cy);
        p.attr("stroke", this.sector.attr("fill"));
        endPt = p.getPointAtLength(p.getTotalLength());
        return c = this.sector.paper.rect(endPt.x, endPt.y, 50, 15, 2);
      });
      return {
        hideDetails: function() {
          return this.detailSet.remove();
        }
      };
    };

    SVGMarker.prototype.hoverOut = function() {
      var point;
      this.pie.stop();
      point = {
        x: this.radius2 + this.buffer,
        y: this.radius2 + this.buffer
      };
      return this.pie.each(function(sector, cover, i) {
        var params;
        params = {
          transform: "s1 1 " + this.cx + " " + this.cy
        };
        return this.sector.animate(params, 200, "easeIn");
      });
    };

    SVGMarker.prototype.draw = function() {
      var canvasPosition, point, position;
      if (this.handler.ownPaper) {
        point = {
          x: this.radius2 + this.buffer,
          y: this.radius2 + this.buffer
        };
        position = this.getProjection().fromLatLngToDivPixel(this.getPosition());
        canvasPosition = {
          x: position.x - (this.radius2 + this.buffer),
          y: position.y - (this.radius2 + this.buffer)
        };
        $(this.myPaper.canvas).css("-webkit-transform", "translate(" + canvasPosition.x + "px, " + canvasPosition.y + "px)");
        $(this.myPaper.canvas).css({
          msTransform: "translate(" + canvasPosition.x + "px, " + canvasPosition.y + "px)"
        });
        $(this.myPaper.canvas).css("-moz-transform", "translate(" + canvasPosition.x + "px, " + canvasPosition.y + "px)");
        $(this.myPaper.canvas).css("-o-transform", "translate(" + canvasPosition.x + "px, " + canvasPosition.y + "px)");
      } else {
        point = this.getProjection().fromLatLngToDivPixel(this.getPosition());
      }
      this.cachedProjection = this.getProjection();
      this.clearGraphic();
      return this.createGraphic(point);
    };

    SVGMarker.prototype.createGraphic = function(point) {
      var colors, i, values, _ref;
      if (this.getValues().length === 0) {
        console.log("we have no values to draw");
        return;
      }
      this.graphic2 = this.myPaper.circle(point.x, point.y, this.radius1 + 5);
      this.graphic2.attr("fill", "#4b4242");
      this.graphic2.attr("stroke", "none");
      this.graphic2.attr("opacity", "0.2");
      this.graphic3 = this.myPaper.circle(point.x, point.y, this.radius1 + 10);
      this.graphic3.attr("fill", "#4b4242");
      this.graphic3.attr("stroke", "none");
      this.graphic3.attr("opacity", "0.1");
      values = this.getValues();
      colors = this.getColours();
      this.pie = this.myPaper.piechart(point.x, point.y, this.radius1, values, colors);
      this.pie.hover(this.pieHoverIn, this.pieHoverOut);
      for (i = 0, _ref = this.getValues().length - 1; 0 <= _ref ? i <= _ref : i >= _ref; 0 <= _ref ? i++ : i--) {
        this.pie.series.items[i].attr({
          stroke: "none"
        });
      }
      this.graphic = this.myPaper.circle(point.x, point.y, this.radius1);
      $(this.graphic.node).css("pointer-events", "visiblePainted");
      this.graphic.hover(this.hoverIn, this.hoverOut);
      this.graphic.click(this.showInfoWindow);
      this.graphic.attr("fill", "#4b4242");
      this.graphic.attr("stroke", "#5a5a5a");
      this.text = this.myPaper.text(point.x, point.y, this.getTotal());
      return this.text.attr("fill", "#fff");
    };

    SVGMarker.prototype.clearGraphic = function() {
      if (this.graphic) return this.myPaper.clear();
    };

    SVGMarker.prototype.redrawGraphic = function(offsetX, offsetY) {
      var newPosition;
      if (this.graphic) {
        if (this.getProjection() === null) {
          return console.log("marker " + this + " lost its projection");
        } else {
          newPosition = this.getProjection().fromLatLngToDivPixel(this.getPosition());
          this.clearGraphic();
          console.log("Printing internal paper object");
          console.log(this.myPaper);
          return this.createGraphic(newPosition);
        }
      }
    };

    SVGMarker.prototype.showInfoWindow = function() {
      var content, currentLevel, info, infoWindow, lyr, _i, _len, _ref, _ref2;
      currentLevel = levels.getLevel(map.getZoom());
      content = "<div class='infoWindowContent'>";
      content += "<h3>Event Summary</h3>";
      content += "<b>Total:</b> " + (this.getTotal()) + "</p>";
      content += "<hr><ul style='list-style: none'>";
      _ref = this.mapInfo.details.events;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        info = _ref[_i];
        if (_ref2 = info.type_id, __indexOf.call(this.handler.activeLayers, _ref2) >= 0) {
          lyr = layers.getLayerById(info.type_id);
          content += "<li><div style='width: 10px; height: 10px; background-color: " + lyr.lyrColor + "; border-radius: 50%; display: inline-block; margin-right: 10px'></div> " + info.name + "</li>";
        }
      }
      content += "</ul>";
      content += "</div>";
      infoWindow = new InfoBubble({
        "content": content,
        borderWidth: 1,
        borderColor: "#000",
        arrowStyle: 1,
        disableAutoPan: true
      });
      if (this.handler.lastShownInfoWindow) {
        this.handler.lastShownInfoWindow.close();
      }
      infoWindow.open(map, this);
      return this.handler.lastShownInfoWindow = infoWindow;
    };

    SVGMarker.prototype.redrawPie = function() {
      var point;
      if (this.myPaper) {
        this.clearGraphic();
        point = {
          x: this.radius2 + this.buffer,
          y: this.radius2 + this.buffer
        };
        return this.createGraphic(point);
      }
    };

    return SVGMarker;

  })(google.maps.OverlayView);

}).call(this);
