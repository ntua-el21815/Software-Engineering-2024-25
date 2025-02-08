document.addEventListener('DOMContentLoaded', () => {
    const map = L.map('map').setView([37.9838, 23.7275], 7); // Centered on Greece

    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Add markers from backend response
    function addMarkers(stations) {
        stations.forEach(station => {
            const marker = L.marker(station.coords).addTo(map).bindPopup(station.info);
            marker.on('click', () => {
                document.getElementById('station-info').innerText = station.info;
                document.getElementById('info-panel').classList.add('visible');
            });
        });
    }

    // Fetch my stations
    document.getElementById('view-my-stations').addEventListener('click', () => {
        fetch('/my-stations')
            .then(response => {
                if (!response.ok) throw new Error('Failed to fetch my stations');
                return response.json();
            })
            .then(data => addMarkers(data))
            .catch(error => console.error('Error:', error));
    });

    // Fetch other companies' stations
    document.getElementById('view-other-companies').addEventListener('click', () => {
        fetch('/other-stations')
            .then(response => {
                if (!response.ok) throw new Error('Failed to fetch other stations');
                return response.json();
            })
            .then(data => addMarkers(data))
            .catch(error => console.error('Error:', error));
    });

    // Close the info panel
    document.getElementById('close-panel').addEventListener('click', () => {
        document.getElementById('info-panel').classList.remove('visible');
    });
});

