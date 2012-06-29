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
			     buildForms();
			 },
			 error: function() { alert("Something went wrong."); }
		       });
	    });
    }

    /**
     * getEmployees
     *
     * NOTE: You MUST have {% csrf_token %} on the page calling this somewhere.
     * fills 'container' with the list of employees for current business.
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
     * buildForms()
     *
     * Creates forms on each employee listing.
     */
    function buildForms() {
	$('.employee_item').each( function(index, element) {
	    var id = $(this).children('.employee_id').val();
	    $(this).append("<form action=\"\" method=\"post\">"
			   +"<input type=\"hidden\" name=\"csrfmiddlewaretoken\" value=\""+$('input[name=csrfmiddlewaretoken]').val()+"\" />"
			   +"<input type=\"submit\" id=\"del_emp_"+employee.id+"\" class=\"del_emp_button\" value=\"Delete\" />");
	});

	bind_delete_buttons();
    }

    /**
     * listEmployees(data)
     *
     * data - JSON data returned by AJAX call for deleting an employee.
     * Re-builds the list of employees.
     */
    _ns.listEmployees = function(data, container) {
	// Clear the current list
	container.empty();
	var listing = $('<ul></ul>');

	for ( e in data.employee_list ) {
	    employee = data.employee_list[e];
	    var listitem = $('<li class="employee_item"></li>');
	    var employee_image = $('<img />');
	    employee_image.prop({'src':employee.image,
				 'alt':employee.first_name+" "+employee.last_name,
				 'class':'profile_image'});
	    var employee_id = $('<input />');
	    employee_id.prop({'type':'hidden',
			      'value':employee.id});
	    listitem.append( employee_image ).append(employee_id);
	    listitem.append( $('<span class="employee_name">'+employee.first_name+" "+employee.last_name+'</span>') );
	    listing.append(listitem);
	}
	
	container.append(listing);

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
		    buildForms();
		},
		error:function(){alert("Something went wrong.");}});
    });
})(apatapa.employee);
