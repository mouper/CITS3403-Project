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

          const gameTypeSelector = document.getElementById("gameTypeSelector");

          if (gameTypeSelector) {
              gameTypeSelector.addEventListener("change", () => {
                  const selectedGame = gameTypeSelector.value;
                  const statSections = document.querySelectorAll(".game-stat");
      
                  statSections.forEach((section) => {
                      if (section.dataset.game === selectedGame) {
                          section.style.display = "block";
                          const canvas = section.querySelector("canvas");
                          if (canvas && !canvas.dataset.rendered) {
                              const wins = parseInt(section.querySelector(".total-stat:nth-child(1) .title2").textContent);
                              const games = parseInt(section.querySelector(".total-stat:nth-child(2) .title2").textContent);
                              const losses = games - wins;
                              renderPieChart(canvas.id, wins, losses);
                              canvas.dataset.rendered = true;
                          }
                      } else {
                          section.style.display = "none";
                      }
                  });
              });
      
              // Run filter once on page load to show default
              gameTypeSelector.dispatchEvent(new Event("change"));
          }
      
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
    
    // Game type selector
    const gameTypeSelectorContainer = document.getElementById('gameTypeSelectorContainer');

    if (viewSelector) {
    viewSelector.addEventListener('change', function () {
        const isPlayer = this.value === 'player';
        playerView.style.display = isPlayer ? 'block' : 'none';
        adminView.style.display = isPlayer ? 'none' : 'block';
        gameTypeSelectorContainer.style.display = 'block';
    });
    }

    // Pie Chart
    window.addEventListener("DOMContentLoaded", () => {
      const canvas = document.getElementById("winRateChart");
      if (canvas) {
        const ctx = canvas.getContext("2d");

        new Chart(ctx, {
          type: "pie",
          data: {
            labels: ["Wins", "Losses"],
            datasets: [
              {
                data: [40, 73],
                backgroundColor: ["#BBB2FF", "#D6D6EE"],
                borderWidth: 2,
                borderColor: '#121212',
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
              legend: {
                display: false,
              },
            },
          },
        });
      }
    });

    function renderPieChart(canvasId, wins, losses) {
      const ctx = document.getElementById(canvasId).getContext("2d");
  
      new Chart(ctx, {
        type: "pie",
        data: {
          labels: ["Wins", "Losses"],
          datasets: [
            {
              data: [wins, losses],
              backgroundColor: ["#BBB2FF", "#D6D6EE"],
              borderWidth: 2,
              borderColor: '#121212',
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          plugins: {
            legend: {
              display: false,
            },
          },
        },
      });
    } 
  

      