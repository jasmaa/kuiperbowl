function gotoRoom(){
  var loc = $('#landing-content').val().trim();
  if(loc == ""){
    loc = 'hs';
  }
  window.location.href = "/game/"+loc;
}

$('#landing-btn').click(function(e) {
  gotoRoom();
});
$('#landing-content').keypress(function(e) {
  if(e.which == 13){
    gotoRoom();
  }
});
