var geocoder;

/**
 * initialize()
 *
 * This gets called when the document is fully loaded.
 */
function initialize() {
    geocoder = new google.maps.Geocoder();
}

function searchError() {
    $('#business_results').empty();
    $('#business_results').append("<p>We could\'t find anything matching your business name and address. Please check your information.");
}

/**
 * handleResults( results, status )
 *
 * Builds the results table using jQuery. Callback to
 * Google Maps API calls this.
 * 
 * results = results of the query to Google Places
 * status = success/fail of the request
 */
function handleResults ( results, status ) {
    // Clear the current results
    $('#business_results').empty();

    if ( status == google.maps.places.PlacesServiceStatus.OK ) {
	// Clear the current results
	$('#business_results').empty();

	// Set up list of results
	var the_list = $('<ul></ul>');
	for ( a in results ) {
	    result = results[a];

	    var list_item = $('<li>'+result.name+' ('+result.vicinity+')</li>');
	    list_item.attr( {'id':'address_'+a} );
	    list_item.click(function() {
		var which_result = $(this).attr('id').split('_')[1];
		$('#id_goog_id').val( results[which_result].id );
	    });
	    the_list.append( list_item );
	}
	$('#business_results').append( the_list );

    }
    else {
	searchError();
    }
}

/**
 * codeAddress()
 *
 * Gets the address in the address field, and performs a search on it using the
 * Google Maps API. Calls handleResults when the request is complete.
 */
function codeAddress() {
    var address = $('input[name="address"]').val();
    var city = $('input[name="city"]').val();
    var state = $('input[name="state"]').val();
    var country = $('input[name="country"]').val();
    
    var to_goog = address + ' ' + ' ' + city + ' ' + state + ' ' + country;

    geocoder.geocode( { 'address': to_goog}, function(results, status) {
	    var business_results = [];
	    if (status == google.maps.GeocoderStatus.OK) {
	        var lat = results[0].geometry.location.lat();
	        var lng = results[0].geometry.location.lng();
	        var address = results[0].formatted_address;
            
	        // Set address and coordinate hidden fields here
	        $('#id_address').val( address );
	        $('#id_latitude').val( lat );
	        $('#id_longitude').val( lng );

	        var loc = new google.maps.LatLng(lat,lng);
	        var request = {
		        location: loc,
		        radius: '100',
		        name: $('#id_business_name').val()
	        };

	        var map = new google.maps.Map(document.getElementById('googlemap'),
					                      { mapTypeId: google.maps.MapTypeId.ROADMAP,
					                        center: loc,
					                        zoom: 15 });

	        var gplaces = new google.maps.places.PlacesService( map );

	        gplaces.search( request, handleResults );
	    }
        else {
	        searchError();
            console.log("Could not make request to Maps api: "+status);
	    }
    });
}

/**
 * jQuery document-on-load code.
 */
$(document).ready(function() {
    // Initialize geocoder
    initialize();

    // Add click handler
    $('#search').click(function() {
	codeAddress();
    });
});
