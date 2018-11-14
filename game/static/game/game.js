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

  if(data.response_type == "update"){
    // sync client with server
    game_state = data.game_state;
    current_time = data.current_time;
    question = data.current_question_content;
    scores = data.scores;

    // update scoreboard
    var scoreboard = $('#scoreboard-body');
    scoreboard.html("")
    for(i=0; i<scores.length; i++){
      scoreboard.append("<tr><td>"+scores[i][0]+"</td><td>"+scores[i][1]+"</td></tr>")
    }

  }
  else if(data.response_type == "new_user"){
    // assign id
  }
}

// Ping server for state
function ping(){
  var message = {
    name: $('#name').val(),
    current_time: Date.now(),
    request_type:"ping",
    content:""
  }

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
