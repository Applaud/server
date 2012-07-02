/* employees.js
 * 
 * Provides the javascript functionality for the 'manage employees'
 * page for businesses. This file also supplies the function
 * 'getEmployee( container, [callback] )', which can be used to list
 * all the employees into a container.
 *
 */

if (! apatapa.employee) {
    apatapa.employee = {};
}

(function (_ns) {
    _ns.bind_delete_buttons = function () {
	$('.del_emp_button').click(
	    function ( event ) {
		event.preventDefault();
		$.ajax({ url: delete_employee_url,
			 type: 'POST',
			 data: {'employee_id':$(this).attr('id').split('_')[2],
				'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()},
			 success: function(data) {
			     _ns.listEmployees(data, $('#employees_listing'));
			     _ns.buildForms();
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
    _ns.getEmployees = function( container, callback ) {
	$.ajax({url: list_employees_url,
		type: 'POST',
		data:{'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()},
		success: function(data) {
		    _ns.listEmployees(data, container);
		    if ( callback )
			callback();
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
    _ns.buildForms = function() {
	$('.employee_item').each( function(index, element) {
	    var id = $(this).children('.employee_id').val();
	    $(this).append("<form action=\"\" method=\"post\">"
			   +"<input type=\"hidden\" name=\"csrfmiddlewaretoken\" value=\""+$('input[name=csrfmiddlewaretoken]').val()+"\" />"
			   +"<input type=\"submit\" id=\"del_emp_"+employee.id+"\" class=\"del_emp_button\" value=\"Delete\" />");
	});

	_ns.bind_delete_buttons();
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
})(apatapa.employee);
