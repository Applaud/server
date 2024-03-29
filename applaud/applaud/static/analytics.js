/* README 
 *
 * Notes:
 * This file is for the display of any and all analytics across the website. It is ONLY for display.
 * That is, it assumes that any particular page makes an initial ajax call to the server, retrieves relevant and consistently formatted data.
 * This ajax function should make a single call to the function initialize, which should take the retrieved data as the sole parameter.
 * 
 * Complications in the display of these charts arise when we consider viewing data between employees with different RatingProfiles
 * The current implementation is to display averages across the time range for all rateable dimensions (e.g. if 'Quickness' is not a
 * relevant paramter for a 'Host', it will still be displayed when viewing a 'Host' and 'Waiter' together, but not when viewing only 'Waiter's)
 * This can be altered later.
 * 
 * Ideally, in the case where the chart range is limited so that there are no ratings for a selected employee, that employee is removed from the chart altogether.
 *
 * The AJAX call should only pull down the employees. Using this, we can assemble the dimensions list
 *
 * Definitions -
 *
 *     Viewable Range: The range of days on which a particular set of employees can be viewed. Specifically, the range is identified by a start and stop date.
 *      The start date will be the date of the earliest rating by any employee to the date of the lastest rating of any employee.
 * 
 *     Chart Range: The range of days which are actually displayed on the graph.
 *
 * Important Functions -
 *
 *     initialize(data):
 *         - Takes the data from the ajax call and performs necessary setup. Should perform necessary bindings, setting global variables, etc.
 *         - After everything else, calls refresh()
 *
 *     buildDateSlider():
e *         - Rebuilds the date slider according to the the viewable range. The viewable range is the range from the earliest date to the latest date in which any of the current employees have data
 *
 * TODO -
 *     Remove employee from chart depiction when there are no ratings for him/her in the chart range
 *     Optimize! This is waaaayyy tooo slow
 */


/********************
 * Global variables *
 ********************/
//Lists retrieved from the ajax call
var employees;
var dimensions;

//Lists who actually determine the composition of the chart
var cur_employees=[];
var cur_dimensions=[];

// The first and last dates of ratings in cur_employees and cur_dimensions
var first;
var last;

// The range between first & last
var range;

// The first and last dates of ratings selected on the bar (JS date objects)
var range_start;
var range_stop;

// Boolean variable to check if user has clicked on a specific employee or dimension yet
// 1 - user hasn't clicked anything
// 0 - user has clicked on something
var isFirstClick = 1;


/*************************
 * CSS related variables *
 *************************/
var selected_background_color = "#bbbbbb";


// This function will take the current 'selected' data and assemble the google chart for it.
// TODO: Combine this function with the setTimeRange?
function make_chart() {
    // This is eventually the data fed into the chart
    var chart_list = [];

    // Build the axes
    var row0 = [ 'Dimension' ];
    for( d in cur_dimensions){
	row0.push(cur_dimensions[d])
    }
    
    chart_list.push(row0);
    
    // Is this all too slow?? Brainstorm efficiencies in here
    // For each employee, calculate avg rating for each dimension
    for ( e in cur_employees ) {
	var avgRatings = [];
	var totalRatings = {};
	var employee = cur_employees[e];


	// Sum up totals for each dimension
	for ( r in employee.ratings ) {
	    if( isRatingInRange(employee.ratings[r])){
		if (! totalRatings[employee.ratings[r].title] ){
		    totalRatings[employee.ratings[r].title] = [];
		}
		totalRatings[employee.ratings[r].title].push( employee.ratings[r].value );
	    }
	}
	// Compute averages
	for ( i in cur_dimensions ) {
	    var dimName = cur_dimensions[i];
	    avgRatings[i] = 0;
	    if ( dimName in totalRatings && totalRatings[dimName].length > 0 ) {
		var total = 0;
		for( r in totalRatings[dimName]) {
		    total += totalRatings[dimName][r];
		}
		avgRatings[i] = total / totalRatings[dimName].length;
	    }
	}

	var nextRow = [employee.first_name+' '+employee.last_name];
	nextRow = nextRow.concat(avgRatings);
	chart_list.push(nextRow);
    }
    // Create and populate the data table.
    var data = google.visualization.arrayToDataTable( chart_list );
    
    // Create and draw the visualization.
    new google.visualization.ColumnChart(document.getElementById('emp_graph')).
	draw(data,
             {title:"Evaluations by Dimension",
              width:"700", height:"500",
              hAxis: {title: "Dimension"},
              vAxis: {title: "Average Rating",
		      viewWindowMode:'explicit',
		      viewWindow:{
		          max:6.0,
		          min:0}
		     }
	     });
}

// This function should take a rating object (of type retrieved with the JSON call)
// and return whether or not it falls in the range of the dateslider
function isRatingInRange(rating){
    var rating_date = dateToJS(rating.date);
    if(rating_date >= range_start && rating_date <= range_stop)
	return true;
    return false;
}

function dateToJS( date ) {
    // This assumes that we are getting dates in the format dd/mm/YYYY
    // As in those passed via the ajax call
    var components = date.split('/');
    return new Date(components[2],components[1],components[0]);
}

// Compare two ratings based on the date they were submitted.
// rating1, rating2 = two ratings
function dateCompare( rating1, rating2 ) {
    return dateToJS(rating1.date) > dateToJS(rating2.date)? 1 : -1;
}

// This function should set up the table of clickable dimensions
// Should only be called once
function buildTable() {
    console.log("table built");
    var the_list = $('<ol></ol>');
    the_list.prop({'id':"dimension_list"});
    for (d in dimensions) {
	var dim = dimensions[d];
	var list_item = $('<li></li>');
        list_item.prop({'id':'dim_'+dim,
	                'class':'dimension'});
	list_item.text(dim);
	list_item.hover(dimension_hover_in, dimension_hover_out);
	list_item.click(dimension_click);
	the_list.append(list_item);
    }

    $('#gt_dims').append(the_list);
}

function sliderValueToDate(sliderValue){
    // This function will take a value from the slider (an integer from 0-n) and convert this to a date using, the 'first' global
    var milliSinceFirst =sliderValue*86400000;
    var firstAsDate = dateToJS(first);
    return new Date( firstAsDate.getTime() + milliSinceFirst );
}

function dateToSliderValue(date){
    var firstAsDate = dateToJS(first);
    milliSinceFirst = date.getTime() - firstAsDate.getTime();
    return milliSinceFirst/86400000;
}

// This function will build a slider which will represent the range of viewable data
// It assumes that ratings for each employee are sorted by date
var buildDateSlider = function() {
   
    var slider = $('#gt_dateslider');
    slider.slider({ animate: true,
	            range: true,
		    min: 0,
		    max: range,
		    values:[0,range],
		  });

    range_start = sliderValueToDate(0);
    range_stop = sliderValueToDate(range);
}

var bindDateSlider = function(){
    var slider = $('#gt_dateslider');
    // Also, it seems as if the jQuery ui value method is slightly broken.... maybe change this? Or look for alternative
    slider.bind( "slide", function(event, ui) {
	range_start = sliderValueToDate($(this).slider("values")[0]);
	range_stop = sliderValueToDate($(this).slider("values")[1]);
	
	var range_as_text= range_start.toDateString()+" - "+range_stop.toDateString();
	$("#dateslider_label").text("Time range: "+range_as_text);
    });

    // Any time the user finishes the selection, construct the new graph
    slider.bind( "slidechange", function(event, ui){
	//Not programatically called - from reconstructing the date slider
	if(event.originalEvent!=undefined)
	    make_chart();
    });
}

// Changes the range of the date slider
// Should be called after setDateRange
var changeDateSlider = function() {
    var slider = $('#gt_dateslider');
    slider.slider("option", "max", range);
}

// This calculates and returns the viewable range in days
// This also sets the global variables first & last
//
// TODO: Optimize this. Is there a better way to achieve the same thing?
var setDateRange = function(){
    
    for( e in cur_employees ){
	var e_ratings = cur_employees[e].ratings;
	var e_ratings_length =  cur_employees[e].ratings.length;
	var e_first;
	var e_last;
	for( r in e_ratings){
	    if(cur_dimensions.indexOf(e_ratings[r].title)!=-1){
		e_first = e_ratings[r].date;
		break;
	    }
	}

	for( var i = e_ratings_length-1; i>=0; i--){
	    if(cur_dimensions.indexOf(e_ratings[i].title)!=-1){
		e_last = e_ratings[i].date;
		break;
	    }
	}
	// Check if first and last have been set yet
	if(typeof(first) === 'undefined' && typeof(last) === 'undefined'){
	    first = e_first;
	    last = e_last;
	}
	else {
	    // If not, determine whether a particular employees rating is the global first (last)
	    first = dateToJS(first) < dateToJS(e_first)? first : e_first;
	    last = dateToJS(last) > dateToJS(e_last)? last : e_last;
	}
    }

    var day1 = dateToJS(last);
    var day2 = dateToJS(first);
    range = day1.getTime() - day2.getTime();
    // Convert ms to days
    range /= 86400000;
}

var dimension_hover_in = function(){
    $(this).css('background-color', selected_background_color);
}
var dimension_hover_out = function(){
    if(!$(this).is(".dim_selected")){
	$(this).css('background-color', '#ffffff');
    }
}

var dimension_click = function(){
    var dim_title = $(this).text();
    
    $(this).toggleClass('dim_selected');

    // Check if it's selected
    if( $(this).hasClass('dim_selected') ){
	add_dimension(dim_title);
	$(this).css('background-color',selected_background_color);
    }
    else {
	remove_dimension(dim_title);
    	$(this).css('background-color',"#ffffff");
    }
    processNewData();
}

var employee_click = function(){
    // TODO: Determine the structure of the html when there are multiple employees
    // From this, we should grab the id.
    var emp_id = $(this).attr('id');
    var employee;
    
    //Is there a better (faster) way to do this?
    for( i in employees ){
	if( employees[i].id == emp_id ){
	    employee = employees[i];
	    break;
	}
    }

    $(this).toggleClass('selected');
    
    if( $(this).is('selected') ){
	add_employee(employee);
	$(this).css('background-color',selected_background_color);
    }
    else {
	remove_employee(employee);
    }
}

// Takes an employee JSON object of the form passed from the view
var add_employee = function(employee){
    if( isFirstClick ){
	cur_employees=[employee];
	isFirstClick=0;
    }
    else{
	//First, make sure the employee isn't in the chart
	var arr_index = cur_employees.indexOf(employee);
	if( arr_index === -1 ) cur_employees.push(employee); 
    }
}

// Takes an employee JSON object of the form passed from the view
var remove_employee = function(employee){
    if( ! isFirstClick){
	var arr_index = cur_employees.indexOf(emp_id);
	if( arr_index != -1 ) cur_employees.splice(arr_index, 1); 
    }
}

// Takes a dimension JSON object of the form passed from the view
var add_dimension = function(dimension){
    if( isFirstClick ){
	isFirstClick=0;
	cur_dimensions=[dimension];
    }
    else{
	//First, make sure the employee isn't in the chart
	var arr_index = cur_dimensions.indexOf(dimension);
	if( arr_index === -1 ) cur_dimensions.push(dimension); 
    }
}

// Takes a dimension JSON object of the form passed from the view
var remove_dimension = function(dimension){
    if( ! isFirstClick ){
	var arr_index = cur_dimensions.indexOf(dimension);
	if( arr_index != -1 ){
	    cur_dimensions.splice(arr_index, 1); 
	    if(cur_dimensions.length === 0)
		cur_dimensions = dimensions;
	}
    }
}

// Using the employees list, assembles a list of dimension titles
var buildDimensions = function(){
    dimensions = [];
    for ( e in employees ){
	var ratings = employees[e].ratings
	for ( r in ratings ){
	    var curRating = ratings[r];
	    if ( dimensions.indexOf(curRating.title) == -1 ){
		dimensions.push(curRating.title);
	    }
	}
    }
}

// This should just set variables
var initialize = function(data){
    employees = data.data.employees;
    buildDimensions();
    buildTable();
    cur_dimensions = dimensions;
    cur_employees = employees;
    setDateRange();
    buildDateSlider();
    bindDateSlider();

    make_chart();
}

// To be called anytime cur_dimensions or cur_employees is changed
var processNewData = function(){
    setDateRange();
    changeDateSlider();

    make_chart();
}
