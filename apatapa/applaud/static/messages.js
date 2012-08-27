if(! apatapa.messages) {
    apatapa.messages={};
}

(function (messages) {
    messages.send_message = function(sender_id, recipient_id, subject, text) {
	$.ajax({url: send_message_url,
		type:'POST',
		dataType:'json',
		data: {'sender_id':sender_id,
		       'recipient_id':recipient_id,
		       'subject':subject,
		       'text':text,
		       'csrfmiddlewaretoken':$("input[name=csrfmiddlewaretoken]").val()},
		error: function() { alert("There was an ungodly error!"); },
		success: function() {
		    alert("Message sent!");
				    }
	       });
    }
    

})(apatapa.messages);


$(document).ready(function () {
    $.ajax({url: get_inbox_url,
	    type:'GET',
	    dataType:'json', 
	    data: {'csrfmiddlewaretoken':$("input[name=csrfmiddlewaretoken]").val()},
	    error: function() { alert("There was an ungodly error"); },
	    success: function(data) {
		for(i in data['inbox_data']['messages']) {
		    var message = data['inbox_data']['messages'][i];
		    var message_div = $("<div></div>");
		    message_div.addClass("message_div");
		    if(message['unread']){
			console.log("inside for");
			message_div.addClass("unread");
		    }

		    var date_div = $("<div>"+message['date']+"</div>");
		    var subject_div = $("<div>"+message['subject']+"</div>");
		    subject_div.addClass("subject_div");
		    var text_div = $("<div>"+message['text']+"</div>");
		    var sender_div = $("<div>"+message['sender']['first_name']+" "+message['sender']['last_name']+"</div>");
		    sender_div.prop('identifier', message['sender']['id']);
		    sender_div.addClass("sender_div");
	
		    var reply_button = $("<button>Reply</button>");
		    reply_button.addClass("reply_button");

		    message_div.append(date_div);
		    message_div.append(sender_div);
		    message_div.append(subject_div);
		    message_div.append(text_div);
		    message_div.append(reply_button);
		    message_div.show();
		    $(".inbox").append(message_div);
		}
		bindClickHandlers();

	    }

	   });


    function bindClickHandlers() {
	$(".reply_button").click( function() {
	    var compose_div = $("<div></div>");
	    compose_div.addClass("compose_div");
	    var textarea = $("<textarea></textarea>");
	    var send_button = $("<button>Send</button>");
	    send_button.addClass("send_button");
	    compose_div.append(textarea).append(send_button);
	    $(this).parent().append(compose_div);
	    compose_div.show(500);
	    bindClickHandlers();
	});

	$(".send_button").click( function () {
	    var message_text = $(this).siblings("textarea").val();
	    var message_subject = $(this).parent().parent().find(".subject_div").val();
	    var recipient_id = $(this).parent().parent().find(".sender_div").prop("identifier");
	    var sender_id = $(this).parent().parent().parent().find("#user_input").val();
	    apatapa.messages.send_message(sender_id, recipient_id, message_subject, message_text);
	    $(this).parent().hide(500);
	});
    }

});

