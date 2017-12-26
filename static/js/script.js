$( "form" ).submit(function( event ) {
  $.post( "/signup?email="+encodeURIComponent($( "#email" ).val()), function( data ) {
    $( "#signup-result" ).html( data );
    alertify.log(data,"default");
  },"json");
  event.preventDefault();
});