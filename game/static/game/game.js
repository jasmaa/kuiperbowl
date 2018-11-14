var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
var gamesock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + window.location.pathname);

var game_state;
var current_time;
var question;
var score_dict;

window.setInterval(ping, 5000);

// Handle server response
gamesock.onmessage = function(message){

  var data = JSON.parse(message.data);
  console.log(data);

  game_state = data.game_state;
  current_time = data.current_time;
  question = data.current_question_content;
  score_dict = data.score_dict;
}

// Ping server for state
function ping(){
  var message = {
    name: $('#name').val(),
    current_time: Date.now(),
    request_type:"ping",
    content:""
  }

  console.log("ping");
  gamesock.send(JSON.stringify(message));
}

// new user
function new_user(){
  var message = {
    name: $('#name').val(),
    current_time: Date.now(),
    request_type:"new_user",
    content:""
  }

  gamesock.send(JSON.stringify(message));
}

// Buzz
function buzz(){

}

// Request next question
function next(){

}
