// game.js
// Plays client-side game

const wsScheme = window.location.protocol == "https:" ? "wss" : "ws";
const gamesock = new WebSocket(wsScheme + '://' + window.location.host + '/ws' + window.location.pathname);

let username;
let userID;
let lockedOut;

let gameState = 'idle';
let currentAction = 'idle';

let currentTime;
let startTime;
let endTime;
let buzzStartTime;
let buzzPassedTime = 0;
let graceTime = 3;
let buzzTime = 8;

let question;
let category;
let currQuestionContent;
let players;
let messages;

// Set up client
gamesock.onopen = () => {

  requestContentInput.style.display = 'none';

  // set up user

  retrieveUserdata();

  if (userID === undefined) {
    newUser();
  } else {
    join();
  }

  nameInput.value = username;

  // set up current time if newly joined
  currentTime = buzzStartTime;
}

/**
 * Update game locally
 */
function update() {

  if (question === undefined) {
    return;
  }

  let timePassed = currentTime - startTime;
  let duration = endTime - startTime;

  // Update if game is going
  buzzProgress.style.width = Math.round(100 * (1.1 * buzzPassedTime / buzzTime)) + '%';
  contentProgress.style.width = Math.round(100 * (1.05 * timePassed / duration)) + '%';
  questionSpace.innerHTML = currQuestionContent;

  switch (gameState) {

    case 'idle':
      lockedOut = false;

      if (answerHeader.innerHTML === '') {
        getAnswer();
      }

      contentProgress.style.width = '0%';
      questionSpace.innerHTML = question;
      break;

    case 'playing':
      buzzPassedTime = 0;
      currQuestionContent = question.substring(
        0,
        Math.round(question.length * (timePassed / (duration - graceTime)))
      );
      currentTime += 0.1;

      contentProgress.style.display = '';
      buzzProgress.style.display = 'none';
      answerHeader.innerHTML = '';
      break;

    case 'contest':
      timePassed = buzzStartTime - startTime;
      currQuestionContent = question.substring(
        0,
        Math.round(question.length * (timePassed / (duration - graceTime)))
      );

      contentProgress.style.display = 'none';
      buzzProgress.style.display = '';

      // auto answer if over buzz time
      if (buzzPassedTime >= buzzTime) {
        answer();
      }
      buzzPassedTime += 0.1;
      break;
  }

  // transition to idle if overtime while playing
  if (gameState === 'playing' && currentTime >= endTime) {
    gameState = 'idle';
    getAnswer();
  }
}

// Handle server response
gamesock.onmessage = message => {

  const data = JSON.parse(message.data);

  if (data['response_type'] === "update") {

    // sync client with server
    gameState = data['game_state'];
    currentTime = data['current_time'];
    startTime = data['start_time'];
    endTime = data['end_time'];
    buzzStartTime = data['buzz_start_time'];
    question = data['current_question_content'];
    category = data['category'];
    messages = data['messages'];
    players = data['players'];

    // Update scoreboard
    // TODO: Make it so we don't have to redo popover??
    $('[data-toggle="popover"]').popover('hide')
    scoreboard.innerHTML = '';
    for (i = 0; i < players.length; i++) {
      const icon = document.createElement('i');
      icon.classList.add('fas');
      icon.classList.add('fa-circle');
      icon.style.margin = '0.5em';
      icon.style.color = players[i]['active'] ? '#00ff00' : '#aaaaaa';

      // Find last seen
      const lastSeenDiff = Date.now() / 1000 - new Date(players[i]['last_seen']);
      let lastSeenMessage = ''
      if (lastSeenDiff < 1) {
        lastSeenMessage = 'Now';
      } else if (lastSeenDiff < 60) {
        lastSeenMessage = `${Math.round(lastSeenDiff)} seconds ago`;
      } else if (lastSeenDiff < 3600) {
        lastSeenMessage = `${Math.round(lastSeenDiff / 60)} minutes ago`;
      } else if (lastSeenDiff < 86400) {
        lastSeenMessage = `${Math.round(lastSeenDiff / 3600)} hours ago`;
      } else {
        lastSeenMessage = 'Over a day ago';
      }

      const row = scoreboard.insertRow(icon);

      const cell1 = row.insertCell();
      cell1.append(icon);
      cell1.append(players[i]['user_name']);
      cell1.style = 'word-break: break-all;'

      cell1.style.outline = 'none';
      cell1.setAttribute('tabindex', 1)
      cell1.setAttribute('data-toggle', 'popover');
      cell1.setAttribute('data-trigger', 'hover');
      cell1.setAttribute('title', players[i]['user_name']);
      cell1.setAttribute('data-content', `
        <table class="table">
          <tbody>
          <tr>
            <td>Correct</td>
            <td>${players[i]['correct']}</td>
          </tr>
          <tr>
            <td>Negs</td>
            <td>${players[i]['negs']}</td>
          </tr>
          <tr>
            <td>Last Seen</td>
            <td>${lastSeenMessage}</td>
          </tr>
        </tbody>
        </table>
      `);
      $(cell1).popover({ html: true });

      const cell2 = row.insertCell();
      cell2.append(players[i]['score']);
    }

    // Update messages
    messageSpace.innerHTML = '';
    for (i = 0; i < messages.length; i++) {

      const [tag, user, content] = messages[i];

      const icon = document.createElement('i');
      let msgHTML;

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
        case "buzz_forfeit":
          msgHTML = `<strong>${user}</strong> has forfeit the question`;
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
    categorySelect.value = data['room_category'];
    difficultySelect.value = data['difficulty'];

  } else if (data['response_type'] === "new_user") {

    setCookie('user_id', data['user_id']);
    setCookie('user_name', data['user_name']);
    userID = data['user_id'];
    username = data['user_name'];
    lockedOut = false;

    // Update name
    name.value = username;
    ping();

  } else if (data['response_type'] === "send_answer") {

    answerHeader.innerHTML = `Answer: ${data['answer']}`;

  } else if (data['response_type'] === "lock_out") {

    lockedOut = data['locked_out'];

  } else if (data['response_type'] === "buzz_grant") {

    // Grant local client buzz
    currentAction = 'buzz';

    requestContentInput.value = '';
    requestContentInput.style.display = '';
    buzzPassedTime = 0;

    nextBtn.style.display = 'none';
    buzzBtn.style.display = 'none';
    chatBtn.style.display = 'none';

    gameState = 'contest';

    setTimeout(() => {
      requestContentInput.focus();
    }, 1);

  }
}

/**
 * Ping server for state
 */
function ping() {
  gamesock.send(JSON.stringify({
    user_id: userID,
    request_type: "ping",
    content: ""
  }));
}

/**
 * Join room
 */
function join() {
  gamesock.send(JSON.stringify({
    user_id: userID,
    request_type: "join",
    content: ""
  }));
}

/**
 * Leave room
 */
function leave() {
  gamesock.send(JSON.stringify({
    user_id: userID,
    request_type: "leave",
    content: ""
  }));
}

/**
 * Request new user
 */
function newUser() {
  gamesock.send(JSON.stringify({
    user_id: userID,
    request_type: "new_user",
    content: ""
  }));
}

/**
 * Request change name
 */
function setName() {
  setCookie('user_name', name.value);
  gamesock.send(JSON.stringify({
    user_id: userID,
    request_type: "set_name",
    content: name.value,
  }));
}

/**
 * Init buzz
 */
function buzz() {
  if (!lockedOut && gameState === 'playing') {
    gamesock.send(JSON.stringify({
      user_id: userID,
      request_type: "buzz_init",
      content: ""
    }));
  }
}

/**
 * Answer question during buzz
 */
function answer() {
  if (gameState === 'contest') {

    nextBtn.style.display = '';
    buzzBtn.style.display = '';
    chatBtn.style.display = '';
    requestContentInput.style.display = 'none';
    gameState = 'playing';
    currentAction = 'idle';

    gamesock.send(JSON.stringify({
      user_id: userID,
      request_type: "buzz_answer",
      content: requestContentInput.value,
    }));
  }
}

/**
 * Open chat
 */
function chatInit() {
  if (currentAction !== 'buzz') {
    currentAction = 'chat';

    requestContentInput.value = '';
    requestContentInput.style.display = '';

    nextBtn.style.display = 'none';
    buzzBtn.style.display = 'none';
    chatBtn.style.display = 'none';

    setTimeout(() => {
      requestContentInput.focus();
    }, 1);
  }
}

/**
 * Send chat message
 */
function sendChat() {
  if (currentAction === 'chat') {

    nextBtn.style.display = '';
    buzzBtn.style.display = '';
    chatBtn.style.display = '';
    requestContentInput.style.display = 'none';
    currentAction = 'idle';

    if (requestContentInput.value === "") {
      return;
    }

    gamesock.send(JSON.stringify({
      user_id: userID,
      request_type: "chat",
      content: requestContentInput.value,
    }));
  }
}

/**
 * Request next question
 */
function next() {
  if (gameState == 'idle') {
    questionSpace.innerHTML = '';

    gamesock.send(JSON.stringify({
      user_id: userID,
      request_type: "next",
      content: ""
    }));
  }
}

/**
 * Request answer
 */
function getAnswer() {
  if (gameState === 'idle') {
    gamesock.send(JSON.stringify({
      user_id: userID,
      request_type: "get_answer",
    }));
  }
}

/**
 * Set category
 */
function setCategory() {
  gamesock.send(JSON.stringify({
    user_id: userID,
    request_type: "set_category",
    content: categorySelect.value,
  }));
}

/**
 * Set difficulty
 */
function setDifficulty() {
  gamesock.send(JSON.stringify({
    user_id: userID,
    request_type: "set_difficulty",
    content: difficultySelect.value,
  }));
}

/**
 * Reset score
 */
function resetScore() {
  gamesock.send(JSON.stringify({
    user_id: userID,
    request_type: "reset_score",
  }));
}