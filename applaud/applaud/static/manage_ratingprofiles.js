var ratingProfile = {};

(function (ratingProfile) {
    // Keeps track of how many dimensions we have when creating
    // a new RatingProfile.
    var dimension_count = 0;

    /**
     * bind_delete_buttons
     *
     * Binds a callback to the buttons that remove an entire ratingprofile.
     */
    var bind_delete_buttons = function() {
	console.log('binding to buttons');
	$('.del_rp_button').click(
	    function ( event ) {
		console.log("Handler called for clik: "+$(this).attr('id').split('_')[2]);
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

	    // // Make this now an 'activate' button
	    // $(this).prop({ 'value':'activate',
	    // 		   'class':'activate_rp_dim_button' });
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

	    // // Make this now an 'deactivate' button
	    // $(this).prop({ 'value':'deactivate',
	    // 		   'class':'deactivate_rp_dim_button' });
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
	    var submit = $("<input type=\"submit\" id=\"submit_"+$(this).attr('id').split('_')[3]+"\" value=\"OK\" />");
	    submit.click( function( event ) {
		event.preventDefault();
		var profile_id = $(this).siblings('.profileid').val();
		console.log("Submitting dimension... --- "+profile_id);
		$.ajax({ url: manage_ratingprofiles_url,
			 type: 'POST',
			 data: {'profile_id':$(this).parent('#insert_dimension_div').siblings('.profileid').val(),
				'insert':escape(escapeHTML( $('#dimension_title').val() )),
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
	console.log("listProfiles is called.");
	// Clear the current list
	$('#profiles_listing').empty();
	var listing = $('<ul></ul>');

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
		if ( "Quality" != dimension ) {
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
		// Don't allow more than one 'new ratingprofile' form at a time
		if ( $('#new_ratingprofile').children().length > 0 )
		    return;


		// Create the form for adding a ratingprofile
		var newprofile_form = $('<form action="/business/create_rating_profile/" method="post" id="newprofile_form"></form>');
		var submit_button = $('<input type="submit" value="OK" />');
		submit_button.click( function( event ) {
		    event.preventDefault();
		    
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
		cancel_button.prop({'type':'submit',
				    'id':'newprofile_cancel_button',
				    'value':"Cancel"});
		cancel_button.click( function( event ) {
		    event.preventDefault();
		    $('#newprofile_form').remove();
		    dimension_count=0;
		});

		// Add insert/delete dimension buttons
		var dim_insert_button = $('<button type="button">+</button>');
		var dim_remove_button = $('<button type="button">-</button>');

		// Register click handlers on each of the insert/delete buttons
		dim_insert_button.click( function() {
		    handle_insert_dimension();
		});
		dim_remove_button.click( function() {
		    handle_remove_dimension();
		});

		newprofile_form.append( dim_insert_button );
		newprofile_form.append( dim_remove_button );
		newprofile_form.append( submit_button );
		newprofile_form.append( cancel_button );

		newprofile_form.append( $('<label for="title">Title</label>') );
		newprofile_form.append( $('<input type="text" name="title" id="profile_title" />') );
		
		// Add the form to the ratingprofile div
		$('#new_ratingprofile').append( newprofile_form );
	    });
    }

    /**
     * This is executed after the page has fully loaded.
     */
    $(document).ready(function() {
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
    });
})(ratingProfile);
