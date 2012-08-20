$(document).ready( function(){
    bindForm();

});

var bindForm = function(){
    var defaultTextDict = {'email':"Email",
                           'first':"First name",
                           'last':"Last name (optional)",
                           'password':"Password"};
    var selector = $('input[type=text]');
    selector.focus( function(){
        var name = $(this).attr('name');
        var text = defaultTextDict[name];
        if($(this).val() === text ){
            $(this).val("");
        }
    });
    selector.blur( function(){
        var name = $(this).attr('name');
        var text = defaultTextDict[name];
        if($(this).val() === ""){
            $(this).val(text);
        }
    });
}

var validateForm = function(){
    // Check for valid email
    var email = $('input[name="email"]').val().toLowerCase();
    console.log(email);
    var patt = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}$/;
    if(patt.test(email)){
        $('input[name="email"]').addClass("error");
    }
    else{
        $('input[name="email"]').removeClass("error");
    }
}


