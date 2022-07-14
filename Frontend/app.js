const volumeUpButton = document.getElementById("volumeUpButton");
const volumeDownButton = document.getElementById("volumeDownButton");
const muteButton = document.getElementById("muteButton");
const channelIncrementButton = document.getElementById("channelIncrementButton");
const channelDecrementButton = document.getElementById("channelDecrementButton");
const powerButton = document.getElementById("powerButton");

volumeUpButton.addEventListener("click", volumeIncrement);
volumeDownButton.addEventListener("click", volumeDecrement);
muteButton.addEventListener("click", muteFunction);
channelIncrementButton.addEventListener("click", channelIncrement);
channelDecrementButton.addEventListener("click", channelDecrement);
powerButton.addEventListener("click", power);

const fetchAPI = (method, header, body, path) => {
  if (header === "default") {
    header = { 'Content-Type': 'application/json' }
  }
  const requestInfo = {
    method: method,
    headers: header,
    body: body,
  };

  return new Promise((resolve, reject) => {
    fetch('http://localhost:5005/' + path, requestInfo)
      .then((response) => {
        if (response.status === 400 || response.status === 403) {
          response.json().then((errorMes) => {
            alert(errorMes['error']);
            reject(errorMes['error']);
          });
        }
        else if (response.status === 200) {
          response.json().then((data) => {
            resolve(data);
          });
        }
      })
      .catch((err)=>{
        alert("Oops crashed due to" + err);
      });
  });

};

function volumeIncrement() {
  console.log("VOLUME UP!");
}

function volumeDecrement() {
  console.log("VOLUME DOWN!");
}

function muteFunction() {
  console.log("MUTE!");
}

function channelIncrement() {
  console.log("CHANNEL += 1");
}

function channelDecrement() {
  console.log("CHANNEL -= 1");
}

function power() {
  console.log("POWER BUTTON PRESSED.");
}
