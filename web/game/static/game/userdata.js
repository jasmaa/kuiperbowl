
/**
 * Get user data from cookie
 */
function retrieve_userdata(){
  const prefs = cookieToDict(document.cookie);
  user_name = prefs['user_name'];
  user_id = prefs['user_id'];
  locked_out = prefs['locked_out'] === 'true';
}

/**
 * Set cookie
 * @param {*} name 
 * @param {*} val 
 */
function setCookie(name, val){
  document.cookie = `${name}=${val}`;
}

/**
 * Set cookie and path
 * @param {*} name 
 * @param {*} val 
 * @param {*} path 
 */
function setCookieAndPath(name, val, path){
  document.cookie = `${name}=${val}; path=${path}`;
}

/**
 * Extract object from cookie
 * @param {*} str 
 */
function cookieToDict(str) {
    str = str.split('; ');
    let result = {};
    for (let i = 0; i < str.length; i++) {
        const cur = str[i].split('=');
        result[cur[0]] = cur[1];
    }
    return result;
}
