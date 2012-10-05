/********
 * apatapa.js
 *
 * Global utilities to the apatapa site.
 * Definition of global namespace for apatapa.
 * */

/* The apatapa namespace */
var apatapa;
if ( null == apatapa ) {
    apatapa = {};
}

/**
 * UTIL
 */
if ( ! apatapa.util ) {
    apatapa.util = {};
}
apatapa.util.escapeHTML = function( str ) {
    var temp = $('<pre></pre>');
    temp.text(str);
    var escaped = temp.html();
    return escaped;
}

// This file contains functions for standard apatapa form processing

if( ! apatapa.forms ){
    apatapa.forms = {};
}
apatapa.forms.handleDefaultText = function(defaultTextArr){
    var selector = $('input[type=text]');

    // Remove default text when field gains focus if it has a defualt text associated with it
    selector.focus( function(){
        if( $.inArray( $(this).attr('name'), defaultTextArr )){
            var name = $(this).attr('name');
            var text = frontPage.defaultText[name];
            if($(this).val() === text ){
                $(this).val("");
            }
        }
    });
    

    // Insert default text when field loses focus if it has a default text associated with it
    selector.blur( function(){
        if( $.inArray( $(this).attr('name'), defaultTextArr )){
            var name = $(this).attr('name');
            var text = frontPage.defaultText[name];
            if($(this).val() === ""){
                $(this).val(text);
            }
        }
    });
    
    return true;
}

/*
 * Shows an alert with an OK and cancel button, kinda like on iOS. The OK button
 * runs the ok_func function.
 */
apatapa.showAlert = function (title, message, ok_func) {
    var alert = $('<div></div>');
    alert.prop({'title': title});
    alert.html('<p>' + message + '<p>');
    alert.dialog({buttons: [
	{text: "OK",
	 click: function () { if( ok_func ) ok_func();
			      alert.dialog('close'); }},
	{text: "Cancel",
	 click: function () { alert.dialog('close'); }},
    ]});
};
