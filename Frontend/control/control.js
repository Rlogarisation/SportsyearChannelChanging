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

window.onload = load = () => {
  const tv_display = document.getElementById('tv_display');
  const control_title = document.getElementById('controlTitle');
  uuid = sessionStorage.getItem('uuid');
  isIR = sessionStorage.getItem("isIR") == 'true';

  if (!isIR && (uuid === null || uuid === 'undefined')) {
    // No TV selected so default to first found
    get_first_uuid();
    control_title.innerHTML = "TV Control: SMART"
  } else if (!isIR) {
    // Display TV
    channel_list();
    tv_display.innerHTML = sessionStorage.getItem('uuid')
    control_title.innerHTML = "TV Control: SMART"
  } else {
    // Display IR Remote
    remote_name = sessionStorage.getItem('remote_name');
    tv_display.innerHTML = remote_name
    control_title.innerHTML = "TV Control: IR REMOTE";
    var changeChannelList = document.getElementById("changeChannelList");
    changeChannelList.style.display = "none";
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
  isIR = sessionStorage.getItem("isIR") == 'true';
  if (isIR) {
    route = 'ir/raise_volume';
    bodyContent = JSON.stringify({
      IP : sessionStorage.getItem("remote_ip") == 'true',
      PORT : sessionStorage.getItem("remote_port") == 'true',
      TYPE : 'NEC'
    })
  } else {
    route = 'smart/raise_volume'
    bodyContent = JSON.stringify({
      uuid : sessionStorage.getItem('uuid')
    })
  }
  fetch(`${FETCHURL}${route}`, {
    method: 'POST',
    headers: {
      'Content-Type' : 'application/json',
      "Accept" : "application/json"
    },
    body: bodyContent
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
  isIR = sessionStorage.getItem("isIR") == 'true';
  if (isIR) {
    route = 'ir/lower_volume';
    bodyContent = JSON.stringify({
      IP : sessionStorage.getItem("remote_ip") == 'true',
      PORT : sessionStorage.getItem("remote_port") == 'true',
      TYPE : 'NEC'
    })
  } else {
    route = 'smart/lower_volume';
    bodyContent = JSON.stringify({
      uuid : sessionStorage.getItem('uuid')
    })
  }
  fetch(`${FETCHURL}${route}`, {
    method: 'POST',
    headers: {
      'Content-Type' : 'application/json',
      "Accept" : "application/json"
    },
    body: bodyContent
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
  isIR = sessionStorage.getItem("isIR") == 'true';
  if (isIR) {
    route = 'ir/mute';
    bodyContent = JSON.stringify({
      IP : sessionStorage.getItem("remote_ip") == 'true',
      PORT : sessionStorage.getItem("remote_port") == 'true',
      TYPE : 'NEC'
    })
  } else {
    route = 'smart/mute';
    bodyContent = JSON.stringify({
      uuid : sessionStorage.getItem('uuid')
    })
  }
  fetch(`${FETCHURL}${route}`, {
    method: 'POST',
    headers: {
      'Content-Type' : 'application/json',
      "Accept" : "application/json"
    },
    body: bodyContent
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
  isIR = sessionStorage.getItem("isIR") == 'true';
  if (isIR) {
    route = 'ir/raise_channel';
    bodyContent = JSON.stringify({
      IP : sessionStorage.getItem("remote_ip") == 'true',
      PORT : sessionStorage.getItem("remote_port") == 'true',
      TYPE : 'NEC'
    })
  } else {
    route = 'smart/raise_channel';
    bodyContent = JSON.stringify({
      uuid : sessionStorage.getItem('uuid')
    })
  }
  fetch(`${FETCHURL}${route}`, {
    method: 'POST',
    headers: {
      'Content-Type' : 'application/json',
      "Accept" : "application/json"
    },
    body: bodyContent
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
  isIR = sessionStorage.getItem("isIR") == 'true';
  if (isIR) {
    route = 'ir/lower_channel';
    bodyContent = JSON.stringify({
      IP : sessionStorage.getItem("remote_ip") == 'true',
      PORT : sessionStorage.getItem("remote_port") == 'true',
      TYPE : 'NEC'
    })
  } else {
    route = 'smart/lower_channel';
    bodyContent = JSON.stringify({
      uuid : sessionStorage.getItem('uuid')
    })
  }
  fetch(`${FETCHURL}${route}`, {
    method: 'POST',
    headers: {
      'Content-Type' : 'application/json',
      "Accept" : "application/json"
    },
    body: bodyContent
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
  isIR = sessionStorage.getItem("isIR") == 'true';
  if (isIR) {
    route = 'ir/power';
    bodyContent = JSON.stringify({
      IP : sessionStorage.getItem("remote_ip") == 'true',
      PORT : sessionStorage.getItem("remote_port") == 'true',
      TYPE : 'NEC'
    })
  } else {
    route = 'smart/power_toggle';
    bodyContent = JSON.stringify({
      uuid : sessionStorage.getItem('uuid')
    })
  }
  fetch(`${FETCHURL}${route}`, {
    method: 'POST',
    headers: {
      'Content-Type' : 'application/json',
      "Accept" : "application/json"
    },
    body: bodyContent
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
