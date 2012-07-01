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