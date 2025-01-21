
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('payments-form');
    const totalElement = document.getElementById('total');
    const checkboxes = form.querySelectorAll('input[type="checkbox"]');

    // Clear the total and all checkboxes when the page loads
    totalElement.textContent = '€0.00';
    checkboxes.forEach((checkbox) => {
        checkbox.checked = false;
    });
    
    // Update the total when checkboxes are clicked
    checkboxes.forEach((checkbox) => {
        checkbox.addEventListener('change', () => {
            let total = 0;
            checkboxes.forEach((cb) => {
                if (cb.checked) {
                    const debtAmount = parseFloat(cb.closest('tr').querySelector('td:nth-child(2)').textContent.replace('€', ''));
                    total += debtAmount;
                }
            });
            totalElement.textContent = `€${total.toFixed(2)}`;
        });
    });

    // Handle form submission
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const selectedOperators = [];
        checkboxes.forEach((cb) => {
            if (cb.checked) {
                const operator = cb.closest('tr').querySelector('td:first-child').textContent;
                selectedOperators.push(operator);
            }
        });

        fetch('/make_payment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                operators: selectedOperators
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            const timezoneOffset = new Date().getTimezoneOffset() * 60000;
            const localISOTime = new Date(Date.now() - timezoneOffset).toISOString().slice(0, 19).replace('T', '_').replace(/[:]/g, '-');
            a.download = `payment_summary_${localISOTime}.csv`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
        alert('Πληρωμή ολοκληρώθηκε!');
    });
});
