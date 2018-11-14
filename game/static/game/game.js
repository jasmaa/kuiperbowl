var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
var gamesock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + window.location.pathname);

window.setInterval(ping, 5000);

// Ping server for state
function ping(){
  console.log("ping");
}

// Buzz
function buzz(){

}

// Request next question
function next(){

}
