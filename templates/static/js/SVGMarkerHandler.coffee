class @SVGMarkerHandler
  constructor: (@paper, @set, @map, @ownPaper) ->
    # not sure what we need just yet ... maybe the paper object
    @markerList = new Array()
    @mapIsBeingDragged = no
    @mousePosition = {x:0, y:0}
    @dragStartPosition
    @dragEndPosition
    @mouseDownPosition = {x:0, y:0}
    @mouseUpPosition = {x:0, y:0}
    @activeLayers = []
    @lastShowInfoWindow

    for lyr in layers.getActiveLayers()
      @activeLayers.push lyr.lyrId
#    console.log "Active layers: #{@activeLayers}"
    @inactiveLayers = []

    if @paper == null
      @embedCanvas = no
    else
      @set = @paper.set()
      console.log 'Using an embedded canvas'
      @embedCanvas = yes

    if @map
      # we need to add the appropriate event listeners to the map ... particularly mouse drag events
      # 1st the jQuery helper event listener
      $(document).mousemove (evt) =>
        @mousePosition = {
          x: evt.pageX,
          y: evt.pageY
        }

      google.maps.event.addListener @map, 'dragstart', =>
        @dragStartPosition = { 
          x: @mousePosition.x, 
          y: @mousePosition.y
        } 
        # console.log "starting drag at #{@dragStartPosition.x}, #{@dragStartPosition.y}"
        @mapIsBeingDragged = yes

      google.maps.event.addListener @map, 'idle', =>
        @dragEndPosition = {
          x: @mousePosition.x,
          y: @mousePosition.y
        } 
        # console.log "map drag complete at #{@dragEndPosition.x}, #{@dragEndPosition.y}"
        if not @ownPaper
          @recenterPaper()
        @mapIsBeingDragged = no


  createMarker: (mapInfo) ->
    marker = new SVGMarker mapInfo, @
    @markerList.push marker
    return marker

  redrawClippedMarkers: ->
    console.log "try redrawing markers that were clipped by moving them into place"
    
  toggleLayerActive: (layerId) ->
    console.log "Toggling layer #{layerId}"
    console.log $.inArray(layerId, @activeLayers)
    if layerId in @activeLayers
      @setLayerInactive layerId
    else
      @setLayerActive layerId
    # refreshMarkers()
#    console.log "Done toggling layer #{layerId}"
    
  setLayerInactive: (layerId) ->
    if layerId in @activeLayers
      layerIndex = $.inArray(layerId, @activeLayers)
      @activeLayers.splice layerIndex, 1
      @inactiveLayers.push layerId
      for marker in @markerList
        console.log "redrawing the marker"
        marker.redrawPie()
  
  setLayerActive: (layerId) ->
    if layerId in @inactiveLayers
      layerIndex = $.inArray(layerId, @inactiveLayers)
      @inactiveLayers.splice layerIndex, 1
      @activeLayers.push layerId
      for marker in @markerList
        marker.redrawPie()

  isLayerActive: (layerId) ->
    return layerId in @activeLayers

  recenterPaper: ->
    # use the 'top' and 'left' css propeties to shift the canvas then apply
    # the appropriate delta to the the marker set
    try
      dX = @dragEndPosition.x - @dragStartPosition.x
      dY = @dragEndPosition.y - @dragStartPosition.y

      if @embedCanvas is yes
        console.log "dX: #{dX}, dY: #{dY}"
        console.log "Current canvas position. Top: #{$(@paper.canvas).css 'top'} left: #{$(@paper.canvas).css 'left'}"
        newTop = parseFloat($(@paper.canvas).css "top") - dY
        newLeft = parseFloat($(@paper.canvas).css "left") - dX
        console.log "The new position will be: Top: #{newTop} left: #{newLeft}"
        $(@paper.canvas).css "top", newTop
        $(@paper.canvas).css "left", newLeft

      # move the markers back to their correct locations
      # @set.translate(dX, dY)
      for grapic in markerClusterer.getMarkers()
        grapic.redrawGraphic(dX, dY)
    catch error
      console.log "Error: not ready yet :("
          
