function Level (id, name, maxZoom, color) {
    this.levelId = typeof id !== 'undefined' ? id : 0;
    this.levelName = typeof name !== 'undefined' ? name : "Unnamed Level";
    this.maxZoom = typeof maxZoom !== 'undefined' ? maxZoom : 0;
    this.levelColor = typeof color !== 'undefined' ? color : "";

    this.getHexColor = function () {
        return this.color;	// return the color as a string for now
    }

    var _strToHex = function (str) {
    // not sure if this is needed yet
    }
}