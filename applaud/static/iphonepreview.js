
if (! apatapa.business.iphone ) {
    apatapa.business.iphone = {};
}

(function(_ns) {
    _ns.refreshPrimary = function() {
	var rgbString = $("#primary_color_input").val();
	var brightRgbString = brighterPrimary(rgbString);
	$(".navbar").css({
	    'filter':'progid:DXImageTransform.Microsoft.gradient(startColorstr='+brightRgbString+'), endColorstr='+rgbString+'))',
	    'background-color':rgbString, // fuck it! chrome sucks.
	    'background-image':'-moz-linear-gradient(90deg, '+brightRgbString+',  '+rgbString+')'});
    };

    _ns.refreshSecondary = function() {
	var rgbString = $("#secondary_color_input").val();
	$("#iphone_screen").css('background-color', rgbString);
	$("#iphone_preview .listitem").css('background-color',rgbString);
    };

    function brighterPrimary(hexColor) {
	hexColor = hexColor.replace(/#/g,"");
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
    apatapa.business.iphone.refreshPrimary();
    apatapa.business.iphone.refreshSecondary();
    $('#iphone_screen').css('background-color', $('#secondary_color').val());
    

    $("#employee_tab_bar").click( function () {
	apatapa.business.control_panel.employee_display();
	$('.cp_nav_button').removeClass('selected');
	$("#employee_button").addClass("selected");
    });

    $("#survey_tab_bar").click( function () {
	apatapa.business.control_panel.survey_display();
	$('.cp_nav_button').removeClass('selected');
	$("#survey_button").addClass("selected");
    });

    $("#newsfeed_tab_bar").click( function () {
	apatapa.business.control_panel.newsfeed_display();
	$('.cp_nav_button').removeClass('selected');	
	$("#newsfeed_button").addClass("selected");	
    });


});
