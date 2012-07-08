if( ! apatapa.functions ){
    apatapa.functions = {};
}

(function (_ns) {
    
    // listEmployees(data, container)
    //
    // data - JSON data returned by an AJAX call
    // container - the DOM container where the list of employees should be stored
    // callback - An optinal callback function.
    _ns.listEmployees = function(container, data) {
	// Clear the current list
	console.log(container);
	container.empty();
	console.log(data);
	var listing = $('<ul></ul>');
	for ( e in data.data.employees ) {
	    employee = data.data.employees[e];
	    var listitem = $('<li class="employee_item"></li>');
	    listitem.append( _ns.makeEmployeeDiv(employee));
	    listing.append(listitem);
	}
	
	container.append(listing);
	
	if( typeof( callback ) == typeof( Function ) )
	    callback();
    };

    /*
     * Returns a div containing employee information
     * 
     * TODO: Pass this a parameter list detailing which information the div should hold
     */
    _ns.makeEmployeeDiv = function(employee){
	console.log("in makeEmployeeDiv");
	var employee_div = $('<div></div>');
	employee_div.prop({'id':'employee_'+employee.id+'_div'});

	var employee_image = $('<img />');
	employee_image.prop({'src':employee.image,
			     'alt':employee.first_name+" "+employee.last_name,
			     'class':'profile_image'});
	var employee_id = $('<input />');
	employee_id.prop({'type':'hidden',
			  'value':employee.id});


	var employee_info_div = $('<div></div>');
	employee_info_div.prop({'class':'employee_info'});

	var employee_name = $('<span></span>');
	employee_name.prop({'class':'employee_name'});
	employee_name.text(employee.first_name+" "+employee.last_name);
	
	var employee_bio = $('<p></p>')
	employee_bio.text(employee.bio);

	employee_info_div.append(employee_name)
	    .append(employee_bio);

	employee_div.append(employee_image)
	    .append(employee_id)
	    .append(employee_info_div);
	
	return employee_div;
    }

})(apatapa.functions);