function initAdminHostedFilters() {
  const countButtons = document.querySelectorAll('.show-count-btn');
  const gameSelect = document.getElementById('adminGameFilter');
  let showCount = 3;

  function updateAdminVisibleCards() {
    const selectedGame = gameSelect?.value || 'all';
    document.querySelectorAll('.hosted-group').forEach(group => {
      const matchesGame = selectedGame === 'all' || group.dataset.game === selectedGame;
      group.style.display = matchesGame ? 'block' : 'none';

      if (matchesGame) {
        const cards = group.querySelectorAll('.hosted-card');
        cards.forEach((card, idx) => {
          card.style.display = idx < showCount ? 'block' : 'none';
        });
      }
    });
  }

  countButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      showCount = parseInt(btn.dataset.count);
      countButtons.forEach(b => b.classList.remove('selected'));
      btn.classList.add('selected');
      updateAdminVisibleCards();
    });
  });

  if (gameSelect) {
    gameSelect.addEventListener('change', updateAdminVisibleCards);
  }

  updateAdminVisibleCards();
}

function injectAdminControls(settingsPanel, switchGroup) {
  const adminControls = document.createElement('div');
  adminControls.className = 'admin-controls';
  adminControls.innerHTML = `
    <div class="toggle-count">
      <button class="show-count-btn selected" data-count="3">Show 3</button>
      <button class="show-count-btn" data-count="5">Show 5</button>
      <button class="show-count-btn" data-count="10">Show 10</button>
    </div>
    <div class="game-dropdown">
      <select id="adminGameFilter">
        <option value="all">All Games</option>
        ${(window.hostedGameTypes || []).map(g => `<option value="${g}">${g}</option>`).join('')}
      </select>
    </div>
  `;
  settingsPanel.insertBefore(adminControls, switchGroup);
}

document.addEventListener('DOMContentLoaded', () => {
  const switchGroup = document.querySelector('.switch-group');
  const top3Card = document.querySelector('.top3-card');
  const dropdown = document.querySelector('.player-dropdown select');
  const settingsPanel = document.querySelector('.settings-panel');

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
    toggleSection();
  }

  document.querySelectorAll('.switch-card').forEach(setupSwitch);

  function bindTabClicks(container = document) {
    container.querySelectorAll('.top3-tab').forEach(button => {
      button.addEventListener('click', () => {
        container.querySelectorAll('.top3-tab').forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');

        const selectedType = button.textContent.includes('Win Rate') ? 'winrate' :
                             button.textContent.includes('Leaderboard') ? 'rank' : 'wins';
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

  if (!window.hostedGameTypes) window.hostedGameTypes = [];

  dropdown.addEventListener('change', () => {
    const isAdmin = dropdown.value === 'Admin';

    document.querySelector('.admin-controls')?.remove();
    document.querySelectorAll('.switch-card:not(.top3-card)').forEach(card => {
      card.style.display = isAdmin ? 'none' : 'flex';
    });

    if (isAdmin) {
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

      injectAdminControls(settingsPanel, switchGroup);
      initAdminHostedFilters();

      document.querySelector('.hosted-preview-section')?.style?.setProperty('display', 'block');
      document.querySelector('[data-section="last3"]')?.style?.setProperty('display', 'none');
      document.querySelector('[data-section="top3"]')?.style?.setProperty('display', 'none');
    } else {
      location.reload();
    }
  });

  const gameTypeSelect = document.getElementById('gameTypeSelect');
  if (gameTypeSelect) {
    function updateVisibleGameType(selectedType) {
      const activeTab = document.querySelector('.top3-tab.active');
      const selectedTypeTab = activeTab?.textContent.includes('Win Rate') ? 'winrate' :
                              activeTab?.textContent.includes('Leaderboard') ? 'rank' : 'wins';

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

  const defaultTab = document.querySelector('.top3-tab:first-child');
  if (defaultTab) defaultTab.click();
});

document.addEventListener('DOMContentLoaded', () => {
  const avatarInput = document.getElementById('avatarUpload');
  const avatarPreview = document.getElementById('avatarPreview');

  if (avatarInput && avatarPreview) {
    avatarInput.addEventListener('change', function () {
      const file = this.files[0];
      if (file && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = function (e) {
          avatarPreview.src = e.target.result;
        };
        reader.readAsDataURL(file);
      }
    });
  }
});

function enableAndSubmit(inputId, buttonEl) {
  const input = document.getElementById(inputId);
  if (input) {
    input.removeAttribute('readonly');
    input.focus();
    input.addEventListener('blur', () => {
      buttonEl.closest('form').submit();
    }, { once: true });
  }
}

