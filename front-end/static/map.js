document.addEventListener('DOMContentLoaded', () => {
    // Initialize the map
    const map = L.map('map').setView([37.9838, 23.7275], 7); // Centered on Greece

    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Example toll station markers
    const tollStations = [
        { name: 'Toll Station 1', coords: [37.9838, 23.7275], info: 'Αθήνα - Σταθμός 1' },
        { name: 'Toll Station 2', coords: [38.291, 21.7886], info: 'Πάτρα - Σταθμός 2' },
        { name: 'Toll Station 3', coords: [40.6401, 22.9444], info: 'Θεσσαλονίκη - Σταθμός 3' }
    ];

    // Add markers to the map
    tollStations.forEach(station => {
        const marker = L.marker(station.coords)
            .addTo(map)
            .bindPopup(station.info);
        
        marker.on('click', () => {
            document.getElementById('station-info').innerText = station.info;
            document.getElementById('info-panel').classList.add('visible');
        });
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

