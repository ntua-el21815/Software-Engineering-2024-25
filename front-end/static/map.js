document.addEventListener('DOMContentLoaded', () => {
    // Get station data from meta tags
    const stationsElement = document.querySelector('meta[name="station_list"]');
    if (!stationsElement) return;
    const rawStations = stationsElement.getAttribute('content');
    if (!rawStations) return;
    const tollStations = JSON.parse(rawStations);

    // Initialize Leaflet map
    const map = L.map('map').setView([37.9838, 23.7275], 7);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Place markers
    tollStations.forEach(station => {
        const marker = L.marker([station.Latitude, station.Longitude]).addTo(map);
        marker.bindPopup(`
            <h3>${station.stationName}</h3>
            <p>Operator: ${station.stationOperator}</p>
            <p>Price 1: ${station.Price1} €</p>
            <p>Price 2: ${station.Price2} €</p>
            <p>Price 3: ${station.Price3} €</p>
            <p>Price 4: ${station.Price4} €</p>
        `);
    });

    // Close info panel
    const closePanelButton = document.getElementById('close-panel');
    if (closePanelButton) {
        closePanelButton.addEventListener('click', () => {
            document.getElementById('info-panel').classList.add('hidden');
        });
    }

    // Filter buttons
    const viewMyStationsButton = document.getElementById('view-my-stations');
    const viewOtherCompaniesButton = document.getElementById('view-other-companies');

    if (viewMyStationsButton) {
        viewMyStationsButton.addEventListener('click', () => {
            const companyEl = document.querySelector('meta[name="company_stations"]');
            if (!companyEl) return;
            const myTollStations = JSON.parse(companyEl.getAttribute('content'));

            map.eachLayer(layer => {
                if (layer instanceof L.Marker) map.removeLayer(layer);
            });

            myTollStations.forEach(station => {
                const marker = L.marker([station.Latitude, station.Longitude]).addTo(map);
                marker.bindPopup(`
                    <h3>${station.stationName}</h3>
                    <p>Operator: ${station.stationOperator}</p>
                    <p>Price 1: ${station.Price1} €</p>
                    <p>Price 2: ${station.Price2} €</p>
                    <p>Price 3: ${station.Price3} €</p>
                    <p>Price 4: ${station.Price4} €</p>
                `);
            });
        });
    }

    if (viewOtherCompaniesButton) {
        viewOtherCompaniesButton.addEventListener('click', () => {
            const othersEl = document.querySelector('meta[name="other_stations"]');
            if (!othersEl) return;
            const otherTollStations = JSON.parse(othersEl.getAttribute('content'));

            map.eachLayer(layer => {
                if (layer instanceof L.Marker) map.removeLayer(layer);
            });

            otherTollStations.forEach(station => {
                const marker = L.marker([station.Latitude, station.Longitude]).addTo(map);
                marker.bindPopup(`
                    <h3>${station.stationName}</h3>
                    <p>Operator: ${station.stationOperator}</p>
                    <p>Price 1: ${station.Price1} €</p>
                    <p>Price 2: ${station.Price2} €</p>
                    <p>Price 3: ${station.Price3} €</p>
                    <p>Price 4: ${station.Price4} €</p>
                `);
            });
        });
    }
});

