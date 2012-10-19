function Layers (source) {
    var layerList = typeof source !== 'undefined' ? source : new Array();	// internal array of layer objects

    /**
	  * Returns all visible layers contained
	  */
    this.getActiveLayers = function () {
        var results = new Array();
        for (var i = 0; i < layerList.length; i++) {
            var layer = layerList[i];
            if (layer.visible === true) {
                results.push(layer);
            }
        }

        return results;
    }

    this.getAllLayers = function () {
        return layerList;
    }

    /**
	  * Returns layer for given name if layer is stored by this object
	  */
    this.getLayerByName = function (name) {
        for (var i = 0; i < layerList.length; i++) {
            var layer = layerList[i];
            if (layer.lyrName === name) {
                return layer;
            }
        }

        return null;
    }

    /**
	  * Returns layer for given layer id if layer is stored by this object
	  */
    this.getLayerById = function (id) {
        for (var i = 0; i < layerList.length; i++) {
            var layer = layerList[i];
            if (layer.lyrId === id) {
                return layer;
            }
        }
        return null;
    }
}