// Responsive Navbar Animations:
    const hamburger = document.getElementById('hamburger-btn');
    const menu = document.getElementById('mobile-menu');
    const overlay = document.getElementById('menu-overlay');
    const body = document.body;

    hamburger.addEventListener('click', (e) => {
        e.stopPropagation();
        toggleMenu();
    });

    // Smooth toggle function
    const toggleMenu = () => {
    menu.classList.toggle('active');
    overlay.classList.toggle('active');
    hamburger.classList.toggle('active');
    body.classList.toggle('no-scroll');

    // Prevent focus trapping when menu is closed
    if (!menu.classList.contains('active')) {
        hamburger.focus();
    }

    overlay.addEventListener('click', toggleMenu);

    // Close menu when pressing Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && menu.classList.contains('active')) {
            toggleMenu();
        }
    });

    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
        if (menu.classList.contains('active') && 
            !e.target.closest('.navbar-menu') && 
            !e.target.closest('.hamburger')) {
            toggleMenu();
        }
    });
    };
