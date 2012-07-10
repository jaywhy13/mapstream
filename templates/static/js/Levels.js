function Levels (source) {

    var levelList = typeof source !== 'undefined' ? source : new Array();

    this.getLevel2 = function(zoom) {
        var smallestDistance = 0;
        var closestLevel;
        var initDistance = false;
		
        for (var i = 0; i < levelList.length; i++) {
            var level = levelList[i];
            var distance = level.maxZoom - zoom;

            if(!initDistance) {		// not sure if this will work like this, testing needed
                smallestDistance = distance;
                closestLevel = level;
                initDistance = true;
            } else if(distance >= 0 && (distance <= smallestDistance || smallestDistance < 0)) {
                smallestDistance = distance;
                closestLevel = level;
            }
        }
        return closestLevel;
    }

    this.getLevel = function (zoom) {
        var levelAboveExists = false;
        var levelBelowExists = false;
        var levelAbove;
        var levelBelow;
        var returnLevel;
		
        for (var i = 0; i < levelList.length; i++) {
            var level = levelList[i];
            //if level is less than zoom
            if(level.maxZoom < zoom) {
                if(levelBelowExists) {
                    // check to see if this lower level is smaller than the current level
                    if(levelBelow.maxZoom < level.maxZoom) {
                        levelBelow = level;
                    }
                } else {
                    levelBelow = level;
                    levelBelowExists = true;
                }
            } else if(level.maxZoom > zoom) {
                if(levelAboveExists) {
                    if(levelAbove.maxZoom > level.maxZoom) {
                        levelAbove = level;
                    }
                } else {
                    levelAbove = level;
                    levelAboveExists = true;
                }
            } else if(level.maxZoom === zoom) {
                returnLevel = level;
                return returnLevel;
            }
        } //end for loop
		
        if(levelAboveExists)
            returnLevel = levelAbove;
        else
            returnLevel = levelBelow;
		
        return returnLevel;
    }

    this.getPointLevel = function () {
        for (var level in levelList) {				
            if(level.name.toUpperCase().indexOf("POINT") >= 0) {
                return level;
            }
        }

        return null;
    }

}
