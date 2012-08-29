
// $(document).ready( function(){
//     $("#features").hide();
//     console.log("reading the javscript file");
//     $("#video-button").click( function(){
//         $('#myModal').modal({
//             backdrop: true
//         });
//     });

//     $("#features-button").click( function () {
// 	$("#info").hide();
// 	$("#features").show();
//     });
// });

/*
 * frontPage.js - The javascript file for the frontpage of apatapa.com
 *
 *
 */

var frontPage = frontPage || {};

(function (frontPage) {
    // Dictionary associating 'name' attributes of the text input fields with their default text
    frontPage.defaultText = {'email':"Email",
                           'first':"First name",
                           'last':"Last name (optional)",
                           'password':"Password"};

    // The jQuery objects of any invalid form elements
    frontPage.errorElements = [];

    // Clears the errors from the screen and performs other necessary cleanup
    frontPage.clearErrors = function(){
        // Remove the list of errors from the div
        $('#error-div ul').empty();

        // Get rid of the other error div styling
        $('#error-div').css("padding-top","0px");
        $('#error-div').css("padding-bottom","0px");
        $('#error-div').css("margin-bottom","0px");

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
                var userType = $('.radio-control-group :checked').val();

                // 'User' radio button pressed, create the account and take them to their profile
                if( userType === "user" ){
                    // TODO: Implement
                }
                // 'Business' radio button pressed, take them to another page to complete registration
                else if( userType === "business" ){
                    // TODO: Implement
                }

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
                          $('#error-div ul').append(errorElement);
                          frontPage.errorElements.push($('#email-control-group :input'));
                          var exMarkImage = $('<img src="media/ExMark.png" alt="Ex Mark" />');
                          $('#email-status-image').append(exMarkImage);
                      }
                      return false;
                  }
                  return true;
              });
    }

    frontPage.validateUserType = function(){
        var userType = $('.radio-control-group :checked').val();

        // Check to see if user type has been selected
        if( ! userType ){
            var errorElement = $('<li></li>');
            errorElement.text("Please select 'User' or 'Business'.");
            $('#error-div ul').append(errorElement);
            frontPage.errorElements.push($('.radio-control-group'));       
        }
    }

    frontPage.validateEmail = function(){
        var email = $('input[name="email"]').val();      

        // Check for valid email
        var patt = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}$/;
        // If the pattern doesn't fit or the error has already been accounted for (i.e. it is already associated to an account)
        if( ! patt.test(email) ||  $.inArray($('#email-control-group :input'), frontPage.errorElements) === -1 ){
            $('#email-control-group').addClass("error");
            var errorElement = $('<li></li>');
            errorElement.text("Invalid email.");
            $('#error-div ul').append(errorElement);
            
            frontPage.errorElements.push($('#email-control-group :input'));
            var exMarkImage = $('<img src="media/ExMark.png" alt="Ex Mark" />');
            $('#email-status-image').append(exMarkImage);
            return false;
        }
        return true;
    }

    frontPage.validateFirstName = function(){
        var firstName = $('input[name="first"]').val();

        // Check First Name
        if( firstName === "" || firstName === frontPage.defaultText['first'] ){
            $('#first-control-group').addClass("error");
            var errorElement = $('<li></li>');
            errorElement.text("You didn't enter a name.");
            $('#error-div ul').append(errorElement);
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

            $('#error-div ul').append(errorElement);
            var exMarkImage = $('<img src="media/ExMark.png" alt="Ex Mark" />');
            $('#password-status-image').append(exMarkImage);
            frontPage.errorElements.push($('#password-control-group :input'));
            return false;
        }
        return true;
    }

    frontPage.validateForm = function(){
        var isValid = frontPage.validateUserType() &&
            frontPage.validateEmail() &&
            frontPage.validateFirstName() &&
            frontPage.validatePassword();
        
        // If there are any errors, style up the error div
        if( frontPage.errorElements.length > 0 ){
            $("#error-div").css("padding-top", "5px");
            $("#error-div").css("padding-bottom", "5px");
            $("#error-div").css("margin-bottom", "5px");            
        }        

        return isValid;
    }

    frontPage.initPage = function () {
	$(".features-text").hide();
	console.log("features");
	$("#features-button").click( function() {
	    frontPage.showFeatures();
	});
    }
	
    frontPage.showFeatures = function() {
	$(".main-text").toggle(500);
	$(".features-text").toggle(500);
    }
})(frontPage);

