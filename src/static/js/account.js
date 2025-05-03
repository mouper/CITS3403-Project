document.addEventListener('DOMContentLoaded', () => {
    const switchGroup = document.querySelector('.switch-group');
    const top3Card = document.querySelector('.top3-card');
    const dropdown = document.querySelector('.player-dropdown select');

    // Add toggle status text and bind listener
    function setupSwitch(card) {
        const checkbox = card.querySelector('input[type="checkbox"]');
        const slider = card.querySelector('.slider');
        if (!checkbox || !slider) return;

        let status = card.querySelector('.status-text');
        if (!status) {
            status = document.createElement('span');
            status.className = 'status-text';
            slider.insertAdjacentElement('afterend', status);
        }
        status.textContent = checkbox.checked ? 'Shown' : 'Hidden';

        checkbox.addEventListener('change', () => {
            status.textContent = checkbox.checked ? 'Shown' : 'Hidden';
        });
    }

    // Setup all switch cards
    document.querySelectorAll('.switch-card').forEach(setupSwitch);

    // Setup tab switching for top3 tabs
    function bindTabClicks(container = document) {
        container.querySelectorAll('.top3-tab').forEach(button => {
            button.addEventListener('click', () => {
                container.querySelectorAll('.top3-tab').forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
            });
        });
    }
    bindTabClicks();

    // Toggle between Player and Admin view
    dropdown.addEventListener('change', () => {
        if (dropdown.value === 'Admin') {
            // Remove all switch-cards except top3
            switchGroup.querySelectorAll('.switch-card:not(.top3-card)').forEach(card => card.remove());

            top3Card.innerHTML = `
                <div class="top3-row">
                  <span class="medium4">Recent Tournaments</span>
                  <label class="switch">
                    <input type="checkbox" checked>
                    <span class="slider"></span>
                  </label>
                </div>

                <div class="top3-tab-group">
                  <button class="top3-tab">Show All</button>
                  <button class="top3-tab">Show 3</button>
                  <button class="top3-tab">Show 5</button>
                  <button class="top3-tab">Show 10</button>
                </div>

                <div class="top3-subline">
                  <span class="caption">Select Game Displayed</span>
                  <span class="medium4">All Games &nbsp; <i class="fas fa-chevron-right"></i></span>
                </div>
            `;
            setupSwitch(top3Card);
            bindTabClicks(top3Card);
        } else {
            location.reload(); // revert to player view
        }
    });

    // Editable email field
    const emailInput = document.getElementById('emailInput');
    const emailEditBtn = document.getElementById('emailEditBtn');

    if (emailInput && emailEditBtn) {
        if (!emailInput.value.trim()) {
            emailInput.value = "username@email.com";
        }

        emailEditBtn.addEventListener('click', () => {
            emailInput.removeAttribute('readonly');
            emailInput.focus();
        });
    }
});
