function bind_delete_buttons() {
    console.log('binding to buttons');
    $('.del_emp_button').click(
	function ( event ) {
	    console.log("Handler called for clik: "+$(this).attr('id').split('_')[2]);
	    event.preventDefault();
	    $.ajax({ url: manage_employees_url,
		     type: 'POST',
		     data: {'employee_id':$(this).attr('id').split('_')[2],
			    'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()},
		     success: listEmployees,
		     error: function() { alert("Something went wrong."); }
		   });
	});
}

/**
 * listEmployees(data)
 *
 * data - JSON data returned by AJAX call for deleting an employee.
 * Re-builds the list of employees.
 */
var listEmployees = function(data) {
    console.log("listing employees now.");
    // Clear the current list
    $('#employees_listing').empty();
    var listing = $('<ul></ul>');

    for ( e in data.employee_list ) {
	employee = data.employee_list[e];
	var listitem = $('<li></li>');

	// This is the way it's done per the EmployeeEncoder
	listitem.html( employee.first_name+" "+employee.last_name
		       +"<br /><form action=\"/business/delete_employee/\" method=\"post\">"
		       +"<input type=\"hidden\" name=\"csrfmiddlewaretoken\" value=\""+$('input[name=csrfmiddlewaretoken]').val()+"\" />"
		       +"<input type=\"submit\" id=\"del_emp_"+employee.id+"\" class=\"del_emp_button\" value=\"Delete\" />"
		       +"<br />" );
	listing.append(listitem);
    }
    
    $('#employees_listing').append(listing);
    bind_delete_buttons();
}

/**
 * This is executed after the page has fully loaded.
 */
$(document).ready(function() {
    // Bind the 'delete' buttons for employees to an AJAX call
    bind_delete_buttons();
});
