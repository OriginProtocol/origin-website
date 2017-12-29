$("#mailing-list").submit(function(event) {
  $.post('/mailing-list/join', $('form').serialize(), function(data) {
      $("#signup-result").html(data);
      alertify.log(data, "default");
    },
    'json'
  );
  event.preventDefault();
});

$("#presale").submit(function(event) {
  $.post('/presale/join', $('form').serialize(), function(data) {
      alertify.log(data, "default");
    },
    'json'
  );
  event.preventDefault();
});

$(function() {
  $(".dropdown-menu a").click(function() {
    $("input[name='desired_allocation_currency']").val($(this).text());
    $("#desired_allocation_currency").text($(this).text());
    $("#desired_allocation_currency").val($(this).text());
  });
});