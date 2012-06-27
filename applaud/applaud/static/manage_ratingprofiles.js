// Keeps track of how many dimensions we have when creating
// a new RatingProfile.
var dimension_count = 0;

/**
 * bind_delete_buttons
 *
 * Binds a callback to the buttons that remove an entire ratingprofile.
 */
function bind_delete_buttons() {
    console.log('binding to buttons');
    $('.del_rp_button').click(
	function ( event ) {
	    console.log("Handler called for clik: "+$(this).attr('id').split('_')[2]);
	    event.preventDefault();
	    $.ajax({ url:'/business/business_manage_ratingprofiles/',
		     type: 'POST',
		     data: {'profile_id':$(this).attr('id').split('_')[3],
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
function bind_remove_buttons() {
    $('.del_rp_dim_button').click(
	function ( event ) {
	    event.preventDefault();
	    $.ajax({ url:'/business/business_manage_ratingprofiles/',
		     type: 'POST',
		     data: {'profile_id':$(this).prev().prev().val(),
			    'remove_dim':$(this).prev().val(),
			    'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()},
		     success: listProfiles,
		     error: function() { alert("Something went wrong."); }
		   });
	});
}

/**
 * submit_dimension
 *
 * Submits information to the server to add a dimension to a ratingprofile.
 */
function submit_dimension( event ) {
    event.preventDefault();
    
    $.ajax({ url:'/business/business_manage_ratingprofiles/',
	     type: 'POST',
	     data: {'profile_id':$(this).attr('id').split('_')[1],
		    'insert':$('#dimension_title').val(),
		    'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()},
	     success: listProfiles,
	     error: function() { alert("Something went wrong."); }
	   });
}

/**
 * bind_insert_buttons
 *
 * Binds a callback to the buttons that insert a dimension for a
 * ratingprofile.
 */
function bind_insert_buttons() {
    $('.ins_rp_button').click( function(event) {
	// Close all other 'insert dimension' forms
	$('#insert_dimension_div').remove();

	event.preventDefault();
	var newdimdiv = $("<div id=\"insert_dimension_div\"></div>");
	var label = $("<label for=\"dimension_title\">New dimension name</label>");
	var textfield = $("<input type=\"text\" name=\"dimension_title\" id=\"dimension_title\" />");
	var submit = $("<input type=\"submit\" id=\"submit_"+$(this).attr('id').split('_')[3]+"\" value=\"OK\" />");
	submit.click( submit_dimension );
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
    var listing = $('<ul></ul>');

    for ( p in data.rating_profiles ) {
	profile = data.rating_profiles[p];
	var listitem = $('<li><strong>'+profile.title+'</strong></li>');

	// This is the way it's done per the RatingProfileEncoder
	var listform = $("<form action=\"/business/business_manage_ratingprofiles/\" method=\"post\">"
			 +"<input type=\"hidden\" name=\"csrfmiddlewaretoken\" value=\""+$('input[name=csrfmiddlewaretoken]').val()+"\" />"
			 +"<input type=\"submit\" id=\"del_rp_button_"+profile.id+"\" class=\"del_rp_button\" value=\"Delete\" />"
			 +"<input type=\"submit\" id=\"ins_rp_button_"+profile.id+"\" class=\"ins_rp_button\" value=\"Insert\" />");
	listitem.append( listform );

	var innerlist = $('<ul></ul>');
	for ( d in profile.dimensions ) {
	    var dimension = profile.dimensions[d];
	    var innerlistitem = $('<li></li>');
	    
	    innerlistitem.append($('<form action="/business/business_manage_ratingprofiles/" method="post" />'
				   +dimension
				   +'<input type="hidden" value="'+profile.id+'" />'
				   +'<input type="hidden" value="'+dimension+'" />'
				   +'<input type="submit" class="del_rp_dim_button" value="-" />'
				   +'</form>'));

	    innerlist.append( innerlistitem );
	}
	
	listitem.append( innerlist );
	listing.append( listitem );
    }
    
    $('#profiles_listing').append(listing);
    bind_delete_buttons();
    bind_insert_buttons();
    bind_remove_buttons();
}

function handle_insert_dimension() {
    $('#newprofile_form').append($('<br />'));

    var dimLabel = $('<label>Quality '+(dimension_count+1)+'</label>');
    dimLabel.attr({'for':'dimension_'+dimension_count});
    $('#newprofile_form').append(dimLabel);

    var dimText = $('<input />');
    dimText.attr({'type':'text',
		  'name':'dimension_'+dimension_count,
		  'class':'rp_dimension'});

    $('#newprofile_form').append( dimLabel ).append( dimText );
    dimension_count++;
}

function handle_remove_dimension() {
    // dimension_count--;
}

function bind_newprofile_button() {

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
		$.ajax({ url:'/business/business_new_ratingprofile/',
			 type: 'POST',
			 data: data,
			 success: listProfiles,
			 error: function() { alert("Something went wrong."); }
		       });
		
		$('#new_ratingprofile').empty();
	    });

	    // Add insert/delete dimension buttons
	    var dim_insert_button = $('<button type="button">+</button>');
	    var dim_remove_button = $('<button type="button">-</button>');

	    // Register click handlers on each of the insert/delete buttons
	    dim_insert_button.click( function() {
		handle_insert_dimension();
	    });
	    dim_insert_button.click( function() {
		handle_remove_dimension();
	    });

	    newprofile_form.append( dim_insert_button );
	    newprofile_form.append( dim_remove_button );
	    newprofile_form.append( submit_button );

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
    bind_delete_buttons();	// Delete an entire profile
    bind_insert_buttons();	// Insert a dimension
    bind_remove_buttons();	// Remove a dimension
    bind_newprofile_button();	// Make a new ratingprofile
});
