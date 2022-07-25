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
  const uuidPortHeading = document.getElementById("uuidPortHeading");
  if (isIR) {
    tableTitle.innerHTML = "IR Remotes";
    discoverButton.innerHTML = "Discover Remotes";
    uuidPortHeading.innerHTML = "PORT";
    for(device_name in remotes) {
      var deviceObject = {device_name : remotes[device_name]}
      var row = tableData.insertRow();
      var cell = row.insertCell();
      cell.innerHTML = device_name;
      cell = row.insertCell();
      cell.innerHTML = remotes[device_name]['ip_address'];
      cell = row.insertCell();
      cell.innerHTML = remotes[device_name]['port'];;
      cell = row.insertCell();
      cell.innerHTML = `<a class="smlButton" id="${device_name}" href="${controlUrl}" onclick="sessionStorage.setItem('ir', '${deviceObject}')">Control TV</a>`;
      cell = row.insertCell();
      cell.innerHTML = `<div class="smlButton" id="${uuid}" onclick="remove_tv('${device_name}')">Remove TV</div>`;
    }
  } else {
    tableTitle.innerHTML = "Smart TVs";
    discoverButton.innerHTML = "Discover TVs";
    uuidPortHeading.innerHTML = "UUID";
    for(uuid in tvs) {
      var row = tableData.insertRow();
      var cell = row.insertCell();
      cell.innerHTML = tvs[uuid]['tv_name'];
      cell = row.insertCell();
      cell.innerHTML = tvs[uuid]['ip_address'];
      cell = row.insertCell();
      cell.innerHTML = uuid;
      cell = row.insertCell();
      cell.innerHTML = `<a class="smlButton" id="${uuid}" href="${controlUrl}" onclick="sessionStorage.setItem('uuid', '${uuid}')">Control TV</a>`;
      cell = row.insertCell();
      cell.innerHTML = `<div class="smlButton" id="${uuid}" onclick="remove_tv('${uuid}')">Remove TV</div>`;
    }
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

// GET Request for current database tv list
window.onload = get_tvs = () => {
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
          loadTVs();
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
  sessionStorage.setItem("isIR", remoteSlider.checked)
}

const automate_event = () => {
  sessionStorage.setItem("isIR", remoteSlider.checked)
  console.log("AUTOMATE BUTTON NOT IMPLEMENTED YET")
  alert("AUTOMATE BUTTON NOT IMPLEMENTED YET")
}

remoteSlider.addEventListener("change", get_tvs);
remoteSlider.addEventListener("change", ir_token);
automateSlider.addEventListener("change", automate_event);
