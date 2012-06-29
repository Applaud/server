var questionTypes = {"CG":"checkbox group",
		     "RG":"radio group",
		     "TA":"textarea",
		     "TF":"textfield"};


function registerClickHandlers() {
        
    // Set up buttons and click handlers.
    $(".question_div").each( function(index, ele){
	console.log($(this).children(".question_option").length + 'asdfasdf');
	questionOptions[index]=$(this).children(".question_option").length;
    });
    
    $(".question_div").click(function() {
	var qnum = $(this).prop('id').split('_')[1];
	console.log(qnum);
	addOption(qnum);
	
    });
    
    $('.deletebutton').click( function () {
	console.log('deleting');
	$(this).parent('.question').children('.should_delete').val('true');
	$(this).parent('.question').hide(1000);
    });
    
    $('.toggleactivebutton').click( function () {
	if($(this).parent('.question').children('.is_active').val() === 'true') {
	    $(this).parent('.question').children('.is_active').val('false');
	    $(this).parent('.question').children('.toggleactivebutton').html('Activate Question');
	}
	else {
	    $(this).parent('.question').children('.is_active').val('true');
	    $(this).parent('.question').children('.toggleactivebutton').html('Deactivate Question');
	}
    });
    
    $("#addquestion_button").click(function(event) {
	event.preventDefault();
	// A new question -- ID is 0.
	addQuestion('', 'CG', [], true, 0);
    });
    
    $('#submit_button').click( function(event) {
	event.preventDefault();
	var questions = [];
	// Get each question out of the DOM and put its info into a dictionary.
	// This is nasty! But we need some form of non-local exit, so a try/catch
	// block will have to do for now.
	try {
	    $('.question').each( function(index, element) {
		var question_id = $(this).children('.question_id').val();
		var question_label = $(this).children('#question_'+index).val();
		var shouldDelete = $(this).children('.should_delete').val();
		var question_active = $(this).children('.is_active').val();
		var question_options = [];
		$(this).children('.question_option').children('.option_field').each( function(ind, ele) {
		    question_options.push($(this).val());
		});
		var question_type = $(this).children('.questionTypeMenu').children(':selected').val();
		// If it's a check or radio, and we don't have options.
		if((question_type === "CG" || question_type === "RG") &&
		   question_options.length === 0) {
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
		console.log(question_dict);
		questions.push(question_dict);
	    });
	}
	catch( err ) {
	    if(err === "no options") {
		console.log('caught the exception');
		return;
	    }
	}
	console.log(questions);
	// Send it all off.
	$.ajax({url: manage_survey_url,
		data: {'survey_id': $('#survey_id').val(),
		       'survey_title': $('#survey_title').val(),
		       'survey_description': $('#survey_description').val(),
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

/*
 * Creates the survey in the DOM from our first AJAX call.
 */
function renderSurvey( data ) {
    var survey = data.survey;
    console.log("Title = "+survey['title']);
    $('#survey_title').val( survey.title );
    $('#survey_description').val( survey['description'] );
    
    for ( q in survey.questions ) {
	var question = survey.questions[q];
	
	addQuestion( question.label,
		     question.type,
		     question.options,
		     question.active,
		     question.id );
    }
    registerClickHandlers();
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



function addQuestion( label, type, options, active, id ) {
    //Objects to instantiate:
    //1.Question label
    //2.Question type
    //3.Option field (e.g. first entry of a radio button)
    //4.Add option button

    var questionDiv = $("<div></div>");
    questionDiv.prop({'id':"question_"+i+"_div"});
    questionDiv.prop({'class':"question"});
    $("#submit_button").before(questionDiv);
    
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
    
    // Render each of the options for the question
    for ( o in options ) {
	var optionLabel = $('<label>Option '+ (parseInt(o) + 1) +'</label>');
	optionLabel.prop({'for':'question_'+i+'_option_'+o});
	var optionWidget = $('<input />');
	optionWidget.prop({'type':'text',
			   'name':'question_'+i+'_option_'+o,
			   'class':'option_field',
			   'value':options[o]});
	
	optionDiv.append( optionLabel ).append( optionWidget ).append($( "<br />" ));
	questionOptions[i]++;
    }
    
    var questionNumber = i;
    var addOptionButton = $("<button>Add Option</button>");
    addOptionButton.prop({'type':"button",
    			  'name':"question_"+i+"_optionbutton",
     			  'id':"question_"+i+"_optionbutton",
			  'class': 'option_button'});
    console.log("question number: "+questionNumber);
    addOptionButton.click(function() {
    	console.log("i is: "+i);
        $("#question_"+questionNumber+"_options").append(addOption(questionNumber));
    });
    
    // Add a delete button.
    var deleteButton = $("<button>Delete Question</button>");
    deleteButton.prop({'type': 'button',
		       'name': 'question_'+i+'_deletebutton',
		       'id': 'question_'+i+'_deletebutton',
		       'class': 'deletebutton'});
    
    var toggleActiveButton = $('<button></button>');
    toggleActiveButton.prop({'type': 'button',
			     'name': 'question_'+i+'_toggleactivebutton',
			     'id': 'question_'+i+'_toggleactivebutton',
			     'class': 'toggleactivebutton'});
    
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
    }
    
    questionDiv
	.append(questionId)
	.append(shouldDelete)
	.append(questionArea)
	.append(isActive)
	.append($( "<br />" ))
	.append(questionAreaLabel)
	.append($("<br />"))
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
    
    // Hide the add option if we're a textfield or textarea.
    if(type === 'TA' || type === 'TF') {
	addOptionButton.hide();
    }
    i++;
}


function addOption(qindex) {
    var questionOptionsDiv = $("#question_"+qindex+"_options");
    
    var optionFieldLabel = $("<label>Option "+(questionOptions[qindex]+1)+"</label>");
    optionFieldLabel.prop({"for":"question_"+qindex+"_option_"+questionOptions[qindex]});

    var optionField = $("<input />");
    optionField.prop( {'type':'text',
		       'class':'option_field',
		       'name':'question_'+qindex+'_option_'+questionOptions[qindex],
		       'id':'question_'+qindex+'_option_'+questionOptions[qindex]} );
    console.log("qindex is :"+qindex);
    questionOptions[qindex]++;
    questionOptionsDiv
	.append(optionFieldLabel)
	.append(optionField);
}