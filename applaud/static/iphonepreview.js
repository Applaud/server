if (! apatapa.business.iphone ) {
    apatapa.business.iphone = {};
}

(function(_ns) {
    _ns.refreshPrimary = function() {
	var rgbString = $("#primary_color").val();
	console.log('primary color: ' + $('#primary_color').val());
	var brightRgbString = brighterPrimary(rgbString);

	console.log("hexes: "+rgbString+" - "+brightRgbString);
	
	$("#iphone_preview .navbar").css({
	    'filter':'progid:DXImageTransform.Microsoft.gradient(startColorstr='+brightRgbString+'), endColorstr='+rgbString+'))',
	    'background-image':'-webkit-gradient(linear, left bottom, left top, from('+brightRgbString+'), to('+rgbString+'))',
	    'background-image':'-moz-linear-gradient(90deg, '+brightRgbString+',  '+rgbString+')'});
    };

    _ns.refreshSecondary = function() {
	var rgbString = $("#secondary_color").val();
	$("#iphone_preview .listitem").css('background-color',rgbString);
    };

    function rgbConvert(str) {
	str = str.replace(/rgb\(|\)/g, "").split(",");
	str[0] = parseInt(str[0], 10).toString(16).toLowerCase();
	str[1] = parseInt(str[1], 10).toString(16).toLowerCase();
	str[2] = parseInt(str[2], 10).toString(16).toLowerCase();
	str[0] = (str[0].length == 1) ? '0' + str[0] : str[0];
	str[1] = (str[1].length == 1) ? '0' + str[1] : str[1];
	str[2] = (str[2].length == 1) ? '0' + str[2] : str[2];
	return ('#' + str.join(""));
    }

    function brighterPrimary(hexColor) {
	hexColor = hexColor.replace(/#/g,"");
	console.log("brighter of "+hexColor);
	var red = Math.round(0.64*parseInt(hexColor.substring(0,2),16)).toString(16).toLowerCase();
	var green = Math.round(0.71*parseInt(hexColor.substring(2,4),16)).toString(16).toLowerCase();
	var blue = Math.round(0.78*parseInt(hexColor.substring(4),16)).toString(16).toLowerCase();
	red = (red.length == 1) ? '0' + red : red;
	green = (green.length == 1) ? '0' + green : green;
	blue = (blue.length == 1) ? '0' + blue : blue;

	// hexify this
	return "#"+red+green+blue;
    }
})(apatapa.business.iphone);

$(document).ready(function() {
    console.log("primary: "+$("#primary_color").val());
    console.log("secondary: "+$("#secondary_color").val());
    apatapa.business.iphone.refreshPrimary();
    apatapa.business.iphone.refreshSecondary();
});