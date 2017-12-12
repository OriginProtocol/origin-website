$( "form" ).submit(function( event ) {
  $.post( "/signup?email="+encodeURIComponent($( "#email" ).val()), function( data ) {
    $( "#signup-result" ).html( data );
  },"json");
  event.preventDefault();
});
