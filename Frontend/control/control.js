// MMAN4010/MMAN4020 PROJECT 8 SPORTSYEAR
// TODO: MUST CHANGE VARIABLE BELOW:
const FETCHURL = 'http://localhost:5000/';

const update_channels = (channels) => {
  const channelDropdown = document.getElementById("channels");

  for (var i = 0; i < channels.length; i++) {
    var opt = document.createElement('option');
    opt.value = channels[i];
    opt.innerHTML = `Channel ${channels[i]}`;
    channelDropdown.appendChild(opt);
  }
}

// Handle Error Messages from requests
const handleResponse = (response) => {
  response.text().then((err) => {
    var errorMessage = err.match('<p>(.*)</p>')[1]
    if (errorMessage) alert(`[${response.status} ${response.statusText}] ${errorMessage}`)
    else alert(`[${response.status} ${response.statusText}]`)
  })
}

const volumeIncrement = () => {
  console.log("VOLUME UP Pressed");
  route = 'smart/raise_volume'
  fetch(`${FETCHURL}${route}`, {
    method: 'POST',
    headers: {
      'Content-Type' : 'application/json',
      "Accept" : "application/json"
    },
    body: JSON.stringify({
      uuid : sessionStorage.getItem('uuid')
    })
  })
  .then((response) => {
    if (response.status === 200) {
      response.json().then((data) => {
        console.log("raise_volume success")
      });
    } else handleResponse(response);
  })
  .catch((err)=>{
    alert("Oops crashed due to " + err + " \n(Check server is running)");
  });
}

const volumeDecrement = () => {
  console.log("VOLUME DOWN!");
  route = 'smart/lower_volume'
  fetch(`${FETCHURL}${route}`, {
    method: 'POST',
    headers: {
      'Content-Type' : 'application/json',
      "Accept" : "application/json"
    },
    body: JSON.stringify({
      uuid : sessionStorage.getItem('uuid')
    })
  })
  .then((response) => {
    if (response.status === 200) {
      response.json().then((data) => {
        console.log("lower_volume success")
      });
    } else handleResponse(response);
  })
  .catch((err)=>{
    alert("Oops crashed due to " + err + " \n(Check server is running)");
  });
}

const mute = () => {
  console.log("MUTE!");
  route = 'smart/mute'
  fetch(`${FETCHURL}${route}`, {
    method: 'POST',
    headers: {
      'Content-Type' : 'application/json',
      "Accept" : "application/json"
    },
    body: JSON.stringify({
      uuid : sessionStorage.getItem('uuid')
    })
  })
  .then((response) => {
    if (response.status === 200) {
      response.json().then((data) => {
        console.log("mute success")
      });
    } else handleResponse(response);
  })
  .catch((err)=>{
    alert("Oops crashed due to " + err + " \n(Check server is running)");
  });
}

const channelIncrement = () => {
  console.log("CHANNEL += 1");
  route = 'smart/raise_channel'
  fetch(`${FETCHURL}${route}`, {
    method: 'POST',
    headers: {
      'Content-Type' : 'application/json',
      "Accept" : "application/json"
    },
    body: JSON.stringify({
      uuid : sessionStorage.getItem('uuid')
    })
  })
  .then((response) => {
    if (response.status === 200) {
      response.json().then((data) => {
        console.log("raise_channel success")
      });
    } else handleResponse(response);
  })
  .catch((err)=>{
    alert("Oops crashed due to " + err + " \n(Check server is running)");
  });
}

const channelDecrement = () => {
  console.log("CHANNEL -= 1");
  route = 'smart/lower_channel'
  fetch(`${FETCHURL}${route}`, {
    method: 'POST',
    headers: {
      'Content-Type' : 'application/json',
      "Accept" : "application/json"
    },
    body: JSON.stringify({
      uuid : sessionStorage.getItem('uuid')
    })
  })
  .then((response) => {
    if (response.status === 200) {
      response.json().then((data) => {
        console.log("lower_channel success")
      });
    } else handleResponse(response);
  })
  .catch((err)=>{
    alert("Oops crashed due to " + err + " \n(Check server is running)");
  });
}

const power = () => {
  console.log("POWER BUTTON PRESSED.");
}

// GET Request for list of available channels with uuid
window.onload = channel_list = () => {
  console.log("GETTING TV CHANNELS");
  route = 'smart/channel_list';
  uuid = sessionStorage.getItem('uuid');
  fetch(`${FETCHURL}${route}/${uuid}`, {
    method: 'GET'
  })
  .then((response) => {
    if (response.status === 200) {
      response.json().then((data) => {
        console.log(data['list'])
        update_channels(data['list'])
      });
    } else handleResponse(response);
  })
  .catch((err)=>{
    alert("Oops crashed due to " + err + " \n(Check server is running)");
  });
}

const setChannel = () => {
  const select = document.getElementById('channels');
  var id = select.options[select.selectedIndex].value
  console.log(`Set Channel ${id}`);

  route = 'smart/set_channel'
  fetch(`${FETCHURL}${route}`, {
    method: 'POST',
    headers: {
      'Content-Type' : 'application/json',
      "Accept" : "application/json"
    },
    body: JSON.stringify({
      uuid : sessionStorage.getItem('uuid'),
      channel_id : id
    })
  })
  .then((response) => {
    if (response.status === 200) {
      response.json().then((data) => {
        console.log("set_channel success")
      });
    } else handleResponse(response);
  })
  .catch((err)=>{
    alert("Oops crashed due to " + err + " \n(Check server is running)");
  });
}
