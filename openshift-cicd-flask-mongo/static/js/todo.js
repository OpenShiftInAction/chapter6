$(document).ready(function() {

  $.ajax({
    type: 'GET',
    url: '/gettasks',
    dataType: 'json',
    success: function (response) {
        console.log(JSON.stringify(response));
        $.each(response, function(index, element) {
            jsonelement = JSON.parse(element);
            addTaskHTML(jsonelement.task, jsonelement.priority);
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
      jsonStr = JSON.stringify(jsonObj);

      $.ajax({
          type: 'POST',
          url: '/addtask',
          data: jsonStr,
          success: function(data) { addTaskHTML(task, priority); },
          error: function(XMLHttpRequest, textStatus, errorThrown) {  bootbox.alert( "Error saving new task to MongoDB" ); },
          contentType: "application/json",
          dataType: 'json'
      });

		} else {
			bootbox.alert("Lazy Bum, nothing is not a task!");
		}

	});

	$(document).on('click', '#remove-button', function() {

		$(this).parent().parent().remove();

  });

});

function addTaskHTML(guid, task, priority){

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

  $("#table").append(tr+ "<td>" + task + "</td><td>" + $("#priority").val() + "</td><td><button data-json-doc-guid="+guid+" type='button' id='remove-button' class='btn btn-default'>Remove</button></td></tr>");

  $('#task').val('');
  $('#priority').val('Low');

}
