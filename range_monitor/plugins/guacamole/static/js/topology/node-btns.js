
// work in progress 
const xhrRequestTo = (endpoint) => {
  const apiEndpoint = `/guacamole/api/${endpoint}`;
  const xhrGuac = new XMLHttpRequest();
  xhrGuac.open("POST", apiEndpoint, true);
  xhrGuac.setRequestHeader("Content-Type", "application/json");
  return xhrGuac;
};


const connectBtn = (selectIds) => {
  $(".btn-connect").on("click", () => {
    const ids = selectIds.map((node) => node.identifier);

    if (!ids) return;

    const xhr = xhrRequestTo("connect-connections");
    xhr.onreadystatechange = function () {
      if (xhr.readyState !== XMLHttpRequest.DONE) {
        return;
      }
      // when ready but not 200
      if (xhr.status !== 200) {
        alert(xhr.responseText);
        return;
      }
      
      const response = JSON.parse(xhr.responseText);
      const link = `${response.url}?token=${response.token}`;
      window.open(link, "_blank");
    };
    const data = JSON.stringify({ identifiers: ids });
    xhr.send(data);
  });
}
// prob incomplete 
const killBtn = () => {
  $(".btn-kill").on("click", () => {
    const xhr = xhrRequestTo("kill-connections");
    xhr.onreadystatechange = function () {
      if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
        const response = JSON.parse(xhr.responseText);
        console.log(response);
      } else if (xhr.readyState === XMLHttpRequest.DONE) {
        alert(xhr.responseText);
      }
    };
  });
};



const timelineBtn = () => {

};


export function setupControlEvents(selectedIds) {
  connectBtn(selectedIds);
  killBtn()
  timelineBtn()
}