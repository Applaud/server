////////////////////////////////////////////////////////////////////////////////////////////////
// overview.js - The javascript file for the product, team, and legal overview of apatapa.com //
////////////////////////////////////////////////////////////////////////////////////////////////
if( ! apatapa.overview ){
    apatapa.overview = {};
}

( function( _ns ){
    
    var sections = ['about', 'team', 'features', 'terms', 'privacy'];

    // A function to call whenever a particular section should be displayed
    _ns.showSection = function( sectionName ){

        // Make the appropriate tab selected
        $(".content-link").removeClass("selected");
        $("#"+sectionName+"-content-link").addClass("selected");

        // Hide the other groups, show the appropriate one
        $(".content-group").hide();
        $("#"+sectionName+"-content-group").show();

    }

    // Call when the page is loaded
    $(document).ready( function () {
        // Grab the url to see if a particular tag was passed in
        var url = location.href;
        var tag = url.split("#")[1].toLowerCase();
        
        // If the tag is one of the sections, navigate to it
        if( sections.indexOf( tag ) !== -1 ){
            _ns.showSection( tag );
        }
        // Otherwise, just start the page off displaying the 'About' section
        else{
            _ns.showSection( "about" );
        }

        // Bind the Nav Bar links
        $(".content-link").click( function() {
            // Grab the name of the clicked section
            var name = $(this).attr('id').split("-")[0];
            console.log(name);
            _ns.showSection( name );
        });
    });
    
}( apatapa.overview ))



