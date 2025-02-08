document.addEventListener('DOMContentLoaded', () => {
    // Initialize the map
    const map = L.map('map').setView([37.9838, 23.7275], 7); // Centered on Greece

    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Example toll station markers (samples)
    const tollStations = [
        { id: 1, name: 'Toll Station 1', coords: [37.9838, 23.7275], info: 'Αθήνα - Σταθμός 1' },
        { id: 2, name: 'Toll Station 2', coords: [38.291, 21.7886], info: 'Πάτρα - Σταθμός 2' },
        { id: 3, name: 'Toll Station 3', coords: [40.6401, 22.9444], info: 'Θεσσαλονίκη - Σταθμός 3' }
    ];

    // Add markers to the map
    tollStations.forEach(station => {
        const marker = L.marker(station.coords)
            .addTo(map)
            .bindPopup(station.info); // Προαιρετικό popup
    
        marker.on('click', async () => {
            console.log(`Clicked on station: ${station.name}`); // Debugging
            // Προσπάθεια για φόρτωση δεδομένων σταθμού
            displayStationDetails({
                name: station.name,
                company: 'Sample Company', // Sample data
                stats: [
                    { companyName: 'Company A', passCount: 50, revenue: 200.5 },
                    { companyName: 'Company B', passCount: 75, revenue: 300.0 }
                ]
            });
        });
    });
    

    // Close info panel
    const closePanelButton = document.getElementById('close-panel');
    closePanelButton.addEventListener('click', () => {
        document.getElementById('info-panel').classList.remove('visible');
    });

    // Function to display station details in the info panel
    function displayStationDetails(details) {
        const infoPanel = document.getElementById('info-panel');
        const stationInfo = document.getElementById('station-info');
        const tableBody = document.getElementById('station-stats-body');

        // Update station information
        stationInfo.innerHTML = `
            <p>Όνομα: ${details.name}</p>
            <p>Εταιρεία: ${details.company}</p>
        `;

        // Clear existing table rows
        tableBody.innerHTML = '';

        // Populate the table with stats
        details.stats.forEach(stat => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${stat.companyName}</td>
                <td>${stat.passCount}</td>
                <td>${stat.revenue}</td>
            `;
            tableBody.appendChild(row);
        });

        // Show the info panel
        infoPanel.classList.add('visible');
    }
});

