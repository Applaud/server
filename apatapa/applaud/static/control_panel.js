if(! apatapa.business.control_panel ){
    apatapa.business.control_panel={};
}

(function (_ns) {

    _ns.employee_display = function(){
	$(".control_panel_div").hide();
	$("#control_panel_employees_div").show();
	$(".employee_management").hide();
	$("#view_employees_div").show();
	$(".hidden").hide();
	$(".tab_bar_div").removeClass("tab_bar_selected");
	$("#employee_tab_bar").addClass("tab_bar_selected");
    };

    _ns.newsfeed_display = function(){
	$(".control_panel_div").hide();
	$("#control_panel_newsfeeds_div").show();
	$(".tab_bar_div").removeClass("tab_bar_selected");
	$("#newsfeed_tab_bar").addClass("tab_bar_selected");
    };

    _ns.survey_display = function(){
	$(".control_panel_div").hide();
	$("#control_panel_survey_div").show();
	$(".tab_bar_div").removeClass("tab_bar_selected");
	$("#survey_tab_bar").addClass("tab_bar_selected");
	console.log('calling display');
	_ns.displayiPhoneDiv("survey");
	console.log('done');
    };
    
    _ns.profile_display = function(){
	$(".control_panel_div").hide();
	$("#control_panel_profile_div").show();
    };

    _ns.home_display = function(){
	$(".control_panel_div").hide();
	$("#home_div").show();
    };
    
    var photos_display = function() {
	$('.control_panel_div').hide();
	$("#control_panel_photos_div").show();
	$(".tab_bar_div").removeClass("tab_bar_selected");
	_ns.displayiPhoneDiv("home");
    };

    // function to hide other iphone divs and display the one that's passed in as an argument. Between "home", "newsfeed", "survey".
    _ns.displayiPhoneDiv = function (name) {
	console.log("hiding iphone divs");
	$(".iphone_divs").hide();
	$("#iphone_"+name+"_div").show();
    }


    // This function is called after the page is fully loaded to populate the control panel
    _ns.initControlPanel = function(data) {

        _ns.applaud.init(data['employees'], data['rating_profiles']);
        _ns.mingle.init(data['threads']);
        _ns.polls.init(data['polls']);
        _ns.photos.init(data['photos']);
        _ns.newsfeed.init(data['newsfeed']);

	    apatapa.business.ratingprofiles.initRatingProfilesPage();
	    apatapa.business.newsfeed.initNewsfeedPage(feed_length );
	    apatapa.business.survey.initSurveyPage();
	    
        // What is this??
	    _ns.createBlankDivs();
	    
	    // Allow us to update the title on the iPhone.
	    $('#survey_title').keyup(function () {
	        apatapa.business.control_panel.updateTitle($(this).val());
	    });
	    
	    // Same for the description.
	    $('#survey_description').keyup( function () {
	        apatapa.business.control_panel.updateDescription($(this).val());
	    });
	    
	    // This creates the sub-tabs for the control panel
	    $(".control_panel_div").hide();
	    $("#home_div").show();
        
	    // This sets the navigation tab clicked as 'selected'
	    $('.cp_nav_button').click( function(event) {
	        $('.cp_nav_button').removeClass('selected');
	        $(this).addClass('selected');
	    })
	    
	    $(".employee_link").click( function(event) {
	        event.preventDefault();
	        _ns.employee_display();
	    });
	    
	    $('.cp_nav_button').click( function(event) {
	        $('.cp_nav_button').removeClass('selected');
	        $(this).addClass('selected');
	    });
        
	    $(".newsfeed_link").click( function(event) {
	        event.preventDefault();
	        _ns.newsfeed_display();
	    });
        
        
	    $(".survey_link").click( function(event) {
	        event.preventDefault();
	        _ns.survey_display()
	    });
        
	    $(".profile_link").click( function(event) {
	        event.preventDefault();
	        _ns.profile_display()
	    });


	    $(".home_link").click( function(event) {
	        event.preventDefault();
	        _ns.home_display();
	    });
	    
	    $('.photos_link').click( function(event) {
	        event.preventDefault();
	        photos_display();
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
	        var emp_id = $(this).siblings("input").val();
	        if($(this).html() === '+') {
		        if ($("#employee_div_"+emp_id).prop("shown")!="true"){
		            $.ajax({url: get_employee_info_url,
			                type:'GET',
			                dataType: 'json',
			                data: {'emp_id':emp_id,
				                   'csrfmiddlewaretoken':$("input[name=csrfmiddlewaretoken]").val()},
                            
			                error: function() { alert("There was an ungodly error!"); },
			                success: function (data) {
				                var emp_expand = $("<div>"+data['bio']+"</div>");
				                $("#employee_div_"+emp_id).append(data['bio']);
				                $("#employee_div_"+emp_id).show();
				                $("#employee_div_"+emp_id).prop("shown", "true");
			                }
			               });
		            $(this).html('-');
		        }
		        else {
		            $("#employee_div_"+emp_id).show();
		            $(this).html('-');
		        }
	        }
	        else {
		        $(this).html('+');
		        $("#employee_div_"+emp_id).hide();
	        }
	    });
	    
	    // When we click the 'activate' button on a photo, actually activate it.
	    $('.photo_active_button').click( function () {
	        var photo_id = $(this).prop('id').split('_')[1];
	        $.ajax({url: toggle_photo_url,
		            type: 'POST',
		            data: {'photo_id': photo_id,
			               'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()},
		            error: function () { alert('Shit!'); },
		            success: function () {
			            alert('Whee!');
			            $('#photo_'+photo_id+'_active').html($('#photo_'+photo_id+'_active').html() === 'active' ? 'inactive' : 'active');
		            }});
	    });
	    
	    $(".contract_employee_button").click( function () {
	        

	    });
	    // This hides all the other iphone divs and chooses the home iphone div
	    _ns.displayiPhoneDiv("home");
	    // Go to the appropriate tab if there's a hash in the URL.
	    if(location.hash === '#questions') {
	        //$('.survey_link').click();
	        _ns.survey_display();
	    }
	    if(location.hash === '#employees') {
	        $('.employee_link').click();
	    }
	    if(location.hash === '#photos') {
	        $('.photos_link').click();
	    }
	    if(location.hash === '#newsfeed') {
	        $('.newsfeed_link').click();
	    }
    };
 


//////////////////////////////////////////
// apatapa.business.controlpanel.photos //
//////////////////////////////////////////

if ( ! apatapa.business.controlpanel.photos ) {
    apatapa.business.controlpanel.photos = {};
}

( function( _ns ) {
    _ns.init = function(photos){

    }

} ( apatapa.business.controlpanel.photos ) )




//////////////////////////////////////////
// apatapa.business.controlpanel.polls //
//////////////////////////////////////////

if ( ! apatapa.business.controlpanel.polls ) {
    apatapa.business.controlpanel.polls = {};
}

( function( _ns ) {
    _ns.init = function(polls){

    }

} ( apatapa.business.controlpanel.polls ) )




//////////////////////////////////////////
// apatapa.business.controlpanel.mingle //
//////////////////////////////////////////

if ( ! apatapa.business.controlpanel.mingle ) {
    apatapa.business.controlpanel.mingle = {};
}

( function( _ns ) {
    _ns.init = function(mingle){

    }

} ( apatapa.business.controlpanel.mingle ) )



////////////////////////////////////////////
// apatapa.business.controlpanel.newsfeed //
////////////////////////////////////////////

if ( ! apatapa.business.controlpanel.newsfeed ){
    apatapa.business.controlpanel.newsfeed = {};
}

( function( _ns ) {
    _ns.init = function(newsfeed){
        // List the newsfeed
        for( var i = 0; i < newsfeed.length; i++){
            var container = addNewsfeedItem(newsfeed[i]);
            $("#newsfeed-list").append( container );
        }

        // Bind the add newsfeed button
        $("#add-newsfeed-item-button").click( function(){
            var container = addNewsfeedItem();
            $("#newsfeed-list").prepend( container );
        });
    }
    
    // Used to create a new item (if newsfeed is undefined), or change an existing one by passing the JSON object in
    // Returns the div containing these elements
    _ns.addItem = function (newsfeed) {
        // TODO: Labels?

	    // The container div
	    var container = $('<div></div>');
	    container.prop({'class': 'newsfeed-item'});
        if( newsfeed ){
            container.prop({'id': 'newsfeed_' + newsfeed.id,
			                'name': 'newsfeed_' + newsfeed.id});
        }

        // The title of the newsfeed
        var title = $("<input></input>");
        title.prop({'type':'text',
                    'class':'input-medium',
                    'default': newsfeed.title ? newsfeed.title : ''});
        
        
        // The body of the newsfeed
        var body = $("<textarea></textarea>");
        body.prop({'rows':'3'});
        if( newsfeed ){
            body.html( newsfeed.body );
        }

        // The image of the newsfeed (thumbnail?)
        if( newsfeed ){
            var img = $("<img></img>");
            img.prop({'src':'/media/'+thumbnail});
        
            // A button to change the newsfeed image
            var changeButton = $("<button></button>");
            changeButton.prop({'type':'button',
                               'class':'btn btn-small'});
        
            // TODO: Bind the change button
        }
        else{
            // TODO: File upload form
        }
        
        // ----------
        // TODO: Should there be an edit/ cancel button, or should every news item be editable from the get-go?

        // The save button (to remember changes to this item). In the future, will changes just be remembered?
        var saveButton = $('<button></button>');
	    saveButton.prop({'type': 'button',
				         'class': 'btn btn-small',
                         'html':'Save'});
        
        // Bind save button
        saveButton.click( function(){
            saveNewsfeed( newsfeed );
        });
        
        // The delete button
	    var deleteButton = $('<button></button>');
	    deleteButton.prop({'type':'button',
                           'class':'btn btn-small',
                           'html':'Delete'});

        // Bind delete button
        deleteButton.click( function(){
            // Show confirmation? On callback, do these
            container.hide();
            deleteNewsfeed( newsfeed );
        });

        // Put all of the elements into the container
        container.append(title)
            .append(body)
            .append(img)
            .append(changeButton)
            .append(saveButton)
            .append(deleteButton);
        
        return container;
	}

    // TODO: Write saveNewsfeed()

    // TODO: Write deleteNewsfeed()

} (apatapa.business.controlpanel.newsfeed) )        

    

    // In the iphone questions view, this adds each question.
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
	listitem.append(heading).append(subtitle);
	$('#listitem_' + index).replaceWith(listitem);
	apatapa.business.iphone.refreshPrimary();
	apatapa.business.iphone.refreshSecondary();
    };
    
    // Also for the iphone questions view.
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

    };
    
    _ns.hideQuestion = function (id, index) {
	console.log('hide question ' + id + ' ' + index);
	if(id !== '0') {
	    $('#listitem_id_'+id).hide(500);
	}
	else {
	    $('#listitem_index_'+index).hide(500);
	}
	addNewBlankQuestion();
    };
    
    _ns.showQuestion = function (id, index) {
	console.log('show question');
	if(id !== '0') {
	    $('#listitem_id_'+id).show(500);
	}
	else {
	    $('#listitem_index_'+index).show(500);
	}
    };
    
    _ns.createBlankDivs = function () {
	var last_blank = $('<div></div>');
	last_blank.prop({'id': 'last_blank',
			 'class': 'listitem'});
	$('#iphone_survey_div').append(last_blank);
	for(i = 0; i < 9; i++) {
	    var listitem = $('<div></div>');
	    console.log('adding listitem!');
	    listitem.prop({'id': 'listitem_' + i,
			   'class': 'listitem'});
	    console.log('appending blanks');
	    $('#last_blank').before(listitem);
	}
    };
    
    var addNewBlankQuestion = function () {
	var listitem = $('<div></div>');
	listitem.prop({'id': 'listitem_' + i,
		       'class': 'listitem'});
	$('#last_blank').before(listitem);
	apatapa.business.iphone.refreshSecondary();
	apatapa.business.iphone.refreshPrimary();	
    };
    
    _ns.updateTitle = function (title) {
	console.log('update title');
	$('#iphone_title').html(title);
    };
    
    _ns.updateDescription = function (text) {
	$('#iphone_description').html(text);
    };
    
})(apatapa.business.control_panel);
