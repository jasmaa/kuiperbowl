// Events in game

// setup and ping
window.setTimeout(setup, 600);
window.setInterval(ping, 5000);

// JQuery events
$('#name').on('input', function() {
  set_name();
});

$(document).keypress(function(e) {
  if(e.which == 110){
    next();
  }
});
