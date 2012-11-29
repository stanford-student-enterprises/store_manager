$.fn.cellBottom = function() {
    var $el;
    return this.each(function() {
    	$el = $(this);
    	var newDiv = $("<div />", {
    		"class": "innerWrapper",
    		"css"  : {
    			"height"  : $el.height(),
    			"width"   : "100%",
    			"position": "relative"
    		}
    	});
    	$el.wrapInner(newDiv);    
    });
};