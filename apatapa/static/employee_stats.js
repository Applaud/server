google.load("visualization", "1", {packages:["corechart"]});

$(document).ready( function() {

    $.ajax({url:employee_stats_url,
	    type:'GET',
	    data:{},
	    success:function(data) {
		apatapa.stats.initialize(data);
		apatapa.functions.listEmployees($('#employee'),data);
	    },
	    error:function(){alert("Something went wrong.");}});
      $(".hidden").hide();
      $(".visible").click( function () {
      $(this).siblings(".hidden").show();
});

      $(".table_view").hide();
      $("#graph").click( function () {
      $(".graph_view").show();
      $(".table_view").hide();
});
      $("#table").click( function () {
      $(".table_view").show();
      $(".graph_view").hide();
});
});
