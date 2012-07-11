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

    _ns.init_control_panel = function( feed_length, employee_list_length ) {
	apatapa.business.ratingprofiles.initRatingProfilesPage();
	apatapa.business.newsfeed.initNewsfeedPage(feed_length );
	apatapa.business.survey.initSurveyPage();
	
	_ns.createBlankDivs();

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

	$(".expand_employee_button").click( function () {
	    var emp_expand_div;
	    var emp_id = $(this).parent().siblings().children("input").val();
	    if ($("#employee_div_"+emp_id).prop("shown")!="true"){
	    $.ajax({url: get_employee_info_url,
		    type:'GET',
		    dataType: 'json',
		    data: {'emp_id':emp_id,
			   'csrfmiddlewaretoken':$("input[name=csrfmiddlewaretoken]").val()},

		    error: function() { alert("There was an error!"); },
		    success: function (data) {
			emp_expand_div = apatapa.functions.makeEmployeeDiv(data['employee']);

			$("#expand_row_"+emp_id).append(emp_expand_div);
			$("#employee_div_"+emp_id).show();
			$("#employee_div_"+emp_id).prop("shown", "true");
			    
		    }
		    
		   });
	    }
	    else {
		$("#employee_div_"+emp_id).show();
	    }

	});
	   
	$(".contract_employee_button").click( function () {
	    var emp_id = $(this).parent().siblings().children("input").val();
	    $("#employee_div_"+emp_id).hide();

	});
	
	
    }
    
    _ns.addQuestion = function (index, id, title) {
	var listitem;
	var heading;
	var subtitle;
	if(id) {
	    listitem = $('<div></div>');
	    listitem.prop({'id': 'listitem_id_' + id,
			   'class': 'listitem'});
	    heading = $('<span></span>');
	    heading.prop({'id': 'heading_id_' + id,
			  'class': 'heading'});
	    subtitle = $('<span></span>');
	    subtitle.prop({'id': 'subtitle_id_' + id,
			   'class': 'subtitle'});
	}
	else {
	    listitem = $('<div></div>');
	    listitem.prop({'id': 'listitem_index_' + index,
			   'class': 'listitem'});
	    heading = $('<span></span>');
	    heading.prop({'id': 'heading_index_' + index,
			  'class': 'heading'});
	    subtitle = $('<span></span>');
	    subtitle.prop({'id': 'subtitle_index_' + index,
			   'class': 'subtitle'});
	}
	if(title.length < 30) {
	    heading.html(title);
	}
	else {
	    heading.html(title.substring(0, 30) + '...');
	    console.log('truncating');
	}
	subtitle.html('This is a generic response');
	listitem.append(heading)
	    .append(subtitle);
	$('#listitem_' + index).replaceWith(listitem);
	apatapa.business.iphone.refreshPrimary();
	apatapa.business.iphone.refreshSecondary();
    }
    
    _ns.updateQuestion = function (id, index, title) {
	if(id) {
	    if(title.length < 30) {
		$('#listitem_id_'+id).children('.heading').html(title);
	    }
	    else {
		$('#listitem_id_'+id).children('.heading').html(title.substring(0, 30) + '...');
	    }
	}
	else {
	    if(title.length < 30) {
		$('#listitem_index_'+index).children('.heading').html(title);
	    }
	    else {
		$('#listitem_index_'+index).children('.heading').html(title.substring(0, 30) + '...');
	    }
	}

    };
    var i = 0;
    _ns.deleteQuestion = function (id, index) {
	console.log(id + '  ' + index);
	if(id !== '0') {
	    $('#listitem_id_'+id).hide(500);
	    console.log('delete id');
	}
	else {
	    $('#listitem_index_'+index).hide(500);
	    console.log('delete index');
	}
	addNewBlankQuestion();

    }
    
    _ns.hideQuestion = function (id, index) {
	console.log('hide question ' + id + ' ' + index);
	if(id !== '0') {
	    $('#listitem_id_'+id).hide(500);
	}
	else {
	    $('#listitem_index_'+index).hide(500);
	}
	addNewBlankQuestion();
    }
    
    _ns.showQuestion = function (id, index) {
	console.log('show question');
	if(id !== '0') {
	    $('#listitem_id_'+id).show(500);
	}
	else {
	    $('#listitem_index_'+index).show(500);
	}
    }
    
    _ns.createBlankDivs = function () {
	var last_blank = $('<div></div>');
	last_blank.prop({'id': 'last_blank',
			 'class': 'listitem'});
	$('#iphone_screen').append(last_blank);
	for(i = 0; i < 9; i++) {
	    var listitem = $('<div></div>');
	    console.log('adding listitem!');
	    listitem.prop({'id': 'listitem_' + i,
			   'class': 'listitem'});
	    console.log('appending blanks');
	    $('#last_blank').before(listitem);
	}
    }
    
    var addNewBlankQuestion = function () {
	var listitem = $('<div></div>');
	listitem.prop({'id': 'listitem_' + i,
		       'class': 'listitem'});
	$('#last_blank').before(listitem);
	apatapa.business.iphone.refreshSecondary();
	apatapa.business.iphone.refreshPrimary();	
    }
    
//    _ns.updateQuestion(index) {
//	
//    }
    
})(apatapa.business.control_panel);
