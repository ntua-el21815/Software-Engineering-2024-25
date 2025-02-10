document.addEventListener('DOMContentLoaded', () => {
    const homeLink = document.getElementById('home-link');
    homeLink.addEventListener('click', (e) => {
        e.preventDefault();
        window.location.href = 'dashboard'; // Κατευθύνει στη σελίδα Dashboard
    });
    function logout() {
        window.location.href = '/logout';
    }
    
});
