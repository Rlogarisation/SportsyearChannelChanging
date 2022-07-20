// MMAN4010/MMAN4020 PROJECT 8 SPORTSYEAR
// TODO: MUST CHANGE VARIABLE BELOW:
const FETCHURL = 'http://localhost:5000/';

const updateChannels = (channels) => {
  const channelDropdown = document.getElementById("channels");

  for (var i = 0; i < channels.length; i++) {
    var opt = document.createElement('option');
    opt.value = channels[i];
    opt.innerHTML = `Channel ${channels[i]}`;
    channelDropdown.appendChild(opt);
  }
}

const updateTv = (tvs) => {
  const tvDropdown = document.getElementById("tv_list");

  for (tv in tvs) {
    var opt = document.createElement('option');
    opt.value = tv;
    opt.innerHTML = `TV ${tv}`;
    tvDropdown.appendChild(opt);
  }
}

window.onload = load = () => {
  uuid = sessionStorage.getItem('uuid')
  if (uuid === null || uuid === 'undefined') {
    // No TV selected so default to first found
    console.log(`catch`)
    get_first_uuid();
  } else {
    channel_list();
    const tv_display = document.getElementById('tv_display');
    tv_display.innerHTML = sessionStorage.getItem('uuid')
  }
}

const get_first_uuid = () => {
  console.log("GETTING TV LIST");
  route = 'smart/get_tvs'
  fetch(`${FETCHURL}${route}`, {
    method: 'GET',
  })
  .then((response) => {
    if (response.status === 200) {
      response.json().then((data) => {
        console.log(data['tv_list']);
        tvs = data['tv_list'];
        uuid = Object.keys(tvs)[0];
        sessionStorage.setItem('uuid', uuid);
        channel_list();
        const tv_display = document.getElementById('tv_display');
        tv_display.innerHTML = uuid;
      });
    } else handleResponse(response);
  })
  .catch((err)=>{
    alert("Oops crashed due to " + err + " \n(Check server is running)");
  });
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
  console.log("POWER BUTTON PRESSED");
  route = 'smart/power_toggle'
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
        console.log("power_toggle success")
      });
    } else handleResponse(response);
  })
  .catch((err)=>{
    alert("Oops crashed due to " + err + " \n(Check server is running)");
  });
}

// GET Request for list of available channels with uuid
const channel_list = () => {
  console.log("GETTING TV CHANNELS");
  route = 'smart/get_tvs';
  uuid = sessionStorage.getItem('uuid');
  fetch(`${FETCHURL}${route}`, {
    method: 'GET'
  })
  .then((response) => {
    if (response.status === 200) {
      response.json().then((data) => {
        channels_list = Object.keys(data['tv_list'][uuid]['tv_channels']);
        updateChannels(channels_list);
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
