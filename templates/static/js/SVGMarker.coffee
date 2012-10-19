class @SVGMarker extends google.maps.OverlayView

  constructor: (@mapInfo, @handler) ->
    @marker = new google.maps.Marker mapInfo
    @map = mapInfo["map"]
    @setMap(@map)
    @cachedProjection
    @graphic
    @myPaper
    @buffer = 20
    @radius1 = 12
    @radius2 = 25

  getPosition: ->
    @marker.getPosition()

  getDraggable: ->
    @marker.getDraggable()
    
  getValues: ->
    result = []
    for info in @mapInfo.details.events
      if info.type_id in @handler.activeLayers
        result.push 1
    return result
    
  getColours: ->
    result = { colors: [] }
    for evt in @mapInfo.details.events
      if evt.type_id in @handler.activeLayers
        lyr = layers.getLayerById(evt.type_id)
        result.colors.push lyr.lyrColor
    return result

  getTotal: ->
    result = 0
    for value in @getValues()
      result += value
    return result

  onAdd: ->
    # get the overlay pane and add the paper object to it, if it's not already there
    panes = @getPanes()
    if @handler.ownPaper
      # console.log "on Add ... creating new paper"
      map_container_id = "##{@map.getDiv().id}"
      map_container = $ map_container_id
      # point = @getProjection().fromLatLngToContainerPixel @getPosition()
      point = @getProjection().fromLatLngToDivPixel @getPosition()
      containerPosition = {
        x: point.x - (@radius2 + @buffer)
        y: point.y - (@radius2 + @buffer)
      }
      containerSize = (@radius2 + @buffer) * 2
      # @myPaper = Raphael containerPosition.x, containerPosition.y, containerSize, containerSize
      @myPaper = Raphael 0, 0, containerSize, containerSize
      $(@myPaper.canvas).css "overflow", "visible"
      $(@myPaper.canvas).css "pointer-events", "none"

      if @myPaper.canvas not in panes.overlayImage.children
        panes.overlayImage.appendChild @myPaper.canvas
      else
        console.log "canvas is already there!?"


  onRemove: ->
    @clearGraphic()
    $(@myPaper.canvas).remove()
    @myPaper = null
    # @myPaper.canvas.parentElement.removeChild @myPaper.canvas

  hoverIn: =>
    # console.log "we're hovering over a point!"
    # params = { "r": 20 }
    # @stop() # stop any animations if any
    # @animate params, 700, "elastic"
    # console.log "Animating the marker"
    @pie.stop()
    @pie.each (sector, cover, i) ->
      params = {
        # transform: "s1.7 1.7 #{this.cx} #{this.cy}"
        transform: "s1.7 1.7 #{this.cx} #{this.cy} r180 #{this.cx} #{this.cy}"
      }
      @sector.animate params, 300, "easeOut"
    # @showDetails()

  showDetails: ->
    # @detailSet = @myPaper.set()
    console.log "Showing details for marker"
    @pie.each (sector, cover, i) ->
      # console.log @mangle
      # console.log @
      # p = @sector.paper.path "M#{this.cx}, #{this.cy} L#{this.x} #{this.y}"
      p = @sector.paper.path "M#{this.cx}, #{this.cy} L#{this.cx}, #{this.cy + 28}"
      p.transform "r#{90-@mangle} #{this.cx} #{this.cy}"
      # p.transform "s1.7 1.7 #{this.cx} #{this.cy} r180 #{this.cx} #{this.cy}"
      # p.attr "stroke", "#f00"
      p.attr "stroke", @sector.attr("fill")
      # @detailSet.push p
      endPt = p.getPointAtLength p.getTotalLength()
      c = @sector.paper.rect endPt.x, endPt.y, 50, 15, 2
      # c.transform "r#{90-@mangle} #{this.cx} #{this.cy}"
      # $(p.node).css "z-index", 10

    hideDetails: ->
      @detailSet.remove()



  hoverOut: =>
    # console.log "we hovered out of the point"
    # params = { "r": 10 }
    # @stop() # stop any animations if any
    # @animate params, 500, "elastic"
    @pie.stop()
    point = {
        x: @radius2 + @buffer,
        y: @radius2 + @buffer
    }
    @pie.each (sector, cover, i) ->
      params = {
        transform: "s1 1 #{this.cx} #{this.cy}"
        # transform: "s1 1 #{this.cx} #{this.cy} r0 #{this.cx} #{this.cy}"
      }
      # console.log "trying to do hover out"
      @sector.animate params, 200, "easeIn"

  draw: ->
    # drawing marker
    # console.log 'drawing marker .. need to reposition canvas here?'
    if @handler.ownPaper
      point = {
        x: @radius2 + @buffer,
        y: @radius2 + @buffer
      }
      position = @getProjection().fromLatLngToDivPixel @getPosition()
      canvasPosition = {
        x: position.x - (@radius2 + @buffer)
        y: position.y - (@radius2 + @buffer)
      }
      $(@myPaper.canvas).css "-webkit-transform", "translate(#{canvasPosition.x}px, #{canvasPosition.y}px)"
      $(@myPaper.canvas).css msTransform: "translate(#{canvasPosition.x}px, #{canvasPosition.y}px)"
      $(@myPaper.canvas).css "-moz-transform", "translate(#{canvasPosition.x}px, #{canvasPosition.y}px)"
      $(@myPaper.canvas).css "-o-transform", "translate(#{canvasPosition.x}px, #{canvasPosition.y}px)"
    else
      point = @getProjection().fromLatLngToDivPixel @getPosition()
    @cachedProjection = @getProjection()
    @clearGraphic()
    @createGraphic(point)

  createGraphic: (point) ->
    if @getValues().length is 0
      console.log "we have no values to draw"
      return
    # @graphic = @handler.paper.circle point.x, point.y, 10
    @graphic2 = @myPaper.circle point.x, point.y, @radius1+5
    @graphic2.attr "fill", "#4b4242"
    @graphic2.attr "stroke", "none"
    @graphic2.attr "opacity", "0.2"

    @graphic3 = @myPaper.circle point.x, point.y, @radius1+10
    @graphic3.attr "fill", "#4b4242"
    @graphic3.attr "stroke", "none"
    @graphic3.attr "opacity", "0.1"
    
    values = @getValues()
    colors = @getColours()
    @pie = @myPaper.piechart point.x, point.y, @radius1, values, colors
    @pie.hover @pieHoverIn, @pieHoverOut
    for i in [0..(@getValues().length-1)]
      @pie.series.items[i].attr stroke: "none"

    @graphic = @myPaper.circle point.x, point.y, @radius1
    $(@graphic.node).css "pointer-events", "visiblePainted"
    @graphic.hover @hoverIn, @hoverOut
    @graphic.click @showInfoWindow
    @graphic.attr "fill", "#4b4242"
    @graphic.attr "stroke", "#5a5a5a"

    # draw the text in the center
    @text = @myPaper.text point.x, point.y, @getTotal()
    @text.attr "fill", "#fff"
    
    # @handler.set.push @graphic
    # @handler.markerList.push @

  clearGraphic: ->
    # removes the marker graphic from the paper
    if @graphic
      @myPaper.clear()


  redrawGraphic: (offsetX, offsetY) ->
    if @graphic
      if @getProjection() is null
        console.log "marker #{@} lost its projection"
      else
        newPosition = @getProjection().fromLatLngToDivPixel @getPosition()
        @clearGraphic()
        console.log "Printing internal paper object"
        console.log @myPaper
        @createGraphic(newPosition)

  showInfoWindow: =>
    currentLevel = levels.getLevel map.getZoom()
    # currentLevel = { label: "Some Level" }
    content = "<div class='infoWindowContent'>"
    content += "<h3>Event Summary</h3>"
    # content += "<p><b>#{currentLevel.levelName} name:</b> #{@mapInfo.details.name}"
    content += "<b>Total:</b> #{@getTotal()}</p>"
    content += "<hr><ul style='list-style: none'>"
    # we want to print out each 'report' that this event has for now .... put nothing much
    for info in @mapInfo.details.events
      if info.type_id in @handler.activeLayers
        lyr = layers.getLayerById info.type_id
        content += "<li><div style='width: 10px; height: 10px; background-color: #{lyr.lyrColor}; border-radius: 50%; display: inline-block; margin-right: 10px'></div> #{info.name}</li>"
    # for info in @mapInfo.details.incident
    #   if info.layer_id in @handler.activeLayers
    #     layer = layers.getLayerById(info.layer_id)
    #     content += "<li><div style='width: 10px; height: 10px; background-color: #{layer.lyrColor}; border-radius: 50%; display: inline-block; margin-right: 10px'></div>"
    #     content += "#{layer.lyrName}: #{info.total}</li>"
    content += "</ul>"
    content += "</div>"

#    infoWindow = new google.maps.InfoWindow "content": content
    infoWindow = new InfoBubble "content": content, borderWidth: 1, borderColor: "#000", arrowStyle: 1, disableAutoPan: true
    if @handler.lastShownInfoWindow
      @handler.lastShownInfoWindow.close()
    infoWindow.open map, @
    @handler.lastShownInfoWindow = infoWindow
    
  redrawPie: ->
    if @myPaper
      @clearGraphic()
      point = {
        x: @radius2 + @buffer,
        y: @radius2 + @buffer
      }
      @createGraphic(point)
    
