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
	container.empty();
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
	
	employee_info_div.append(employee_name)

	employee_div.append(employee_image)
	    .append(employee_id)
	    .append(employee_info_div);
    
	apatapa.stats.bind_employee_click(employee_div, employee);
	
	return employee_div;
    }

    // listQuestions(data, container)
    //
    // data - JSON data returned by an AJAX call
    // container - the DOM container where the list of employees should be stored
    // callback - An optinal callback function.
    _ns.listUsers = function(container, data) {
	// Clear the current list
	container.empty();
	var listing = $('<ul></ul>');
	var listed_users = [];
	for ( q in data.data.questions ) {
	    question = data.data.questions[q];

	    // debug
	    console.log("listUsers: "+question);
	    
	    for ( r in question.ratings ) {
		var response = question.ratings[r];
		var user = response.user;

		// debug
		console.log(user);

		if ( listed_users.indexOf(user.id) < 0 ) {
		    var listitem = $('<li class="user_item"></li>');
		    listitem.append(_ns.makeUserDiv(user));
		    listing.append(listitem);
		    listed_users.push(user.id);
		}
	    }
	}
	
	container.append(listing);
    }

    _ns.makeUserDiv = function(user) {
        var user_div = $("<div></div>");
        user_div.prop({'class':'user_div'});
        
        var para = $("<p></p>");
        para.text(user.first_name+" "+user.last_name);

	user_div.click(function() {
	    $(this).toggleClass('selected');
	    if ( $(this).hasClass('selected') ) {
		apatapa.stats.addUser(user);
	    } else {
		apatapa.stats.removeUser(user);
	    }
	    apatapa.stats.processNewSurveyData();
	});

        user_div.append(para);
        
        return user_div;
    }

    // listQuestions(data, container)
    //
    // data - JSON data returned by an AJAX call
    // container - the DOM container where the list of employees should be stored
    // callback - An optinal callback function.
    _ns.listQuestions = function(container, data) {
	// Clear the current list
	container.empty();
	var listing = $('<ul></ul>');
	for ( q in data.data.questions ) {
	    question = data.data.questions[q];
	    var listitem = $('<li class="question_item"></li>');
	    listitem.append( _ns.makeQuestionDiv(question));
	    listing.append(listitem);
	}
	
	container.append(listing);
    };


    _ns.makeQuestionDiv = function(question){
        var question_div = $("<div></div>");
        question_div.prop({'class':'question_div'});
        
        var para = $("<p></p>");
        para.text(question.label);

	question_div.click(function() {
	    $(this).toggleClass('selected');
	    if ( $(this).hasClass('selected') ) {
		apatapa.stats.addQuestion(question);
	    } else {
		apatapa.stats.removeQuestion(question);
	    }
	    apatapa.stats.processNewSurveyData();
	});

        question_div.append(para);
        
        return question_div;
    }




})(apatapa.functions);