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
 * apatapa.business.coupons
 * */


if (! apatapa.business) {
    apatapa.business = {};
}

(function (business) {
    
    // To indicate that a question is inactive right now.
    var inactive_color = 'rgb(200, 200, 200)';
    var question_div_bg_color = 'rgb(255, 235, 250)';
    
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
		    return false;
		});
	}

	/**
	 * getEmployees
	 *
	 * fills 'container' with the list of employees for current business.
	 */
	_ns.getEmployees = function( container, callback ) {
	    $.ajax({url: list_employees_url,
		    type: 'GET',
		    data:{},
		    success: function(data) {
			_ns.listEmployee(data, container);
			if ( callback )
			    callback();
		    },
		    error: function() {
			alert("Something went wrong....");
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
	
	/*
         * Returns a div containing employee information
	 * 
	 * TODO: Pass this a parameter list detailing which information the div should hold
	 */
	_ns.listEmployee = function(employee){
	    var employee_div = $('<div></div>');
	    employee_div.prop({'id':'employee_'+employee.id+'_div'});

	    var employee_image = $('<input />');
	    employee_image.prop({'value':employee.image,
				 'type':'hidden',
				 'class':'nfimage'});
	    var employee_id = $('<input />');
	    employee_id.prop({'type':'hidden',
			      'value':employee.id});


	    var employee_info_div = $('<div></div>');
	    employee_info_div.prop({'class':'employee_info'});

	    var employee_name = $('<span></span>');
	    employee_name.prop({'class':'employee_name'});
            employee_name.text(employee.first_name+" "+employee.last_name);
	    
	    var employee_info = $('<div></div>')
	    employee_info.prop({'bio':employee.bio});

	    employee_info_div.append(employee_name)
		.append(employee_info);

	    employee_div.append(employee_image)
		.append(employee_id)
	        .append(employee_info_div);
	    
	    return employee_div;

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
	    return false;
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
	    return false;
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
	    return false;
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
	    return false;
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
		var edit_span = $('<span class="edit_span"></span>');
		var dimfield = $('<input />');
		dimfield.prop({'type':'text',
			       'value':	dimdom.text(),
			       'class':'dimfield_edit'});
		dimdom.replaceWith( edit_span.append(dimfield)
				    .append($('<input type="checkbox" id="is_text" name="is_text"></input>'))
				    .append($('<label for="is_text">text response?</label>')));
		
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
				  'is_text': $(this).siblings('.edit_span').children('#is_text').is(':checked') ? 'true' : 'false',
				  'with_dim': $(this).siblings('.edit_span').children('.dimfield_edit').val(),
				  'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()},
			    success: listProfiles,
			    error: function() { alert("Something went wrong."); }
			   });
		    return false;
		});
		return false;
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
		var is_text = $('<input type="checkbox" id="is_text" name="is_text"></input>');
		var is_text_label = $('<label for="is_text">text response?</label>');
		submit.click( function( event ) {
		    event.preventDefault();
		    var profile_id = $(this).siblings('.profileid').val();
		    $.ajax({ url: manage_ratingprofiles_url,
			     type: 'POST',
			     data: {'profile_id':$(this).parent('#insert_dimension_div').siblings('.profileid').val(),
				    'insert':escape(apatapa.util.escapeHTML( $('#dimension_title').val() )),
				    'is_text': $(this).siblings('#is_text').is(':checked') ? 'true' : 'false',
				    'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()},
			     success: listProfiles,
			     error: function() { alert("Something went wrong."); }
			   });
		    return false;
		});

		newdimdiv
		    .append( '<br />' )
		    .append( label )
		    .append( textfield )
		    .append( is_text )
		    .append( is_text_label )
		    .append( submit );
		$(this).parent().append(newdimdiv);
		return false;
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
		    var is_text = dimension.is_text;
		    var innerlistitem = $('<li></li>');
		    var innerlistform = $('<form></form>');
		    var is_text_text;
		    if(is_text) {
			is_text_text = " (text response) ";
		    }
		    else {
			is_text_text = "";
		    }
		    // Regular dimensions
		    if ( "Quality" != dim_title ) {
			if (! dimension.active ) {
			    innerlistform.append($('<span class="dimension_text" id="'+dim_id+'">'+dim_title+'</span>'
						   +'<span>'+is_text_text+'</span>'
						   +'<input type="hidden" class="profileid" value="'+profile.id+'" />'
						   +'<input type="submit" class="edit_rp_dim_button" value="edit" />'
						   +'<input type="submit" class="activate_rp_dim_button" value="activate" />'
						   +'<input type="submit" class="del_rp_dim_button" value="-" />'));
			}
			else {
			    innerlistform.append($('<span class="dimension_text" id="'+dim_id+'">'+dim_title+'</span>'
						   +'<span class="deactivated">'+is_text_text+'</span>'
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
	    
	    var is_text = $('<input />');
	    is_text.prop({'type': 'checkbox',
			  'class': 'is_text',
			  'name': 'is_text'});
	    
	    var is_text_label = $('<label>Text rating</label>');
	    is_text_label.prop({'for': 'is_text'});
	    
	    var dimText = $('<input />');
	    dimText.attr({'type':'text',
			  'name':'dimension_'+dimension_count,
			  'class':'rp_dimension'});
	    newDimSpan.append($('<br />')).append( dimLabel )
		.append( dimText)
		.append(is_text)
		.append(is_text_label);

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
		    $('#new_ratingprofile').slideToggle(300);
		    // Don't allow more than one 'new ratingprofile' form at a time
		    if ( $('#new_ratingprofile').children().length > 0 )
			return;
		    // Create the form for adding a ratingprofile
		    var newprofile_form = $('<form action="/business/create_rating_profile/" method="post" id="newprofile_form"></form>');
		    var submit_button = $('<input type="submit" class="rp_okbutton" value="OK" />');
		    submit_button.click( function( event ) {
			event.preventDefault();
			// Grab all dimensions
			dimensions = []
			$('.rp_dimension').each( function(index, element) {
			    dim_dict = {'dimension': $(this).val(),
					'is_text': $(this).siblings('.is_text').is(':checked')};
			    dimensions.push(dim_dict);
			});
			if(dimensions.length === 0) {
			    apatapa.showAlert('Hold on!', 'You should maybe add some dimensions before submitting.', null);
			    return;
			}
			// Hide the new profile form
			$('#new_ratingprofile').slideUp(100);
			data = {'title':$('#profile_title').val()};
			data['csrfmiddlewaretoken'] = $('input[name=csrfmiddlewaretoken]').val();
			data['dimensions'] = JSON.stringify(dimensions);
			// Make the call to the db
			$.ajax({ url: new_ratingprofile_url,
				 type: 'POST',
				 data: data,
				 success: listProfiles,
				 error: function() { alert("Something went wrong."); }
			       });
			$('#new_ratingprofile').empty();
			return false;
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
	    return false;
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
		addFeed(0, "", "Today", "<strong>right now</strong>", "", "", "", true);
		registerClickHandlers();
	    });
	    for(d in data) {
		feed = data[d];
		addFeed(feed.id,
			feed.title,
			feed.date,
			feed.date_edited,
			feed.subtitle,
			feed.body,
			feed.image,
			false);
	    }
	    $('#add_newsfeed_button').click( function () {
		addFeed(0, "New Newsfeed Item", "Today", "<strong>right now</strong>", "", "", "", true);
	    });
	};
	
	/**
	 * Delete a single newsfeed.
	 *
	 * index - The index of the newsfeed to delete. This is the index as it appears
	 * on the page, NOT the id.
	 */
	var deleteNewsfeed = function( index ) {
	    console.log("delete newsfeed");
	    // easay peasay
	    $.ajax({url: manage_newsfeed_url,
		    type:'POST',
		    data: {'delete_newsfeed':'true',
			   'id':$("#feed_id_"+index).val(),
			   'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()
			  },
		    error: function(){alert("Something went wrong.");}
		   });
	}

	/**
	 * Edits a single newsfeed item. Editing div appears instead of the summary
	 * of the original feed listing.
	 *
	 * feedNo - the index of the newsfeed to edit. -1 is a new feed.
	 */
	var editFeed = function( feedNo ) {
	    // Fields to fill in with already existing data, potentially
	    var id,title,date,date_edited,subtitle,body,image;

	    // Where to put all this stuff. Will be with summary unless this is a new
	    // news feed item.
	    var container;

	    // Dates in Javascript. Seriously, Javascript?
	    var the_date = new Date();
	    var dd = the_date.getDate();
	    var mm = the_date.getMonth()+1;
	    mm = mm < 10? '0'+mm : mm;
	    var yyyy = the_date.getFullYear();
	    date_edited = mm+'/'+dd+'/'+yyyy;

	    if ( feedNo >= 0 ) {
		var sourceFeed = $('#feed_'+feedNo);
		id = sourceFeed.children('.id').val();
		title = sourceFeed.children('.nftitle').text();
		date = sourceFeed.children('.nfdate').text();
		subtitle = sourceFeed.children('.nfsubtitle').val();
		body = sourceFeed.children('.nfbody').val();
		image = sourceFeed.children('.nfimage').val();
		container = $("#feed_"+feedNo);
	    } else {
		// id = 0 means we have a new newsfeed item
		id = 0;
		// increment count of newsfeed items
		i++;
		// set all fields to blank by default, except for 'date'
		title = subtitle = body = image = "";
		date = date_edited;
		// A new div for this item.
		container = ("<div></div>");
		container.prop({'class': 'feed',
				'id': 'feed_' + i,
				'name': 'feed_' + i});
	    }
	    
	    var feed_id = $('<input />');
	    feed_id.prop({'type': 'hidden',
			  'value': id,
			  'class': 'id',
			  'id': 'id_feed_id',
			  'name': 'feed_id'});
	    
	    var imgDiv = $('<div></div>');
	    imgDiv.addClass('imagediv');
	    var img = $('<img />');
	    img.prop({'src': image,
		      'class': 'nfimage',
		      'alt': title});
	    
	    var imgFieldDiv = $('<div></div>');
	    imgFieldDiv.addClass('imgfield');
	    var img_label = $('<label>Image</label>');
	    img_label.prop("for","nf_image");
	    var img_input = $('<input />');
	    img_input.prop({'type': 'file',
			    'accept': 'image/*',
			    'class': 'image_input',
			    'name': 'nf_image',
			    'id': 'nf_image'});
	    imgDiv
		.append(img)
		.append(
		    imgFieldDiv
			.append(img_label)
			.append(img_input));
	    
	    var title_label = $('<label>Title</label>');
	    title_label.prop("for","title");
	    var title_text = $('<input />');
	    title_text.prop({'value': title,
			     'type': 'text',
			     'id': 'id_title',
			     'name': 'title'});
	    
	    var csrf_field = $('<input />');
 	    csrf_field.prop({'type':'hidden',
			     'name':"csrfmiddlewaretoken",
			     'value':$('input[name=csrfmiddlewaretoken]').val()});

	    var date_text = $('<p></p>');
	    date_text.html(date + ' (last edited ' + date_edited + ')');

	    var subtitle_label = $('<label>Subtitle</label>');
	    subtitle_label.prop("for","nfsubtitle");
	    var subtitle_text = $('<input />');
	    subtitle_text.prop({'type': 'text',
				'name': 'subtitle',
				'class': 'nfsubtitle',
				'name': 'nfsubtitle',
				'id': 'id_subtitle',
				'value': subtitle});
	    
	    var body_label = $('<label>Body</label>');
	    body_label.prop("for","body");
	    var body_text = $('<textarea></textarea>');
	    body_text.prop({'class':'nfbody',
			    'name': 'body',
			    'id': 'id_body'})
	    body_text.val(body);

	    // delete_button is the button that deletes any particular newsfeed
	    var delete_button = $('<button></button>');
	    delete_button.prop({'type': 'button',
				'class': 'nf_delete_button',
				'id': 'feed_delete_button_' + i,
				'name': 'feed_delete_button_' + i});
	    delete_button.html('Delete');
	    delete_button.click( function () {
	    	console.log("delete button clicked");
	    	feed = $(this).parents('.feed');
	    	apatapa.showAlert('Are you sure you want to delete?',
	    			  '',
				  function() {
	    			      feed.hide(700);
				      // This gets the index of the feed
				      deleteNewsfeed(feed.find(".id").prop("id").split("_")[2]);
				  });
	    });

	    var editForm = $('<form></form>');
	    editForm.prop({"action": manage_newsfeed_url,
			   "method": "POST",
			   "enctype": "multipart/form-data",
			   "id":"nf_editing_form"});

	    var wrapFormField = function() {
		var newDiv = $('<div></div>');
		newDiv.addClass("formfield");
		return newDiv;
	    };
	    
	    editForm
		.append(csrf_field)
	    	.append(feed_id)
		.append(wrapFormField()
			.append(title_label)
	    		.append(title_text))
		.append(imgDiv)
		.append(wrapFormField()
			.append(subtitle_label)
	    		.append(subtitle_text))
		.append(wrapFormField()
			.append(body_label)
	    		.append(body_text));
	    var submitButton = $("<button>OK</button>");
	    submitButton.prop({"type":"submit"});
	    editForm.append(submitButton);

	    // Build all the elements.
	    container.append(editForm)
	    i++;
	}

	/*
	 * Adds a summary version of a NewsFeedItem. This includes a button to "edit", which
	 * calls 'editFeed()'. 'addFeed()' is used to list the newsfeed items.
	 */
	var addFeed = function (id, title, date, date_edited, subtitle, body, image, animated) {

	    console.log("Adding feed with body: "+body);
	    
	    // DIV to house the newsfeed listing
	    var feed_div = $('<div></div>');
	    feed_div.prop({'class': 'feed',
			   'id': 'feed_' + i,
			   'name': 'feed_' + i});

	    // Give the id of the NewsFeedItem
	    var feed_id = $('<input />');
	    feed_id.prop({'type': 'hidden',
			  'value': id,
			  'class': 'id',
			  'id': 'feed_id_' + i,
			  'name': 'feed_id_' + i});
	    
	    if( animated ) {
		feed_div.hide();
	    }
	    
	    // SPAN to hold the title text, as well as the text itself.
	    var title_text = $('<span></span>');
	    title_text.prop({'type': 'text',
			     'id': 'title_' + i,
			     'class':'nftitle',
			     'name': 'title_' + i});
	    title_text.html(title);
	    
	    // When the newsfeed item was first created
	    var date_text = $('<span></span>');
	    date_text.addClass('nfdate');
	    date_text.html(date);

	    // When the newsfeed item was last edited
	    var date_edited_text = $('<span></span>');
	    date_edited_text.addClass('nfdateedited');
	    date_edited_text.html('(last edited ' + date_edited + ')');

	    // The body of the newsfeed item
	    var bodyField = $('<input/>');
	    bodyField.prop({'type':'hidden',
			    'value':body,
			    'class':'nfbody',
			    'name': 'body_' + i,
			    'id': 'body_' + i});

	    // And the subtitle
	    var subtitleField = $('<input/>');
	    subtitleField.prop({'type':'hidden',
				'value':subtitle,
				'class':'nfsubtitle',
				'name':'subtitle_'+i,
				'id':'subtitle_'+i});

	    // Field for uploading a new image for this item.
	    var img = $('<input />');
	    img.prop({'value': image,
		      'class': 'nfimage',
		      'type': 'hidden'});

	    // delete_button is the button that deletes any particular newsfeed
	    var delete_button = $('<button></button>');
	    delete_button.prop({'type': 'button',
				'class': 'nf_delete_button',
				'id': 'feed_delete_button_' + i,
				'name': 'feed_delete_button_' + i});
	    delete_button.html('Delete');
	    delete_button.click( function () {
	    	feed = $(this).parents('.feed');
	    	apatapa.showAlert('Are you sure you want to delete?',
	    			  '',
				  function() {
	    			      feed.hide(700);
				      // This gets the index of the feed
				      deleteNewsfeed(feed.find(".id").prop("id").split("_")[2]);
				  });
	    });
	    // edit_button is the button that creates an edit form for this newsfeed
	    // TODO: implement this without DEEP recursion. Hahahahaha
	    var edit_button = $('<button></button>');
	    edit_button.prop({'type':'button',
			      'class':'nf_edit_button',
			      'id':'feed_edit_button_'+i,
			      'name':'feed_edit_button_'+i});
	    edit_button.html("Edit");
	    edit_button.click(function() {
		// Make sure there are no other "cancel" buttons
		$('.nf_cancel_button').hide();
		$('.nf_edit_button').show();

		// Hide this edit button
		$(this).hide();
		// Turn on the cancel button
		cancel_button.css("display","inline");

		var index = edit_button.prop('id').split('_')[3];
	    	$('#nf_editing_form').hide("fast");
	    	$('#nf_editing_form').remove();
	    	editFeed(index);
	    });
	    var cancel_button = $('<button></button>');
	    cancel_button.prop({'type':'button',
				'class':'nf_cancel_button',
				'id':'feed_cancel_button_'+i,
				'name':'feed_cancel_button_'+i});
	    cancel_button.html("Cancel");
	    cancel_button.click(function() {
		$(this).hide();
		edit_button.css("display","inline");
		$('#nf_editing_form').hide("fast");
	    	$('#nf_editing_form').remove();
	    });
	    cancel_button.hide();

	    var buttonsSpan = $('<span></span>');
	    buttonsSpan.addClass("deleteedit");
	    buttonsSpan
		.append(delete_button)
		.append(edit_button)
		.append(cancel_button);

	    // Add this item to the rest of the listings.
	    $('#newsfeeds').append(feed_div
	    			   .append(title_text)
				   .append(img)
				   .append(subtitleField)
				   .append(bodyField)
	    			   .append(feed_id)
	    			   .append(date_text)
				   .append(date_edited_text)
				   .append(buttonsSpan));

	    // Animate! (oooooh----aaaaaaaaaaah....)
	    if( animated ) {
		feed_div.show(700);
	    }
	    i++;
	}

	_ns.initNewsfeedPage = function(num_feeds) {
	    $.ajax({url: list_newsfeed_url,
	    	    type: 'GET',
	    	    data: {'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()},
	    	    error: function () { alert('Something went wrong.'); },
	    	    success: handleNewsfeedData
	    	   });

	    $(".hidden").hide();
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
			     "TA":"long text",
			     "TF":"short text"};
	
	// Keeps track of # of questions
	var i = 0;
	


	var registerClickHandlers = function () {

	    // Set up buttons and click handlers.
	    	    
	    $("#submit_button").click ( function (event) {
		event.preventDefault();
		var survey_title = $("#survey_title").val();
		var survey_description = $("#survey_description").val();
		var survey_id = $("#survey_id").val();
		var questions = [];
	
		$(".question").each( function( index, element ) {
		    var question_dict={};
		    question_dict['question_id']=$(this).children(".question_id").val();
		    question_dict['label'] = $(this).find("textarea").val();
		    question_dict['options'] = [];
		    $(this).find(".option_field").each( function (ind, ele) {
			question_dict['options'].push($(this).val());
		    });
		    
		    question_dict['active'] = $(this).find(".is_active").val();
		    question_dict['type'] = $(this).find("option:selected").val();
		    question_dict['should_delete'] = $(this).find(".should_delete").val();

		    questions.push(question_dict);

		});
	

		$.ajax({url: manage_survey_url,
			type: 'POST',
			dataType: 'json',
			data: {'survey_id':survey_id,
			       'survey_title':survey_title,
			       'survey_description':survey_description,
			       'questions':JSON.stringify(questions),
			   'csrfmiddlewaretoken':$("input[name=csrfmiddlewaretoken]").val()},
			success: function() { window.location.reload(); },
			error: function() {alert("something went wrong.")}
		       });
	    });

	}

	/*
	 * Creates the survey in the DOM from our first AJAX call.
	 */
	renderSurvey = function( data ) {
	    var survey = data.survey;
	    $("#survey_id").val(survey['id']);
	    $('#survey_title').val( survey.title );
	    $('#survey_description').val( survey['description'] );
	    $("#addquestion_button").click(function(event) {
		event.preventDefault();
		// A new question -- ID is 0.
		addQuestion('', 'CG', [], true, 0, false);
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
	    
	}


	// Start off with question 0 has 1 option
	var questionOptions = [0];

	function addQuestion( label, type, options, active, id, animated ) {
	    //Objects to instantiate:
	    //1.Question label
	    //2.Question type
	    //3.Option field (e.g. first entry of a radio button)
	    //4.Add option button

	    var questionDiv = $("<div></div>");
	    questionDiv.prop({'id':"question_"+i+"_div",
			      'class':"question"});
	    if( animated ) {
		questionDiv.hide();
	    }
	    
	    
	    // If ID is 0, it's a new question.
	    var questionId = $('<input />');
	    questionId.prop({'type': 'hidden',
			     'class': 'question_id',
			     'value': id});
	    
	    var shouldDelete = $('<input />');
	    shouldDelete.prop({'type': 'hidden',
			       'class': 'should_delete',
			       'value': 'false'});
	    
	    // This div will contain the parts that are visible (there will be an expand button)
	    var question_visible_div = $("<div></div>");
	    question_visible_div.prop({'id':"question_visible_"+i+"_div",
				       'class':"question_visible_div visible"});

	    var questionAreaLabel = $("<label>Question</label>");
	    questionAreaLabel.prop({"for":"question_"+i});
	    
	    var questionArea = $("<textarea></textarea>");
	    questionArea.prop({'name':"question_"+i,
			       'id':"question_"+i});
	    questionArea.keyup(function () {
		var index = $(this).prop('id').split('_')[1];
		apatapa.business.control_panel.updateQuestion(id, index, $(this).val());
	    });
	    questionArea.text( label );

	    var expand_button = $("<button>+</button>");
	    expand_button.prop({'id':"survey_expand_button_"+(i+1),
				'class': "expand_button visible"});

	    var contract_button = $("<button>-</button>");
	    contract_button.prop({'id':"survey_contract_button_"+(i+1),
				  'class': "contract_button"});
	    

	    question_visible_div
		.append(questionAreaLabel)
		.append(expand_button)
		.append(contract_button)
		.append(questionArea);

	    // All the other fields will initially be hidden, and in this div
	    var question_hidden_div = $("<div></div>");
	    question_hidden_div.prop({'id':"question_hidden_"+(i+1)+"_div",
				      'class':"question_hidden_div"});

	    var questionTypeLabel = $("<label>Question type </label>");
	    questionTypeLabel.prop({"for":"question_"+i+"_type"});
	    
	    var questionType = $("<select></select>");
	    questionType.prop({'name':"question_"+i+"_type",
			       'id':"question_"+i+"_type",
			       'class': 'questionTypeMenu'});
	    questionType.change( function() {
		if( $(this).children(':selected').val() === 'TA' ||
		    $(this).children(':selected').val() === 'TF') {
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
	    addOptionButton.click(function() {
		addOption(questionNumber, true);
		return false;
	    });
	    
	    // Add a delete button.
	    var deleteButton = $("<button>Delete Question</button>");
	    deleteButton.prop({'type': 'button',
			       'name': 'question_'+i+'_deletebutton',
			       'id': 'question_'+i+'_deletebutton',
			       'class': 'deletebutton'});
	    var toggleActiveButton = $('<button></button>');
	    toggleActiveButton.prop({'type': 'button',
				     'name': 'question_'+i+'_toggleactivebutton',
				     'id': 'question_'+i+'_toggleactivebutton',
				     'class': 'toggleactivebutton'});
	    var isActive = $('<input />');
	    isActive.prop({'type': 'hidden',
			   'class': 'is_active'
			  });
	    // Add the iphone question, so that we can hide it if necessary
	    apatapa.business.control_panel.addQuestion(i, id, label);
	    
	    if(active) {
		toggleActiveButton.html('Deactivate Question');
		isActive.prop({'value': 'true'});
	    }
	    else {
		toggleActiveButton.html('Activate Question');
		isActive.prop({'value': 'false'});
		questionDiv.css('background-color', inactive_color);
		console.log('hiding');
		apatapa.business.control_panel.hideQuestion(id,
							    toggleActiveButton.prop('id').split('_')[1]);
	    }

	    question_hidden_div
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

	    questionDiv
		.append(questionId)
		.append(shouldDelete)
		.append(question_visible_div)
		.append(question_hidden_div)

	    
	    if( animated ) {
		questionDiv.show(700);
	    }
	    
	    // Hide the add option if we're a textfield or textarea.
	    if(type === 'TA' || type === 'TF') {
		addOptionButton.hide();
	    }
	    
	    $("#survey_questions_div").append(questionDiv);
	    
	    // Hide the hidden div for each question.
	    question_hidden_div.hide();

	    // Click handlers that were moved from registerClickHandlers because they were being called more than once.

	    $("#question_"+i+"_div").find('.deletebutton').click( function () {
		var parent = $(this).parents('.question');
		var id_to_delete = parent.children('.question_id').val();
		var index_to_delete = $(this).prop('id').split('_')[1];
		apatapa.showAlert('Are you sure you want to delete?',
				  'This will this question\'s data forever!',
				  function () {
				      apatapa.business.control_panel.deleteQuestion(id_to_delete, index_to_delete);
				      parent.children('.should_delete').val('true');
				      parent.hide(1000);
				  });
		return false;
	    });

	    $("#question_"+i+"_div").find(".expand_button").click( function (event) {
		event.preventDefault();
		$(this).parent().siblings(".question_hidden_div").show();
		$(this).siblings(".contract_button").show();
		$(this).hide();
		return false;
	    });
	    
	    $("#question_"+i+"_div").find(".contract_button").hide();
	    $("#question_"+i+"_div").find(".contract_button").click( function (event) {
		event.preventDefault();
		$(this).parent().siblings(".question_hidden_div").hide();
		$(this).siblings(".expand_button").show();
		$(this).hide();
		return false;
	    });
	    
	    
	    $("#question_"+i+"_div").find('.toggleactivebutton').click( function () {
		if($(this).parents('.question').find('.is_active').val() === 'true') {
		    $(this).parents('.question').find('.is_active').val('false');
		    $(this).parents('.question').find('.toggleactivebutton').html('Activate Question');
		    $(this).parents('.question').animate({backgroundColor: inactive_color}, 500);
		    apatapa.business.control_panel.hideQuestion($(this).parents('.question').children('.question_id').val(),
								$(this).prop('id').split('_')[1]);
		}
		else {
		    $(this).parents('.question').find('.is_active').val('true');
		    $(this).parents('.question').find('.toggleactivebutton').html('Deactivate Question');
		    $(this).parents('.question').animate({backgroundColor: question_div_bg_color}, 500);
		    apatapa.business.control_panel.showQuestion($(this).parents('.question').children('.question_id').val(),
								$(this).prop('id').split('_')[1]);
		}
		return false;
	    });


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
		type: 'GET',
		error: function() { alert("Something went wrong."); }
	    });
   
	}
    })(business.survey);
    


    //////////////////////////////
    // apatapa.business.coupons //
    //////////////////////////////

    if (! business.coupons ) {
	business.coupons = {};
    }

    (function ( _ns ) {
	/**
	 * briefCouponDiv(coupon)
	 * 
	 * Build an HTML div to display a single coupon in a compact and concise manner.
	 *
	 * coupon = JSON-encoded representation of a Coupon. See the CouponEncoder for details.
	 */
	var briefCouponDiv = function(coupon) {
	    var newDiv = $("<div></div>");
	    newDiv.addClass("coupon");

	    var couponTitle = $("<span>"+coupon.title+"</span>");
	    couponTitle.addClass("coupontitle");

	    newDiv.append(couponTitle).append(couponDate);
	    return newDiv;
	};

	/**
	 * listCouponsBriefly(coupons)
	 *
	 * Builds a list of coupons in HTML. Takes a JSON'd list of coupons, per
	 * the CouponEncoder. Calls "briefCouponDiv(coupon)". The resulting list contains
	 * a minimal amount of information about each coupon, just enough to select
	 * one and award one to a customer. Compare this function with 'listCoupons(coupons)'
	 *
	 * coupons = The JSON'd list of coupons.
	 * container = An HTML node to insert the list into (e.g., a "div")
	 */
	_ns.listCouponsBriefly = function(coupons, container) {
	    console.log(coupons);

	    var couponList = $("<ul></ul>");
	    couponList.prop({"id":"coupon_list"});

	    for (var c in coupons) {
		var coupon = coupons[c];
		couponList.append( briefCouponDiv(coupon) );
	    }

	    container.append( couponList );
	};
	
    })(business.coupons);

})(apatapa.business);
