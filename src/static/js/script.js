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

    // Analytics Toggle:
    document.addEventListener("DOMContentLoaded", () => {
        const viewSelector = document.getElementById('viewSelector');
        const playerView = document.getElementById('playerView');
        const adminView = document.getElementById('adminView');
    
        if (viewSelector && playerView && adminView) {
            viewSelector.addEventListener('change', function () {
                if (this.value === 'player') {
                    playerView.style.display = 'block';
                    adminView.style.display = 'none';
                } else {
                    playerView.style.display = 'none';
                    adminView.style.display = 'block';
                }
            });
        }
    });
    
    const gameTypeSelectorContainer = document.getElementById('gameTypeSelectorContainer');

    if (viewSelector) {
    viewSelector.addEventListener('change', function () {
        const isPlayer = this.value === 'player';
        playerView.style.display = isPlayer ? 'block' : 'none';
        adminView.style.display = isPlayer ? 'none' : 'block';
        gameTypeSelectorContainer.style.display = 'block'; // Show in both views
        // If you only want it in player view:
        // gameTypeSelectorContainer.style.display = isPlayer ? 'block' : 'none';
    });
    }
