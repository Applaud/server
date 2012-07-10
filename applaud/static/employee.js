/**
 * employee.js
 *
 * Contains all the javascript functionality for the employee-end of the website.
 *
 * modules:
 *
 *
 *
 */

if (! apatapa.employee) {
    apatapa.employee = {};
}

(function (employee) {

    if (! employee.stats) {
	employee.stats = {};
    }

    ////////////////////////////
    // apatapa.employee.stats //
    ////////////////////////////

    (function (_ns) {
	
	_ns.buildTable = function( data ) {

	};


    })(employee.stats);
 
    /**
     * getEmployee - Singular version of getEmployees. Request done with a GET instead
     *
     */
    employee.getEmployee = function( employee_id, container, callback ) {
	$.ajax({url: employee_list_employee_url,
		type: 'GET',
		data: {'employee':employee_id},
		success: function(data) {
		    var emp = data.employee;
		    var emp_div = employee.listEmployee(emp);

		    if ( container ){
			container.empty();
			container.append(emp_div);
		    }

		    if ( callback )
			callback();
		},
		error: function() {
		    alert("Something went wrong.");
		}
	       });
    }

    employee.listEmployee = function(emp){
	var employee_div = $('<div></div>');
	employee_div.prop({'id':'employee_'+emp.id+'_div',
			   'class':'employee_div'});

	var employee_image = $('<img />');
	employee_image.prop({'src':emp.image,
			     'alt':emp.first_name+" "+emp.last_name,
			     'class':'profile_image'});
	var employee_id = $('<input />');
	employee_id.prop({'type':'hidden',
			  'value':emp.id});
	employee_div.append( employee_image ).append(employee_id);
	employee_div.append( $('<span class="employee_name">'+emp.first_name+" "+emp.last_name+'</span>') );
	employee_div.append( $('<p>'+emp.bio+'</p>') );

	
	
	return employee_div;
    }



})(apatapa.employee);