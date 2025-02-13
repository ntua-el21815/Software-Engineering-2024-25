document.addEventListener('DOMContentLoaded', () => {
    let selectedStartDate = null;
    let selectedEndDate = null;

    // Intercept the form submission to store the chosen dates
    const filterForm = document.getElementById('filter-form');
    filterForm.addEventListener('submit', (e) => {
        e.preventDefault();
        selectedStartDate = document.getElementById('start-date').value;
        selectedEndDate = document.getElementById('end-date').value;
    });

    // Initialize the map
    const map = L.map('map').setView([37.9838, 23.7275], 7);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Parse the main stations list
    const stations = document.querySelector('meta[name="station_list"]').content;
    let tollStations = JSON.parse(stations).map(station => ({
        id: station.stationID,
        name: station.stationName,
        latitude: station.Latitude,
        longitude: station.Longitude,
        description: `Operator: ${station.stationOperator}<br>Price 1: ${station.Price1}<br>Price 2: ${station.Price2}<br>Price 3: ${station.Price3}<br>Price 4: ${station.Price4}`
    }));

    // Display markers
    function addMarkers(stationsArray) {
        // Remove existing markers
        map.eachLayer(layer => {
            if (layer instanceof L.Marker) map.removeLayer(layer);
        });
        // Add new markers
        stationsArray.forEach(station => {
            const marker = L.marker([station.latitude, station.longitude]).addTo(map);
            marker.bindPopup(`
                <h3>${station.name}</h3>
                <p>${station.description}</p>
                <p>Latitude: ${station.latitude}</p>
                <p>Longitude: ${station.longitude}</p>
                <button onclick="showInfoPanel('${station.id}')">More info</button>
            `);
        });
    }
    addMarkers(tollStations);

    // Show info panel and fetch stats with dates
    window.showInfoPanel = function(stationId) {
        fetch('/getStats', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                station_id: stationId,
                start_date: selectedStartDate,
                end_date: selectedEndDate
            })
        })
        .then(response => {
            if (!response.ok) {
                window.location.reload();
            }
            return response.json();
        })
        .then(data => {
            const infoPanel = document.getElementById('info-panel');
            const table = infoPanel.querySelector('table')

            const stations = JSON.parse(document.querySelector('meta[name="station_list"]').content);
            const stationOperator = stations.find(station => station.stationID === stationId).stationOperator;

            table.innerHTML = `
                <tr><th colspan="2">Station Info</th></tr>
                <tr><td>Station ID</td><td>${data.stationID}</td></tr>
                <tr><td>Operator Name</td><td>${stationOperator}</td></tr>
                <tr><td>Total Passes in Time Period</td><td>${data.nPasses}</td></tr>
                <tr><td>Total Revenue in Time Period</td><td>${(data.totalRevenue === null || data.totalRevenue === 'None') ? '-' : data.totalRevenue}</td></tr>
                <tr><th colspan="2">Pass List</th></tr>
            `;
            data.passList.forEach(passItem => {
                table.innerHTML += `
                    <tr>
                        <td>#${passItem.passIndex} (${passItem.passType})</td>
                        <td>
                            Timestamp: ${passItem.timestamp}<br>
                            Charge: ${passItem.passCharge}<br>
                            Provider: ${passItem.tagProvider}
                        </td>
                    </tr>
                `;
            });

            infoPanel.classList.add('visible');
        })
        .catch(err => console.error('Error fetching stats:', err));
    };

    // Close info panel
    document.getElementById('close-panel').addEventListener('click', () => {
        document.getElementById('info-panel').classList.remove('visible');
    });

    // Handle "my stations"
    document.getElementById('view-my-stations').addEventListener('click', () => {
        const companyStations = JSON.parse(document.querySelector('meta[name="company_stations"]').content).map(station => ({
            id: station.stationID,
            name: station.stationName,
            latitude: station.Latitude,
            longitude: station.Longitude,
            description: `Operator: ${station.stationOperator}<br>Price 1: ${station.Price1}<br>Price 2: ${station.Price2}<br>Price 3: ${station.Price3}<br>Price 4: ${station.Price4}`
        }));
        addMarkers(companyStations);
    });

    // Handle "other companies"
    document.getElementById('view-other-companies').addEventListener('click', () => {
        const otherStations = JSON.parse(document.querySelector('meta[name="other_stations"]').content).map(station => ({
            id: station.stationID,
            name: station.stationName,
            latitude: station.Latitude,
            longitude: station.Longitude,
            description: `Operator: ${station.stationOperator}<br>Price 1: ${station.Price1}<br>Price 2: ${station.Price2}<br>Price 3: ${station.Price3}<br>Price 4: ${station.Price4}`
        }));
        addMarkers(otherStations);
    });
});
