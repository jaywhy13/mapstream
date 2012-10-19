function Layer (id, name, description, color, visible) {
	
    // fields
    this.lyrId = typeof id !== 'undefined' ? id : 0;
    this.lyrName = typeof name !== 'undefined' ? name : "Unnamed Layer";
    this.lyrDescription = typeof description !== 'undefined' ? description : "";
    this.lyrColor = typeof color !== 'undefined' ? color : "";
    this.count = 0
    this.visible = typeof visible !== 'undefined' ? visible : true;

    this.getHexColor = function () {
        return this.color;	// return the color as a string for now
    }

    var _strToHex = function (str) {
    // not sure if this is needed yet
    }

}
