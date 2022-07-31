const FETCHURL = 'http://localhost:5000/';
const controlUrl = `${window.location.href.slice(0,-17)}/control/index.html`;
const remoteSlider = document.getElementById("remoteSlider");
const automateSlider = document.getElementById("automateSlider");

var tvs = {};
var remotes = {};

// Load TV data into table
const loadTVs = (isIR) => {
  const tableData = document.getElementById("tableData");
  tableData.innerHTML = "";
  const tableTitle = document.getElementById("tableTitle");
  const discoverButton = document.getElementById("discoverButton");
  const uuidProtocolHeading = document.getElementById("uuidProtocolHeading");
  const ipHeading = document.getElementById("ipHeading");
  if (isIR) {
    tableTitle.innerHTML = "IR Remotes";
    discoverButton.innerHTML = "Discover Remotes";
    uuidProtocolHeading.innerHTML = "PROTOCOL";
    ipHeading.innerHTML = "IP:PORT";
    for(device_name in remotes) {
      try {
        var remote_protocol = remotes[device_name]['type'];
      } catch {
        var remote_protocol = 'NEC';
        update_protocol(device_name);
      }
      console.log(remotes);
      var row = tableData.insertRow();
      var cell = row.insertCell();
      cell.innerHTML = device_name;
      cell = row.insertCell();
      cell.innerHTML = remotes[device_name]['ip_address'] + ':' + remotes[device_name]['port'];
      cell = row.insertCell();
      cell.innerHTML = `<select name="tvProtocols" id="tvProtocols_${device_name}" onchange="update_protocol('${device_name}')">
                          <option value="NEC"  ${remote_protocol=='NEC' ? 'selected' : ''}>NEC</option>
                          <option value="PANASONIC" ${remote_protocol=='PANASONIC' ? 'selected' : ''}>Panasonic</option>
                          <option value="SONY"  ${remote_protocol=='SONY' ? 'selected' : ''}>Sony</option>
                          <option value="SAMSUNG"  ${remote_protocol=='SAMSUNG' ? 'selected' : ''}>Samsung</option>
                        </select>`;
      cell = row.insertCell();
      cell.innerHTML = `<a class="smlButton" id="control_${device_name}" onclick="sessionStorage.setItem('remote_name', '${device_name}')" href="${controlUrl}">Control TV</a>`;
      cell = row.insertCell();
      cell.innerHTML = `<div class="smlButton" id="remove_${device_name}" onclick="remove_tv('${device_name}')">Remove TV</div>`;
    }
  } else {
    tableTitle.innerHTML = "Smart TVs";
    discoverButton.innerHTML = "Discover TVs";
    uuidProtocolHeading.innerHTML = "UUID";
    ipHeading.innerHTML = "IP ADDRESS";
    for(uuid in tvs) {
      var row = tableData.insertRow();
      var cell = row.insertCell();
      cell.innerHTML = tvs[uuid]['tv_name'];
      cell = row.insertCell();
      cell.innerHTML = tvs[uuid]['ip_address'];
      cell = row.insertCell();
      cell.innerHTML = uuid;
      cell = row.insertCell();
      cell.innerHTML = `<a class="smlButton" id="${uuid}" href="${controlUrl}" onclick="store_smart_tv('${uuid}','${tvs[uuid]['tv_name']}')">Control TV</a>`;
      cell = row.insertCell();
      cell.innerHTML = `<div class="smlButton" id="${uuid}" onclick="remove_tv('${uuid}')">Remove TV</div>`;
    }
  }
}

const store_smart_tv = (uuid, tv_name) => {
  sessionStorage.setItem('uuid', uuid);
  console.log(uuid)
  console.log(tvs)
  console.log(tvs[uuid])
  sessionStorage.setItem('smart_tv_name', tv_name);
}

const update_protocol = (device_name) => {
  const dropdown = document.getElementById('tvProtocols_' + device_name);
  const new_protocol = dropdown.options[dropdown.selectedIndex].value;
  route = 'ir/brand'
  fetch(`${FETCHURL}${route}`, {
    method: 'POST',
    headers: {
      'Content-Type' : 'application/json',
      "Accept" : "application/json"
    },
    body: JSON.stringify({
      DEVICE_NAME : device_name,
      TYPE : new_protocol
    })
  })
  .then((response) => {
    if (response.status === 200) {
      response.json().then((data) => {
        console.log("Update protocol success");
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

window.onload = remember_ir_slider = () => {
  if (sessionStorage.getItem("isIR") == 'true') {
    document.getElementById("remoteSlider").checked = true;
  }
  if (sessionStorage.getItem("isAutomated") == 'true') {
    document.getElementById("automateSlider").checked = true;
  }
  get_tvs()
  automate_event()
}

// GET Request for current database tv list
const get_tvs = () => {
  console.log("GETTING TV LIST");
  isIR = document.getElementById("remoteSlider").checked;
  if (isIR) route = 'ir/get_remotes'
  else route = 'smart/get_tvs'
  fetch(`${FETCHURL}${route}`, {
    method: 'GET',
  })
  .then((response) => {
    if (response.status === 200) {
      response.json().then((data) => {
        console.log(data)
        if (isIR) remotes = data['ir_remotes']
        else tvs = data['tv_list'];
        loadTVs(isIR);
      });
    } else handleResponse(response);
  })
  .catch((err)=>{
    alert("Oops crashed due to " + err + " \n(Check server is running)");
  });
}

// GET Request to scan for new tvs, will return updated list of tv's
const discover = () => {
  document.getElementById("loader").style.display = "block";
  isIR = document.getElementById("remoteSlider").checked;
  console.log(isIR);
  if (!(isIR)) {
    console.log("DISCOVER SMART BUTTON PRESSED");
    route = 'smart/scan';
    fetch(`${FETCHURL}${route}`, {
      method: 'GET',
    })
    .then((response) => {
      if (response.status === 200) {
        response.json().then((data) => {
          console.log(data)
          update = false
          for (var key in data['scan']) {
            if (!(key in tvs)) {
              update = true
            }
          }
          if (update) {
            tvs = data['scan']
            console.log('Update TV List')
            loadTVs(isIR);
          }
        });
      } else handleResponse(response);
      document.getElementById("loader").style.display = "none";
    })
    .catch((err)=>{
      alert("Oops crashed due to " + err + " \n(Check server is running)");
      document.getElementById("loader").style.display = "none";
    });
  } else {
    console.log("DISCOVER IR BUTTON PRESSED");
    route = 'ir/scan';
    fetch(`${FETCHURL}${route}`, {
      method: 'GET',
    })
    .then((response) => {
      if (response.status === 200) {
        response.json().then((data) => {
          console.log(data)
          update = false
          for (var key in data['scan']) {
            if (!(key in remotes)) {
              update = true
            }
          }
          if (update) {
            remotes = data['scan']
            console.log('Update TV List')
            loadTVs(isIR);
          }
        });
      } else handleResponse(response);
      document.getElementById("loader").style.display = "none";
    })
    .catch((err)=>{
      alert("Oops crashed due to " + err + " \n(Check server is running)");
      document.getElementById("loader").style.display = "none";
    });
  }
}

// DELETE Request to delete tv with uuid will return updated list of tv's
const remove_tv = (uuid) => {
  console.log("DELETE BUTTON PRESSED");
  isIR = document.getElementById("remoteSlider").checked;
  if (!(isIR)) {
    route = 'smart/remove_tv'
    fetch(`${FETCHURL}${route}`, {
      method: 'DELETE',
      headers: {
        'Content-Type' : 'application/json',
        "Accept" : "application/json"
      },
      body: JSON.stringify({
        uuid : uuid
      })
    })
    .then((response) => {
      if (response.status === 200) {
        response.json().then((data) => {
          console.log(data)
          tvs = data['tv_list']
          loadTVs(isIR);
        });
      } else handleResponse(response);
    })
    .catch((err)=>{
      alert("Oops crashed due to " + err + " \n(Check server is running)");
    });
  } else {
    //TODO remove ir remote
    console.log("REMOVE IR BUTTON NOT IMPLEMENTED YET")
    alert("REMOVE IR BUTTON NOT IMPLEMENTED YET")
  }
}

const ir_token = () => {
  sessionStorage.setItem("isIR", remoteSlider.checked);
}

const automate_event = () => {
  console.log("AUTOMATION SMART TV");
  isAutomated = document.getElementById("automateSlider").checked;
  if (isAutomated) {
    route = 'automation/resume';
  } else {
    route = 'automation/pause';
  }
  fetch(`${FETCHURL}${route}`, {
    method: 'POST',
  })
  .then((response) => {
    if (response.status === 200) {
      response.json().then((data) => {
        if (isAutomated) {
          console.log("Automate Resume Success")
        } else {
          console.log("Automate Pause Success")
        }
      });
    } else handleResponse(response);
  })
  .catch((err)=>{
    alert("Oops crashed due to " + err + " \n(Check server is running)");
  });
}

const automate_token = () => {
  sessionStorage.setItem("isAutomated", automateSlider.checked);
}

remoteSlider.addEventListener("change", get_tvs);
remoteSlider.addEventListener("change", ir_token);
automateSlider.addEventListener("change", automate_token);
automateSlider.addEventListener("change", automate_event);
