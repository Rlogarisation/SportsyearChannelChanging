const FETCHURL = 'http://localhost:5000/';
const frontend = "file:///C:/Users/Jack%20O'Leary/Documents/6th%20Year%20Uni/MMAN4010/SportsYear/Frontend/index.html"

const discoverButton = document.getElementById("discoverButton");
var tvs = {};

// Load TV data into table
const loadTVs = () => {
  const tableData = document.getElementById("tableData");
  tableData.innerHTML = ""

  for(uuid in tvs) {
    var row = tableData.insertRow();
    var cell = row.insertCell();
    cell.innerHTML = tvs[uuid]['tv_name'];
    cell = row.insertCell();
    cell.innerHTML = tvs[uuid]['ip_address'];
    cell = row.insertCell();
    cell.innerHTML = uuid;
    cell = row.insertCell();
    cell.innerHTML = `<a class="smlButton" id="${uuid}" href="${frontend}">Control TV</a>`;
    cell = row.insertCell();
    cell.innerHTML = `<div class="smlButton" id="${uuid}" onclick="remove_tv('${uuid}')">Remove TV</div>`;
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
  route = 'smart/get_tvs'
  fetch(`${FETCHURL}${route}`, {
    method: 'GET',
  })
  .then((response) => {
    if (response.status === 200) {
      response.json().then((data) => {
        console.log(data)
        tvs = data['tv_list'];
        loadTVs();
      });
    } else handleResponse(response);
  })
}

// GET Request to scan for new tvs, will return updated list of tv's
const discover = () => {
  console.log("DISCOVER BUTTON PRESSED");
  document.getElementById("loader").style.display = "block";
  route = 'smart/scan'
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
          loadTVs();
        }
      });
    } else handleResponse(response);
    document.getElementById("loader").style.display = "none";
  })
}

// DELETE Request to delete tv with uuid will return updated list of tv's
const remove_tv = (uuid) => {
  console.log("DELETE BUTTON PRESSED");
  console.log(uuid)
  // const formData = new FormData();
  // formData.append('uuid', uuid);
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
}

discoverButton.addEventListener("click", discover);