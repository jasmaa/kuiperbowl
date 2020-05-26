// game.js
// Plays client-side game

const ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
const gamesock = new WebSocket(ws_scheme + '://' + window.location.host + '/ws' + window.location.pathname);

let user_name;
let user_id;
let locked_out;

let game_state = 'idle';
let current_action = 'idle';

let current_time;
let start_time;
let end_time;
let buzz_start_time;
let buzz_passed_time = 0;
let grace_time = 3;
let buzz_time = 8;

let question;
let category;
let curr_question_content;
let scores;
let messages;

// Set up client
gamesock.onopen = () => {

  requestContentInput.style.display = 'none';

  // set up user

  retrieve_userdata();

  if (user_id == undefined) {
    new_user();
  } else {
    join();
  }

  nameInput.value = user_name;

  // set up current time if newly joined
  current_time = buzz_start_time;
}

// Update game locally
function update() {
  if (question == undefined) {
    return;
  }

  let time_passed = current_time - start_time;
  let duration = end_time - start_time;

  // Update if game is going
  buzzProgress.style.width = Math.round(100 * (1.1 * buzz_passed_time / buzz_time)) + '%';
  contentProgress.style.width = Math.round(100 * (1.05 * time_passed / duration)) + '%';
  questionSpace.innerHTML = curr_question_content;

  if (game_state == 'idle') {

    locked_out = false;

    if ($('#answer-header').html() == "") {
      get_answer();
    }

    contentProgress.style.width = '0%';
    questionSpace.innerHTML = question;
  }

  else if (game_state == 'playing') {
    buzz_passed_time = 0;
    curr_question_content = question.substring(
      0,
      Math.round(question.length * (time_passed / (duration - grace_time)))
    );
    current_time += 0.1;

    contentProgress.style.display = '';
    buzzProgress.style.display = 'none';
    answerHeader.innerHTML = '';
  }

  else if (game_state == 'contest') {
    time_passed = buzz_start_time - start_time;
    curr_question_content = question.substring(
      0,
      Math.round(question.length * (time_passed / (duration - grace_time)))
    );

    contentProgress.style.display = 'none';
    buzzProgress.style.display = '';

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
gamesock.onmessage = function (message) {

  const data = JSON.parse(message.data);

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
    scoreboard.innerHTML = '';
    for (i = 0; i < scores.length; i++) {
      const icon = document.createElement('i');
      icon.classList.add('fas');
      icon.classList.add('fa-circle');
      icon.style.margin = '0.5em';
      if (scores[i][2]) {
        icon.style.color = '#00ff00';
      }
      else {
        icon.style.color = '#aaaaaa';
      }
      const row = scoreboard.insertRow(icon);
      const cell1 = row.insertCell();
      cell1.append(icon);
      cell1.append(scores[i][0]);
      const cell2 = row.insertCell();
      cell2.append(scores[i][1])
    }

    messageSpace.innerHTML = '';
    for (i = 0; i < messages.length; i++) {
      const [tag, user, content] = messages[i];
      const icon = document.createElement('i');
      let msgHTML;

      console.log(messages[i])

      icon.style.margin = '0.5em';
      switch (tag) {
        case "buzz_correct":
          icon.classList.add('far');
          icon.classList.add('fa-circle');
          icon.style.color = '#00cc00';
          break;
        case "buzz_wrong":
          icon.classList.add('far');
          icon.classList.add('fa-circle');
          icon.style.color = '#cc0000';
          break;
        case "chat":
          icon.classList.add('far');
          icon.classList.add('fa-comment-alt');
          icon.style.color = '#aaaaaa';
          break;
        case "leave":
          icon.classList.add('fas');
          icon.classList.add('fa-door-open');
          icon.style.color = '#99bbff';
          break;
        case "join":
          icon.classList.add('fas');
          icon.classList.add('fa-sign-in-alt');
          icon.style.color = '#99bbff';
          break;
        default:
          icon.classList.add('far');
          icon.classList.add('fa-circle');
          icon.style.opacity = 0;
          break;
      }

      switch (tag) {
        case "join":
          msgHTML = `<strong>${user}</strong> has joined the room`;
          break;
        case "leave":
          msgHTML = `<strong>${user}</strong> has left the room`;
          break;
        case "buzz_init":
          msgHTML = `<strong>${user}</strong> has buzzed`;
          break;
        case "buzz_correct":
          msgHTML = `<strong>${user}</strong> has correctly answered <strong>${content}</strong>`;
          break;
        case "buzz_wrong":
          msgHTML = `<strong>${user}</strong> has incorrectly answered <strong>${content}</strong>`;
          break;
        case "set_category":
          msgHTML = `<strong>${user}</strong> has changed the category to <strong>${content}</strong>`;
          break;
        case "set_difficulty":
          msgHTML = `<strong>${user}</strong> has changed the difficulty to <strong>${content}</strong>`;
          break;
        case "reset_score":
          msgHTML = `<strong>${user}</strong> has reset their score`;
          break;
        case "chat":
          msgHTML = `<strong>${user}</strong>: ${content}`;
          break;
      }

      const li = document.createElement('li');
      li.classList.add('list-group-item');
      li.style.display = 'flex';
      li.style.flexDirection = 'row';
      li.style.alignItems = 'center';
      li.append(icon);
      const msg = document.createElement('div');
      msg.innerHTML = msgHTML;
      li.append(msg);
      messageSpace.append(li);
    }

    categoryHeader.innerHTML = `Category ${category}`;
    categorySelect.value = data.room_category;
    difficultySelect.value = data.difficulty;
  }
  else if (data.response_type == "new_user") {
    setCookie('user_id', data.user_id);
    setCookie('user_name', data.user_name);
    user_id = data.user_id;
    user_name = data.user_name;
    locked_out = false;

    // Update name
    name.value = user_name;
    ping();
  }
  else if (data.response_type == "send_answer") {
    answerHeader.innerHTML = `Answer: ${data.answer}`;
  }
  else if (data.response_type == "lock_out") {
    locked_out = data.locked_out;
  }
  else if (data.response_type == "buzz_grant") {

    // Grant local client buzz
    current_action = 'buzz';

    requestContentInput.value = '';
    requestContentInput.style.display = '';
    buzz_passed_time = 0;

    nextBtn.style.display = 'none';
    buzzBtn.style.display = 'none';
    chatBtn.style.display = 'none';

    game_state = 'contest';

    setTimeout(function () {
      requestContentInput.focus();
    }, 1);
  }
}

// Ping server for state
function ping() {
  gamesock.send(JSON.stringify({
    user_id: user_id,
    request_type: "ping",
    content: ""
  }));
}

function join() {
  gamesock.send(JSON.stringify({
    user_id: user_id,
    request_type: "join",
    content: ""
  }));
}

function leave() {
  gamesock.send(JSON.stringify({
    user_id: user_id,
    request_type: "leave",
    content: ""
  }));
}

// Request new user
function new_user() {
  gamesock.send(JSON.stringify({
    user_id: user_id,
    request_type: "new_user",
    content: ""
  }));
}

// Request change name
function set_name() {
  setCookie('user_name', name.value);
  gamesock.send(JSON.stringify({
    user_id: user_id,
    request_type: "set_name",
    content: name.value,
  }));
}

// Buzz
function buzz() {
  if (!locked_out && game_state == 'playing') {
    gamesock.send(JSON.stringify({
      user_id: user_id,
      request_type: "buzz_init",
      content: ""
    }));
  }
}

// open chat
function chat_init() {
  if (current_action != 'buzz') {
    current_action = 'chat';

    requestContentInput.value = '';
    requestContentInput.style.display = '';

    nextBtn.style.display = 'none';
    buzzBtn.style.display = 'none';
    chatBtn.style.display = 'none';

    setTimeout(function () {
      requestContentInput.focus();
    }, 1);
  }
}

function send_chat() {
  if (current_action == 'chat') {

    nextBtn.style.display = '';
    buzzBtn.style.display = '';
    chatBtn.style.display = '';
    requestContentInput.style.display = 'none';
    current_action = 'idle';

    if ($('#request-content').val() == "") {
      return;
    }

    gamesock.send(JSON.stringify({
      user_id: user_id,
      request_type: "chat",
      content: requestContentInput.value,
    }));
  }
}

// Answer
function answer() {
  if (game_state == 'contest') {

    nextBtn.style.display = '';
    buzzBtn.style.display = '';
    chatBtn.style.display = '';
    requestContentInput.style.display = 'none';
    game_state = 'playing';
    current_action = 'idle';

    gamesock.send(JSON.stringify({
      user_id: user_id,
      request_type: "buzz_answer",
      content: requestContentInput.value,
    }));
  }
}

// Request next question
function next() {
  if (game_state == 'idle') {
    questionSpace.innerHTML = '';

    gamesock.send(JSON.stringify({
      user_id: user_id,
      request_type: "next",
      content: ""
    }));
  }
}

// Request answer
function get_answer() {
  if (game_state == 'idle') {
    gamesock.send(JSON.stringify({
      user_id: user_id,
      request_type: "get_answer",
    }));
  }
}

// Set category
function set_category() {
  gamesock.send(JSON.stringify({
    user_id: user_id,
    request_type: "set_category",
    content: categorySelect.value,
  }));
}

// Set difficulty
function set_difficulty() {
  gamesock.send(JSON.stringify({
    user_id: user_id,
    request_type: "set_difficulty",
    content: difficultySelect.value,
  }));
}

// resets score
function reset_score() {
  gamesock.send(JSON.stringify({
    user_id: user_id,
    request_type: "reset_score",
  }));
}