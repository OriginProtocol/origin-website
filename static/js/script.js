$( "form" ).submit(function( event ) {
  $.post( "/signup?email="+$( "#email" ).val(), function( data ) {
    $( "#signup-result" ).html( data );
  },"json");
  event.preventDefault();
});