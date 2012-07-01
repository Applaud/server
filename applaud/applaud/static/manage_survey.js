if ( !apatapa.survey ) {
    apatapa.survey = {};
}

(function ( _ns ) {
    var questionTypes = {"CG":"checkbox group",
			 "RG":"radio group",
			 "TA":"textarea",
			 "TF":"textfield"};
    
    // To indicate that a question is inactive right now.
    var inactive_color = 'rgb(200, 200, 200)';
    
    var question_div_bg_color = 'rgb(255, 235, 250)';

    var registerClickHandlers = function () {
	
	// Set up buttons and click handlers.
	$(".question_div").each( function(index, ele){
	    console.log($(this).children(".question_option").length + 'asdfasdf');
	    questionOptions[index]=$(this).children(".question_option").length;
	});
	
	$('.deletebutton').click( function () {
	    console.log('deleting');
	    var parent = $(this).parent('.question');
	    apatapa.showAlert('Are you sure you want to delete?',
			      'This will this question\'s data forever!',
			      function () {
				  parent.children('.should_delete').val('true');
				  parent.hide(1000);
			      });
	});
	
	$('.toggleactivebutton').click( function () {
	    if($(this).parent('.question').children('.is_active').val() === 'true') {
		$(this).parent('.question').children('.is_active').val('false');
		$(this).parent('.question').children('.toggleactivebutton').html('Activate Question');
		$(this).parent('.question').animate({backgroundColor: inactive_color}, 500);
		console.log('made inactive');
	    }
	    else {
		$(this).parent('.question').children('.is_active').val('true');
		$(this).parent('.question').children('.toggleactivebutton').html('Deactivate Question');
		$(this).parent('.question').animate({backgroundColor: question_div_bg_color}, 500);
		console.log('made active');
	    }
	});
	


    }

    /*
     * Creates the survey in the DOM from our first AJAX call.
     */
    renderSurvey = function( data ) {
	var survey = data.survey;
	console.log("Title = "+survey['title']);
	$('#survey_title').val( survey.title );
	$('#survey_description').val( survey['description'] );
	
	$("#addquestion_button").click(function(event) {
	    event.preventDefault();
	    // A new question -- ID is 0.
	    addQuestion('', 'CG', [], true, 0, true);
	    registerClickHandlers();
	});
	
	
	
	
	for ( q in survey.questions ) {
	    var question = survey.questions[q];
	    
	    addQuestion( question.label,
			 question.type,
			 question.options,
			 question.active,
			 question.id,
			 false);
	}
	registerClickHandlers();
	$('#submit_button').click( function(event) {
	    event.preventDefault();
	    var title = apatapa.util.escapeHTML( $('#survey_title').val() );
	    var description = apatapa.util.escapeHTML( $('#survey_description').val() )
	    if( title === "" || description === "") {
		apatapa.showAlert("You're missing something!",
				  'You should fix that.',
				  function () {/* Doesn't really need to do much. */ });
		return;
	    }
	    console.log('returns are for noobs');
	    var questions = [];
	    // Get each question out of the DOM and put its info into a dictionary.
	    // This is nasty! But we need some form of non-local exit, so a try/catch
	    // block will have to do for now.
	    try {
		$('.question').each( function(index, element) {
		    var question_id = $(this).children('.question_id').val();
		    var question_label = apatapa.util.escapeHTML( $(this).children('#question_'+index).val() );
		    var shouldDelete = $(this).children('.should_delete').val();
		    var question_active = $(this).children('.is_active').val();
		    var question_options = [];
		    $(this).children('.question_option').find('.option_field').each( function(ind, ele) {
			question_options.push(apatapa.util.escapeHTML( $(this).val()) );
		    });
		    var question_type = $(this).children('.questionTypeMenu').children(':selected').val();
		    // If it's a check or radio, and we don't have options.
		    if((question_type === "CG" || question_type === "RG") &&
		       question_options.length === 0 &&
		       shouldDelete === 'false') {
			// Complain about it, and don't let the user create the survey.
			alert('Question ' + question_label + ' has question type ' + question_type +' but no options!');
			throw "no options";
		    }
		    var question_dict = {'question_id': question_id,
					 'question_label': question_label,
					 'question_active': question_active,
					 'question_options': question_options,
					 'should_delete': shouldDelete,
					 'question_type': question_type};
		    questions.push(question_dict);
		});
	    }
	    catch( err ) {
		if(err === "no options") {
		    console.log('caught the exception');
		    return;
		}
	    }
	    // Send it all off.
	    $.ajax({url: manage_survey_url,
		    data: {'survey_id': $('#survey_id').val(),
			   'survey_title': title,
			   'survey_description': description,
			   'questions': JSON.stringify(questions),
			   'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()
			  },
		    type: 'POST',
		    error: function() { alert('Something went wrong.'); },
		    success: function () { alert('Great success!');
					   window.location.replace('/business/');
					 }
		   });
	});
    }

    // Keeps track of # of questions
    var i = 0;

    // Start off with question 0 has 1 option
    var questionOptions = [0];

    $(document).ready(function() {
	// Pull down the survey
	$.ajax( {
	    url: manage_survey_url,
	    success: renderSurvey,
	    data: {'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()},
	    type: 'POST',
	    error: function() { alert("Something went wrong."); }
	});

    });



    function addQuestion( label, type, options, active, id, animated ) {
	//Objects to instantiate:
	//1.Question label
	//2.Question type
	//3.Option field (e.g. first entry of a radio button)
	//4.Add option button
	console.log('Adding question: ' + label + ' animated: ' + animated);
	var questionDiv = $("<div></div>");
	questionDiv.prop({'id':"question_"+i+"_div",
			  'class':"question"});
	if( animated ) {
	    questionDiv.hide();
	}
	
	$("#submit_button").before(questionDiv);
	$('#submit_button').button();
	$('#addquestion_button').button();
	
	// If ID is 0, it's a new question.
	var questionId = $('<input />');
	questionId.prop({'type': 'hidden',
			 'class': 'question_id',
			 'value': id});
	
	var shouldDelete = $('<input />');
	shouldDelete.prop({'type': 'hidden',
			   'class': 'should_delete',
			   'value': 'false'});
	
	var questionAreaLabel = $("<label>Question #"+(i+1)+"</label>");
	questionAreaLabel.prop({"for":"question_"+i});
	
	var questionArea = $("<textarea></textarea>");
	questionArea.prop({'name':"question_"+i,
			   'id':"question_"+i});
	questionArea.text( label );
	var questionTypeLabel = $("<label>Question type </label>");
	questionTypeLabel.prop({"for":"question_"+i+"_type"});
	
	var questionType = $("<select></select>");
	questionType.prop({'name':"question_"+i+"_type",
			   'id':"question_"+i+"_type",
			   'class': 'questionTypeMenu'});
	questionType.change( function() {
	    if( $(this).children(':selected').val() === 'TA' ||
		$(this).children(':selected').val() === 'TF') {
		console.log('changing question type');
		$(this).siblings('.question_option').hide(1000);
		$(this).siblings('.option_button').hide(1000);
	    }
	    else {
		$(this).siblings('.question_option').show(1000);
		$(this).siblings('.option_button').show(1000);
	    }
	});
	// Render question types, selecting the appropriate one by default
	for ( o in questionTypes ) {
	    var optionWidget = $('<option value="'+o+'">'+questionTypes[o]+'</option>');
	    if ( type === o ) {
		optionWidget.prop({'selected':'selected'});
	    }
	    questionType.append( optionWidget );
	}
	
	// Create a new question bucket for storing # of options
	questionOptions.push(0);
	
	var optionDiv = $("<div></div>");
	optionDiv.prop({'id':"question_"+i+"_options",
			'class':"question_option",
		       });
	var optionList = $("<ul></ul>");
	optionList.addClass("question_optionlist");

	// Render each of the options for the question
	for ( o in options ) {
	    var optionLabel = $('<label>Option '+ (parseInt(o) + 1) +'</label>');
	    optionLabel.prop({'for':'question_'+i+'_option_'+o});
	    var optionWidget = $('<input />');
	    optionWidget.prop({'type':'text',
			       'name':'question_'+i+'_option_'+o,
			       'class':'option_field',
			       'value':options[o]});
	    
	    var optionItem = $('<li></li>');
	    optionItem.addClass('question_item');

	    optionItem.append( optionLabel ).append( optionWidget );
	    optionList.append( optionItem );
	    questionOptions[i]++;
	}

	optionDiv.append( optionList );

	var questionNumber = i;
	var addOptionButton = $("<button>Add Option</button>");
	addOptionButton.prop({'type':"button",
    			      'name':"question_"+i+"_optionbutton",
     			      'id':"question_"+i+"_optionbutton",
			      'class': 'option_button'});
	addOptionButton.button();
	console.log("question number: "+questionNumber);
	addOptionButton.click(function() {
    	    console.log("i is: "+i);
            addOption(questionNumber, true);
	});
	
	// Add a delete button.
	var deleteButton = $("<button>Delete Question</button>");
	deleteButton.prop({'type': 'button',
			   'name': 'question_'+i+'_deletebutton',
			   'id': 'question_'+i+'_deletebutton',
			   'class': 'deletebutton'});
	deleteButton.button();
	
	var toggleActiveButton = $('<button></button>');
	toggleActiveButton.prop({'type': 'button',
				 'name': 'question_'+i+'_toggleactivebutton',
				 'id': 'question_'+i+'_toggleactivebutton',
				 'class': 'toggleactivebutton'});
	toggleActiveButton.button();
	
	var isActive = $('<input />');
	isActive.prop({'type': 'hidden',
		       'class': 'is_active'
		      });
	if(active) {
	    toggleActiveButton.html('Deactivate Question');
	    console.log('setting to true');
	    isActive.prop({'value': 'true'});
	    console.log(isActive.val());
	}
	else {
	    toggleActiveButton.html('Activate Question');
	    isActive.prop({'value': 'false'});
	    questionDiv.css('background-color', inactive_color);
	}
	
	questionDiv
	    .append(questionId)
	    .append(shouldDelete)
	    .append(questionAreaLabel)
	    .append(questionArea)
	    .append(isActive)
	    .append(questionTypeLabel)
	    .append(questionType)
	    .append($("<br />"))
	    .append(optionDiv)
	    .append($("<br />"))
	    .append(addOptionButton)
	    .append($("<br />"))
	    .append(deleteButton)
	    .append(toggleActiveButton);
	console.log(i);
	
	if( animated ) {
	    questionDiv.show(700);
	}
	
	// Hide the add option if we're a textfield or textarea.
	if(type === 'TA' || type === 'TF') {
	    addOptionButton.hide();
	}
	i++;
    }


    function addOption(qindex, animated) {
	var questionOptionsDiv = $("#question_"+qindex+"_options");
	var optionList = questionOptionsDiv.children('.question_optionlist');

	var optionFieldLabel = $("<label>Option "+(questionOptions[qindex]+1)+"</label>");
	optionFieldLabel.prop({"for":"question_"+qindex+"_option_"+questionOptions[qindex]});

	var optionField = $("<input />");
	optionField.prop( {'type':'text',
			   'class':'option_field',
			   'name':'question_'+qindex+'_option_'+questionOptions[qindex],
			   'id':'question_'+qindex+'_option_'+questionOptions[qindex]} );
	console.log("qindex is :"+qindex);
	questionOptions[qindex]++;

	var optionItem = $('<li></li>');
	optionItem.addClass('question_item');
	
	if( animated ) {
	    optionItem.hide();
	}

	optionItem
	    .append(optionFieldLabel)
	    .append(optionField);

	optionList.append( optionItem );
	questionOptionsDiv.append( optionList );
	if( animated ) {
	    optionItem.show(500);
	}
    }
})(apatapa.survey);
