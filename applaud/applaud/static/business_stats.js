google.load("visualization", "1", {packages:["corechart"]});


var display_employees = function(){
    $("#survey_stats_choice_div").hide();
    $("#employee_stats_choice_div").show();
    $(".graph_link").removeAttr("disabled");
}

    var display_survey = function(){
        $("#employee_stats_choice_div").hide();
        $("#survey_stats_choice_div").show();
	$(".graph_link").attr("disabled","disabled");
    }

    var display_employee_graph = function(){
        console.log("employee graph");
        $(".data_view").hide();
        $("#dateslider").show();
        $("#employee_graph").show();
    }
            
    var display_employee_table = function(){
        console.log("employee table");
         $(".data_view").hide();
        $("#dateslider").hide();
         $("#employee_table").show();
    }

   var display_survey_table = function(){
       console.log("survey table");
         $(".data_view").hide();
       $("#dateslider").hide();
         $("#survey_table").show();
    }

$(document).ready( function(){

    $(".employee_link").click( function(){
            console.log("employee link");
            apatapa.stats.setAsEmployee();
            display_employees();
            display_employee_graph();
    });

    $(".survey_link").click( function(){
            console.log("survey_linked");
            apatapa.stats.setAsSurvey();
            display_survey();
            display_survey_table();
    });

    $(".graph_link").click( function(){
            if ( apatapa.stats.isEmployees )
                display_employee_graph();
    });
    
    $(".table_link").click( function(){
            if ( apatapa.stats.isEmployees )
                display_employee_table();
            else
                display_survey_table();

    });
    
    $.ajax({url: business_stats_url,
	    type:'GET',
	    data:{},
	    success:function(data) {
		console.log('success!');
		apatapa.stats.initialize(data);
		apatapa.functions.listEmployees($('#employees'), data);
		apatapa.functions.listQuestions($('#survey'), data);
		apatapa.functions.listUsers($("#survey_filters"), data);
		display_employees();
		display_employee_graph();
            },
	    error:function(){alert("Something went wrong.");}
	   });
    console.log("is employee is....");
    console.log(apatapa.stats.isEmployees);

    // Create accordions
    $("#employee_stats_choice_div").accordion({fillSpace: true});
    $("#survey_stats_choice_div").accordion({fillSpace: true});
});
