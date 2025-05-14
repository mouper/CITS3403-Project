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

    if (isAdmin) {
      fetch('/account/save_display_settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          show_win_rate: false,
          show_total_wins_played: false,
          show_last_three: false,
          show_best_three: false,
          show_admin: true
        })
      }).then(res => res.json()).then(data => {
        if (!data.success) {
          alert('Failed to set admin display settings.');
        }
      }).catch(err => {
        console.error('Error saving admin view settings:', err);
      });

      // 清空除 hosted 以外显示内容
      document.querySelectorAll('[data-section]').forEach(el => {
        el.style.display = 'none';
      });

      document.querySelector('[data-section="hosted"]')?.style?.setProperty('display', 'block');

      // 修改 top3Card 只显示标题，不再放置 admincards 内容
      top3Card.innerHTML = `
        <div class="top3-row">
          <span class="medium4">Recent Tournaments Hosted</span>
          <label class="switch">
            <input type="checkbox" class="admin-toggle" checked>
            <span class="slider"></span>
          </label>
        </div>
      `;
      setupSwitch(top3Card);

      document.querySelector('.admin-controls')?.remove();
      injectAdminControls(settingsPanel, switchGroup);
      initAdminHostedFilters();

    } else {
      // ✅ 切换为 Player 模式时，先保存状态
      fetch('/account/save_display_settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            show_win_rate: true,            // 默认 Player 显示什么你自己定
            show_total_wins_played: false,
            show_last_three: true,
            show_best_three: true,
            show_admin: false
        })
      }).then(res => res.json()).then(data => {
        if (data.success) {
            location.reload();  // ✅ 状态存好了再刷新
        } else {
            alert('Failed to switch to Player view.');
        }
      }).catch(err => {
        console.error('Error switching to Player view:', err);
      });
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

  const saveStatsBtn = document.getElementById('save-stats-btn');
  if (saveStatsBtn) {
    saveStatsBtn.addEventListener('click', () => {
      let show_win_rate = document.querySelector('.switch-card:nth-child(1) input')?.checked || false;
      let show_total_wins_played = document.querySelector('.switch-card:nth-child(2) input')?.checked || false;
      let show_last_three = document.querySelector('.switch-card:nth-child(3) input')?.checked || false;
      let show_best_three = document.querySelector('.top3-card input[type="checkbox"]')?.checked || false;
      let show_admin = document.querySelector('.admin-toggle')?.checked || false;

      // ✅ 互斥逻辑：如果 Admin 开启，则禁用其他选项
      if (show_admin) {
        show_win_rate = false;
        show_total_wins_played = false;
        show_last_three = false;
        show_best_three = false;
      }

      // ✅ 互斥逻辑：如果其他任何一个打开，则强制关闭 Admin
      if (show_win_rate || show_total_wins_played || show_last_three || show_best_three) {
        show_admin = false;
      }

      const data = {
        show_win_rate,
        show_total_wins_played,
        show_last_three,
        show_best_three,
        show_admin
      };

      // 仅在 Player 模式下添加 sorting 和 game_type
      if (!show_admin) {
        const selectedGameType = document.getElementById('gameTypeSelect')?.value || null;
        const selectedTab = document.querySelector('.top3-tab.active')?.textContent || '';
        const preferredSorting = selectedTab.includes('Win Rate') ? 'winrate' : 'wins';

        data.preferred_game_type = selectedGameType;
        data.preferred_top3_sorting = preferredSorting;
      }

      fetch('/account/save_display_settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
        .then(res => res.json())
        .then(response => {
          if (response.success) {
            alert('Settings saved!');
          } else {
            alert('Failed to save settings.');
          }
        })
        .catch(err => {
          console.error(err);
          alert('Error saving settings.');
        });
    });
  }

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

  const isAdminFlag = document.getElementById('isAdminFlag')?.value === 'true';
  if (isAdminFlag) {
    dropdown.value = 'Admin';
    dropdown.dispatchEvent(new Event('change'));
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
