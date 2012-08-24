$(document).ready( function(){
    $("#features").hide();
    console.log("reading the javscript file");
    $("#video-button").click( function(){
        $('#myModal').modal({
            backdrop: true
        });
    });

    $("#features-button").click( function () {
	$("#info").hide();
	$("#features").show();
    });
});
