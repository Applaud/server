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
