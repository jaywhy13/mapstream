function MarkerManager(map) {
    this.map = map;
    this.markers = new Array();
    
    
    this.drawCircle = function () {
        var paper = Raphael(10, 50, 320, 200);
        var circle = paper.circle(50, 40, 10);
        circle.attr("fill", "#f00");
        circle.attr("stroke", "#fff");
        circle.id = "test";
        return circle;
    }
    
    this.marker = null;
    this.paper = null;
    this.addRichMarker = function () {
        var content = $('<div></div>');
        var paper = Raphael(content, 32, 32);
        var circle = paper.circle(16, 16, 16);
        circle.attr("fill", "#f00");
        circle.attr("stroke", "#fff");
        content.append(paper);
        paper.remove();
        
        console.log("we have content: " + $(content).html());
        this.marker = content;
        this.paper = paper;
        
        var marker = new RichMarker({
            position: new google.maps.LatLng(17.992731,-76.792009),
            map: this.map,
            draggable: false,
            content: content.html()
//                    content: '<div class="my-marker"><div>This is a nice image</div>' +
//                    '<div><img src="http://farm4.static.flickr.com/3212/3012579547_' +
//                    '097e27ced9_m.jpg"/></div><div>You should drag it!</div></div>'
        });
        map.addOverlay(marker);
    }
    
    this.addRaphaelMarker = function () {
        var marker = new RaphaelOverlay({
            map: this.map,
            shapes: [{
                // A circle center coincides with the position 
                // but the center has priority 
                center: new google.maps.LatLng(85, 175),
                type: "Circle" ,
                radius: 100 ,
                attr: {
                    stroke: '# FFF' , 
                    "stroke-width" : 2 ,
                    fill: '# 0f0' , 
                    "fill-Opacity" : 0.3
                }
            }]
        });
        
        this.markers.push(marker);
    }
}
