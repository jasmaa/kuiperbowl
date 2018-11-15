var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
var gamesock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + window.location.pathname);

var player_name;
var player_id;

var game_state;
var current_time;
var start_time;
var end_time;
var question;
var curr_question_content;
var score_dict;

function update(){
  if(question == undefined){
    return;
  }

  var time_passed = current_time - start_time;
  var time_end = end_time - start_time;

  curr_question_content = question.substring(0, parseInt(question.length * (time_passed / time_end)))
  current_time += 0.1;

  var question_body = $('#question-space');
  question_body.html(curr_question_content);
}

// Handle server response
gamesock.onmessage = function(message){
  var data = JSON.parse(message.data);
  console.log(data);

  if(data.response_type == "update"){
    // sync client with server
    game_state = data.game_state;
    current_time = data.current_time;
    start_time = data.start_time;
    end_time = data.end_time;
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
    setCookie('player_id', data.player_id);
    setCookie('player_name', data.player_name);
    player_id = data.player_id;
    player_name = data.player_name;
  }
}

// Set up
function setup(){
  retrieve_userdata();
  if(player_id == undefined){
    new_user();
  }
  ping();

  $('#name').val(player_name);
}

// Ping server for state
function ping(){
  var message = {
    player_id: player_id,
    current_time: Date.now(),
    request_type:"ping",
    content:""
  }
  gamesock.send(JSON.stringify(message));
}

// Request new user
function new_user(){
  var message = {
    player_id: player_id,
    current_time: Date.now(),
    request_type:"new_user",
    content:$('#name').val()
  }
  gamesock.send(JSON.stringify(message));
}

// Request change name
function set_name(){
  setCookie('player_name', $('#name').val());
  var message = {
    player_id: player_id,
    current_time: Date.now(),
    request_type:"set_name",
    content:$('#name').val()
  }
  gamesock.send(JSON.stringify(message));
}

// Buzz
function buzz(){

}

// Request next question
function next(){
  var question_body = $('#question-space');
  question_body.html("");

  var message = {
    player_id: player_id,
    current_time: Date.now(),
    request_type:"next",
    content:""
  }
  gamesock.send(JSON.stringify(message));
}
