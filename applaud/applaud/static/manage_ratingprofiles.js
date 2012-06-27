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
	    var innerlistitem = $('<li>'+dimension+'</li>');
	    innerlist.append( innerlistitem );
	}
	
	listitem.append( innerlist );
	listing.append( listitem );
    }
    
    $('#profiles_listing').append(listing);
    bind_delete_buttons();
    bind_insert_buttons();
}

/**
 * This is executed after the page has fully loaded.
 */
$(document).ready(function() {
    // Bind the 'delete' buttons for ratingprofiles to an AJAX call
    bind_delete_buttons();
    bind_insert_buttons();
});
