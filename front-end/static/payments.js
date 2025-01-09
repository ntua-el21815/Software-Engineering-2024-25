document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('payments-form');
    const totalElement = document.getElementById('total');
    const checkboxes = form.querySelectorAll('input[type="checkbox"]');

    // Update the total when checkboxes are clicked
    checkboxes.forEach((checkbox) => {
        checkbox.addEventListener('change', () => {
            let total = 0;
            checkboxes.forEach((cb) => {
                if (cb.checked) {
                    const amount = parseFloat(cb.closest('tr').querySelector('td:nth-child(2)').textContent.replace('€', ''));
                    total += amount;
                }
            });
            totalElement.textContent = `€${total.toFixed(2)}`;
        });
    });

    // Handle form submission
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        alert('Πληρωμή ολοκληρώθηκε!');
    });
});
