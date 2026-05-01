document.addEventListener('DOMContentLoaded', () => {
    const navLinks = document.getElementById('nav-links');
    const accessToken = localStorage.getItem('access_token');

    if (accessToken) {
        navLinks.innerHTML = `
            <li class="nav-item">
                <a class="nav-link" href="/">Collections</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="/files/">Files</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="#" id="logout-link">Logout</a>
            </li>
        `;

        // Handle logout
        document.getElementById('logout-link').addEventListener('click', (e) => {
            e.preventDefault();
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login';
        });
    } else {
        navLinks.innerHTML = `
            <li class="nav-item">
                <a class="nav-link" href="/login">Login</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="/register">Register</a>
            </li>
        `;
    }
});
