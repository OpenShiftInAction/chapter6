$(document).ready(function() {

  $.ajax({
    type: 'GET',
    url: '/gettasks',
    data: { get_param: 'value' },
    dataType: 'json',
    success: function (data) {
        $.each(data, function(index, element) {
            addTaskHTML(element.name, element.value);
        });
    }
  });

	$("#add-button").click(function() {

    task = $("#task").val().trim();
    priority = $("#priority").val();

    if (task != '') {


      jsonObj = [];
      var item = {};
      item ["task"] = task;
      item ["priority"] = priority;
      jsonObj.push(item);

      var jqxhr = $.post( "/addtask", function(JSON.stringify(jsonObj)) {

        addTaskHTML(task, priority);

      })
      .fail(function() {
        bootbox.alert( "Error saving new task to MongoDB" );
      });

		} else {
			bootbox.alert("Lazy Bum, nothing is not a task!");
		}

	});

	$(document).on('click', '#remove-button', function() {

		$(this).parent().parent().remove();

  });

});

function addTaskHTML(task, priority){

  tr = "";
  if(priority == "Low"){
    tr += "<tr class=\"info\">";
  }else if(priority == "Medium"){
    tr += "<tr class=\"active\">";
  }else if(priority == "High"){
    tr += "<tr class=\"warning\">";
  }else {
    tr += "<tr class=\"danger\">";
  }

  $("#table").append(tr+ "<td>" + $("#task").val() + "</td><td>" + $("#priority").val() + "</td><td><button type='button' id='remove-button' class='btn btn-default'>Remove</button></td></tr>");

  $('#task').val('');
  $('#priority').val('Low');

}
