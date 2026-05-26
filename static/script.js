

/** @type {import('leaflet').Map} */
/** @param {import('leaflet').LeafletMouseEvent} e */

// Setup Map | read Leaflet Docs for understanding 

const map = L.map('map').setView([26.9124, 75.7873], 13);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap'
}).addTo(map);

console.log("Map loaded successfully");

let markers = {}; // use to track the device location and marker by last location, persent or not, what the new location is? 
let deviceCounter = 1; // start couting fromm 1 ex -> _001 _002 and all. 

// Listen clicks -> what change on map lat lng devices and set location.
map.on('click', function (e) {
    // Round to 5 decimal places for clean input handling
    const clickedLat = e.latlng.lat.toFixed(5);
    const clickedLng = e.latlng.lng.toFixed(5);
 
    document.getElementById('lat').value = clickedLat;
    document.getElementById('lng').value = clickedLng;
 
    document.getElementById('spawn-lat').value = clickedLat;
    document.getElementById('spawn-lng').value = clickedLng;

    // 3. Update UI Hints and ID
    document.getElementById('device-id').value = 'device_' + String(deviceCounter).padStart(3, '0');
    document.getElementById('click-hint').textContent = '✅ Location set! Fill speed & road.';
});

// put the colors based on the speed 
function getSpeedColor(speed) {
    if (speed < 10) return '#ef4444';
    if (speed < 30) return '#f59e0b';
    return '#22c55e';
}

// DRAW MARKER ON MAP
function addMarkerToMap(id, lat, lng, speed, road) {
    const color = getSpeedColor(speed)

    const icon = L.divIcon({ // create the icons with size 
        html: `<div style="width:11px;height:11px;background:${color};
                border-radius:50%;border:2px solid #fff;
                box-shadow:0 0 6px ${color}88;"></div>`,
        iconSize: [11, 11],
        className: ''
    });
    // avoid duplicate markers, no ghost dots. 
    if (markers[id]) map.removeLayer(markers[id]);
    // makr the location with icon road name speed and device id 
    markers[id] = L.marker([lat, lng], { icon })
        .addTo(map)
        .bindPopup(`<b>${id}</b><br>Road: ${road}<br>Speed: ${speed} km/h`);

}

// Add Devices

async function addDevice() {

    // Easy to understand

    const id = document.getElementById('device-id').value || `device_${Date.now()}`
    const lat = parseFloat(document.getElementById('lat').value);

    const lng = parseFloat(document.getElementById('lng').value);
    const speed = parseFloat(document.getElementById('speed').value);
    const road = document.getElementById('road').value || 'unknown';

  // Checking condition and return  
    if (isNaN(lat) || isNaN(lng)) {
        alert('Click the map first to set location!')
        return;
    }
    try {
        const res = await fetch( // Send device data to Python server with POST request
            `/device/add?device_id=${id}&lat=${lat}&lng=${lng}&speed=${speed}&road=${road}`,
            { method: 'POST' }
        );
        const data = await res.json(); // waiting for data
        addMarkerToMap(id, lat, lng, speed, road); // draw the map and increment the device data.
        deviceCounter++;
        document.getElementById('click-hint').textContent = 'Click map to set locations';

        refreshAll();

    } catch (error) {

        console.log('Failed to add device: ', error);

    }

}

// Spawn many device at once

async function spawnDevice() {

    const road = document.getElementById('spawn-road').value || 'Road_A';
    const count = parseInt(document.getElementById('spawn-count').value);
    const speed = parseFloat(document.getElementById('spawn-speed').value);
    // If spawn center not set, default to city center
    const centerLat = parseFloat(document.getElementById('spawn-lat').value) || 26.9124;
    const centerLng = parseFloat(document.getElementById('spawn-lng').value) || 75.7873;

    for (let i = 0; i < count; i++) {

        const id = `${road}_${Date.now()}_${i}`;
        const lat = centerLat + (Math.random() - 0.5) * 0.003;
        const lng = centerLng + (Math.random() - 0.5) * 0.003;

        await fetch( // add the device with id lat lng spped annd road.
            `/device/add?device_id=${id}&lat=${lat}&lng=${lng}&speed=${speed}&road=${road}`,
            { method: 'POST' }
        );

        addMarkerToMap(id, lat, lng, speed, road)

    }
    refreshAll()
}


async function removeDevice(id) {
    // remove a particular 
    await fetch(`/device/remove/${id}`, { method: 'DELETE' });
    if (markers[id]) {
        map.removeLayer(markers[id]);
        delete markers[id];
    }
    refreshAll();

}

async function clearAll() {
    await fetch('/devices/clear', { method: 'DELETE' });
    Object.values(markers).forEach(m => map.removeLayer(m)); // object because js store all the data in object form
    markers = {}; // set the object again as empty
    refreshAll();
}

async function refreshAll() {

    const devRes = await fetch('/devices'); // Get the devices 
    const devices = await devRes.json();    // parse Json to 
    const count = Object.keys(devices).length; // changed into object to coutn key in object 

    document.getElementById('device-count').textContent = `${count} devices`;

    const listEl = document.getElementById('device-list');
    listEl.innerHTML = '';  // clear old list before rebuilding

    for (const [id, d] of Object.entries(devices)) {
        const color = getSpeedColor(d.speed);
        // Truncate long IDs so they fit in sidebar
        const label = id.length > 16 ? id.substring(0, 16) + '…' : id;
        addMarkerToMap(id, d.lat, d.lng, d.speed, d.road);
        // Build HTML string for each device row
        // onclick="removeDevice('${id}')" → calls JS function when ✕ clicked
        listEl.innerHTML += `
      <div class="device-item">
        <span>
          <span style="color:${color}">●</span>
          ${label}
          <span style="color:#4b5563">${d.speed}km/h</span>
        </span>
        <button class="del-btn" onclick="removeDevice('${id}')">✕</button>
      </div>`;
    }



    // --- Refresh road summary cards ---
    const trafficRes = await fetch('/traffic/summary');  // GET /traffic/summary
    const summary = await trafficRes.json();
    const sumEl = document.getElementById('traffic-summary');

    if (Object.keys(summary).length === 0) {
        sumEl.innerHTML = '<p class="empty-msg">No devices yet</p>';
        return;
    }

    sumEl.innerHTML = '';
    // Loop each road: road = "Road_A", data = {avg_speed, status, devices}
    for (const [road, data] of Object.entries(summary)) {
        sumEl.innerHTML += `
      <div class="road-card">
        <div class="road-name">${road}</div>
        <div class="road-meta">${data.status} · ${data.avg_speed} km/h avg · ${data.devices} devices</div>
      </div>`;
    }
}


// ── AUTO REFRESH ───────────────────────────────────────────
// setInterval(fn, ms) = run fn every 5000ms = 5 seconds
// This simulates live updates — in real system, server pushes via WebSocket
setInterval(refreshAll, 5000);

// Run once immediately on page load
refreshAll();


