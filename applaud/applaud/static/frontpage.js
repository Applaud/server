//////////////////////////////////////////////////////////////////////////
// frontpage.js - The javascript file for the front page of apatapa.com //
//////////////////////////////////////////////////////////////////////////

var frontPage = frontPage || {};

(function (frontPage) {
    // Dictionary associating 'name' attributes of the text input fields with their default text
    frontPage.defaultText = {'email':"Email",
                           'first':"First name",
                           'last':"Last name (optional)",
                           'password':"Password"};

    // The jQuery objects of any invalid form elements
    frontPage.errorElements = [];

    // The timer for switching the feature
    frontPage.featureTimer;
    
    // The time between automagically switching between pictures (in milliseconds)
    frontPage.featureTimerLength = 1000000;//4000;

    // The counter determining the current feature
    frontPage.featureCounter = 0;
    
    // Clears the errors from the screen and performs other necessary cleanup
    frontPage.clearErrors = function(){
        // Remove the list of errors from the div
        $('#form-error ul').empty();

        // Get rid of the other error div styling
        $('#form-error').css("padding-top","0px");
        $('#form-error').css("padding-bottom","0px");
        $('#form-error').css("margin-bottom","0px");

        // Remove the status images
        $('#email-status-image').empty();
        $('#first-status-image').empty();
        $('#password-status-image').empty();

        // Remove the list of errors from the errorElements array
        frontPage.errorElements = [];

        // Remove the error class (and borders) from each of the invalid fields
        $('#email-control-group').removeClass('error');
        $('#first-control-group').removeClass('error');
        $('#password-control-group').removeClass('error');

        // TODO: Give focus to the field of the first occuring error
    }

    frontPage.bindClearErrorHandlers = function(){
        // Reset the errors when...

        // Window loses focus
        $(window).blur( function(event){
            frontPage.clearErrors();
        });
        
        // Any of the invalid fields are edited
        $(':input[type=text]').keydown( function(event){
            if( $.inArray( $(this), frontPage.errorElements ) ){
                frontPage.clearErrors();
            }
        });

        // Any other times?

    }
    
    // Binds form events to their callbacks
    frontPage.bindForm = function(){

        // Handle the default text when text fields go in and out of focus
        apatapa.forms.handleDefaultText(frontPage.defaultText);

        // When email goes out of focus, immediately check it on the server
        $("input[name='email']").blur(function(){
            frontPage.checkIfEmailUsed();
        });
        
        // When the register button is pressed, validate the data in the form and proceed with registration if all good
        $('#register-button').click( function(event){
            event.preventDefault();
            frontPage.clearErrors();

            // Form is valid, proceed with registration
            if(frontPage.validateForm()){
                console.log("Form is valid!!!!");


            }
        });
    }

    
    // Makes a get request to the server to check if an account with a particular email address already exists
    frontPage.checkIfEmailUsed = function(){
        var email = $('input[name="email"]').val();
        // Check to see if email is already being used
        $.get('mobile/check_email/',
              {email:email},
              function(d){
                  var data = JSON.parse(d);

                  // The email already exists
                  if( data['does_exist'] ){
                      // If email is not already in the error array, add it
                      if( $.inArray($('#email-control-group :input'), frontPage.errorElements) < 0 ){
                          var errorElement = $('<li></li>');
                          errorElement.text("An account with that email address already exists.");
                          $('#form-error ul').append(errorElement);
                          frontPage.errorElements.push($('#email-control-group :input'));
                          var exMarkImage = $('<img src="media/ExMark.png" alt="Ex Mark" />');
                          $('#email-status-image').append(exMarkImage);
                      }
                      return false;
                  }
                  return true;
              });
    }
    
    // Currently unused -- should be implemented down the line
    frontPage.validateUserType = function(){
        var userType = $('.radio-control-group :checked').val();

        // Check to see if user type has been selected
        if( ! userType ){
            var errorElement = $('<li></li>');
            errorElement.text("Please select 'User' or 'Business'.");
            $('#form-error ul').append(errorElement);
            frontPage.errorElements.push($('.radio-control-group'));       
        }
    }

    frontPage.validateEmail = function(){
        var email = $('input[name="email"]').val();      

        // Check for valid email
        var patt = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}$/;
        // If the pattern doesn't fit or the error has already been accounted for (i.e. it is already associated to an account)
        if( ! patt.test(email) ||  $.inArray($('#email-control-group :input'), frontPage.errorElements) !== -1 ){
            $('#email-control-group').addClass("error");
            var errorElement = $('<li></li>');
            errorElement.text("Invalid email.");
            $('#form-error ul').append(errorElement);
            
            frontPage.errorElements.push($('#email-control-group :input'));
            var exMarkImage = $('<img src="media/ExMark.png" alt="Ex Mark" />');
            $('#email-status-image').append(exMarkImage);
            return false;
        }
        return true;
    }
    
    // This function is currently not used
    frontPage.validateFirstName = function(){
        var firstName = $('input[name="first"]').val();

        // Check First Name
        if( firstName === "" || firstName === frontPage.defaultText['first'] ){
            $('#first-control-group').addClass("error");
            var errorElement = $('<li></li>');
            errorElement.text("You didn't enter a name.");
            $('#form-error ul').append(errorElement);
            var exMarkImage = $('<img src="media/ExMark.png" alt="Ex Mark" />');
            $("#first-status-image").append(exMarkImage);
            frontPage.errorElements.push($('#first-control-group :input'));
            return false;
        }
        return true;
    }

    frontPage.validatePassword = function(){
        var password = $('input[name="password"]').val();

        // Check for valid password
        patt = /^\w{8,30}$/;
        if( ! patt.test(password) || password === frontPage.defaultText['password']){
            $('#password-control-group').addClass("error");
            var errorElement = $('<li></li>');
            
            // If password is too short
            if(password.length < 8){
                errorElement.text("Password is too short (it has to be at least 8 characters).");
            }

            // If password wasn't changed
            if( password === frontPage.defaultText['password']){
                errorElement.text("You didn't enter a password");
            }

            // Other password checks??

            $('#form-error ul').append(errorElement);
            var exMarkImage = $('<img src="media/ExMark.png" alt="Ex Mark" />');
            $('#password-status-image').append(exMarkImage);
            frontPage.errorElements.push($('#password-control-group :input'));
            return false;
        }
        return true;
    }

    frontPage.validateForm = function(){
        var isValid = frontPage.validateEmail() &&
            frontPage.validatePassword(); //&&
            //frontPage.validateFirstName() &&    
            //frontPage.validateUserType();
        
        // If there are any errors, style up the error div
        if( frontPage.errorElements.length > 0 ){
            $("#form-error").css("padding-top", "5px");
            $("#form-error").css("padding-bottom", "5px");
            $("#form-error").css("margin-bottom", "5px");            
        }        

        return isValid;
    }

    
    frontPage.initPage = function () {
        // Hide all of the features but the first
	    $(".feature").hide();
	    $("#feature-0").show();

        // Assign the picture timer
        frontPage.featureTimer = window.setTimeout( "frontPage.shiftRight()", frontPage.featureTimerLength);

        // Bind the carousel buttons
	    $("#carousel-right").click( function() {
	        frontPage.shiftRight();
	    });

	    $("#carousel-left").click( function() {
            frontPage.shiftLeft();
	    });
    }
    frontPage.shiftRight = function() {
        // Stop and restart the timer whenever we shift
        clearTimeout( frontPage.featureTimer );
        frontPage.featureTimer = window.setTimeout( "frontPage.shiftRight()", frontPage.featureTimerLength );
        
        $(".feature").hide();

	    frontPage.featureCounter += 1;
        if(frontPage.featureCounter === 6){
            frontPage.featureCounter = 0;
        }
        
	    $("#feature-"+frontPage.featureCounter).fadeIn("slow");
    }
    
    frontPage.shiftLeft = function() {
        // Stop and reset the timer whenever we shift
        clearTimeout( frontPage.featureTimer );
        frontPage.featureTimer = window.setTimeout( "frontPage.shiftRight()", frontPage.featureTimerLength );

        $(".feature-image").hide();

        // Calculate the new index
	    frontPage.featureCounter -= 1;
	    if(frontPage.featureCounter === -1){
            frontPage.featureCounter = 5;
        }

	    $("#feature-image-"+frontPage.featureCounter).fadeIn("slow");
    }
})(frontPage);

