var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
var gamesock = new WebSocket(ws_scheme + '://' + window.location.host + window.location.pathname);

var player_name;
var player_id;
var locked_out;

var game_state = 'idle';
var current_action = 'idle';

var current_time;
var start_time;
var end_time;
var buzz_start_time;
var buzz_passed_time = 0;
var grace_time = 3;
var buzz_time = 8;

var question;
var category;
var curr_question_content;
var scores;
var messages;

// Set up client
function setup() {
  // set up user
  retrieve_userdata();
  if (player_id == undefined) {
    new_user();
  }
  else{
    ping();
    join();
  }

  $('#name').val(player_name);
  $('#request-content').hide();

  // set up current time if newly joined
  current_time = buzz_start_time;
}

// Update game locally
function update() {
  if (question == undefined) {
    return;
  }

  var time_passed = current_time - start_time;
  var duration = end_time - start_time;

  // Update if game is going
  var buzz_progress = $('#buzz-progress');
  buzz_progress.css('width', Math.round(100 * (1.1 * buzz_passed_time / buzz_time)) + '%');
  var content_progress = $('#content-progress');
  content_progress.css('width', Math.round(100 * (1.05 * time_passed / duration)) + '%');
  var question_body = $('#question-space');
  question_body.html(curr_question_content);

  if(game_state == 'idle'){

    locked_out = false;
    setCookie('locked_out', locked_out);

    if ($('#answer-header').html() == "") {
      get_answer();
    }

    var content_progress = $('#content-progress');
    content_progress.css('width', '0%');

    var question_space = $('#question-space');
    question_space.html(question);
  }

  else if (game_state == 'playing') {
    buzz_passed_time = 0;
    curr_question_content = question.substring(0, Math.round(question.length * (time_passed / (duration - grace_time))))
    current_time += 0.1;

    $('#content-progress').show();
    $('#buzz-progress').hide();
    $('#answer-header').html("");
  }

  else if (game_state == 'contest') {
    time_passed = buzz_start_time - start_time;
    curr_question_content = question.substring(0, Math.round(question.length * (time_passed / (duration - grace_time))))

    $('#content-progress').hide();
    $('#buzz-progress').show();

    // auto answer if over buzz time
    if (buzz_passed_time >= buzz_time) {
      answer();
    }
    buzz_passed_time += 0.1;
  }

  // transition to idle if overtime while playing
  if (game_state == 'playing' && current_time >= end_time) {
    game_state = 'idle';
    get_answer();
  }
}

// Handle server response
gamesock.onmessage = function(message) {
  console.log(message);

  var data = JSON.parse(message.data);

  if (data.response_type == "update") {
    // sync client with server
    game_state = data.game_state;
    current_time = data.current_time;
    start_time = data.start_time;
    end_time = data.end_time;
    buzz_start_time = data.buzz_start_time;
    question = data.current_question_content;
    category = data.category;
    scores = data.scores;
    messages = data.messages

    // update ui
    var scoreboard = $('#scoreboard-body');
    scoreboard.html("")
    for (i = 0; i < scores.length; i++) {
      var icon = '<i class="fas fa-circle" style="color:#aaaaaa;"></i>&nbsp'
      if(scores[i][2]){
        icon = '<i class="fas fa-circle" style="color:#00ff00;"></i>&nbsp'
      }
      scoreboard.append("<tr><td>" + icon + scores[i][0] + "</td><td>" + scores[i][1] + "</td></tr>")
    }

    var message_space = $('#message-space');
    message_space.html("")
    for (i = 0; i < messages.length; i++) {
      var tag = messages[i][0]
      var icon = '<i class="far fa-circle" style="opacity: 0;"></i>&nbsp';
      if(tag == "buzz_correct"){
        icon = '<i class="far fa-circle" style="color:#00cc00;"></i>&nbsp';
      }
      else if(tag == "buzz_wrong"){
        icon = '<i class="far fa-circle" style="color:#cc0000;"></i>&nbsp';
      }
      else if(tag == "chat"){
        icon = '<i class="far fa-comment-alt" style="color:#aaaaaa;"></i>&nbsp';
      }
      else if(tag == "leave"){
        icon = '<i class="fas fa-door-open" style="color:#99bbff;"></i>&nbsp';
      }
      else if(tag == "join"){
        icon = '<i class="fas fa-sign-in-alt" style="color:#99bbff;"></i>&nbsp';
      }

      message_space.append('<li class="list-group-item">'+icon+messages[i][1]+'</li>');
    }

    $('#category-header').html("Category: " + category);
    $('#category-select').val(data.room_category);
    $('#difficulty-select').val(data.difficulty);
  }
  else if (data.response_type == "new_user") {
    setCookie('player_id', data.player_id);
    setCookie('player_name', data.player_name);
    player_id = data.player_id;
    player_name = data.player_name;
    locked_out = false;

    // Update name
    $('#name').val(player_name);
    ping();
  }
  else if (data.response_type == "send_answer") {
    $('#answer-header').html("Answer: " + data.answer);
  }
  else if(data.response_type == "lock_out"){
    locked_out = true;
    setCookie('locked_out', locked_out);
  }
}

// Ping server for state
function ping() {
  var message = {
    player_id: player_id,
    request_type: "ping",
    content: ""
  }
  gamesock.send(JSON.stringify(message));
}

function join() {
  var message = {
    player_id: player_id,
    request_type: "join",
    content: ""
  }
  gamesock.send(JSON.stringify(message));
}

function leave() {
  var message = {
    player_id: player_id,
    request_type: "leave",
    content: ""
  }
  gamesock.send(JSON.stringify(message));
}

// Request new user
function new_user() {
  var message = {
    player_id: player_id,
    request_type: "new_user",
    content: ""
  }
  gamesock.send(JSON.stringify(message));
}

// Request change name
function set_name() {
  setCookie('player_name', $('#name').val());
  var message = {
    player_id: player_id,
    request_type: "set_name",
    content: $('#name').val()
  }
  gamesock.send(JSON.stringify(message));
}

// Buzz
function buzz() {
  if (!locked_out && game_state == 'playing') {
    current_action = 'buzz';

    $('#request-content').val('');
    $('#request-content').show();
    buzz_passed_time = 0;

    $('#next-btn').hide();
    $('#buzz-btn').hide();
    $('#chat-btn').hide();

    game_state = 'contest';
    var message = {
      player_id: player_id,
      request_type: "buzz_init",
      content: ""
    }
    gamesock.send(JSON.stringify(message));

    setTimeout(function(){
      $('#request-content').focus();
    }, 1);
  }
}

// open chat
function chat_init() {
  if (current_action != 'buzz') {
    current_action = 'chat';

    $('#request-content').val('');
    $('#request-content').show();

    $('#next-btn').hide();
    $('#buzz-btn').hide();
    $('#chat-btn').hide();

    setTimeout(function(){
      $('#request-content').focus();
    }, 1);
  }
}

function send_chat(){
  if (current_action == 'chat') {

    $('#next-btn').show();
    $('#buzz-btn').show();
    $('#chat-btn').show();
    $('#request-content').hide();
    current_action = 'idle';

    if($('#request-content').val() == ""){
      return;
    }

    var message = {
      player_id: player_id,
      request_type: "chat",
      content: $('#request-content').val()
    }
    gamesock.send(JSON.stringify(message));
  }
}

// Answer
function answer() {
  if (game_state == 'contest') {

    $('#next-btn').show();
    $('#buzz-btn').show();
    $('#chat-btn').show();
    $('#request-content').hide();
    game_state = 'playing';
    current_action = 'idle';

    var message = {
      player_id: player_id,
      request_type: "buzz_answer",
      content: $('#request-content').val()
    }
    gamesock.send(JSON.stringify(message));
  }
}

// Request next question
function next() {
  if (game_state == 'idle') {
    var question_body = $('#question-space');
    question_body.html("");

    var message = {
      player_id: player_id,
      request_type: "next",
      content: ""
    }
    gamesock.send(JSON.stringify(message));
  }
}

// Request answer
function get_answer() {
  if (game_state == 'idle') {
    var message = {
      request_type: "get_answer",
    }
    gamesock.send(JSON.stringify(message));
  }
}

// Set category
function set_category(){
  var message = {
    request_type: "set_category",
    content: $('#category-select').val()
  }
  gamesock.send(JSON.stringify(message));
}

// Set difficulty
function set_difficulty(){
  var message = {
    request_type: "set_difficulty",
    content: $('#difficulty-select').val()
  }
  gamesock.send(JSON.stringify(message));
}

// resets score
function reset_score(){
  var message = {
    player_id: player_id,
    request_type: "reset_score",
  }
  gamesock.send(JSON.stringify(message));
}