// home.js
// Scripts for landing page

const landingContent = document.getElementById('landing-content');
const landingForm = document.getElementById('landing-form');

landingForm.onsubmit = (e) => {

  e.preventDefault();
  e.stopPropagation();

  const loc = landingContent.value.trim();
  
  if (loc != '' && loc.match(/^[a-z0-9_-]+$/)) {
    window.location.href = "/game/" + loc;
  }
  else {
    landingContent.classList.add('is-invalid');
  }
}

/*
landingBtn.onclick = (e) => {
  gotoRoom();
}

landingContent.onkeypress = (e) => {
  if (e.which == 13) {
    //gotoRoom();
    e.preventDefault();
    e.stopPropagation();
  }
}
*/