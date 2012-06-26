/**
 * This is executed after the page has fully loaded.
 */
$(document).ready(function() {
    // Bind the 'delete' button for employees to an AJAX call
    $('#id_employee').each().click(function() {
	$.getJSON('/business/delete_employee',
		  {'employee_id':$(self).attr('id').val()},
		  listEmployees);
    });
});

/**
 * listEmployees(data)
 *
 * data - JSON data returned by AJAX call for deleting an employee.
 * Re-builds the list of employees.
 */
function listEmployees(data) {
    // Clear the current list
    $('#employees_listing').clear();
    var listing = $('<ul></ul>');

    for ( e in data.employee_list ) {
	employee = data.employee_list[e];
	var listitem = $('<li></li>');

	// This is the way it's done per the EmployeeEncoder
	listitem.html( employee.first_name+" "+employee.last_name
		       +"<br /><form action=\"/business/delete_employee\" method=\"get\">"
		       +"<input type=\"hidden\" value=\""+employee.id+"\" />"
		       +"<input type=\"submit\" value=\"Delete\" />"
		       +"<br />" );
	listing.append(listitem);
    }

    $('#employees_listing').append(listing);
}