/**
 * business.js
 * 
 * Provides all javascript functionality for the business-end of the website.
 * Includes four modules:
 * 
 * apatapa.business.employees
 * apatapa.business.newsfeed
 * apatapa.business.ratingprofiles
 * apatapa.business.survey
 * */


if (! apatapa.business) {
    apatapa.business = {};
}

(function (business) {

    ////////////////////////////////
    // apatapa.business.employees //
    ////////////////////////////////

    if (! business.employees) {
	business.employees = {};
    }

    (function (_ns) {
	_ns.bind_delete_buttons = function () {
	    $('.del_emp_button').click(
		function ( event ) {
		    event.preventDefault();
		    $.ajax({ url: delete_employee_url,
			     type: 'POST',
			     data: {'employee_id':$(this).attr('id').split('_')[2],
				    'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()},
			     success: function(data) {
				 _ns.listEmployees(data, $('#employees_listing'));
				 _ns.buildForms();
			     },
			     error: function() { alert("Something went wrong."); }
			   });
		});
	}

	/**
	 * getEmployees
	 *
	 * NOTE: You MUST have {% csrf_token %} on the page calling this somewhere.
	 * fills 'container' with the list of employees for current business.
	 */
	_ns.getEmployees = function( container, callback ) {
	    $.ajax({url: list_employees_url,
		    type: 'POST',
		    data:{'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()},
		    success: function(data) {
			_ns.listEmployee(data, container);
			if ( callback )
			    callback();
		    },
		    error: function() {
			alert("Something went wrong.");
		    }
		   });
	};



	/**
	 * buildForms()
	 *
	 * Creates forms on each employee listing.
	 */
	_ns.buildForms = function() {
	    $('.employee_item').each( function(index, element) {
		var id = $(this).children('.employee_id').val();
		$(this).append("<form action=\"\" method=\"post\">"
			       +"<input type=\"hidden\" name=\"csrfmiddlewaretoken\" value=\""+$('input[name=csrfmiddlewaretoken]').val()+"\" />"
			       +"<input type=\"submit\" id=\"del_emp_"+employee.id+"\" class=\"del_emp_button\" value=\"Delete\" />");
	    });

	    _ns.bind_delete_buttons();
	}

	/**
	 * listEmployees(data)
	 *
	 * data - JSON data returned by AJAX call
	 * Re-builds the list of employees.
	 */
	_ns.listEmployees = function(data, container) {
	    // Clear the current list
	    container.empty();
	    var listing = $('<ul></ul>');

	    for ( e in data.employee_list ) {
		employee = data.employee_list[e];
		var listitem = $('<li class="employee_item"></li>');
		listitem.append( _ns.listEmployee(employee));
		listing.append(listitem);
	    }
	    
	    container.append(listing);
	};
	
	///////////////////////////////////////////////////
        // Returns a div containing employee information //
        ///////////////////////////////////////////////////
	_ns.listEmployee = function(employee){
	    var employee_div = $('<div></div>');
	    employee_div.prop({'id':'employee_'+employee.id+'_div'});

	    var employee_image = $('<img />');
	    employee_image.prop({'src':employee.image,
				 'alt':employee.first_name+" "+employee.last_name,
				 'class':'profile_image'});
	    var employee_id = $('<input />');
	    employee_id.prop({'type':'hidden',
			      'value':employee.id});
	    listitem.append( employee_image ).append(employee_id);
	    listitem.append( $('<span class="employee_name">'+employee.first_name+" "+employee.last_name+'</span>') );
	    
	    return listitem;

	}
    })(business.employees);


    /////////////////////////////////////
    // apatapa.business.ratingprofiles //
    /////////////////////////////////////

    if (! business.ratingprofiles) {
	business.ratingprofiles = {};
    }

    (function (_ns) {
	// Keeps track of how many dimensions we have when creating
	// a new RatingProfile.
	var dimension_count = 0;

	/**
	 * bind_delete_buttons
	 *
	 * Binds a callback to the buttons that remove an entire ratingprofile.
	 */
	var bind_delete_buttons = function() {
	    $('.del_rp_button').click(
		function ( event ) {
		    event.preventDefault();
		    $.ajax({ url: manage_ratingprofiles_url,
			     type: 'POST',
			     data: {'profile_id':$(this).siblings('.profileid').val(),
				    'remove':'True',
				    'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()},
			     success: listProfiles,
			     error: function() { alert("Something went wrong."); }
			   });
		});
	}

	/**
	 * bind_remove_buttons
	 *
	 * Binds a callback to the buttons that remove a single dimension 
	 * from a ratingprofile.
	 */
	var bind_remove_buttons = function() {
	    $('.del_rp_dim_button').click(
		function ( event ) {
		    event.preventDefault();
		    $.ajax({ url: manage_ratingprofiles_url,
			     type: 'POST',
			     data: {'profile_id':$(this).siblings('.profileid').val(),
				    'remove_dim': $(this).siblings('.dimension_text').prop('id'),
				    'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()},
			     success: listProfiles,
			     error: function() { alert("Something went wrong."); }
			   });
		});
	}

	/**
	 * bind_deactivate_buttons
	 *
	 * Binds a callback to the buttons that deactivate (remove from RP, but keep data)
	 * a dimension.
	 */
	var bind_deactivate_buttons = function() {
	    $('.deactivate_rp_dim_button').click( function( event ) {
		event.preventDefault();

		$.ajax({ url: manage_ratingprofiles_url,
			 type: 'POST',
			 data: {'profile_id':$(this).siblings('.profileid').val(),
				'deactivate_dim':$(this).siblings('.dimension_text').prop('id'),
				'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()},
			 success: listProfiles,
			 error: function() { alert("Something went wrong."); }
		       });
	    });
	}

	/**
	 * bind_activate_buttons
	 *
	 * Binds a callback to the buttons that activate a dimension.
	 */
	var bind_activate_buttons = function() {
	    $('.activate_rp_dim_button').click( function( event ) {
		event.preventDefault();

		$.ajax({ url: manage_ratingprofiles_url,
			 type: 'POST',
			 data: {'profile_id':$(this).siblings('.profileid').val(),
				'activate_dim':$(this).siblings('.dimension_text').prop('id'),
				'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()},
			 success: listProfiles,
			 error: function() { alert("Something went wrong."); }
		       });
	    });
	}

	/**
	 * bind_edit_buttons
	 *
	 * Binds a callback to the buttons that edit a dimension's text.
	 */
	var bind_edit_buttons = function() {
	    $('.edit_rp_dim_button').click( function(event) {
		event.preventDefault();

		// Turn dimension text into text field
		var dimdom = $(this).siblings('.dimension_text');
		var dimfield = $('<input />');
		dimfield.prop({'type':'text',
			       'value':	dimdom.text(),
			       'class':'dimfield_edit'});
		dimdom.replaceWith( dimfield );
		
		// Turn edit button into "done" button
		$(this).val("done");

		// Hide close and delete buttons
		$(this).siblings('.deactivate_rp_dim_button').hide();
		$(this).siblings('.del_rp_dim_button').hide();

		// Bind click handler to "done" button to one which submits the edit
		$(this).click( function( event ) {
		    event.preventDefault();

		    $.ajax({url: manage_ratingprofiles_url,
			    type:'POST',
			    data:{'profile_id':$(this).siblings('.profileid').val(),
				  'replace_dim':dimdom.prop('id'),
				  'with_dim': $(this).siblings('.dimfield_edit').val(),
				  'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()},
			    success: listProfiles,
			    error: function() { alert("Something went wrong."); }
			   });
		});
	    });
	}

	/**
	 * bind_insert_buttons
	 *
	 * Binds a callback to the buttons that insert a dimension for a
	 * ratingprofile.
	 */
	var bind_insert_buttons = function() {
	    $('.ins_rp_button').click( function(event) {
		// Close all other 'insert dimension' forms
		$('#insert_dimension_div').remove();

		event.preventDefault();

		var newdimdiv = $("<div id=\"insert_dimension_div\"></div>");
		var label = $("<label for=\"dimension_title\">New dimension name</label>");
		var textfield = $("<input type=\"text\" name=\"dimension_title\" id=\"dimension_title\" />");
		var submit = $("<input type=\"submit\" id=\"submit_"+$(this).attr('id').split('_')[3]+"\" class=\"ratingprofile_submit\" value=\"OK\" />");
		submit.click( function( event ) {
		    event.preventDefault();
		    var profile_id = $(this).siblings('.profileid').val();
		    $.ajax({ url: manage_ratingprofiles_url,
			     type: 'POST',
			     data: {'profile_id':$(this).parent('#insert_dimension_div').siblings('.profileid').val(),
				    'insert':escape(apatapa.util.escapeHTML( $('#dimension_title').val() )),
				    'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()},
			     success: listProfiles,
			     error: function() { alert("Something went wrong."); }
			   });
		});

		newdimdiv
		    .append( '<br />' )
		    .append( label )
		    .append( textfield )
		    .append( submit );
		$(this).parent().append(newdimdiv);
	    });
	}


	/**
	 * listProfiles(data)
	 *
	 * data - JSON data returned by AJAX call for deleting/inserting a profile.
	 * Re-builds the list of profiles.
	 */
	var listProfiles = function(data) {
	    // Clear the current list
	    $('#profiles_listing').empty();
	    var listing = $('<ul id="profiles_listing"></ul>');

	    for ( p in data.rating_profiles ) {
		profile = data.rating_profiles[p];
		var listitem = $('<li><strong>'+unescape(profile.title)+'</strong></li>');

		// This is the way it's done per the RatingProfileEncoder
		var listform = $("<form action=\"/business/business_manage_ratingprofiles/\" method=\"post\">"
				 +"<input type=\"hidden\" name=\"csrfmiddlewaretoken\" value=\""+$('input[name=csrfmiddlewaretoken]').val()+"\" />"
				 +"<input type=\"hidden\" class=\"profileid\" value=\""+profile.id+"\" />"
				 +"<input type=\"submit\" id=\"del_rp_button_"+profile.id+"\" class=\"del_rp_button\" value=\"Delete\" />"
				 +"<input type=\"submit\" id=\"ins_rp_button_"+profile.id+"\" class=\"ins_rp_button\" value=\"Insert\" />");
		listitem.append( listform );

		var innerlist = $('<ul></ul>');
		for ( d in profile.dimensions ) {
		    var dimension = profile.dimensions[d];
		    var dim_title = dimension.title;
		    var dim_id = dimension.id;
		    var innerlistitem = $('<li></li>');
		    var innerlistform = $('<form></form>');
		    
		    // Regular dimensions
		    if ( "Quality" != dim_title ) {
			if (! dimension.active ) {
			    innerlistform.append($('<span class="deactivated">(not active)</span>'
						   +'<span class="dimension_text" id="'+dim_id+'">'+dim_title+'</span>'
						   +'<input type="hidden" class="profileid" value="'+profile.id+'" />'
						   +'<input type="submit" class="edit_rp_dim_button" value="edit" />'
						   +'<input type="submit" class="activate_rp_dim_button" value="activate" />'
						   +'<input type="submit" class="del_rp_dim_button" value="-" />'));
			}
			else {
			    innerlistform.append($('<span class="dimension_text" id="'+dim_id+'">'+dim_title+'</span>'
						   +'<input type="hidden" class="profileid" value="'+profile.id+'" />'
						   +'<input type="submit" class="edit_rp_dim_button" value="edit" />'
						   +'<input type="submit" class="deactivate_rp_dim_button" value="deactivate" />'
						   +'<input type="submit" class="del_rp_dim_button" value="-" />'));
			}
		    }
		    // The permanent "Quality" dimension
		    else {
			innerlistform.append($('<span class="dimension_text" id="'+dim_id+'">'+dim_title+'</span>'
					       +'<input type="hidden" class="profileid" value="'+profile.id+'" />'
					       +'</form>'));
		    }
		    innerlistitem.append( innerlistform );
		    innerlist.append( innerlistitem );
		}
		
		listitem.append( innerlist );
		listing.append( listitem );
	    }
	    
	    $('#profiles_listing').append(listing);

	    bind_edit_buttons();
	    bind_deactivate_buttons();
	    bind_activate_buttons();
	    bind_delete_buttons();
	    bind_insert_buttons();
	    bind_remove_buttons();
	}

	var handle_insert_dimension = function() {
	    var newDimSpan = $('<span class="newdimension_span"></span>');
	    var dimLabel = $('<label>Quality '+(dimension_count+1)+'</label>');
	    dimLabel.attr({'for':'dimension_'+dimension_count});
	    $('#newprofile_form').append(dimLabel);

	    var dimText = $('<input />');
	    dimText.attr({'type':'text',
			  'name':'dimension_'+dimension_count,
			  'class':'rp_dimension'});
	    newDimSpan.append($('<br />')).append( dimLabel ).append( dimText);

	    $('#newprofile_form').append( newDimSpan );
	    dimension_count++;
	}

	var handle_remove_dimension = function() {
	    if ( dimension_count > 0 ) {
		$('#newprofile_form').children('.newdimension_span').last().remove();
		dimension_count--;
	    }
	}

	var bind_newprofile_button = function() {

	    $('#new_ratingprofile_button').click(
		function( event ) {
		    // Toggle visibility
		    $('#new_ratingprofile').slideToggle(100);

		    
		    // Don't allow more than one 'new ratingprofile' form at a time
		    if ( $('#new_ratingprofile').children().length > 0 )
			return;


		    // Create the form for adding a ratingprofile
		    var newprofile_form = $('<form action="/business/create_rating_profile/" method="post" id="newprofile_form"></form>');
		    var submit_button = $('<input type="submit" class="rp_okbutton" value="OK" />');
		    submit_button.click( function( event ) {
			event.preventDefault();

			// Hide the new profile form
			$('#new_ratingprofile').slideUp(100);
			
			data = {'title':$('#profile_title').val()}
			// Grab all dimensions
			$('.rp_dimension').each( function(index, element) {
			    data['dim'+index] = $(this).val();
			});
			data['csrfmiddlewaretoken'] = $('input[name=csrfmiddlewaretoken]').val();

			// Make the call to the db
			$.ajax({ url: new_ratingprofile_url,
				 type: 'POST',
				 data: data,
				 success: listProfiles,
				 error: function() { alert("Something went wrong."); }
			       });
			
			$('#new_ratingprofile').empty();
		    });
		    var cancel_button = $('<input />');
		    cancel_button.prop({'type':"submit",
					'id':"newprofile_cancel_button",
					'value':"Cancel",
					'class':"rp_cancel"});
		    cancel_button.click( function( event ) {
			event.preventDefault();
			$('#newprofile_form').remove();
			dimension_count=0;
		    });

		    // Add insert/delete dimension buttons
		    var dim_insert_button = $('<button class="rp_add" type="button">+</button>');
		    var dim_remove_button = $('<button class="rp_minus" type="button">-</button>');

		    // Register click handlers on each of the insert/delete buttons
		    dim_insert_button.click( function() {
			handle_insert_dimension();
		    });
		    dim_remove_button.click( function() {
			handle_remove_dimension();
		    });

		    var new_title = $('<div class="profile_title"></div>');
		    new_title.append( $('<label for="title">Title</label>') );
		    new_title.append( $('<input type="text" name="title" id="profile_title" />') );
		    newprofile_form.append( new_title );
		    newprofile_form.append( dim_insert_button );
		    newprofile_form.append( dim_remove_button );
		    newprofile_form.append( submit_button );
		    newprofile_form.append( cancel_button );



		    
		    // Add the form to the ratingprofile div
		    $('#new_ratingprofile').append( newprofile_form );
		});
	}

	/**
	 * Initilialize the page for managing ratingprofiles.
	 */
	_ns.initRatingProfilesPage = function() {
	    // New profile form is invisible
	    $('#new_ratingprofile').hide();
	    
	    // Get all the rating profiles
	    $.ajax( {
		url: list_ratingprofiles_url,
		success: listProfiles,
		error: function() { alert("Something went wrong."); }
	    });

	    bind_edit_buttons();		// Edit a single dimension's text
	    bind_deactivate_buttons();	// Deactivate one dimension
	    bind_activate_buttons();	// Activate one dimension
	    bind_delete_buttons();		// Delete an entire profile
	    bind_insert_buttons();		// Insert a dimension
	    bind_remove_buttons();		// Remove a dimension
	    bind_newprofile_button();	// Make a new ratingprofile
	}	    

    })(business.ratingprofiles);




    ///////////////////////////////
    // apatapa.business.newsfeed //
    ///////////////////////////////

    if (! business.newsfeed) {
	business.newsfeed = {};
    }

    (function (_ns) {
	
	// Keeps track of which feed is which.
	var i = 0;
	
	/*
	 * Creates the newsfeed in the DOM after receiving data from
	 * our AJAX call.
	 */
	var handleNewsfeedData = function (data) {
	    var add_newsfeed_button = $('<button></button>');
	    add_newsfeed_button.prop({'type': 'button',
				      'name': 'add_newsfeed_button',
				      'id': 'add_newsfeed_button',
				      'class': 'add_newsfeed_button'});
	    add_newsfeed_button.html('Add New Item');
	    add_newsfeed_button.click( function () {
		addFeed(0, "", "Today", "<strong>right now</strong>", "", "", true);
		registerClickHandlers();
	    });
	    add_newsfeed_button.button();
	    var save_newsfeed_button = $('<button></button>');
	    save_newsfeed_button.prop({'type': 'button',
				       'name': 'save_newsfeed_button',
				       'id': 'save_newsfeed_button',
				       'class': 'save_newsfeed_button'});
	    save_newsfeed_button.html('Save Changes');
	    save_newsfeed_button.button();
	    $('#newsfeeds').append(save_newsfeed_button)
		.append(add_newsfeed_button);
	    for(d in data) {
		console.log(data[d]);
		feed = data[d];
		addFeed(feed.id,
			feed.title,
			feed.date,
			feed.date_edited,
			feed.subtitle,
			feed.body,
			false);
	    }
	    registerClickHandlers();
	};
	
	/*
	 * Registers click handlers for all buttons. Called from handleNewsfeedData().
	 */
	var registerClickHandlers = function () {
	    $('.nf_delete_button').click( function () {
		feed = $(this).parent('.feed');
		apatapa.showAlert('Are you sure you want to delete?',
				  'This will erase this item\'s data permanently!',
				  function() {
				      feed.children('#should_delete').val('true');
				      feed.hide(700);
				  });
	    });
	    $('#save_newsfeed_button').click( function () {
		apatapa.showAlert('Are you sure?', 'Saving changes!', saveChanges);
	    });
	};
	
	/*
	 * Save the newsfeed -- just collects all the information from the DOM and
	 * sends it off through AJAX.
	 */
	var saveChanges = function () {
	    var newsfeeds = [];
	    $('.feed').each( function (index, element) {
		var feed_dict = {'title': $(this).children('#title').val(),
				 'id': $(this).children('#feed_' + index + '_id').val(),
				 'should_delete': $(this).children('#should_delete').val(),
				 'subtitle': $(this).children('#subtitle').val(),
				 'body': $(this).children('#body').val()};
		newsfeeds.push(feed_dict);
	    });
	    $.ajax({url: manage_newsfeed_url,
		    type: 'POST',
		    dataType: 'json',
		    data: {'feeds': JSON.stringify(newsfeeds),
			   'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()},
		    error: function () { alert('Something went wrong.'); },
		    success: function () {
			alert('Great success!');
			window.location.replace('/business/');
		    }});
	};
	
	/*
	 * Adds a single newsfeed item to the DOM. Called from handleNewsfeedData().
	 */
	var addFeed = function (id, title, date, date_edited, subtitle, body, animated) {
	    
	    var should_delete = $('<input />');
	    should_delete.prop({'type': 'hidden',
				'value': 'false',
				'name': 'should_delete',
				'id': 'should_delete'});
	    
	    var feed_id = $('<input />');
	    feed_id.prop({'type': 'hidden',
			  'value': id,
			  'class': 'id',
			  'id': 'feed_' + i + '_id',
			  'name': 'feed_' + i + '_id'});
	    
	    var feed_div = $('<div></div>');
	    feed_div.prop({'class': 'feed',
			   'id': 'feed_' + i,
			   'name': 'feed_' + i});
	    
	    if( animated ) {
		feed_div.hide();
	    }
	    
	    var title_text = $('<input />');
	    title_text.prop({'value': title,
			     'type': 'text',
			     'id': 'title',
			     'name': 'title'});
	    
	    var date_text = $('<p></p>');
	    date_text.html(date + ' (last edited ' + date_edited + ')');

	    var subtitle_text = $('<input />');
	    subtitle_text.prop({'type': 'text',
				'name': 'subtitle',
				'id': 'subtitle',
				'value': subtitle});
	    
	    var body_text = $('<textarea></textarea>');
	    body_text.prop({'value': body,
			    'name': 'body',
			    'id': 'body'});
	    
	    var delete_button = $('<button></button>');
	    delete_button.prop({'type': 'button',
				'class': 'nf_delete_button',
				'id': 'feed_' + i + '_delete_button',
				'name': 'feed_' + i + '_delete_button'})
	    delete_button.html('Delete');
	    delete_button.button();
	    
	    $('#save_newsfeed_button').before(feed_div.append('Title: ')
					      .append(feed_id)
					      .append(should_delete)
					      .append(title_text)
					      .append(date_text)
					      .append('Subtitle: ')
					      .append(subtitle_text)
					      .append('<br />')
					      .append('Body: ')
					      .append(body_text)
					      .append('<br />')
					      .append(delete_button));
	    if( animated ) {
		feed_div.show(700);
	    }
	    i++;
	}

	_ns.initNewsfeedPage = function() {
	    $.ajax({url: list_newsfeed_url,
		    type: 'GET',
		    data: {'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()},
		    error: function () { alert('Something went wrong.'); },
		    success: handleNewsfeedData
		   });
	};

    })(business.newsfeed);






    /////////////////////////////
    // apatapa.business.survey //
    /////////////////////////////

    if (! business.survey ) {
	business.survey = {};
    }

    (function ( _ns ) {
	var questionTypes = {"CG":"checkbox group",
			     "RG":"radio group",
			     "TA":"textarea",
			     "TF":"textfield"};
	
	// To indicate that a question is inactive right now.
	var inactive_color = 'rgb(200, 200, 200)';
	
	var question_div_bg_color = 'rgb(255, 235, 250)';

	var registerClickHandlers = function () {
	    
	    // Set up buttons and click handlers.
	    $(".question_div").each( function(index, ele){
		console.log($(this).children(".question_option").length + 'asdfasdf');
		questionOptions[index]=$(this).children(".question_option").length;
	    });
	    
	    $('.deletebutton').click( function () {
		console.log('deleting');
		var parent = $(this).parent('.question');
		apatapa.showAlert('Are you sure you want to delete?',
				  'This will this question\'s data forever!',
				  function () {
				      parent.children('.should_delete').val('true');
				      parent.hide(1000);
				  });
	    });
	    
	    $('.toggleactivebutton').click( function () {
		if($(this).parent('.question').children('.is_active').val() === 'true') {
		    $(this).parent('.question').children('.is_active').val('false');
		    $(this).parent('.question').children('.toggleactivebutton').html('Activate Question');
		    $(this).parent('.question').animate({backgroundColor: inactive_color}, 500);
		    console.log('made inactive');
		}
		else {
		    $(this).parent('.question').children('.is_active').val('true');
		    $(this).parent('.question').children('.toggleactivebutton').html('Deactivate Question');
		    $(this).parent('.question').animate({backgroundColor: question_div_bg_color}, 500);
		    console.log('made active');
		}
	    });
	    


	}

	/*
	 * Creates the survey in the DOM from our first AJAX call.
	 */
	renderSurvey = function( data ) {
	    var survey = data.survey;
	    console.log("Title = "+survey['title']);
	    $('#survey_title').val( survey.title );
	    $('#survey_description').val( survey['description'] );
	    
	    $("#addquestion_button").click(function(event) {
		event.preventDefault();
		// A new question -- ID is 0.
		addQuestion('', 'CG', [], true, 0, true);
		registerClickHandlers();
	    });
	    
	    
	    
	    
	    for ( q in survey.questions ) {
		var question = survey.questions[q];
		
		addQuestion( question.label,
			     question.type,
			     question.options,
			     question.active,
			     question.id,
			     false);
	    }
	    registerClickHandlers();
	    $('#submit_button').click( function(event) {
		event.preventDefault();
		var title = apatapa.util.escapeHTML( $('#survey_title').val() );
		var description = apatapa.util.escapeHTML( $('#survey_description').val() )
		if( title === "" || description === "") {
		    apatapa.showAlert("You're missing something!",
				      'You should fix that.',
				      function () {/* Doesn't really need to do much. */ });
		    return;
		}
		console.log('returns are for noobs');
		var questions = [];
		// Get each question out of the DOM and put its info into a dictionary.
		// This is nasty! But we need some form of non-local exit, so a try/catch
		// block will have to do for now.
		try {
		    $('.question').each( function(index, element) {
			var question_id = $(this).children('.question_id').val();
			var question_label = apatapa.util.escapeHTML( $(this).children('#question_'+index).val() );
			var shouldDelete = $(this).children('.should_delete').val();
			var question_active = $(this).children('.is_active').val();
			var question_options = [];
			$(this).children('.question_option').find('.option_field').each( function(ind, ele) {
			    question_options.push(apatapa.util.escapeHTML( $(this).val()) );
			});
			var question_type = $(this).children('.questionTypeMenu').children(':selected').val();
			// If it's a check or radio, and we don't have options.
			if((question_type === "CG" || question_type === "RG") &&
			   question_options.length === 0 &&
			   shouldDelete === 'false') {
			    // Complain about it, and don't let the user create the survey.
			    alert('Question ' + question_label + ' has question type ' + question_type +' but no options!');
			    throw "no options";
			}
			var question_dict = {'question_id': question_id,
					     'question_label': question_label,
					     'question_active': question_active,
					     'question_options': question_options,
					     'should_delete': shouldDelete,
					     'question_type': question_type};
			questions.push(question_dict);
		    });
		}
		catch( err ) {
		    if(err === "no options") {
			console.log('caught the exception');
			return;
		    }
		}
		// Send it all off.
		$.ajax({url: manage_survey_url,
			data: {'survey_id': $('#survey_id').val(),
			       'survey_title': title,
			       'survey_description': description,
			       'questions': JSON.stringify(questions),
			       'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()
			      },
			type: 'POST',
			error: function() { alert('Something went wrong.'); },
			success: function () { alert('Great success!');
					       window.location.replace('/business/');
					     }
		       });
	    });
	}

	// Keeps track of # of questions
	var i = 0;

	// Start off with question 0 has 1 option
	var questionOptions = [0];

	function addQuestion( label, type, options, active, id, animated ) {
	    //Objects to instantiate:
	    //1.Question label
	    //2.Question type
	    //3.Option field (e.g. first entry of a radio button)
	    //4.Add option button
	    console.log('Adding question: ' + label + ' animated: ' + animated);
	    var questionDiv = $("<div></div>");
	    questionDiv.prop({'id':"question_"+i+"_div",
			      'class':"question"});
	    if( animated ) {
		questionDiv.hide();
	    }
	    
	    $("#submit_button").before(questionDiv);
	    $('#submit_button').button();
	    $('#addquestion_button').button();
	    
	    // If ID is 0, it's a new question.
	    var questionId = $('<input />');
	    questionId.prop({'type': 'hidden',
			     'class': 'question_id',
			     'value': id});
	    
	    var shouldDelete = $('<input />');
	    shouldDelete.prop({'type': 'hidden',
			       'class': 'should_delete',
			       'value': 'false'});
	    
	    var questionAreaLabel = $("<label>Question #"+(i+1)+"</label>");
	    questionAreaLabel.prop({"for":"question_"+i});
	    
	    var questionArea = $("<textarea></textarea>");
	    questionArea.prop({'name':"question_"+i,
			       'id':"question_"+i});
	    questionArea.text( label );
	    var questionTypeLabel = $("<label>Question type </label>");
	    questionTypeLabel.prop({"for":"question_"+i+"_type"});
	    
	    var questionType = $("<select></select>");
	    questionType.prop({'name':"question_"+i+"_type",
			       'id':"question_"+i+"_type",
			       'class': 'questionTypeMenu'});
	    questionType.change( function() {
		if( $(this).children(':selected').val() === 'TA' ||
		    $(this).children(':selected').val() === 'TF') {
		    console.log('changing question type');
		    $(this).siblings('.question_option').hide(1000);
		    $(this).siblings('.option_button').hide(1000);
		}
		else {
		    $(this).siblings('.question_option').show(1000);
		    $(this).siblings('.option_button').show(1000);
		}
	    });
	    // Render question types, selecting the appropriate one by default
	    for ( o in questionTypes ) {
		var optionWidget = $('<option value="'+o+'">'+questionTypes[o]+'</option>');
		if ( type === o ) {
		    optionWidget.prop({'selected':'selected'});
		}
		questionType.append( optionWidget );
	    }
	    
	    // Create a new question bucket for storing # of options
	    questionOptions.push(0);
	    
	    var optionDiv = $("<div></div>");
	    optionDiv.prop({'id':"question_"+i+"_options",
			    'class':"question_option",
			   });
	    var optionList = $("<ul></ul>");
	    optionList.addClass("question_optionlist");

	    // Render each of the options for the question
	    for ( o in options ) {
		var optionLabel = $('<label>Option '+ (parseInt(o) + 1) +'</label>');
		optionLabel.prop({'for':'question_'+i+'_option_'+o});
		var optionWidget = $('<input />');
		optionWidget.prop({'type':'text',
				   'name':'question_'+i+'_option_'+o,
				   'class':'option_field',
				   'value':options[o]});
		
		var optionItem = $('<li></li>');
		optionItem.addClass('question_item');

		optionItem.append( optionLabel ).append( optionWidget );
		optionList.append( optionItem );
		questionOptions[i]++;
	    }

	    optionDiv.append( optionList );

	    var questionNumber = i;
	    var addOptionButton = $("<button>Add Option</button>");
	    addOptionButton.prop({'type':"button",
    				  'name':"question_"+i+"_optionbutton",
     				  'id':"question_"+i+"_optionbutton",
				  'class': 'option_button'});
	    addOptionButton.button();
	    console.log("question number: "+questionNumber);
	    addOptionButton.click(function() {
    		console.log("i is: "+i);
		addOption(questionNumber, true);
	    });
	    
	    // Add a delete button.
	    var deleteButton = $("<button>Delete Question</button>");
	    deleteButton.prop({'type': 'button',
			       'name': 'question_'+i+'_deletebutton',
			       'id': 'question_'+i+'_deletebutton',
			       'class': 'deletebutton'});
	    deleteButton.button();
	    
	    var toggleActiveButton = $('<button></button>');
	    toggleActiveButton.prop({'type': 'button',
				     'name': 'question_'+i+'_toggleactivebutton',
				     'id': 'question_'+i+'_toggleactivebutton',
				     'class': 'toggleactivebutton'});
	    toggleActiveButton.button();
	    
	    var isActive = $('<input />');
	    isActive.prop({'type': 'hidden',
			   'class': 'is_active'
			  });
	    if(active) {
		toggleActiveButton.html('Deactivate Question');
		console.log('setting to true');
		isActive.prop({'value': 'true'});
		console.log(isActive.val());
	    }
	    else {
		toggleActiveButton.html('Activate Question');
		isActive.prop({'value': 'false'});
		questionDiv.css('background-color', inactive_color);
	    }
	    
	    questionDiv
		.append(questionId)
		.append(shouldDelete)
		.append(questionAreaLabel)
		.append(questionArea)
		.append(isActive)
		.append(questionTypeLabel)
		.append(questionType)
		.append($("<br />"))
		.append(optionDiv)
		.append($("<br />"))
		.append(addOptionButton)
		.append($("<br />"))
		.append(deleteButton)
		.append(toggleActiveButton);
	    console.log(i);
	    
	    if( animated ) {
		questionDiv.show(700);
	    }
	    
	    // Hide the add option if we're a textfield or textarea.
	    if(type === 'TA' || type === 'TF') {
		addOptionButton.hide();
	    }
	    i++;
	}


	function addOption(qindex, animated) {
	    var questionOptionsDiv = $("#question_"+qindex+"_options");
	    var optionList = questionOptionsDiv.children('.question_optionlist');

	    var optionFieldLabel = $("<label>Option "+(questionOptions[qindex]+1)+"</label>");
	    optionFieldLabel.prop({"for":"question_"+qindex+"_option_"+questionOptions[qindex]});

	    var optionField = $("<input />");
	    optionField.prop( {'type':'text',
			       'class':'option_field',
			       'name':'question_'+qindex+'_option_'+questionOptions[qindex],
			       'id':'question_'+qindex+'_option_'+questionOptions[qindex]} );
	    console.log("qindex is :"+qindex);
	    questionOptions[qindex]++;

	    var optionItem = $('<li></li>');
	    optionItem.addClass('question_item');
	    
	    if( animated ) {
		optionItem.hide();
	    }

	    optionItem
		.append(optionFieldLabel)
		.append(optionField);

	    optionList.append( optionItem );
	    questionOptionsDiv.append( optionList );
	    if( animated ) {
		optionItem.show(500);
	    }
	}

	_ns.initSurveyPage = function() {
	    // Pull down the survey
	    $.ajax( {
		url: manage_survey_url,
		success: renderSurvey,
		data: {'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()},
		type: 'POST',
		error: function() { alert("Something went wrong."); }
	    });
	}
    })(business.survey);
})(apatapa.business);
