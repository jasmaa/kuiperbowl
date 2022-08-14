// home.js
// Scripts for landing page

const landingContent = document.getElementById('landing-content');
const landingForm = document.getElementById('landing-form');
const landingButton = document.getElementById('landing-btn')

function submitGamePage() {
  const loc = landingContent.value.trim();

  if (loc != '' && loc.match(/^[a-z0-9_-]+$/)) {
    window.location.href = "/game/" + loc;
  }
  else {
    landingContent.classList.add('is-invalid');
  }
}

landingForm.onsubmit = (e) => {
  e.preventDefault();
  e.stopPropagation();
  submitGamePage();
}

landingButton.onclick = (e) => {
  e.preventDefault();
  e.stopPropagation();
  submitGamePage();
}