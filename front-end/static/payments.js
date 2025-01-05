document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('payments-form');
    const totalElement = document.getElementById('total');
    const checkboxes = form.querySelectorAll('input[type="checkbox"]');
    const amounts = [100, 200, 300]; // Example amounts for each company

    // Update the total when checkboxes are clicked
    checkboxes.forEach((checkbox, index) => {
        checkbox.addEventListener('change', () => {
            let total = 0;
            checkboxes.forEach((cb, i) => {
                if (cb.checked) {
                    total += amounts[i];
                }
            });
            totalElement.textContent = `€${total}`;
        });
    });

    // Handle form submission
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        alert('Πληρωμή ολοκληρώθηκε!');
    });
});
