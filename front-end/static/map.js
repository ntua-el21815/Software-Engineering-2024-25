document.addEventListener('DOMContentLoaded', () => {
    // Initialize the map
    const map = L.map('map').setView([37.9838, 23.7275], 7); // Centered on Greece

    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Add a marker for each toll station
    

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
        // Add logic to highlight user's toll stations
    });

    viewOtherCompaniesButton.addEventListener('click', () => {
        alert('Showing other companies’ toll stations...');
        // Add logic to display other companies' toll stations
    });
});

