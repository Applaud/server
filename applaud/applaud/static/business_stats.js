google.load("visualization", "1", {packages:["corechart"]});

$(document).ready( function(){
    $.ajax({url: business_stats_url,
	    type:'GET',
	    data:{},
	    success:function(data) {
		console.log('success!');
		apatapa.stats.initialize(data);
		apatapa.functions.listEmployees($('#employees'), data)
	    },
	    error:function(){alert("Something went wrong.");}
	   });

    
});
