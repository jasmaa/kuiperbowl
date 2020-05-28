// gameEvents.js
// Listeners for events during game

const nameInput = document.getElementById('name');
const requestContentInput = document.getElementById('request-content');
const buzzProgress = document.getElementById('buzz-progress');
const contentProgress = document.getElementById('content-progress');
const questionSpace = document.getElementById('question-space');
const answerHeader = document.getElementById('answer-header');
const scoreboard = document.getElementById('scoreboard-body');
const messageSpace = document.getElementById('message-space');
const categoryHeader = document.getElementById('category-header');
const categorySelect = document.getElementById('category-select');
const difficultySelect = document.getElementById('difficulty-select');
const name = document.getElementById('name');
const nextBtn = document.getElementById('next-btn');
const buzzBtn = document.getElementById('buzz-btn');
const chatBtn = document.getElementById('chat-btn');
const resetBtn = document.getElementById('reset-btn');

// Init tooltip and popover
$(document).ready(() => {
  $('[data-toggle="tooltip"]').tooltip();
  $('[data-toggle="popover"]').popover();
});

// Timed events
window.setInterval(() => {
  ping();
  getPlayers();
}, 5000);
window.setInterval(update, 100);

window.onbeforeunload = leave;

name.oninput = debounce(setName, 100);

document.onkeypress = (e) => {
  if (e.target.tagName != 'INPUT') {
    if (e.which == 110) {
      next();
    }
    else if (e.which == 32) {
      buzz();
      e.preventDefault();
    }
    else if (e.which == 99) {
      chatInit();
    }
  }
}

requestContentInput.onkeypress = (e) => {
  if (e.which == 13) {
    if (currentAction == 'buzz') {
      answer();
    }
    else if (currentAction == 'chat') {
      sendChat();
    }
  }
}

categorySelect.onchange = setCategory;
difficultySelect.onchange = setDifficulty;
buzzBtn.onclick = buzz;
nextBtn.onclick = next;
resetBtn.onclick = resetScore;
chatBtn.onclick = chatInit