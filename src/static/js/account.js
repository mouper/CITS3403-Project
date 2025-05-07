document.addEventListener('DOMContentLoaded', () => {
    const switchGroup = document.querySelector('.switch-group');
    const top3Card = document.querySelector('.top3-card');
    const dropdown = document.querySelector('.player-dropdown select');

    // label 显示名 => data-section 映射
    const sectionMap = {
        'Win Rate': 'winrate',
        'Total Wins/Total Played': 'totalcount',
        'Last 3 Tournaments': 'last3',
        'Top 3 Tournaments': 'top3',
        'Recent Tournaments': 'top3',
        'Recent Tournaments Hosted': 'hosted'
    };

    function setupSwitch(card) {
        const checkbox = card.querySelector('input[type="checkbox"]');
        const slider = card.querySelector('.slider');
        if (!checkbox || !slider) return;

        const labelText = card.querySelector('.medium4')?.textContent?.trim();
        const sectionName = sectionMap[labelText];

        let status = card.querySelector('.status-text');
        if (!status) {
            status = document.createElement('span');
            status.className = 'status-text';
            slider.insertAdjacentElement('afterend', status);
        }

        function toggleSection() {
            status.textContent = checkbox.checked ? 'Shown' : 'Hidden';
            if (sectionName) {
                document.querySelectorAll(`[data-section="${sectionName}"]`).forEach(elem => {
                    elem.style.display = checkbox.checked ? 'block' : 'none';
                });
            }
        }

        checkbox.addEventListener('change', toggleSection);
        toggleSection(); // 初始状态执行一次
    }

    // Setup all switch cards
    document.querySelectorAll('.switch-card').forEach(setupSwitch);

    // Setup tab switching for top3 tabs
    function bindTabClicks(container = document) {
        container.querySelectorAll('.top3-tab').forEach(button => {
            button.addEventListener('click', () => {
                container.querySelectorAll('.top3-tab').forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');

                const selectedType = button.textContent.includes('Win Rate') ? 'winrate' : 'wins';
                const selectedGame = document.getElementById('gameTypeSelect')?.value;

                document.querySelectorAll('.top3-section').forEach(section => {
                    const matchesType = section.dataset.type === selectedType;
                    const matchesGame = section.dataset.gameType === selectedGame;
                    section.style.display = (matchesType && matchesGame) ? 'block' : 'none';
                });
            });
        });
    }
    bindTabClicks();

    // Toggle between Player and Admin view
    dropdown.addEventListener('change', () => {
        const isAdmin = dropdown.value === 'Admin';

        // 隐藏除 top3 外所有 switch 卡片
        document.querySelectorAll('.switch-card:not(.top3-card)').forEach(card => {
            card.style.display = isAdmin ? 'none' : 'flex';
        });

        if (isAdmin) {
            // 设置 admin 的卡片内容
            top3Card.innerHTML = `
                <div class="top3-row">
                  <span class="medium4">Recent Tournaments Hosted</span>
                  <label class="switch">
                    <input type="checkbox" checked>
                    <span class="slider"></span>
                  </label>
                </div>
            `;
            setupSwitch(top3Card);

            // 显示 Admin 专属板块，隐藏 Player 模式的显示内容
            document.querySelector('.hosted-preview-section')?.style?.setProperty('display', 'block');
            document.querySelector('[data-section="last3"]')?.style?.setProperty('display', 'none');
            document.querySelector('[data-section="top3"]')?.style?.setProperty('display', 'none');
        } else {
            location.reload(); // 切回 Player 模式时直接刷新还原
        }
    });

    // Game type selection handler
    const gameTypeSelect = document.getElementById('gameTypeSelect');
    const top3Sections = document.querySelectorAll('.top3-section');

    if (gameTypeSelect) {
        function updateVisibleGameType(selectedType) {
            const activeTab = document.querySelector('.top3-tab.active');
            const selectedTypeTab = activeTab?.textContent.includes('Win Rate') ? 'winrate' : 'wins';

            document.querySelectorAll('.top3-section').forEach(section => {
                const matchesType = section.dataset.type === selectedTypeTab;
                const matchesGame = section.dataset.gameType === selectedType;
                section.style.display = (matchesType && matchesGame) ? 'block' : 'none';
            });
        }

        updateVisibleGameType(gameTypeSelect.value);

        gameTypeSelect.addEventListener('change', () => {
            updateVisibleGameType(gameTypeSelect.value);
        });
    }

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

    // 默认激活第一个 tab（最高胜场）
    const defaultTab = document.querySelector('.top3-tab:first-child');
    if (defaultTab) defaultTab.click();
});


