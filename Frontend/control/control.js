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
  channel_list();

  if (!isIR && (uuid === null || uuid === 'undefined')) {
    // No TV selected so default to first found
    get_first_uuid();
    control_title.innerHTML = "TV Control: SMART"
  } else if (!isIR) {
    // Display TV
    tv_display.innerHTML = sessionStorage.getItem('smart_tv_name')
    control_title.innerHTML = "TV Control: SMART"
  } else {
    // Display IR Remote
    remote_name = sessionStorage.getItem('remote_name');
    tv_display.innerHTML = remote_name
    control_title.innerHTML = "TV Control: IR REMOTE";
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
        console.log(tvs)
        smart_tv_name = tvs[uuid]['tv_name'];
        sessionStorage.setItem('uuid', uuid);
        sessionStorage.setItem('smart_tv_name', smart_tv_name);
        channel_list();
        const tv_display = document.getElementById('tv_display');
        tv_display.innerHTML = smart_tv_name;
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
      DEVICE_NAME : sessionStorage.getItem("remote_name")
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
      DEVICE_NAME : sessionStorage.getItem("remote_name")
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
      DEVICE_NAME : sessionStorage.getItem("remote_name")
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
      DEVICE_NAME : sessionStorage.getItem("remote_name")
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
      DEVICE_NAME : sessionStorage.getItem("remote_name")
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
      DEVICE_NAME : sessionStorage.getItem("remote_name")
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
  isIR = sessionStorage.getItem("isIR") == 'true';
  if (!(isIR)) {
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
  } else {
    ir_channels_list = [...Array(99).keys()].map(i => i + 1);
    console.log(ir_channels_list);
    updateChannels(ir_channels_list);
  }
}
  
  const setChannel = () => {
  const select = document.getElementById('channels');
  var id = select.options[select.selectedIndex].value;
  console.log(`Set Channel ${id}`);
  isIR = sessionStorage.getItem("isIR") == 'true';
  if (!(isIR)) {
  route = 'smart/set_channel';
  bodyContent = JSON.stringify({
    uuid : sessionStorage.getItem('uuid'),
    channel_id : id
  })
  } else {
    route = 'ir/set_channel';
    bodyContent = JSON.stringify({
      DEVICE_NAME : sessionStorage.getItem('remote_name'),
      CHANNEL : id
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
        console.log("set_channel success")
      });
    } else handleResponse(response);
  })
  .catch((err)=>{
    alert("Oops crashed due to " + err + " \n(Check server is running)");
  });
}
