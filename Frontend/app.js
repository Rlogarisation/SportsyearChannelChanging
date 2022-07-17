// MMAN4010/MMAN4020 PROJECT 8 SPORTSYEAR BY ZHENG LUO(Z5206267)
// TODO: MUST CHANGE VARIABLE BELOW:
const FETCHURL = 'http://localhost:5005/';

const volumeUpButton = document.getElementById("volumeUpButton");
const volumeDownButton = document.getElementById("volumeDownButton");
const muteButton = document.getElementById("muteButton");
const channelIncrementButton = document.getElementById("channelIncrementButton");
const channelDecrementButton = document.getElementById("channelDecrementButton");
const powerButton = document.getElementById("powerButton");

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
    fetch(FETCHURL + path, requestInfo)
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

const volumeIncrement = () => {
  console.log("VOLUME UP Pressed");
  const jsonString = JSON.stringify({});
  fetchAPI('POST', "default", jsonString, 'smart/raise_volume')
    .then(() =>{
      console.log("You Have Been Successfully VOLUME UP!");
    })
    .catch((err) => {
      alert("Oops API fetched failed due to" + err);
    });
}

const volumeDecrement = () => {
  console.log("VOLUME DOWN!");
}

const muteFunction = () => {
  console.log("MUTE!");
}

const channelIncrement = () => {
  console.log("CHANNEL += 1");
}

const channelDecrement = () => {
  console.log("CHANNEL -= 1");
}

const power = () => {
  console.log("POWER BUTTON PRESSED.");
}

volumeUpButton.addEventListener("click", volumeIncrement);
volumeDownButton.addEventListener("click", volumeDecrement);
muteButton.addEventListener("click", muteFunction);
channelIncrementButton.addEventListener("click", channelIncrement);
channelDecrementButton.addEventListener("click", channelDecrement);
powerButton.addEventListener("click", power);
