if (! apatapa.newsfeed) {
    apatapa.newsfeed = {};
}

(function (_ns) {
    
    // Keeps track of which feed is which.
    var i = 0;
    
    /*
     * Creates the newsfeed in the DOM after receiving data from
     * our AJAX call.
     */
    var handleNewsfeedData = function (data) {
	var add_newsfeed_button = $('<button></button>');
	add_newsfeed_button.prop({'type': 'button',
				  'name': 'add_newsfeed_button',
				  'id': 'add_newsfeed_button',
				  'class': 'add_newsfeed_button'});
	add_newsfeed_button.html('Add New Item');
	add_newsfeed_button.click( function () {
	    addFeed(0, "", "Today", "Today", "", "");
	});
	var save_newsfeed_button = $('<button></button>');
	save_newsfeed_button.prop({'type': 'button',
				   'name': 'save_newsfeed_button',
				   'id': 'save_newsfeed_button',
				   'class': 'save_newsfeed_button'});
	save_newsfeed_button.html('Save Changes');
	$('#newsfeeds').append(save_newsfeed_button)
	    .append(add_newsfeed_button);
	for(d in data) {
	    console.log(data[d]);
	    feed = data[d];
	    addFeed(feed.id,
		    feed.title,
		    feed.date,
		    feed.date_edited,
		    feed.subtitle,
		    feed.body);
	}
	registerClickHandlers();
    };
    
    /*
     * Registers click handlers for all buttons. Called from handleNewsfeedData().
     */
    var registerClickHandlers = function () {
	$('.delete_button').click( function () {
	    var feed = $(this).parent('.feed');
	    feed.children('#should_delete').val('true');
	    feed.hide(1000);
	});
	$('#save_newsfeed_button').click( function () {
	    var newsfeeds = [];
	    $('.feed').each( function (index, element) {
		var feed_dict = {'title': $(this).children('#title').val(),
				 'id': $(this).children('#feed_' + index + '_id').val(),
				 'should_delete': $(this).children('#should_delete').val(),
				 'subtitle': $(this).children('#subtitle').val(),
				 'body': $(this).children('#body').val()};
		newsfeeds.push(feed_dict);
	    });
	    $.ajax({url: manage_newsfeed_url,
		    type: 'POST',
		    dataType: 'json',
		    data: {'feeds': JSON.stringify(newsfeeds),
			   'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()},
		    error: function () { alert('Something went wrong.'); },
		    success: function () {
			alert('Great success!');
			window.location.replace('/business/');
		    }});
	});
    };
    
    /*
     * Adds a single newsfeed item to the DOM. Called from handleNewsfeedData().
     */
    var addFeed = function (id, title, date, date_edited, subtitle, body) {
	
	var should_delete = $('<input />');
	should_delete.prop({'type': 'hidden',
			    'value': 'false',
			    'name': 'should_delete',
			    'id': 'should_delete'});
	
	var feed_id = $('<input />');
	feed_id.prop({'type': 'hidden',
		      'value': id,
		      'class': 'id',
		      'id': 'feed_' + i + '_id',
		      'name': 'feed_' + i + '_id'});
	
	var feed_div = $('<div></div>');
	feed_div.prop({'class': 'feed',
		       'id': 'feed_' + i,
		       'name': 'feed_' + i});
	
	var title_text = $('<input />');
	title_text.prop({'value': title,
			 'type': 'text',
			 'id': 'title',
			 'name': 'title'});
	
	var date_text = $('<p></p>');
	date_text.html(date + ' (last edited ' + date_edited + ')');

	var subtitle_text = $('<input />');
	subtitle_text.prop({'type': 'text',
			    'name': 'subtitle',
			    'id': 'subtitle',
			    'value': subtitle});
	
	var body_text = $('<textarea></textarea>');
	body_text.prop({'value': body,
			'name': 'body',
			'id': 'body'});
	
	var delete_button = $('<button></button>');
	delete_button.prop({'type': 'button',
			    'class': 'nf_delete_button',
			    'id': 'feed_' + i + '_delete_button',
			    'name': 'feed_' + i + '_delete_button'})
	delete_button.html('Delete');
	
	$('#save_newsfeed_button').before(feed_div.append('Title: ')
					  .append(feed_id)
					  .append(should_delete)
					  .append(title_text)
					  .append(date_text)
					  .append('Subtitle: ')
					  .append(subtitle_text)
					  .append('<br />')
					  .append('Body: ')
					  .append(body_text)
					  .append('<br />')
					  .append(delete_button));
	i++;
    }
    
    $(document).ready( function () {
	$.ajax({url: list_newsfeed_url,
		type: 'GET',
		data: {'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()},
		error: function () { alert('Something went wrong.'); },
		success: handleNewsfeedData});
    });
})(apatapa.newsfeed);
