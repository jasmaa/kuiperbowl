
// Events in game
$(document).ready(function(){
  $('[data-toggle="tooltip"]').tooltip();
});

// timed events
window.setTimeout(setup, 600);
window.setInterval(ping, 5000);
window.setInterval(update, 100);

$(window).on("unload", function(e) {
  leave();
});

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
      e.preventDefault();
    }
    else if(e.which == 99){
      chat_init();
    }
  }
});

$('#request-content').keypress(function(e) {
  if(e.which == 13){
    if(current_action == 'buzz'){
      answer();
    }
    else if(current_action == 'chat'){
      send_chat();
    }
  }
});

$('#category-select').change(function(e) {
  set_category();
});
$('#difficulty-select').change(function(e) {
  set_difficulty();
});

$('#buzz-btn').click(function(e) {
  buzz();
});
$('#next-btn').click(function(e) {
  next();
});
$('#reset-btn').click(function(e) {
  if(confirm("Are you sure you want to reset?")){
      reset_score();
  }
});
$('#chat-btn').click(function(e) {
  chat_init();
});