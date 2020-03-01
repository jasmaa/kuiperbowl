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

// Init tooltips
$(document).ready(function () {
  $('[data-toggle="tooltip"]').tooltip();
});

// Timed events
window.setTimeout(setup, 600);
window.setInterval(ping, 5000);
window.setInterval(update, 100);

window.onbeforeunload = leave;

name.oninput = set_name;

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
      chat_init();
    }
  }
}

requestContentInput.onkeypress = (e) => {
  if (e.which == 13) {
    if (current_action == 'buzz') {
      answer();
    }
    else if (current_action == 'chat') {
      send_chat();
    }
  }
}

categorySelect.onchange = set_category;
difficultySelect.onchange = set_difficulty;
buzzBtn.onclick = buzz;
nextBtn.onclick = next;
resetBtn.onclick = () => {
  if (confirm("Are you sure you want to reset?")) {
    reset_score();
  }
}
chatBtn.onclick = chat_init