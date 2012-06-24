var geocoder;

/**
 * initialize()
 *
 * This gets called when the document is fully loaded.
 */
function initialize() {
    geocoder = new google.maps.Geocoder();
}

/**
 * buildTable()
 *
 * Builds the results table using jQuery. Callback to
 * Google Maps API calls this.
 */
function buildTable ( addresses ) {
    // Clear the current results
    $('#business_results').empty();

    var the_list = $('<ul></ul>');
    for ( a in addresses ) {
	address = addresses[a];
	var list_item = $('<li>'+address.address+'</li>');
	list_item.attr( {'id':'address_'+a} );
	list_item.click(function() {
            var which_address = $(this).attr('id').split('_')[1];
            $('#address_result').text(addresses[which_address].latitude);
	});
	the_list.append( list_item );
    }
    $('#business_results').append( the_list );
}

/**
 * codeAddress()
 *
 * Gets the address in the address field, and performs a search on it using the
 * Google Maps API. Calls buildTable when the request is complete.
 */
function codeAddress() {
    var address = $('#business_address').attr('value');

    geocoder.geocode( { 'address': address}, function(results, status) {
	var business_results = [];
	if (status == google.maps.GeocoderStatus.OK) {
            for ( r in results ) {
		result = results[r];
		business_results.push( {'address': result.formatted_address,
					'latitude': result.geometry.location.lat(),
					'longitude': result.geometry.location.lng()} );
            }
            buildTable( business_results );
	} else {
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