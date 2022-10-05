/**
 * Send post request to URL without query string, informing backend to refresh cache for current page.
 * */
function refresh() {
    let xhr = new XMLHttpRequest();
    xhr.open("POST", `${location.protocol}//${location.host}${location.pathname}`, true);
    xhr.setRequestHeader("X-CSRFToken", `${csrf_token}`);
    xhr.send("refresh");
}