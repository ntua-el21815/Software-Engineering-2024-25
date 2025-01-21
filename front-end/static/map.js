document.addEventListener('DOMContentLoaded', () => {
    // Initialize the map
    const map = L.map('map').setView([37.9838, 23.7275], 7); // Centered on Greece

    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Add a marker for each toll station
    const stations = document.getElementById('stations').dataset.results;

    var tollStations = JSON.parse(stations);

    tollStations = tollStations.map(station => ({
        id: station.stationID,
        name: station.stationName,
        latitude: station.Latitude,
        longitude: station.Longitude,
        description: `Operator: ${station.stationOperator}, Prices: [${station.Price1}, ${station.Price2}, ${station.Price3}, ${station.Price4}]`
    }));

    console.log(tollStations);

    tollStations.forEach(station => {
        const marker = L.marker([station.latitude, station.longitude]).addTo(map);

        marker.bindPopup(`
            <h3>${station.name}</h3>
            <p>${station.description}</p>
            <button onclick="showInfoPanel(${station.id})">More info</button>
        `);
    });

    // Close info panel
    const closePanelButton = document.getElementById('close-panel');
    closePanelButton.addEventListener('click', () => {
        document.getElementById('info-panel').classList.remove('visible');
    });

    // Buttons for filtering stations
    const viewMyStationsButton = document.getElementById('view-my-stations');
    const viewOtherCompaniesButton = document.getElementById('view-other-companies');

    viewMyStationsButton.addEventListener('click', () => {
        alert('Showing your toll stations...');
        const companyStations = document.getElementById('company-stations').dataset.results;

        console.log(companyStations);   

        var myTollStations = JSON.parse(companyStations);

        myTollStations = myTollStations.map(station => ({
            id: station.stationID,
            name: station.stationName,
            latitude: station.Latitude,
            longitude: station.Longitude,
            description: `Operator: ${station.stationOperator}, Prices: [${station.Price1}, ${station.Price2}, ${station.Price3}, ${station.Price4}]`
        }));

        console.log(myTollStations);

        // Remove existing markers
        map.eachLayer(layer => {
            if (layer instanceof L.Marker) {
            map.removeLayer(layer);
            }
        });
        myTollStations.forEach(station => {
            const marker = L.marker([station.latitude, station.longitude]).addTo(map);

            marker.bindPopup(`
                <h3>${station.name}</h3>
                <p>${station.description}</p>
                <button onclick="showInfoPanel(${station.id})">More info</button>
            `);
        });
    });

    viewOtherCompaniesButton.addEventListener('click', () => {
        alert('Showing other companies’ toll stations...');
        // Add logic to display other companies' toll stations
    const otherStations = document.getElementById('other-stations').dataset.results;

    console.log(otherStations);

    var otherTollStations = JSON.parse(otherStations);

    otherTollStations = otherTollStations.map(station => ({
        id: station.stationID,
        name: station.stationName,
        latitude: station.Latitude,
        longitude: station.Longitude,
        description: `Operator: ${station.stationOperator}, Prices: [${station.Price1}, ${station.Price2}, ${station.Price3}, ${station.Price4}]`
    }));

    console.log(otherTollStations);

    // Remove existing markers
    map.eachLayer(layer => {
        if (layer instanceof L.Marker) {
            map.removeLayer(layer);
        }
    });

    otherTollStations.forEach(station => {
        const marker = L.marker([station.latitude, station.longitude]).addTo(map);

        marker.bindPopup(`
            <h3>${station.name}</h3>
            <p>${station.description}</p>
            <button onclick="showInfoPanel(${station.id})">More info</button>
        `);
    });
    });
});

