document.addEventListener('DOMContentLoaded', () => {
    const filterForm = document.getElementById('filter-form');
    const resultsTable = document.getElementById('results-table');

    // Example data for demonstration purposes
    const sampleData = {
        passes: [
            { category: 'Station A', details: '100 Passes', amount: '€50' },
            { category: 'Station B', details: '200 Passes', amount: '€100' },
        ],
        revenues: [
            { category: 'Station A', details: 'Revenue from passes', amount: '€500' },
            { category: 'Station B', details: 'Revenue from passes', amount: '€1000' },
        ],
        debt: [
            { category: 'Company A', details: 'Outstanding debt', amount: '€150' },
            { category: 'Company B', details: 'Outstanding debt', amount: '€250' },
        ],
    };

    // Populate table based on filters
    filterForm.addEventListener('submit', (e) => {
        e.preventDefault();

        const dataType = document.getElementById('data-type').value;
        const startDate = document.getElementById('start-date').value;
        const endDate = document.getElementById('end-date').value;

        // Clear the table
        resultsTable.innerHTML = '';

        // Validate dates
        if (!startDate || !endDate || startDate > endDate) {
            alert('Please select a valid date range.');
            return;
        }

        // Populate the table with filtered data
        const data = sampleData[dataType];
        data.forEach((row) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${row.category}</td>
                <td>${row.details}</td>
                <td>${row.amount}</td>
            `;
            resultsTable.appendChild(tr);
        });
    });
});
