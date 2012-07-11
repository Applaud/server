/* README 
 *
 * Notes: This file is for the display of any and all analytics across
 * the website. It is ONLY for display.  That is, it assumes that any
 * particular page makes an initial ajax call to the server, retrieves
 * relevant and consistently formatted data.  Then it should make a
 * single call to the function initialize, which should take the
 * retrieved data as the sole parameter.
 * 
 * Complications in the display of these charts arise when we consider
 * viewing data between employees with different RatingProfiles The
 * current implementation is to display averages across the time range
 * for all rateable dimensions (e.g. if 'Quickness' is not a relevant
 * paramter for a 'Host', it will still be displayed when viewing a
 * 'Host' and 'Waiter' together, but not when viewing only 'Waiter's)
 * This can be altered later.
 * 
 * Ideally, in the case where the chart range is limited so that there
 * are no ratings for a selected employee, that employee is removed
 * from the chart altogether.
 *
 * The AJAX call should only pull down the employees. Using this, we
 * can assemble the dimensions list
 *
 * Definitions -
 *
 *     Viewable Range: The range of days on which a particular set of
 *      employees can be viewed. Specifically, the range is identified
 *      by a start and stop date.  The start date will be the date of
 *      the earliest rating by any employee to the date of the lastest
 *      rating of any employee.
 * 
 *     Chart Range: The range of days which are actually displayed on
 *      the graph. This is subset of the viewable range.
 *
 * Important Functions -
 *
 *     initialize(data):
 *	- Takes the data from the ajax call and performs necessary
 *           setup. Should perform necessary bindings, setting global
 *           variables, etc.
 *      - After everything else, calls refresh()
 *
 *     buildDateSlider():
 * 	- Rebuilds the date slider according to the the viewable
 * 		range. The viewable range is the range from the earliest date to the
 * 		latest date in which any of the current employees have data
 *
 * TODO -
 *     Remove employee from chart depiction when there are no ratings for him/her in the chart range
 *     Optimize! This is waaaayyy tooo slow
 */

if( ! apatapa.stats ){
	apatapa.stats = {};
}

(function (_ns) {

    /********************
     * Global variables *
     ********************/
    //Lists retrieved from the ajax call
    _ns.employees;
    _ns.dimensions;

    //Lists who actually determine the composition of the chart
    _ns.cur_employees=[];
    _ns.cur_dimensions=[];

    // The first and last dates of ratings in cur_employees and cur_dimensions
    _ns.first;
    _ns.last;

    // The range between first & last
    _ns.range;

    // The first and last dates of ratings selected on the bar (JS date objects)
    _ns.range_start;
    _ns.range_stop;
    
    // Boolean variable to check if user has clicked on a specific employee or dimension yet
    // 1 - user hasn't clicked anything
    // 0 - user has clicked on something
    _ns.isFirstClick = 1;


    /*************************
     * CSS related variables *
     *************************/
    _ns.selected_background_color = "#bbbbbb";


    // This function will take the current 'selected' data and assemble the google chart for it.
    // TODO: Combine this function with the setTimeRange?
    _ns.make_chart = function() {
	// This is eventually the data fed into the chart
	var chart_list = [];
	
	// Build the axes
	var row0 = [ 'Dimension' ];
	for( d in _ns.cur_dimensions){
	    row0.push(_ns.cur_dimensions[d])
	}
	
	chart_list.push(row0);
	
	// Is this all too slow?? Brainstorm efficiencies in here
	// For each employee, calculate avg rating for each dimension
	for ( e in _ns.cur_employees ) {
	    var avgRatings = [];
	    var totalRatings = {};
	    var employee = _ns.cur_employees[e];


	    // Sum up totals for each dimension
	    for ( r in employee.ratings ) {
		if( _ns.isRatingInRange(employee.ratings[r])){
		    if (! totalRatings[employee.ratings[r].title] ){
			totalRatings[employee.ratings[r].title] = [];
		    }
		    totalRatings[employee.ratings[r].title].push( employee.ratings[r].value );
		}
	    }
	    // Compute averages
	    for ( i in _ns.cur_dimensions ) {
		var dimName = _ns.cur_dimensions[i];
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
    _ns.isRatingInRange = function(rating){
	var rating_date = _ns.dateToJS(rating.date);
	if(rating_date >= _ns.range_start && rating_date <= _ns.range_stop)
	    return true;
	return false;
    }

    _ns.dateToJS = function( date ) {
	// This assumes that we are getting dates in the format dd/mm/YYYY
	// As in those passed via the ajax call
	var components = date.split('/');
	return new Date(components[2],components[1],components[0]);
    }

    // Compare two ratings based on the date they were submitted.
    // rating1, rating2 = two ratings
    _ns.dateCompare = function( rating1, rating2 ) {
	return dateToJS(rating1.date) > dateToJS(rating2.date)? 1 : -1;
    }

    // This function should set up the table of clickable dimensions
    // Should only be called once
    _ns.buildTable = function() {
	var the_list = $('<ol></ol>');
	the_list.prop({'id':"dimension_list"});
	for (d in _ns.dimensions) {
	    var dim = _ns.dimensions[d];
	    var list_item = $('<li></li>');
	    list_item.prop({'id':'dim_'+dim,
			    'class':'dimension'});
	    list_item.text(dim);
	    list_item.hover(_ns.dimension_hover_in, _ns.dimension_hover_out);
	    list_item.click(_ns.dimension_click);
	    the_list.append(list_item);
	}

	$('#gt_dims').append(the_list);
    }

    _ns.sliderValueToDate = function(sliderValue){
	// This function will take a value from the slider (an integer from 0-n) and convert this to a date using, the 'first' global
	var milliSinceFirst =sliderValue*86400000;
	var firstAsDate = _ns.dateToJS(_ns.first);
	return new Date( firstAsDate.getTime() + milliSinceFirst );
    }

    _ns.dateToSliderValue = function(date){
	var firstAsDate = _ns.dateToJS(_ns.first);
	milliSinceFirst = date.getTime() - firstAsDate.getTime();
	return milliSinceFirst/86400000;
    }

    // This function will build a slider which will represent the range of viewable data
    // It assumes that ratings for each employee are sorted by date
    // Should only be called once, afterwards should only change slider
    _ns.buildDateSlider = function() {
	
	var slider = $('#gt_dateslider');
	slider.slider({ animate: true,
			range: true,
			min: 0,
			max: _ns.range,
			values:[0,_ns.range],
		      });
	
	_ns.range_start = _ns.sliderValueToDate(0);
	_ns.range_stop = _ns.sliderValueToDate(_ns.range);
    }

    _ns.bindDateSlider = function(){
	var slider = $('#gt_dateslider');
	// Also, it seems as if the jQuery ui value method is slightly broken.... maybe change this? Or look for alternative
	slider.bind( "slide", function(event, ui) {
	    _ns.range_start = _ns.sliderValueToDate($(this).slider("values")[0]);
	    _ns.range_stop = _ns.sliderValueToDate($(this).slider("values")[1]);
	    
	    var range_as_text= _ns.range_start.toDateString()+" - "+_ns.range_stop.toDateString();
	    $("#dateslider_label").text("Time range: "+range_as_text);
	});

	// Any time the user finishes the selection, construct the new graph
	slider.bind( "slidechange", function(event, ui){
	    //Not programatically called - from reconstructing the date slider
	    if(event.originalEvent!=undefined)
		_ns.make_chart();
	});
    }

    // Changes the range of the date slider
    // Should be called after setDateRange
    _ns.changeDateSlider = function() {
	var slider = $('#gt_dateslider');
	slider.slider("option", "max", _ns.range);
    }

    // This calculates and returns the viewable range in days
    // This also sets the global variables first & last
    //
    // TODO: Optimize this. Is there a better way to achieve the same thing?
    _ns.setDateRange = function(){
	
	for( e in _ns.cur_employees ){
	    var e_ratings =  _ns.cur_employees[e].ratings;
	    var e_ratings_length =  _ns.cur_employees[e].ratings.length;
	    var e_first;
	    var e_last;
	    for( r in e_ratings){
		if(_ns.cur_dimensions.indexOf(e_ratings[r].title)!=-1){
		    e_first = e_ratings[r].date;
		    break;
		}
	    }

	    for( var i = e_ratings_length-1; i>=0; i--){
		if(_ns.cur_dimensions.indexOf(e_ratings[i].title)!=-1){
		    e_last = e_ratings[i].date;
		    break;
		}
	    }
	    // Check if first and last have been set yet
	    if(typeof(_ns.first) === 'undefined' && typeof(_ns.last) === 'undefined'){
		_ns.first = e_first;
		_ns.last = e_last;
	    }
	    else {
		// If not, determine whether a particular employees rating is the global first (last)
		_ns.first = _ns.dateToJS(_ns.first) < _ns.dateToJS(e_first)? _ns.first : e_first;
		_ns.last = _ns.dateToJS(_ns.last) > _ns.dateToJS(e_last)? _ns.last : e_last;
	    }
	}

	var day1 = _ns.dateToJS(_ns.last);
	var day2 = _ns.dateToJS(_ns.first);
	_ns.range = day1.getTime() - day2.getTime();
	// Convert ms to days
	_ns.range /= 86400000;
    }

    _ns.dimension_hover_in = function(){
	$(this).css('background-color', _ns.selected_background_color);
    }
    _ns.dimension_hover_out = function(){
	if(!$(this).is(".dim_selected")){
	    $(this).css('background-color', '#ffffff');
	}
    }

    _ns.dimension_click = function(){
	var dim_title = $(this).text();
	
	$(this).toggleClass('dim_selected');

	// Check if it's selected
	if( $(this).hasClass('dim_selected') ){
	    _ns.add_dimension(dim_title);
	    $(this).css('background-color', _ns.selected_background_color);
	}
	else {
	    _ns.remove_dimension(dim_title);
    	    $(this).css('background-color',"#ffffff");
	}
	_ns.processNewData();
    }

    _ns.employee_click = function(){
	// TODO: Determine the structure of the html when there are multiple employees
	// From this, we should grab the id.
	var emp_id = $(this).attr('id');
	var employee;
	
	//Is there a better (faster) way to do this?
	for( i in _ns.employees ){
	    if( _ns.employees[i].id == emp_id ){
		employee = _ns.employees[i];
		break;
	    }
	}
	
	$(this).toggleClass('selected');
	
	if( $(this).is('selected') ){
	    _ns.add_employee(employee);
	    $(this).css('background-color',selected_background_color);
	}
	else {
	    _ns.remove_employee(employee);
	}
    }

    // Takes an employee JSON object of the form passed from the view
    _ns.add_employee = function(employee){
	if( _ns.isFirstClick ){
	    _ns.cur_employees=[employee];
	    _ns.isFirstClick=0;
	}
	else{
	    //First, make sure the employee isn't in the chart
	    var arr_index = _ns.cur_employees.indexOf(employee);
	    if( arr_index === -1 ) _ns.cur_employees.push(employee); 
	}
    }
    
    // Takes an employee JSON object of the form passed from the view
    _ns.remove_employee = function(employee){
	if( ! _ns.isFirstClick){
	    var arr_index = _ns.cur_employees.indexOf(emp_id);
	    if( arr_index != -1 ) _ns.cur_employees.splice(arr_index, 1); 
	}
    }

    // Takes a dimension JSON object of the form passed from the view
    _ns.add_dimension = function(dimension){
	if( _ns.isFirstClick ){
	    _ns.isFirstClick=0;
	    _ns.cur_dimensions=[dimension];
	}
	else{
	    //First, make sure the employee isn't in the chart
	    var arr_index = _ns.cur_dimensions.indexOf(dimension);
	    if( arr_index === -1 ) _ns.cur_dimensions.push(dimension); 
	}
    }

    // Takes a dimension JSON object of the form passed from the view
    _ns.remove_dimension = function(dimension){
	if( ! _ns.isFirstClick ){
	    var arr_index = _ns.cur_dimensions.indexOf(dimension);
	    if( arr_index != -1 ){
		_ns.cur_dimensions.splice(arr_index, 1); 
		if(_ns.cur_dimensions.length === 0)
		    _ns.cur_dimensions = _ns.dimensions;
	    }
	}
    }

    // Using the employees list, assembles a list of dimension titles
    _ns.buildDimensions = function(){
	_ns.dimensions = [];
	for ( e in _ns.employees ){
	    var ratings = _ns.employees[e].ratings
	    for ( r in ratings ){
		var curRating = ratings[r];
		if ( _ns.dimensions.indexOf(curRating.title) == -1 ){
		    _ns.dimensions.push(curRating.title);
		}
	    }
	}
    }

    // This should just set variables
    _ns.initialize = function(data){
	_ns.employees = data.data.employees;
	_ns.buildDimensions();
	_ns.buildTable();
	_ns.cur_dimensions = _ns.dimensions;
	_ns.cur_employees = _ns.employees;
	_ns.setDateRange();
	_ns.buildDateSlider();
	_ns.bindDateSlider();

	_ns.make_chart();
    }

    // To be called anytime cur_dimensions or cur_employees is changed
    _ns.processNewData = function(){
	_ns.setDateRange();
	_ns.changeDateSlider();

	_ns.make_chart();
    }
})(apatapa.stats);