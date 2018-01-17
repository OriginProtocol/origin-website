$("#mailing-list").submit(function(event) {
  $.post('/mailing-list/join', $('form').serialize(), function(data) {
      $("#signup-result").html(data);
      alertify.log(data, "default");
      fbq('track', 'Lead');
    },
    'json'
  );
  event.preventDefault();
});

$("#presale").submit(function(event) {
  event.preventDefault();
  $.post('/presale/join', $('form').serialize(), function(data) {
    if (data == "OK") {
      fbq('track', 'Lead');
      window.location = "/";
    }
    alertify.log(data, "default");
  },
  'json');
});

$("#huh").click(function() {
  alertify.log('An accredited investor must have a net worth of at least $1,000,000, excluding the value of one\'s primary residence, or have income at least $200,000 each year for the last two years (or $300,000 combined income if married.)','default',0);
});

$(function() {
  $(".dropdown-menu a").click(function() {
    $("input[name='desired_allocation_currency']").val($(this).text());
    $("#desired_allocation_currency").text($(this).text());
    $("#desired_allocation_currency").val($(this).text());
  });
});
