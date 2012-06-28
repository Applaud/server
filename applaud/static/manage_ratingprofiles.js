function bind_delete_buttons() {
    console.log('binding to buttons');
    $('.del_rp_button').click(
	function ( event ) {
	    console.log("Handler called for clik: "+$(this).attr('id').split('_')[2]);
	    event.preventDefault();
	    $.ajax({ url: manage_ratingprofiles_url,
		     typee: 'POST',
		     data: {'profile_id':$(this).attr('id').split('_')[3],
			    'remove':'True',
			    'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()},
		     success: listProfiles,
		     error: function() { alert("Something went wrong."); }
		   });
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
	var listform = $("<form action=\"\" method=\"post\">"
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
}

/**
 * This is executed after the page has fully loaded.
 */
$(document).ready(function() {
    // Bind the 'delete' buttons for ratingprofiles to an AJAX call
    bind_delete_buttons();
});
