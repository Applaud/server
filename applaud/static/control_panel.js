if(! apatapa.business.control_panel ){
    apatapa.business.control_panel={};
}

(function (_ns) {

    var employee_display = function(){
	$(".control_panel_div").hide();
	$("#control_panel_employees_div").show();
	$(".employee_management").hide();
	$("#view_employees_div").show();
	$(".hidden").hide();
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


	$("#rating_profile_changes_button").click (function () {
	    var dict = {};
	    $(this).siblings("table").find("option:selected").each(function (ind, ele){
		dict[$(this).parent().siblings("input").val()]=$(this).val();
	    });
	    $.ajax({url: change_ratingprofiles_url,
		    type: 'POST',
		    dataType: 'json',
		    error: function() { alert("There was an error!"); },
		    success: function () { window.location.replace(control_panel_home); },
		    data: {'emp_profile_change':JSON.stringify(dict),
			   'csrfmiddlewaretoken':$("input[name=csrfmiddlewaretoken]").val()}
		   });

	    
	});
	var i =0;
	for(i=1; i<6; i++) {
	    $("#employee_row_"+i).click( function () {
		var emp_id = $(this).parent().siblings().children("input").val();
		var emp_expand_div;
		var x=i;
		console.log(x);
		$.ajax({url: get_employee_info_url,
			type:'GET',
			dataType: 'json',
			data: {'emp_id':emp_id,
			       'csrfmiddlewaretoken':$("input[name=csrfmiddlewaretoken]").val()},

			error: function() { alert("There was an error!"); },
			success: function (data) {
			    emp_expand_div = apatapa.functions.makeEmployeeDiv(data['employee']);
			    console.log("#expand_row_"+x);
			    $("#expand_row_"+x).append(emp_expand_div);
			    $("#employee_div_"+x).show();
			    
			}
			
		       });


	    });
	}

    }
    
})(apatapa.business.control_panel);