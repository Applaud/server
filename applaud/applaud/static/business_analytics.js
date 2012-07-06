var employee_ids = [];
var rating_dimension_ids = [];

//css related variables
var selected_background_color = "#dddddd";


$(document).ready( function(){
    console.log("Document.ready");
    apatapa.employee.getEmployees($('#employees'), bind_employee_divs);
    make_chart();
});

var make_chart = function(){

    var data = JSON.stringify({'employee_ids':employee_ids,
			       'rating_categories':rating_dimension_ids});

    $.ajax({ url: "{% url get_analytics %}",
	     type: 'POST',
	     dataType: 'json',
	     data: {'data':data,
		    'csrfmiddlewaretoken':$("input[name=csrfmiddlewaretoken]").val()},
	     success: function(data){drawVisualization(data);},
	     //success: function(data){ console.log(data); },
	     error: function(a, b, c) { alert(a+"  "+b+"   "+c); }
    });
}

var bind_employee_divs = function(){

    //When we hover over a div, it should be highlighted,
    $('.employee_item').hover(employee_div_hover_in, employee_div_hover_out );

    //When we click on a div it should remain permanently highlighted and also pass
    //the updated employee id form the graph
    $('.employee_item').click( function() {
	var e_id = $(this).children(':hidden').attr('value');
	console.log(e_id);
	$(this).toggleClass('selected');
	
	if( $(this).is('.selected') ) {
	    add_employee_to_chart(e_id);
	    $(this).css('background-color',selected_background_color);
	}
	else {
	    remove_employee_from_chart(e_id);
	    $(this).css('background-color','#ffffff');
	}

    });

}
var employee_div_hover_in = function(){
    $(this).css('background-color',selected_background_color);
}
var employee_div_hover_out = function(){
    if( !$(this).is('.selected')){
	$(this).css('background-color','#ffffff');
    }
}
var add_employee_to_chart = function(emp_id){
    //First, make sure the employee isn't in the chart
    var arr_index = employee_ids.indexOf(emp_id);
    if( arr_index === -1 ) employee_ids.push(emp_id); 

    make_chart()
}
var remove_employee_from_chart = function(emp_id){
    console.log("employee is: "+emp_id);
    var arr_index = employee_ids.indexOf(emp_id);
    if( arr_index != -1 ) employee_ids.splice(arr_index, 1); 
    
    make_chart();
}

var add_rating_dimension_to_chart = function(rating_id){
    var arr_index = rating_dimension_ids.indexOf(emp_id);
    if( arr_index === -1 ) rating_dimension_ids.push(emp_id); 
    
    make_chart();
}
var remove_rating_dimension_from_chart = function(rating_id){
    var arr_index = rating_dimension_ids.indexOf(emp_id);
    if( arr_index != -1 ) rating_dimension_ids.splice(arr_index, 1);

    make_chart();
}