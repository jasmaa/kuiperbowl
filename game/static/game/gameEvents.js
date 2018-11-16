// Events in game

// timed events
window.setTimeout(setup, 600);
window.setInterval(ping, 5000);
window.setInterval(update, 100);

// JQuery events
$('#name').on('input', function() {
  set_name();
});

$(document).keypress(function(e) {
  if(!$(e.target).is("input")){
    if(e.which == 110){
      next();
    }
    else if(e.which == 32){
      buzz();
    }
    else if(e.which == 122){
      answer();
    }
  }
});
