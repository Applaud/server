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
        $("#graph_div").show();
    }
            
    var display_employee_table = function(){
        console.log("employee table");
         $(".data_view").hide();
        $("#dateslider").hide();
	$('#table_div').show();
	$('#survey_table').hide();
        $("#employee_table").show();
    }

   var display_survey_table = function(){
       console.log("survey table");
       $(".data_view").hide();
       $("#dateslider").hide();
       $('#table_div').show();
       $('#employee_table').hide();
       $("#survey_table").show();
    }

$(document).ready( function(){

    $(".employee_link").click( function(){
            apatapa.stats.setAsEmployee();
            display_employees();
            display_employee_graph();
	$('.graph_link').show();
//	$('.graph_link').hasClass('selected') ? $('#graph_div').show() : $('#table_div').show();
	if($('.graph_link').hasClass('selected')) {
	    $('.table_link').removeClass('selected');
	}
	$(".survey_link").removeClass('selected');
	$(this).addClass("selected");
    });

    $(".survey_link").click( function(){
            console.log("survey_linked");
            apatapa.stats.setAsSurvey();
            display_survey();
            display_survey_table();
	$('.graph_link').hide();
	$('.table_link').addClass('selected');
	$(".employee_link").removeClass('selected');
	$(this).addClass("selected");
    });

    $(".graph_link").click( function(){
	if(! $(this).hasClass('selected')) {
	    $(this).addClass('selected');
	    $('.table_link').removeClass('selected');
	}
        if ( apatapa.stats.isEmployees ) {
            display_employee_graph();
	}
    });
    
    $(".table_link").click( function(){
	if(! $(this).hasClass('selected')) {
	    $(this).addClass('selected');
	    $('.graph_link').removeClass('selected');
	}
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
