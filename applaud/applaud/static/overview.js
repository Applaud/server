$(document).ready( function () {
    $(".overview-content").hide();
    if(location.hash) {
	var name = location.hash.substring(1);
	show_overview_div(name);
    }
    $(".collapse").collapse();
});
function show_overview_div(name) {
    $(".overview-content").hide();
    $("#overview-"+name).show();
    $(".nav").children().removeClass("active");
    $("."+name).addClass("active");
};

// The hash functions trigger events even when clicked on the page iteself
$(function(){
// Bind an event to window.onhashchange that, when the hash changes, gets the
// hash and adds the class "selected" to any matching nav link.
    $(window).hashchange( function(){
	var hash = location.hash;
	
	// Set the page title based on the hash.
	document.title = 'Apatapa | ' + hash.substring(1,2).toUpperCase() + hash.substring(2);
	show_overview_div(hash.substring(1))
    })
    
    // Since the event is only triggered when the hash changes, we need to trigger
    // the event now, to handle the hash the page may have loaded with.
	$(window).hashchange();
});