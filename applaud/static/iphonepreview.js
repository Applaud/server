if (! apatapa.business.iphone ) {
    apatapa.business.iphone = {};
}

(function(_ns) {
    _ns.refreshPrimary = function() {
	var rgbString = $("#primary_color").val();
	var colorList = rgbString.split(",");
	var brighterColorList = brighterPrimary(colorList);
	var brightRgbString = brighterColorList.join();

	// convert to hex
	rgbString = rgbConvert(rgbString);
	brightRgbString = rgbConvert(brightRgbString);
	console.log("hexes: "+rgbString+" - "+brightRgbString);
	
	console.log('filter:progid:DXImageTransform.Microsoft.gradient(startColorstr='+brightRgbString+', endColorstr='+rgbString+')');
	console.log('background:-webkit-gradient(linear, left top, left bottom, from('+brightRgbString+'), to('+rgbString+'))');
	console.log('background:-moz-linear-gradient(top, '+rgbString+',  '+brightRgbString+')');

	$("#iphone_preview .navbar").css({
	    'filter':'progid:DXImageTransform.Microsoft.gradient(startColorstr='+brightRgbString+'), endColorstr='+rgbString+'))',
	    'background-image':'-webkit-gradient(linear, left bottom, left top, from('+brightRgbString+'), to('+rgbString+'))',
	    'background-image':'-moz-linear-gradient(90deg, '+brightRgbString+',  '+rgbString+')'});
    }

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

    function brighterPrimary(colorList) {
	return [0.64*colorList[0],0.71*colorList[1],0.78*colorList[2]];
    }
})(apatapa.business.iphone);