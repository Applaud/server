/**
 * This is executed after the page has fully loaded.
 */
$(document).ready(function() {
    // Bind the 'delete' buttons for employees to an AJAX call
    apatapa.employee.bind_delete_buttons();

    // Fetch the list of employees
    $.ajax({'url':list_employees_url,
	    success: function(data) {
		apatapa.employee.listEmployees(data, $('#employees_listing'));
		apatapa.employee.buildForms();
	    },
	    error:function(){alert("Something went wrong.");}});
});