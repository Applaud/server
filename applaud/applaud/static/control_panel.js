if(! apatapa.business.control_panel ){
    apatapa.business.control_panel={};
}

(function (_ns) {

    var employee_display = function(){
	$(".control_panel_div").hide();
	$("#control_panel_employees_div").show();
	$(".employee_management").hide();
	$("#view_employees_div").show();

    }

    var newsfeed_display = function(){
	$(".control_panel_div").hide();
	$("#control_panel_newsfeeds_div").show();
    }

    var survey_display = function(){
	$(".control_panel_div").hide();
	$("#control_panel_survey_div").show();
    }

    var home_display = function(){
	$(".control_panel_div").hide();
	$("#home_div").show();
    }

    /**
     * This is executed after the page has fully loaded.
     */

    _ns.init_control_panel = function( feed_length ) {
	apatapa.business.ratingprofiles.initRatingProfilesPage();
	apatapa.business.newsfeed.initNewsfeedPage(feed_length );
	apatapa.business.survey.initSurveyPage();


	// This creates the sub-tabs for the control panel
	$(".control_panel_div").hide();
	$("#home_div").show();
	
	$(".employee_link").click( function(event) {
	    event.preventDefault();
	    employee_display();
	});


	$(".newsfeed_link").click( function(event) {
	    event.preventDefault();
	    newsfeed_display();
	});


	$(".survey_link").click( function(event) {
	    event.preventDefault();
	    survey_display()
	});

	$(".home_link").click( function(event) {
	    event.preventDefault();
	    home_display();
	});


	// These are the sub-navigation buttons within employee management within the control panel
	$("#view_employees_button").click( function () {
	    $(".employee_management").hide();
	    $("#view_employees_div").show()
	});

	$("#add_employees_button").click( function () {
	    $(".employee_management").hide();
	    $("#add_employees_div").show()
	});
	$("#edit_rating_profiles_button").click( function () {
	    $(".employee_management").hide();
	    $("#edit_rating_profiles_div").show();
	});

	
    };

})(apatapa.business.control_panel);