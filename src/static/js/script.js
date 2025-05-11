// script.js

// =============================================
// TOURNAMENT FORM FUNCTIONALITY
// =============================================

function initTournamentForm() {
  // DOM Elements
  const competitorCountSelect = document.getElementById('competitorCount');
  const playersContainer = document.getElementById('playersContainer');
  const playerTabs = document.getElementById('playerTabs');
  const playerContent = document.getElementById('playerContent');
  const discardTournamentBtn = document.getElementById('discardTournament');
  const saveTournamentBtn = document.getElementById('saveTournament');
  const isCompetitorCheckbox = document.getElementById('isCompetitor');
  
  // Check if we're on the tournament form page
  if (!competitorCountSelect) return;

  // Current user info (passed from Flask via window object)
  const currentUser = {
    id: window.currentUserId || "",
    firstName: window.currentUserFirstName || "",
    lastName: window.currentUserLastName || "",
    email: window.currentUserEmail || "",
    username: window.currentUserFirstName || "" // Fallback to firstName if username not available
  };

  // Event Listeners
  competitorCountSelect.addEventListener('change', handleCompetitorCountChange);
  discardTournamentBtn.addEventListener('click', handleDiscardTournament);
  isCompetitorCheckbox.addEventListener('change', handleIsCompetitorChange);
  saveTournamentBtn.addEventListener('click', handleSaveTournament);

  // Functions
  function handleCompetitorCountChange() {
    const count = parseInt(competitorCountSelect.value);
    
    // Clear existing players
    playerTabs.innerHTML = '';
    playerContent.innerHTML = '';
    
    if (!isNaN(count)) {
      // Show player container
      playersContainer.style.display = 'block';
      
      // Generate player tabs and content
      for (let i = 1; i <= count; i++) {
        createPlayerTab(i);
        createPlayerSection(i);
      }
      
      // Check if user is competitor and update accordingly
      if (isCompetitorCheckbox.checked) {
        updatePlayerOneAsMyself();
      }
      
      // Activate first player by default
      activatePlayer(1);
    } else {
      // Hide player container if custom or no selection
      playersContainer.style.display = 'none';
    }
  }

  function createPlayerTab(playerId) {
    const tab = document.createElement('div');
    tab.className = 'player-tab';
    tab.dataset.player = playerId;
    
    const label = document.createElement('span');
    
    // Change label for player 1 if user is competitor
    if (playerId === 1 && isCompetitorCheckbox.checked) {
      label.textContent = 'Player 1 (Myself)';
    } else {
      label.textContent = `Player ${playerId}`;
    }
    
    const chevron = document.createElement('div');
    chevron.className = 'DropdownIcon';
    
    tab.appendChild(label);
    tab.appendChild(chevron);
    playerTabs.appendChild(tab);
    
    tab.addEventListener('click', () => activatePlayer(playerId));
  }

  function createPlayerSection(playerId) {
    const section = document.createElement('div');
    section.className = 'player-section';
    section.dataset.player = playerId;
    
    // Header with details title and discard button
    const header = document.createElement('div');
    header.className = 'player-details-header';
    
    const title = document.createElement('h3');
    
    // Change title for player 1 if user is competitor
    if (playerId === 1 && isCompetitorCheckbox.checked) {
      title.textContent = 'Player 1 (Myself) Details:';
    } else {
      title.textContent = `Player ${playerId} Details:`;
    }
    
    title.style.margin = '0';
    
    const discardBtn = document.createElement('button');
    discardBtn.className = 'player-discard';
    discardBtn.innerHTML = '<span class="DiscardIcon"></span> Discard';
    
    header.appendChild(title);
    header.appendChild(discardBtn);
    
    // TourneyPro Account Question
    const radioGroup = document.createElement('div');
    radioGroup.className = 'RadioSelection';
    
    const radioQuestion = document.createElement('p');
    radioQuestion.textContent = 'Does this competitor have a TourneyPro account?';
    
    const radioOptions = document.createElement('div');
    radioOptions.className = 'RadioSelection-group';
    
    // Yes Option
    const yesLabel = document.createElement('label');
    yesLabel.className = 'radio-option';
    
    const yesInput = document.createElement('input');
    yesInput.type = 'radio';
    yesInput.name = `tourneyPro${playerId}`;
    yesInput.value = 'yes';
    yesInput.className = 'radio-input';
    yesInput.id = `tourneyProYes${playerId}`;
    
    const yesCustom = document.createElement('div');
    yesCustom.className = 'radio-custom';
    
    const yesIcon = document.createElement('div');
    yesIcon.className = 'radio-icon';
    
    const yesUnselected = document.createElement('div');
    yesUnselected.className = 'unselected-icon RadialIcon';
    
    const yesSelected = document.createElement('div');
    yesSelected.className = 'selected-icon RadialSelectedIcon';
    
    const yesText = document.createElement('span');
    yesText.className = 'radio-label';
    yesText.textContent = 'Yes';
    
    yesIcon.appendChild(yesUnselected);
    yesIcon.appendChild(yesSelected);
    yesCustom.appendChild(yesIcon);
    yesCustom.appendChild(yesText);
    
    yesLabel.appendChild(yesInput);
    yesLabel.appendChild(yesCustom);
    
    // No Option
    const noLabel = document.createElement('label');
    noLabel.className = 'radio-option';
    
    const noInput = document.createElement('input');
    noInput.type = 'radio';
    noInput.name = `tourneyPro${playerId}`;
    noInput.value = 'no';
    noInput.className = 'radio-input';
    noInput.id = `tourneyProNo${playerId}`;
    
    const noCustom = document.createElement('div');
    noCustom.className = 'radio-custom';
    
    const noIcon = document.createElement('div');
    noIcon.className = 'radio-icon';
    
    const noUnselected = document.createElement('div');
    noUnselected.className = 'unselected-icon RadialIcon';
    
    const noSelected = document.createElement('div');
    noSelected.className = 'selected-icon RadialSelectedIcon';
    
    const noText = document.createElement('span');
    noText.className = 'radio-label';
    noText.textContent = 'No';
    
    noIcon.appendChild(noUnselected);
    noIcon.appendChild(noSelected);
    noCustom.appendChild(noIcon);
    noCustom.appendChild(noText);
    
    noLabel.appendChild(noInput);
    noLabel.appendChild(noCustom);
    
    radioOptions.appendChild(yesLabel);
    radioOptions.appendChild(noLabel);
    
    radioGroup.appendChild(radioQuestion);
    radioGroup.appendChild(radioOptions);
    
    // Create the username field (initially hidden)
    const usernameGroup = document.createElement('div');
    usernameGroup.className = 'TextForm';
    usernameGroup.style.display = 'none';
    usernameGroup.id = `usernameGroup${playerId}`;
    
    const usernameInput = document.createElement('input');
    usernameInput.type = 'text';
    usernameInput.placeholder = 'TourneyPro Username';
    usernameInput.id = `username${playerId}`;
    usernameGroup.appendChild(usernameInput);
    
    // Form Grid for name fields (initially hidden)
    const formGrid = document.createElement('div');
    formGrid.className = 'player-form-grid';
    formGrid.style.display = 'none';
    formGrid.id = `formGrid${playerId}`;
    
    // First Name Field
    const firstNameGroup = document.createElement('div');
    firstNameGroup.className = 'TextForm';
    const firstNameInput = document.createElement('input');
    firstNameInput.type = 'text';
    firstNameInput.placeholder = 'First Name';
    firstNameInput.id = `firstName${playerId}`;
    firstNameGroup.appendChild(firstNameInput);
    
    // Last Name Field
    const lastNameGroup = document.createElement('div');
    lastNameGroup.className = 'TextForm';
    const lastNameInput = document.createElement('input');
    lastNameInput.type = 'text';
    lastNameInput.placeholder = 'Last Name';
    lastNameInput.id = `lastName${playerId}`;
    lastNameGroup.appendChild(lastNameInput);
    
    // Email Field
    const emailGroup = document.createElement('div');
    emailGroup.className = 'TextForm';
    emailGroup.style.gridColumn = '1 / span 2';
    const emailInput = document.createElement('input');
    emailInput.type = 'email';
    emailInput.placeholder = 'Email Address';
    emailInput.id = `email${playerId}`;
    emailGroup.appendChild(emailInput);
    
    formGrid.appendChild(firstNameGroup);
    formGrid.appendChild(lastNameGroup);
    formGrid.appendChild(emailGroup);
    
    // Add event listeners to radio buttons
    yesInput.addEventListener('change', function() {
      if (this.checked) {
        usernameGroup.style.display = 'block';
        formGrid.style.display = 'none';
      }
    });
    
    noInput.addEventListener('change', function() {
      if (this.checked) {
        usernameGroup.style.display = 'none';
        formGrid.style.display = 'grid';
      }
    });
    
    // Assemble the section
    section.appendChild(header);
    section.appendChild(radioGroup);
    section.appendChild(usernameGroup);
    section.appendChild(formGrid);
    
    playerContent.appendChild(section);
    
    // Setup discard button functionality
    discardBtn.addEventListener('click', () => {
      document.getElementById(`username${playerId}`).value = '';
      document.getElementById(`firstName${playerId}`).value = '';
      document.getElementById(`lastName${playerId}`).value = '';
      document.getElementById(`email${playerId}`).value = '';
      const radioInputs = section.querySelectorAll('input[type="radio"]');
      radioInputs.forEach(input => input.checked = false);
      
      // Reset display
      document.getElementById(`usernameGroup${playerId}`).style.display = 'none';
      document.getElementById(`formGrid${playerId}`).style.display = 'none';
    });
  }

  function activatePlayer(playerId) {
    // Deactivate all tabs
    const allTabs = playerTabs.querySelectorAll('.player-tab');
    allTabs.forEach(tab => {
      tab.classList.remove('active');
      const tabIcon = tab.querySelector('.DropdownIcon');
      if (tabIcon) tabIcon.classList.remove('DropdownIcon-open');
    });
    
    // Hide all sections
    const allSections = playerContent.querySelectorAll('.player-section');
    allSections.forEach(section => section.classList.remove('is-visible'));
    
    // Activate selected tab and section
    const selectedTab = playerTabs.querySelector(`.player-tab[data-player="${playerId}"]`);
    const selectedSection = playerContent.querySelector(`.player-section[data-player="${playerId}"]`);
    
    if (selectedTab && selectedSection) {
      selectedTab.classList.add('active');
      selectedSection.classList.add('is-visible');
      
      // Update dropdown icon
      const selectedIcon = selectedTab.querySelector('.DropdownIcon');
      if (selectedIcon) selectedIcon.classList.add('DropdownIcon-open');
    }
  }

  function handleDiscardTournament() {
    // Reset all form inputs
    document.querySelectorAll('input[type="text"]').forEach(input => input.value = '');
    document.querySelectorAll('input[type="email"]').forEach(input => input.value = '');
    document.querySelectorAll('select').forEach(select => select.selectedIndex = 0);
    document.getElementById('isCompetitor').checked = false;
    
    // Hide player container
    playersContainer.style.display = 'none';
    
    // Clear player tabs and content
    playerTabs.innerHTML = '';
    playerContent.innerHTML = '';
  }

  function handleIsCompetitorChange() {
    // If competitor count is already selected, update player 1
    const count = parseInt(competitorCountSelect.value);
    if (!isNaN(count) && count > 0) {
      if (isCompetitorCheckbox.checked) {
        updatePlayerOneAsMyself();
      } else {
        resetPlayerOneToDefault();
      }
    }
  }

  function updatePlayerOneAsMyself() {
    // Update the tab label
    const playerOneTab = playerTabs.querySelector('.player-tab[data-player="1"]');
    if (playerOneTab) {
      const label = playerOneTab.querySelector('span:not(.DropdownIcon)');
      if (label) {
        label.textContent = 'Player 1 (Myself)';
      }
    }
    
    // Update the section title
    const playerOneSection = playerContent.querySelector('.player-section[data-player="1"]');
    if (playerOneSection) {
      const title = playerOneSection.querySelector('h3');
      if (title) {
        title.textContent = 'Player 1 (Myself) Details:';
      }
      
      // Set TourneyPro account to Yes
      const tourneyProYes = document.getElementById('tourneyProYes1');
      if (tourneyProYes) {
        tourneyProYes.checked = true;
        // Trigger the change event
        tourneyProYes.dispatchEvent(new Event('change'));
      }
      
      // Auto-fill username with currentUser.username
      const usernameInput = document.getElementById('username1');
      if (usernameInput) {
        usernameInput.value = currentUser.username || currentUser.firstName;
      }
    }
  }

  function resetPlayerOneToDefault() {
    // Reset the tab label
    const playerOneTab = playerTabs.querySelector('.player-tab[data-player="1"]');
    if (playerOneTab) {
      const label = playerOneTab.querySelector('span:not(.DropdownIcon)');
      if (label) {
        label.textContent = 'Player 1';
      }
    }
    
    // Reset the section title
    const playerOneSection = playerContent.querySelector('.player-section[data-player="1"]');
    if (playerOneSection) {
      const title = playerOneSection.querySelector('h3');
      if (title) {
        title.textContent = 'Player 1 Details:';
      }
      
      // Clear the fields
      const usernameInput = document.getElementById('username1');
      const firstName = document.getElementById('firstName1');
      const lastName = document.getElementById('lastName1');
      const email = document.getElementById('email1');
      
      if (usernameInput) usernameInput.value = '';
      if (firstName) firstName.value = '';
      if (lastName) lastName.value = '';
      if (email) email.value = '';
      
      // Reset radio buttons
      const tourneyProYes = document.getElementById('tourneyProYes1');
      const tourneyProNo = document.getElementById('tourneyProNo1');
      if (tourneyProYes) tourneyProYes.checked = false;
      if (tourneyProNo) tourneyProNo.checked = false;
      
      // Hide both form sections
      document.getElementById('usernameGroup1').style.display = 'none';
      document.getElementById('formGrid1').style.display = 'none';
    }
  }

  function handleSaveTournament() {
    // Collect tournament data
    const tournamentData = {
      title: document.getElementById('tournamentName').value,
      format: document.getElementById('tournamentType').value,
      game_type: document.getElementById('gameType').value,
      include_creator_as_player: isCompetitorCheckbox.checked,
      is_draft: true,  // Always save as draft initially
      created_by: currentUser.id,
      players: []
    };
    
    // Validate core tournament data
    if (!tournamentData.title || tournamentData.title.trim() === '') {
      alert('Please enter a tournament name');
      return;
    }
    
    if (!tournamentData.format || tournamentData.format === '') {
      alert('Please select a tournament type');
      return;
    }
    
    // Get number of players
    const playerCount = parseInt(competitorCountSelect.value);
    if (isNaN(playerCount) || playerCount < 2) {
      alert('Please select a valid number of competitors');
      return;
    }
    
    // Collect player data
    let validPlayers = true;
    for (let i = 1; i <= playerCount; i++) {
      const hasTourneyProAccount = document.getElementById(`tourneyProYes${i}`).checked;
      const needsGuestInfo = document.getElementById(`tourneyProNo${i}`).checked;
      
      let playerData = {
        is_confirmed: false
      };
      
      // If TourneyPro account
      if (hasTourneyProAccount) {
        const username = document.getElementById(`username${i}`).value;
        
        if (!username || username.trim() === '') {
          alert(`Please enter TourneyPro username for Player ${i}`);
          validPlayers = false;
          break;
        }
        
        playerData.username = username;
        
        // For player 1 when it's the current user
        if (i === 1 && isCompetitorCheckbox.checked) {
          playerData.user_id = currentUser.id;
          playerData.is_confirmed = true; // Auto-confirm the tournament creator
          playerData.guest_name = `${currentUser.firstName} ${currentUser.lastName}`.trim();
          playerData.email = currentUser.email;
        } else {
          // User will be matched by username in the backend
          playerData.guest_name = username; // Use username as guest name until matched
        }
      } 
      // If guest entry
      else if (needsGuestInfo) {
        const firstName = document.getElementById(`firstName${i}`).value;
        const lastName = document.getElementById(`lastName${i}`).value;
        const email = document.getElementById(`email${i}`).value;
        
        // Check if required fields are filled
        if (!firstName || firstName.trim() === '' || !lastName || lastName.trim() === '') {
          alert(`Please enter first and last name for Player ${i}`);
          validPlayers = false;
          break;
        }
        
        playerData.guest_name = `${firstName} ${lastName}`.trim();
        playerData.email = email;
      }
      // If neither radio button is selected
      else {
        alert(`Please specify if Player ${i} has a TourneyPro account`);
        validPlayers = false;
        break;
      }
      
      tournamentData.players.push(playerData);
    }
    
    if (!validPlayers) {
      return;  // Stop if player validation failed
    }
    
    // Send data to server
    fetch('/save_tournament', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(tournamentData),
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      if (data.success) {
        alert('Tournament saved successfully!');
        window.location.href = '/dashboard';  // Redirect to dashboard
      } else {
        alert('Error: ' + data.message);
      }
    })
    .catch(error => {
      console.error('Error:', error);
      alert('Failed to save tournament. Please try again.');
    });
  }
}

// =============================================
// NAVBAR FUNCTIONALITY
// =============================================

function initNavbar() {
  const hamburger = document.getElementById('hamburger-btn');
  const menu = document.getElementById('mobile-menu');
  const overlay = document.getElementById('menu-overlay');
  const body = document.body;

  if (!hamburger) return;

  hamburger.addEventListener('click', (e) => {
    e.stopPropagation();
    toggleMenu();
  });

  const toggleMenu = () => {
    menu.classList.toggle('active');
    overlay.classList.toggle('active');
    hamburger.classList.toggle('active');
    body.classList.toggle('no-scroll');

    // Prevent focus trapping when menu is closed
    if (!menu.classList.contains('active')) {
      hamburger.focus();
    }
  };

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
}

// =============================================
// ANALYTICS FUNCTIONALITY
// =============================================

function initAnalytics() {
  const viewSelector      = document.getElementById('viewSelector');
  const playerView        = document.getElementById('playerView');
  const adminView         = document.getElementById('adminView');
  const gameTypeSelector  = document.getElementById('gameTypeSelector');
  const limitSelector     = document.getElementById('adminLimitSelector');

  if (!viewSelector) return;

  // Game-type filtering + pie-chart rendering
  if (gameTypeSelector) {
    gameTypeSelector.addEventListener('change', () => {
      const selected = gameTypeSelector.value;
      document.querySelectorAll('.game-stat').forEach(section => {
        if (section.dataset.game === selected) {
          section.style.display = 'block';
          const canvas = section.querySelector('canvas');
          if (canvas && !canvas.dataset.rendered) {
            const wins   = +section.querySelector('.total-stat:nth-child(1) .title2').textContent;
            const games  = +section.querySelector('.total-stat:nth-child(2) .title2').textContent;
            renderPieChart(canvas.id, wins, games - wins);
            canvas.dataset.rendered = 'true';
          }
        } else {
          section.style.display = 'none';
        }
      });

      // Page reload to apply game type filter
      const params = new URLSearchParams(window.location.search);
      params.set('game_type', gameTypeSelector.value);
      window.location.search = params.toString();
    });

    gameTypeSelector.dispatchEvent(new Event('change'));
  }

  // Player/Admin toggle
  viewSelector.addEventListener('change', () => {
    const isPlayer = viewSelector.value === 'player';
    playerView.style.display = isPlayer ? 'block' : 'none';
    adminView .style.display = isPlayer ? 'none'  : 'block';
    if (gameTypeSelector)
      gameTypeSelector.style.display = isPlayer ? 'block' : 'none';
  });

  viewSelector.dispatchEvent(new Event('change'));

  // Admin Statcards modal handling
  document.querySelectorAll('#adminStatcards .view-tourney').forEach(link => {
    link.addEventListener('click', e => {
      e.preventDefault();
      const id      = link.dataset.tourneyId;
      const tourney = window.recentTournaments.find(t => t.id == id);
      if (!tourney) return;

      document.getElementById('modalTitle').textContent = tourney.title;
      const info  = document.querySelectorAll('.modal-info .info-item .regular4');
      info[0].textContent = tourney.format;
      info[1].textContent = tourney.game_type;
      info[2].textContent = tourney.round_time_minutes + ' Minutes';
      document.querySelector('.modal-date .regular4').textContent = tourney.date;

      const tbody = document.querySelector('.table-wrapper tbody');
      tbody.innerHTML = '';
      tourney.standings.forEach((p, i) => {
        tbody.insertAdjacentHTML('beforeend', `
          <tr>
            <td>${i + 1}</td>
            <td>${p.username}</td>
            <td>${p.wins}/${p.losses}</td>
            <td>${p.owp}%</td>
            <td>${p.opp_owp}%</td>
          </tr>
        `);
      });

      document.getElementById('modalBackdrop').style.display = 'block';
    });
  });

  // Admin Limit Selector
  if (limitSelector) {
    limitSelector.addEventListener('change', function () {
      const params = new URLSearchParams(window.location.search);
      params.set('limit', this.value);
      params.set('view', viewSelector.value); // preserve current tab
      window.location.search = params.toString();
    });
  }
}

// =============================================
// CHART FUNCTIONS
// =============================================

function renderPieChart(canvasId, wins, losses) {
  const ctx = document.getElementById(canvasId).getContext('2d');

  new Chart(ctx, {
    type: 'pie',
    data: {
      labels: ['Wins', 'Losses'],
      datasets: [
        {
          data: [wins, losses],
          backgroundColor: ['#BBB2FF', '#D6D6EE'],
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

function closeModal() {
  const modalBackdrop = document.getElementById('modalBackdrop');
  if (modalBackdrop) {
    modalBackdrop.style.display = 'none';
  }
}

// =============================================
// MAIN INITIALIZATION
// =============================================

document.addEventListener('DOMContentLoaded', function() {
  // Initialize all components
  initNavbar();
  initTournamentForm();
  initAnalytics();

  // Initialize any charts on page load
  const winRateChart = document.getElementById('winRateChart');
  if (winRateChart) {
    renderPieChart('winRateChart', 40, 73);
  }

  // Add event listeners to statcard captions
  document.querySelectorAll('.statcard .caption').forEach(link => {
    link.addEventListener('click', function(event) {
      event.preventDefault();
      document.getElementById('modalBackdrop').style.display = 'block';
    });
  });

  // Add event listener to close button if you prefer to use event listeners instead of inline onclick
  const closeButton = document.querySelector('.close-button');
  if (closeButton) {
    closeButton.addEventListener('click', closeModal);
  }
  const params    = new URLSearchParams(window.location.search);
  const viewParam = params.get('view');
  const limParam  = params.get('limit');
  if (viewParam) {
    const vs = document.getElementById('viewSelector');
    vs.value = viewParam;
    vs.dispatchEvent(new Event('change'));
  }
  if (limParam) {
    const ls = document.getElementById('adminLimitSelector');
    if (ls) ls.value = limParam;
  }
  
  // finally, show the right panel
  viewSelector.dispatchEvent(new Event('change'));
  requestAnimationFrame(() => {
    initAnalytics();
  });
});