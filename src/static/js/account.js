document.addEventListener('DOMContentLoaded', function () {
    const switchCards = document.querySelectorAll('.switch-card');
    const top3Card = document.querySelector('.top3-card');

    function updateSwitchStatus(card) {
        const input = card.querySelector('input[type="checkbox"]');
        const switchLabel = input?.parentElement;

        if (!input || !switchLabel) return;

        const existingStatus = card.querySelector('.status-text');
        if (!existingStatus) {
            const statusLabel = document.createElement('span');
            statusLabel.className = 'status-text';
            statusLabel.textContent = input.checked ? 'Shown' : 'Hidden';
            switchLabel.after(statusLabel);
        }

        input.addEventListener('change', () => {
            const status = card.querySelector('.status-text');
            if (status) status.textContent = input.checked ? 'Shown' : 'Hidden';
        });
    }

    switchCards.forEach(updateSwitchStatus);

    function bindTabClicks() {
        document.querySelectorAll('.top3-tab').forEach(button => {
            button.addEventListener('click', () => {
                document.querySelectorAll('.top3-tab').forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
            });
        });
    }

    bindTabClicks();

    // Admin/Player Layout Switch
    const dropdown = document.querySelector('.player-dropdown select');
    const switchGroup = document.querySelector('.switch-group');

    dropdown.addEventListener('change', () => {
        if (dropdown.value === 'Admin') {
            // 清空除了 top3-card 以外的所有 switch-card
            const cards = Array.from(switchGroup.querySelectorAll('.switch-card'));
            cards.forEach(card => {
                if (!card.classList.contains('top3-card')) {
                    card.remove();
                }
            });

            // 重设 top3-card 为 admin 模式
            top3Card.innerHTML = `
                <div class="top3-row">
                  <span class="medium4">Recent Tournaments</span>
                  <label class="switch">
                    <input type="checkbox" checked>
                    <span class="slider"></span>
                  </label>
                  <span class="status-text">Shown</span>
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

            updateSwitchStatus(top3Card);
            bindTabClicks();
        } else {
            location.reload(); // 简单恢复为原始 player 模式
        }
    });
});
