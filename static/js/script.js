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

function presaleFormSubmit(event) {
  $.post('/presale/join', $('form').serialize(), function(data) {
    if (data == "OK") {
      fbq('track', 'Lead');
      window.location = "/";
    }
    alertify.log(data, "default");
  },
  'json')
}

function partnerFormSubmit(event) {
  $.post('/partners/interest', $('form').serialize(), function(data) {

    if (data == "OK") {
      fbq('track', 'Lead');
      window.location = "/";
    }
    alertify.log(data, "default");
  },
  'json');
}


$(function() {
  $(".dropdown-menu a").click(function() {
    $("input[name='desired_allocation_currency']").val($(this).text());
    $("#desired_allocation_currency").text($(this).text());
    $("#desired_allocation_currency").val($(this).text());
  });
});

$(function(){
  // toggle button icons
  $('.navbar-toggler').on('click', function (e) {
    var target = $(this);
    var other = $('.navbar-toggler').not(this);
    var icon = target.find('i');
    var iconClass = 'fa-' + icon.data('icon');

    // attr value is a string, not bool
    if (target.attr('aria-expanded') === 'false') {
      icon.addClass('fa-times').removeClass(iconClass);
    } else {
      icon.addClass(iconClass).removeClass('fa-times');
    }

    icon = other.find('i');
    iconClass = 'fa-' + icon.data('icon');

    if (icon.hasClass('fa-times')) {
      icon.addClass(iconClass).removeClass('fa-times');
    }
  });

  // prevent simulataneous navbar menus
  $('.navbar-origin .navbar-collapse').on('show.bs.collapse', function(e) {
    // ensure that menu is not hidden
    $(this).removeClass('obscured');
    // hide immediately to disguise 'hide' transition
    $('.navbar-origin .navbar-collapse').not(this).addClass('obscured');
    // will trigger transition
    $('.navbar-origin .navbar-collapse').not(this).collapse('hide');
  });

  // ensure that hidden menus can be shown
  $('.navbar-origin .navbar-collapse').on('hidden.bs.collapse', function(e) {
    $('.navbar-origin .navbar-collapse').not('.show').removeClass('obscured');
  });
});
