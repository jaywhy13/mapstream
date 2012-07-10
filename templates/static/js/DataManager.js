function DataManager() {
    this.currentLevelLoaded = null;
    this.filter = "";
    this.settings = new Settings();
    
    var dataURL = "/map/view";
    
    this.getSettings = function() {
        // fetch settings from url
        $.get(dataURL, { mode: "settings" }, function(data) {
            var dataObj = eval(data);
            
            // get filters
            settings.filters = new Array();
            for (var f in dataObj.filters) {
                var filter = new Filter();
                filter.src_expr = f.src_expr;
                filter.ds_name = f.ds_name;
                filter.ds_field_name = f.ds_field_name;
                filter.label = f.label;
                filter.type = f.type;
                settings.filters.push(filter);
            }
            
            // get layers
            for (var lyr in dataObj.layer) {
                var id = lyr.id;
                var name = lyr.label;
                var description = lyr.description;
                var layerColor = lyr.colour;
                var newLayer = new Layer(id, name, description, layerColor);
		settings.layers.push(newLayer);
            }
        });
    }
    
}
