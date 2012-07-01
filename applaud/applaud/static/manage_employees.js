if (! apatapa.employee) {
    apatapa.employee = {};
}

(function (_ns) {
    var bind_delete_buttons = function () {
	$('.del_emp_button').click(
	    function ( event ) {
		event.preventDefault();
		$.ajax({ url: delete_employee_url,
			 type: 'POST',
			 data: {'employee_id':$(this).attr('id').split('_')[2],
				'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()},
			 success: function(data) {
			     _ns.listEmployees(data, $('#employees_listing'));
			 },
			 error: function() { alert("Something went wrong."); }
		       });
	    });
    }

    /**
     * you must have {% csrf_token %} on the page calling this somewhere.
     */
    _ns.getEmployees = function( container ) {
	$.ajax({url: list_employees_url,
		type: 'POST',
		data:{'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()},
		success: function(data) {
		    _ns.listEmployees(data, container);
		},
		error: function() {
		    alert("Something went wrong.");
		}
	       });
    };

    /**
     * listEmployees(data)
     *
     * data - JSON data returned by AJAX call for deleting an employee.
     * Re-builds the list of employees.
     */
    _ns.listEmployees = function(data, container) {
	// Clear the current list
	$('#employees_listing').empty();
	var listing = $('<ul></ul>');

	for ( e in data.employee_list ) {
	    employee = data.employee_list[e];
	    var listitem = $('<li></li>');
	    var employee_image = $('<img />');
	    employee_image.prop({'src':employee.image,
				 'alt':employee.first_name+" "+employee.last_name,
				 'class':'profile_image'});

	    // This is the way it's done per the EmployeeEncoder
	    listitem.append( employee_image );
	    listitem.append( '<span class="employee_name">'+employee.first_name+" "+employee.last_name+'</span>'
			     +"<form action=\"\" method=\"post\">"
			     +"<input type=\"hidden\" name=\"csrfmiddlewaretoken\" value=\""+$('input[name=csrfmiddlewaretoken]').val()+"\" />"
			     +"<input type=\"submit\" id=\"del_emp_"+employee.id+"\" class=\"del_emp_button\" value=\"Delete\" />");
	    listing.append(listitem);
	}
	
	$('#employees_listing').append(listing);
	bind_delete_buttons();
    };

    /**
     * This is executed after the page has fully loaded.
     */
    $(document).ready(function() {
	// Bind the 'delete' buttons for employees to an AJAX call
	bind_delete_buttons();

	// Fetch the list of employees
	$.ajax({'url':list_employees_url,
		success: function(data) {
			     _ns.listEmployees(data, $('#employees_listing'));
			 },
		error:function(){alert("Something went wrong.");}});
    });
})(apatapa.employee);
