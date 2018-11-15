

function retrieve_userdata(){
  var prefs = cookieToDict(document.cookie);
  name = prefs['name'];
  player_id = prefs['player_id'];
}

function setCookie(name, val){
  document.cookie = name+"="+val;
}

// I stole this
function cookieToDict(str) {
    str = str.split('; ');
    var result = {};
    for (var i = 0; i < str.length; i++) {
        var cur = str[i].split('=');
        result[cur[0]] = cur[1];
    }
    return result;
}
