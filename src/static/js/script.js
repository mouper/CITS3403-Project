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
  const startTournamentBtn = document.getElementById('startTournament');
  
  let confirmDetailsTab = null;
  let confirmDetailsSection = null;
  let allPlayersFilledOut = false;
  
  // Check if we're on the tournament form page
  if (!competitorCountSelect) return;

  // Current user info (passed from Flask via window object)
  const currentUser = {
    id: window.currentUserId || "",
    firstName: window.currentUserFirstName || "",
    lastName: window.currentUserLastName || "",
    email: window.currentUserEmail || "",
    username: window.currentUserUsername || "" 
  };

  // Initialize tournament data if available
  const tournamentDataElement = document.getElementById('tournamentData');
  if (tournamentDataElement) {
    window.existingTournament = JSON.parse(tournamentDataElement.dataset.tournament);
    
    // Trigger competitor count change to create player sections
    competitorCountSelect.value = window.existingTournament.num_players;
    handleCompetitorCountChange();
    
    // Wait for player sections to be created
    setTimeout(() => {
      // Populate player data
      window.existingTournament.players.forEach((player, index) => {
        const playerId = index + 1;
        
        // Set TourneyPro account radio
        if (player.has_tourney_pro_account) {
          document.getElementById(`tourneyProYes${playerId}`).checked = true;
          document.getElementById(`usernameGroup${playerId}`).style.display = 'block';
          document.getElementById(`formGrid${playerId}`).style.display = 'none';
          
          // Set username
          if (player.username) {
            document.getElementById(`username${playerId}`).value = player.username;
          }
        } else {
          document.getElementById(`tourneyProNo${playerId}`).checked = true;
          document.getElementById(`usernameGroup${playerId}`).style.display = 'none';
          document.getElementById(`formGrid${playerId}`).style.display = 'block';
          
          // Set guest info
          document.getElementById(`firstName${playerId}`).value = player.guest_firstname || '';
          document.getElementById(`lastName${playerId}`).value = player.guest_lastname || '';
          document.getElementById(`email${playerId}`).value = player.email || '';
        }
      });
      
      // Check if all players are filled out
      checkAndCreateConfirmDetailsTab();
    }, 100);
  }

  // Error message container
  const errorContainer = document.createElement('div');
  errorContainer.className = 'error-container mt-2';
  playersContainer.parentNode.insertBefore(errorContainer, playersContainer.nextSibling);

  // Show error message function
  function showError(message) {
    errorContainer.innerHTML = message;
    errorContainer.style.display = 'block';
    
    // Scroll to error
    errorContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  // Clear error message function
  function clearError() {
    errorContainer.innerHTML = '';
    errorContainer.style.display = 'none';
  }

  // Event Listeners
  competitorCountSelect.addEventListener('change', handleCompetitorCountChange);
  discardTournamentBtn.addEventListener('click', handleDiscardTournament);
  isCompetitorCheckbox.addEventListener('change', handleIsCompetitorChange);
  saveTournamentBtn.addEventListener('click', handleSaveTournament);

  // Add event listener for the Start Tournament button
  if (startTournamentBtn) {
    startTournamentBtn.addEventListener('click', handleStartTournament);
  }

  // Fix the global event listeners function to ensure form updates
  function addGlobalChangeListeners() {
    // This will check if we can show the Confirm Details tab whenever any input changes
    document.querySelectorAll('input, select').forEach(element => {
      element.addEventListener('change', function() {
        const playerCount = parseInt(competitorCountSelect.value);
        if (!isNaN(playerCount) && playerCount > 0) {
          checkAndCreateConfirmDetailsTab();
        }
      });
    });
  }

  // Functions

  // Call this when creating player sections
  function addFormListeners() {
    addEmailValidationListeners();
    addGlobalChangeListeners();
  }

    // Ensure email fields get validation on change
    function addEmailValidationListeners() {
      // Find all email inputs
      const emailInputs = document.querySelectorAll('input[type="email"]');
      
      emailInputs.forEach(emailInput => {
        const playerId = emailInput.id.replace('email', '');
        const emailError = document.getElementById(`emailError${playerId}`);
        
        emailInput.addEventListener('blur', function() {
          const email = this.value.trim();
          if (email !== '') {
            const errorMsg = validate_email_address(email);
            if (errorMsg && emailError) {
              emailError.textContent = errorMsg;
              emailError.style.display = 'block';
            } else if (emailError) {
              emailError.style.display = 'none';
            }
          } else if (emailError) {
            emailError.style.display = 'none';
          }
        });
      });
    }

  function validate_email_address(email) {
    // Enhanced Basic Format Check with no spaces allowed
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return "Invalid email format.";
    }
    return null; // No error
  }

  function handleCompetitorCountChange() {
    // Clear any previous errors
    clearError();
    
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

    // Check if we should show the Confirm Details tab
    checkAndCreateConfirmDetailsTab();
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
    
    // Hide discard button for player 1 when user is a competitor
    if (playerId === 1 && isCompetitorCheckbox.checked) {
      discardBtn.style.display = 'none';
    }
    
    header.appendChild(title);
    header.appendChild(discardBtn);
    
    // Player section container - used for disabling fields when player 1 is current user
    const playerSectionContent = document.createElement('div');
    playerSectionContent.className = 'player-section-content';
    
    // Apply disabled styling if player 1 is current user
    if (playerId === 1 && isCompetitorCheckbox.checked) {
      playerSectionContent.classList.add('disabled-player-section');
    }
    
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
    
    // Disable for player 1 when user is competitor
    if (playerId === 1 && isCompetitorCheckbox.checked) {
      yesInput.disabled = true;
    }
    
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
    
    // Disable for player 1 when user is competitor
    if (playerId === 1 && isCompetitorCheckbox.checked) {
      noInput.disabled = true;
    }
    
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
    
    // Disable for player 1 when user is competitor
    if (playerId === 1 && isCompetitorCheckbox.checked) {
      usernameInput.disabled = true;
    }
    
    // Username error message
    const usernameError = document.createElement('div');
    usernameError.className = 'field-error regular4 display-none';
    usernameError.id = `usernameError${playerId}`;
    
    usernameGroup.appendChild(usernameInput);
    usernameGroup.appendChild(usernameError);
    
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
    
    // Disable for player 1 when user is competitor
    if (playerId === 1 && isCompetitorCheckbox.checked) {
      firstNameInput.disabled = true;
    }
    
    firstNameGroup.appendChild(firstNameInput);
    
    // Last Name Field
    const lastNameGroup = document.createElement('div');
    lastNameGroup.className = 'TextForm';
    const lastNameInput = document.createElement('input');
    lastNameInput.type = 'text';
    lastNameInput.placeholder = 'Last Name';
    lastNameInput.id = `lastName${playerId}`;
    
    // Disable for player 1 when user is competitor
    if (playerId === 1 && isCompetitorCheckbox.checked) {
      lastNameInput.disabled = true;
    }
    
    lastNameGroup.appendChild(lastNameInput);
    
    // Email Field
    const emailGroup = document.createElement('div');
    emailGroup.className = 'TextForm';
    emailGroup.style.gridColumn = '1 / span 2';
    const emailInput = document.createElement('input');
    emailInput.type = 'email';
    emailInput.placeholder = 'Email Address';
    emailInput.id = `email${playerId}`;
    
    // Disable for player 1 when user is competitor
    if (playerId === 1 && isCompetitorCheckbox.checked) {
      emailInput.disabled = true;
    }
    
    // Email error message
    const emailError = document.createElement('div');
    emailError.className = 'field-error regular4 display-none';
    emailError.id = `emailError${playerId}`;
    
    emailGroup.appendChild(emailInput);
    emailGroup.appendChild(emailError);
    
    formGrid.appendChild(firstNameGroup);
    formGrid.appendChild(lastNameGroup);
    formGrid.appendChild(emailGroup);
    
    // Clear error messages when changing radio selection
    function clearFieldErrors() {
      const usernameErrorEl = document.getElementById(`usernameError${playerId}`);
      const emailErrorEl = document.getElementById(`emailError${playerId}`);
      
      if (usernameErrorEl) usernameErrorEl.style.display = 'none';
      if (emailErrorEl) emailErrorEl.style.display = 'none';
    }
    
    // Add event listeners to radio buttons
    yesInput.addEventListener('change', function() {
      if (this.checked) {
        clearFieldErrors();
        usernameGroup.style.display = 'block';
        formGrid.style.display = 'none';
      }
    });
    
    noInput.addEventListener('change', function() {
      if (this.checked) {
        clearFieldErrors();
        usernameGroup.style.display = 'none';
        formGrid.style.display = 'grid';
      }
    });
    
    // Add all elements to playerSectionContent
    playerSectionContent.appendChild(radioGroup);
    playerSectionContent.appendChild(usernameGroup);
    playerSectionContent.appendChild(formGrid);
    
    // Assemble the section
    section.appendChild(header);
    section.appendChild(playerSectionContent);
    
    playerContent.appendChild(section);
    
    // Setup discard button functionality
    discardBtn.addEventListener('click', () => {
      if (playerId === 1 && isCompetitorCheckbox.checked) {
        // Don't allow discarding player 1 when user is competitor
        return;
      }
      
      document.getElementById(`username${playerId}`).value = '';
      document.getElementById(`firstName${playerId}`).value = '';
      document.getElementById(`lastName${playerId}`).value = '';
      document.getElementById(`email${playerId}`).value = '';
      
      // Clear any field errors
      clearFieldErrors();
      
      const radioInputs = section.querySelectorAll('input[type="radio"]');
      radioInputs.forEach(input => input.checked = false);
      
      // Reset display
      document.getElementById(`usernameGroup${playerId}`).style.display = 'none';
      document.getElementById(`formGrid${playerId}`).style.display = 'none';
    });

    addFormListeners();
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

  function checkAllPlayersFilledOut(playerCount) {
    let allFilled = true;
    
    for (let i = 1; i <= playerCount; i++) {
      const hasTourneyProAccount = document.getElementById(`tourneyProYes${i}`).checked;
      const needsGuestInfo = document.getElementById(`tourneyProNo${i}`).checked;
      
      // Check if player type has been selected
      if (!hasTourneyProAccount && !needsGuestInfo) {
        allFilled = false;
        break;
      }
      
      // Check required fields based on account type
      if (hasTourneyProAccount) {
        const username = document.getElementById(`username${i}`).value;
        if (!username || username.trim() === '') {
          allFilled = false;
          break;
        }
      } else if (needsGuestInfo) {
        const firstName = document.getElementById(`firstName${i}`).value;
        const lastName = document.getElementById(`lastName${i}`).value;
        const email = document.getElementById(`email${i}`).value;
        
        if (!firstName || firstName.trim() === '' || !lastName || lastName.trim() === '') {
          allFilled = false;
          break;
        }
        
        // Email validation (optional field)
        if (email && email.trim() !== '') {
          const emailError = validate_email_address(email);
          if (emailError) {
            allFilled = false;
            break;
          }
        }
      }
    }
    
    return allFilled;
  }

  // Add this function to create the Confirm Details tab and section
  function createConfirmDetailsTab(playerCount) {
    // Create confirm details tab
    confirmDetailsTab = document.createElement('div');
    confirmDetailsTab.className = 'player-tab';
    confirmDetailsTab.dataset.player = 'confirm';
    
    const label = document.createElement('span');
    label.textContent = 'Details Summary';
    
    confirmDetailsTab.appendChild(label);
    playerTabs.appendChild(confirmDetailsTab);
    
    // Create confirm details section
    confirmDetailsSection = document.createElement('div');
    confirmDetailsSection.className = 'player-section';
    confirmDetailsSection.dataset.player = 'confirm';
    
    // Add header
    const header = document.createElement('div');
    header.className = 'player-details-header medium3';
    
    const title = document.createElement('h3');
    title.textContent = 'Player Details Summary';
    title.style.margin = '0';
    
    header.appendChild(title);
    confirmDetailsSection.appendChild(header);
    
    // Create summary content
    const summaryContent = document.createElement('div');
    summaryContent.className = 'player-section-content summary-content';
    
    // Add summary for each player
    for (let i = 1; i <= playerCount; i++) {
      const playerRow = createPlayerSummaryRow(i);
      summaryContent.appendChild(playerRow);
    }
    
    confirmDetailsSection.appendChild(summaryContent);
    playerContent.appendChild(confirmDetailsSection);
    
    // Add event listener to tab
    confirmDetailsTab.addEventListener('click', () => activatePlayer('confirm'));
    
    // Show the Start Tournament button now that we can confirm details
    document.querySelector('.SendJoinBtn').classList.remove('hidden');
  }

  // Add this function to create a player summary row
  function createPlayerSummaryRow(playerId) {
    const row = document.createElement('div');
    row.className = 'player-summary-row';
    
    // Player number column
    const playerNumber = document.createElement('div');
    playerNumber.className = 'player-number medium4';
    
    // Check if player 1 is current user
    if (playerId === 1 && isCompetitorCheckbox.checked) {
      playerNumber.textContent = `Player ${playerId}:`;
      
      // Add (Myself) tag
      const myselfTag = document.createElement('span');
      myselfTag.textContent = " (Myself)";
      playerNumber.appendChild(myselfTag);
    } else {
      playerNumber.textContent = `Player ${playerId}:`;
    }
    
    // Player name column
    const playerName = document.createElement('div');
    playerName.className = 'player-name regular3';
    
    // Player username/account column
    const playerAccount = document.createElement('div');
    playerAccount.className = 'player-account regular3';
    
    // Edit button column
    
    const editButton = document.createElement('div');
    editButton.className = 'edit-button';
    
    const editIcon = document.createElement('div');
    editIcon.className = 'EditIcon';
    
    editButton.appendChild(editIcon);
    
    // Add event listener to edit button to navigate to the player's tab
    editButton.addEventListener('click', () => activatePlayer(playerId));
    
    // Assemble the row
    row.appendChild(playerNumber);
    row.appendChild(playerName);
    row.appendChild(playerAccount);
    row.appendChild(editButton);
    
    // Update function to populate player details
    function updatePlayerDetails() {
      // Clear previous content
      playerName.textContent = '';
      playerAccount.textContent = '';
      
      const hasTourneyProAccount = document.getElementById(`tourneyProYes${playerId}`).checked;
      const needsGuestInfo = document.getElementById(`tourneyProNo${playerId}`).checked;
      
      if (hasTourneyProAccount) {
        const username = document.getElementById(`username${playerId}`).value;
        
        // If player 1 is the current user
        if (playerId === 1 && isCompetitorCheckbox.checked) {
          playerName.textContent = `${currentUser.firstName} ${currentUser.lastName}`.trim();
        } else {
          playerName.textContent = "Name Hidden";
        }
        
        playerAccount.textContent = username;
      } 
      else if (needsGuestInfo) {
        const firstName = document.getElementById(`firstName${playerId}`).value;
        const lastName = document.getElementById(`lastName${playerId}`).value;
        const email = document.getElementById(`email${playerId}`).value;
        
        playerName.textContent = `${firstName} ${lastName}`.trim();
        playerAccount.textContent = email;
      }
      else {
        playerName.textContent = "Not configured";
        playerAccount.textContent = "N/A";
      }
    }
    
    // Initial update
    updatePlayerDetails();
    
    // Add event listeners to update the summary when player details change
    const inputIds = [
      `username${playerId}`, 
      `firstName${playerId}`, 
      `lastName${playerId}`, 
      `email${playerId}`,
      `tourneyProYes${playerId}`,
      `tourneyProNo${playerId}`
    ];
    
    inputIds.forEach(id => {
      const element = document.getElementById(id);
      if (element) {
        element.addEventListener('change', updatePlayerDetails);
        element.addEventListener('input', updatePlayerDetails);
      }
    });
    
    return row;
  }

  // Add this function to check if we should show the Confirm Details tab
  function checkAndCreateConfirmDetailsTab() {
    const playerCount = parseInt(competitorCountSelect.value);
    
    if (!isNaN(playerCount) && playerCount > 0) { 
      allPlayersFilledOut = checkAllPlayersFilledOut(playerCount);
      
      // If all players are filled out but confirm tab doesn't exist yet
      if (allPlayersFilledOut && !confirmDetailsTab) {
        createConfirmDetailsTab(playerCount);
        
        // Show the Start Tournament button when confirm tab is created
        const startTournamentBtnContainer = document.querySelector('.SendJoinBtn');
        if (startTournamentBtnContainer) {
          startTournamentBtnContainer.classList.remove('hidden');
        }
      }
      
      // If we already have a confirm tab, update the player details
      if (confirmDetailsTab && confirmDetailsSection) {
        // Clear existing summary content
        const summaryContent = confirmDetailsSection.querySelector('.summary-content');
        if (summaryContent) {
          summaryContent.innerHTML = '';
          
          // Recreate player summary rows
          for (let i = 1; i <= playerCount; i++) {
            const playerRow = createPlayerSummaryRow(i);
            summaryContent.appendChild(playerRow);
          }
        }
      }
    }
  }

  function handleDiscardTournament() {
    // Reset all form inputs
    document.querySelectorAll('input[type="text"]').forEach(input => input.value = '');
    document.querySelectorAll('input[type="email"]').forEach(input => input.value = '');
    document.querySelectorAll('select').forEach(select => select.selectedIndex = 0);
    document.getElementById('isCompetitor').checked = false;
    
    // Clear any errors
    clearError();
    document.querySelectorAll('.field-error').forEach(el => el.style.display = 'none');
    
    // Hide player container
    playersContainer.style.display = 'none';
    
    // Clear player tabs and content
    playerTabs.innerHTML = '';
    playerContent.innerHTML = '';
  }

  function handleIsCompetitorChange() {
    // Clear any errors
    clearError();
    
    // If competitor count is already selected, update player 1
    const count = parseInt(competitorCountSelect.value);
    if (!isNaN(count) && count > 0) {
      if (isCompetitorCheckbox.checked) {
        updatePlayerOneAsMyself();
      } else {
        resetPlayerOneToDefault();
      }
    }
    checkAndCreateConfirmDetailsTab();
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
      
      // Hide discard button
      const discardBtn = playerOneSection.querySelector('.player-discard');
      if (discardBtn) {
        discardBtn.style.display = 'none';
      }
      
      // Add disabled class to player section content
      const playerSectionContent = playerOneSection.querySelector('.player-section-content');
      if (playerSectionContent) {
        playerSectionContent.classList.add('disabled-player-section');
      }
      
      // Set TourneyPro account to Yes
      const tourneyProYes = document.getElementById('tourneyProYes1');
      if (tourneyProYes) {
        tourneyProYes.checked = true;
        tourneyProYes.disabled = true;
        // Trigger the change event
        tourneyProYes.dispatchEvent(new Event('change'));
      }
      
      // Disable the "No" option
      const tourneyProNo = document.getElementById('tourneyProNo1');
      if (tourneyProNo) {
        tourneyProNo.disabled = true;
      }
      
      // Auto-fill username with currentUser.username and disable field
      const usernameInput = document.getElementById('username1');
      if (usernameInput) {
        usernameInput.value = currentUser.username || currentUser.firstName;
        usernameInput.disabled = true;
      }
      
      // Disable other fields
      const firstName = document.getElementById('firstName1');
      const lastName = document.getElementById('lastName1');
      const email = document.getElementById('email1');
      
      if (firstName) firstName.disabled = true;
      if (lastName) lastName.disabled = true;
      if (email) email.disabled = true;
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
      
      // Show discard button
      const discardBtn = playerOneSection.querySelector('.player-discard');
      if (discardBtn) {
        discardBtn.style.display = 'block';
      }
      
      // Remove disabled class from player section content
      const playerSectionContent = playerOneSection.querySelector('.player-section-content');
      if (playerSectionContent) {
        playerSectionContent.classList.remove('disabled-player-section');
      }
      
      // Clear the fields
      const usernameInput = document.getElementById('username1');
      const firstName = document.getElementById('firstName1');
      const lastName = document.getElementById('lastName1');
      const email = document.getElementById('email1');
      
      if (usernameInput) {
        usernameInput.value = '';
        usernameInput.disabled = false;
      }
      
      if (firstName) {
        firstName.value = '';
        firstName.disabled = false;
      }
      
      if (lastName) {
        lastName.value = '';
        lastName.disabled = false;
      }
      
      if (email) {
        email.value = '';
        email.disabled = false;
      }
      
      // Reset and enable radio buttons
      const tourneyProYes = document.getElementById('tourneyProYes1');
      const tourneyProNo = document.getElementById('tourneyProNo1');
      if (tourneyProYes) {
        tourneyProYes.checked = false;
        tourneyProYes.disabled = false;
      }
      if (tourneyProNo) {
        tourneyProNo.checked = false;
        tourneyProNo.disabled = false;
      }
      
      // Hide both form sections
      document.getElementById('usernameGroup1').style.display = 'none';
      document.getElementById('formGrid1').style.display = 'none';
      
      // Clear any field errors
      const usernameError = document.getElementById('usernameError1');
      const emailError = document.getElementById('emailError1');
      if (usernameError) usernameError.style.display = 'none';
      if (emailError) emailError.style.display = 'none';
    }
  }

  // Extract common tournament data collection and validation into a separate function
  function collectAndValidateTournamentData() {
    // Collect tournament data
    const tournamentData = {
      title: document.getElementById('tournamentName').value,
      format: document.getElementById('tournamentType').value,
      game_type: document.getElementById('gameType').value,
      include_creator_as_player: isCompetitorCheckbox.checked,
      created_by: currentUser.id,
      round_time_minutes: parseInt(document.getElementById('roundTimeLimit').value)
    };

    // Validate core tournament data
    if (!tournamentData.title || tournamentData.title.trim() === '') {
      showError('Please enter a tournament name');
      return null;
    }

    if (!tournamentData.round_time_minutes || isNaN(tournamentData.round_time_minutes)) {
      showError('Please select a round time limit');
      return null;
    }
    
    if (!tournamentData.format || tournamentData.format === '') {
      showError('Please select a tournament type');
      return null;
    }

    if (!tournamentData.game_type || tournamentData.game_type === '') {
      showError('Please select a game type');
      return null;
    }
    
    // Get number of players
    const playerCount = parseInt(competitorCountSelect.value);
    if (isNaN(playerCount) || playerCount < 2) {
      showError('Please select a valid number of competitors');
      return null;
    }
    
    // Validate player data
    const playerData = validatePlayerData(playerCount);
    if (!playerData) {
      return null; // Validation failed, errors already shown
    }
    
    // Add validated player data to tournament data
    tournamentData.players = playerData;
    
    return tournamentData;
  }

  // Extract common error handling into a separate function
  function handleTournamentError(error, buttonElement, defaultButtonText, playerCount) {
    console.error('Error:', error);
    
    // Reset button state
    buttonElement.disabled = false;
    buttonElement.textContent = defaultButtonText;
    
    // Check if we have a response with data
    if (error.data) {
        // Handle invalid usernames
        if (error.data.invalid_usernames) {
            error.data.invalid_usernames.forEach(username => {
                // Find which player has this username
                for (let i = 1; i <= playerCount; i++) {
                    const playerUsername = document.getElementById(`username${i}`)?.value;
                    if (playerUsername === username) {
                        const usernameError = document.getElementById(`usernameError${i}`);
                        if (usernameError) {
                            usernameError.textContent = `User '${username}' does not exist`;
                            usernameError.style.display = 'block';
                            activatePlayer(i);
                        }
                        break;
                    }
                }
            });
            showError('One or more TourneyPro usernames are invalid. Please correct them and try again.');
        } 
        // Handle non-friend usernames
        else if (error.data.non_friend_usernames) {
            error.data.non_friend_usernames.forEach(username => {
                // Find which player has this username
                for (let i = 1; i <= playerCount; i++) {
                    const playerUsername = document.getElementById(`username${i}`)?.value;
                    if (playerUsername === username && playerUsername !== currentUser.username) {
                        const usernameError = document.getElementById(`usernameError${i}`);
                        if (usernameError) {
                            usernameError.textContent = `You must be friends with '${username}' to add them`;
                            usernameError.style.display = 'block';
                            activatePlayer(i);
                        }
                        break;
                    }
                }
            });
            showError('You must be friends with all users you add to your tournament. Please correct the entries and try again.');
        }
        // Handle emails with existing accounts
        else if (error.data.emails_with_accounts) {
            error.data.emails_with_accounts.forEach(email => {
                // Find which player has this email
                for (let i = 1; i <= playerCount; i++) {
                    const playerEmail = document.getElementById(`email${i}`)?.value;
                    if (playerEmail === email) {
                        const emailError = document.getElementById(`emailError${i}`);
                        if (emailError) {
                            emailError.textContent = `A TourneyPro Account exists for '${email}'`;
                            emailError.style.display = 'block';
                            activatePlayer(i);
                        }
                        break;
                    }
                }
            });
            showError('One or more emails are linked to existing accounts. Please correct them and try again.');
        }
        // Handle duplicate usernames/emails
        else if (error.data.duplicate_usernames || error.data.duplicate_emails) {
            let errorMsg = '';
            if (error.data.duplicate_usernames) {
                errorMsg += 'Duplicate usernames detected. ';
            }
            if (error.data.duplicate_emails) {
                errorMsg += 'Duplicate emails detected. ';
            }
            showError(errorMsg + 'Please correct them and try again.');
        }
        // Handle generic error messages
        else if (error.data.message) {
            showError(error.data.message);
        }
        // Handle detailed errors array if present
        else if (error.data.detailed_errors) {
            showError(error.data.detailed_errors.join('\n'));
        }
        else {
            showError('Failed to process tournament. Please try again.');
        }
    } 
    // Handle network errors or other exceptions
    else {
        showError('Failed to process tournament. Please try again.');
    }
  }
  // Modify validatePlayerData to include email validation
  function validatePlayerData(playerCount) {
    let validPlayers = true;
    let playerData = [];
    
    // Clear previous errors
    clearError();
    document.querySelectorAll('.field-error').forEach(el => el.style.display = 'none');
    
    // Arrays to track duplicate detection
    const usedUsernames = [];
    const usedEmails = [];
    
    for (let i = 1; i <= playerCount; i++) {
      const hasTourneyProAccount = document.getElementById(`tourneyProYes${i}`).checked;
      const needsGuestInfo = document.getElementById(`tourneyProNo${i}`).checked;
      
      let player = {
        is_confirmed: false,
        has_tourney_pro_account: hasTourneyProAccount
      };
      
      // If neither option is selected
      if (!hasTourneyProAccount && !needsGuestInfo) {
        showError(`Please specify if Player ${i} has a TourneyPro account`);
        validPlayers = false;
        break;
      }
      
      // If TourneyPro account
      if (hasTourneyProAccount) {
        const username = document.getElementById(`username${i}`).value;
        
        if (!username || username.trim() === '') {
          const usernameError = document.getElementById(`usernameError${i}`);
          if (usernameError) {
            usernameError.textContent = 'Please enter a TourneyPro username';
            usernameError.style.display = 'block';
          }
          validPlayers = false;
          continue;
        }
        
        // Check for duplicate username in the tournament
        if (usedUsernames.includes(username.toLowerCase())) {
          const usernameError = document.getElementById(`usernameError${i}`);
          if (usernameError) {
            usernameError.textContent = `Username '${username}' is already used in this tournament`;
            usernameError.style.display = 'block';
            activatePlayer(i);
          }
          validPlayers = false;
          continue;
        }
        usedUsernames.push(username.toLowerCase());
        
        player.username = username;
        
        // For player 1 when it's the current user
        if (i === 1 && isCompetitorCheckbox.checked) {
          player.user_id = currentUser.id;
          player.is_confirmed = true; // Auto-confirm the tournament creator
          player.guest_firstname = currentUser.firstName;
          player.guest_lastname = currentUser.lastName;
          player.email = currentUser.email;
          
          // Track the email for duplicate detection
          if (currentUser.email) {
            usedEmails.push(currentUser.email.toLowerCase());
          }
        } else {
          // User will be matched by username in the backend
          player.guest_firstname = ''; // Will be filled from user record
          player.guest_lastname = ''; // Will be filled from user record
        }
      } 
      // If guest entry
      else if (needsGuestInfo) {
        const firstName = document.getElementById(`firstName${i}`).value;
        const lastName = document.getElementById(`lastName${i}`).value;
        const email = document.getElementById(`email${i}`).value;
        
        // Check if required fields are filled
        if (!firstName || firstName.trim() === '') {
          showError(`Please enter first name for Player ${i}`);
          validPlayers = false;
          continue;
        }
        
        if (!lastName || lastName.trim() === '') {
          showError(`Please enter last name for Player ${i}`);
          validPlayers = false;
          continue;
        }
        
        if (email && email.trim() === '') {
          showError(`Please enter an email for Player ${i}`);
          validPlayers = false;
          continue;
        }

        // Validate email
        else {
          const emailError = validate_email_address(email);
          if (emailError) {
            const emailErrorEl = document.getElementById(`emailError${i}`);
            if (emailErrorEl) {
              emailErrorEl.textContent = emailError;
              emailErrorEl.style.display = 'block';
            }
            validPlayers = false;
            continue;
          }
          
          // Check for duplicate email in the tournament
          if (usedEmails.includes(email.toLowerCase())) {
            const emailErrorEl = document.getElementById(`emailError${i}`);
            if (emailErrorEl) {
              emailErrorEl.textContent = `Email '${email}' is already used in this tournament`;
              emailErrorEl.style.display = 'block';
              activatePlayer(i);
            }
            validPlayers = false;
            continue;
          }
          usedEmails.push(email.toLowerCase());
        }
        
        player.guest_firstname = firstName.trim();
        player.guest_lastname = lastName.trim();
        player.email = email;
      }
      
      playerData.push(player);
    }
    
    return validPlayers ? playerData : null;
  }

  // Replace handleSaveTournament with simplified version that uses common functions
  function handleSaveTournament() {
    const button = document.getElementById('saveTournament');
    const defaultButtonText = button.innerHTML;
    
    // Disable button and show saving state
    button.disabled = true;
    button.innerHTML = '<div class="SaveIcon"></div>Saving...';
    
    // Collect and validate tournament data
    const tournamentData = collectAndValidateTournamentData();
    if (!tournamentData) {
        button.disabled = false;
        button.innerHTML = defaultButtonText;
        return;
    }
    
    // Set tournament as draft
    tournamentData.is_draft = true;
    
    // Get tournament ID from URL if editing
    const urlParams = new URLSearchParams(window.location.search);
    const tournamentId = urlParams.get('tournament_id');
    if (tournamentId) {
        tournamentData.tournament_id = tournamentId;
    }
    
    // Send tournament data to server
    fetch('/save_tournament', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(tournamentData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Show success message
            const successMessage = document.createElement('div');
            successMessage.className = 'success-message';
            successMessage.textContent = 'Tournament draft saved successfully!';
            document.querySelector('.tournament-form-container').insertBefore(
                successMessage,
                document.querySelector('.action-buttons')
            );
            
            // Remove success message after 3 seconds
            setTimeout(() => {
                successMessage.remove();
            }, 3000);
            
            // Update URL with tournament ID without reloading
            const newUrl = `/new_tournament?tournament_id=${data.tournament_id}`;
            window.history.pushState({}, '', newUrl);
            
            // Re-enable button
            button.disabled = false;
            button.innerHTML = defaultButtonText;
        } else {
            handleTournamentError(data, button, defaultButtonText);
        }
    })
    .catch(error => {
        handleTournamentError(error, button, defaultButtonText);
    });
  }

  // Replace handleStartTournament with simplified version that uses common functions
  function handleStartTournament() {
    const tournamentData = collectAndValidateTournamentData();
    if (!tournamentData) {
      return; // Validation failed
    }
    
    // Set as not draft
    tournamentData.is_draft = false;
    
    // Show loading state
    startTournamentBtn.disabled = true;
    startTournamentBtn.textContent = 'Starting...';
    
    // Get tournament ID from URL if we're editing a draft
    const urlParams = new URLSearchParams(window.location.search);
    const tournamentId = urlParams.get('tournament_id');
    if (tournamentId) {
      tournamentData.tournament_id = tournamentId;
    }
    
    // Send data to server
    fetch('/start_tournament', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(tournamentData),
    })
    .then(response => {
      return response.json().then(data => {
        if (!response.ok) {
          throw {
            status: response.status,
            data: data
          };
        }
        return data;
      });
    })
    .then(data => {
      if (data.success) {
        // Redirect to the tournament view page
        window.location.href = `/tournament/${data.tournament_id}`;
      } else {
        showError('Error: ' + data.message);
      }
    })
    .catch(error => {
      handleTournamentError(error, startTournamentBtn, 'Start Tournament', parseInt(competitorCountSelect.value));
    });
  }
}

// =============================================
// TOURNAMENT MANAGEMENT FUNCTIONALITY
// =============================================
function initTournamentManager() {
  // Get tournament information
  const tournamentId = document.getElementById('tournamentId').value;
  const tournamentFormat = document.getElementById('tournamentFormat').value;
  const roundState = document.getElementById('roundState').value;
  const roundTimeMinutes = parseInt(document.getElementById('roundTime').value) || 50; // Default to 50 minutes if not set
  const viewState = document.getElementById('viewState').value; // Get the view state
  
  let timerInterval;
  let timeRemaining = roundTimeMinutes * 60; // Convert to seconds
  
  // Error message container setup
  let errorContainer;
  if (!document.querySelector('.error-container')) {
    errorContainer = document.createElement('div');
    errorContainer.className = 'error-container mt-2';
    errorContainer.style.display = 'none';
    
    // Insert after the pairings table
    const pairingsTableContainer = document.querySelector('.pairings-table-container');
    if (pairingsTableContainer) {
      pairingsTableContainer.parentNode.insertBefore(errorContainer, pairingsTableContainer.nextSibling);
    }
  } else {
    errorContainer = document.querySelector('.error-container');
  }

  // Show error message function
  function showError(message) {
    errorContainer.innerHTML = message;
    errorContainer.style.display = 'block';
    
    // Scroll to error
    errorContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  // Clear error message function
  function clearError() {
    errorContainer.innerHTML = '';
    errorContainer.style.display = 'none';
  }
  
  // Error handling function for tournament operations
  function handleTournamentError(error, buttonElement, defaultButtonText) {
    console.error('Error:', error);
    
    // Reset button state if provided
    if (buttonElement) {
      buttonElement.disabled = false;
      buttonElement.textContent = defaultButtonText;
    }
    
    // Handle different error responses
    if (error.json) {
      error.json().then(data => {
        if (data.message) {
          showError(data.message);
        } else if (data.detailed_errors && data.detailed_errors.length) {
          showError(data.detailed_errors.join('<br>'));
        } else {
          showError('An error occurred while processing your request. Please try again.');
        }
      }).catch(() => {
        showError('An error occurred while processing your request. Please try again.');
      });
    } else if (error.data) {
      if (error.data.message) {
        showError(error.data.message);
      } else if (error.data.detailed_errors && error.data.detailed_errors.length) {
        showError(error.data.detailed_errors.join('<br>'));
      } else {
        showError('Failed to process tournament operation. Please try again.');
      }
    } else {
      showError('An error occurred. Please try again.');
    }
  }
  
  // Initialize timer if round is in progress and not in confirm results view
  if (roundState === 'in progress' && viewState !== 'confirm_results') {
      startTimer();
  }

  // Handle tournament results viewing
  const viewResultsBtn = document.getElementById('viewResultsBtn');
  if (viewResultsBtn) {
      viewResultsBtn.addEventListener('click', () => {
          // Redirect to the tournament completed view since results are already saved
          window.location.href = `/tournament/${tournamentId}/completed`;
      });
  }
  
  // Handle automatic selection for bye matches
  document.querySelectorAll('.match-row').forEach(row => {
      if (row.dataset.isBye === 'true') {
          const radioButton = row.querySelector('input[value="player1"]');
          if (radioButton) {
              radioButton.checked = true;
              radioButton.disabled = true;
          }
      }
  });
  
  // Validation function to check if all winners are selected
  function validateAllSelectionsComplete() {
      clearError();
      
      const matchRows = document.querySelectorAll('.match-row');
      const incompleteMatches = [];
      
      matchRows.forEach(row => {
          const matchId = row.dataset.matchId;
          const isBye = row.dataset.isBye === 'true';
          
          // Skip validation for bye matches
          if (isBye) {
              return;
          }
          
          const player1Radio = row.querySelector(`input[name="winner${matchId}"][value="player1"]`);
          const player2Radio = row.querySelector(`input[name="winner${matchId}"][value="player2"]`);
          
          // Check if a winner has been selected
          if ((!player1Radio || !player1Radio.checked) && (!player2Radio || !player2Radio.checked)) {
              // Get table number
              const tableCell = row.querySelector('td:first-child');
              const tableNumber = tableCell ? tableCell.textContent.trim() : matchId;
              incompleteMatches.push(tableNumber);
          }
      });
      
      if (incompleteMatches.length > 0) {
          showError(`Please select winners for all matches before proceeding. Missing selections for table(s): ${incompleteMatches.join(', ')}`);
          return false;
      }
      
      return true;
  }
  
  // Timer functions
  function startTimer() {
      updateTimerDisplay();
      timerInterval = setInterval(() => {
          timeRemaining--;
          updateTimerDisplay();
          
          if (timeRemaining <= 0) {
              clearInterval(timerInterval);
              // Instead of ending the round directly, transition to confirm results view
              transitionToConfirmResultsView();
          }
      }, 1000);
  }
  
  function updateTimerDisplay() {
      const minutes = Math.floor(timeRemaining / 60);
      const seconds = timeRemaining % 60;
      const display = document.getElementById('timerDisplay');
      
      if (display) {
          display.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
      }
  }
  
  function resetTimer() {
      clearInterval(timerInterval);
      timeRemaining = roundTimeMinutes * 60;
      updateTimerDisplay();
      timerInterval = setInterval(() => {
          timeRemaining--;
          updateTimerDisplay();
          
          if (timeRemaining <= 0) {
              clearInterval(timerInterval);
              // Instead of ending the round directly, transition to confirm results view
              transitionToConfirmResultsView();
          }
      }, 1000);
  }
  
  // Transition to confirm results view
  function transitionToConfirmResultsView() {
      // Navigate to confirm results view while preserving current selections
      window.location.href = `/tournament/${tournamentId}?view_state=confirm_results`;
  }
  
  // Button event listeners
  const startRoundBtn = document.getElementById('startRoundBtn');
  if (startRoundBtn) {
      startRoundBtn.addEventListener('click', () => {
          const defaultText = startRoundBtn.textContent;
          startRoundBtn.textContent = 'Starting...';
          startRoundBtn.disabled = true;
          
          fetch(`/tournament/${tournamentId}/start_round`, {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
              }
          })
          .then(response => {
              if (!response.ok) {
                  throw response;
              }
              return response.json();
          })
          .then(data => {
              if (data.success) {
                  window.location.reload();
              } else {
                  handleTournamentError({ data }, startRoundBtn, defaultText);
              }
          })
          .catch(error => {
              handleTournamentError(error, startRoundBtn, defaultText);
          });
      });
  }
  
  const resetRoundBtn = document.getElementById('resetRoundBtn');
  if (resetRoundBtn) {
      resetRoundBtn.addEventListener('click', () => {
          clearError(); // Clear any existing errors
          
          // Reset all radio selections except for bye matches
          document.querySelectorAll('.match-row').forEach(row => {
              if (row.dataset.isBye !== 'true') {
                  const inputs = row.querySelectorAll('input[type="radio"]');
                  inputs.forEach(input => {
                      if (!input.disabled) {
                          input.checked = false;
                      }
                  });
              }
          });
          
          // Reset timer
          resetTimer();
      });
  }
  
  const endRoundEarlyBtn = document.getElementById('endRoundEarlyBtn');
  if (endRoundEarlyBtn) {
      endRoundEarlyBtn.addEventListener('click', () => {
          clearInterval(timerInterval);
          
          const defaultText = endRoundEarlyBtn.textContent;
          endRoundEarlyBtn.textContent = 'Processing...';
          endRoundEarlyBtn.disabled = true;
          
          // Instead of ending the round directly, save current state and transition to confirm results view
          saveResults()
          .then(data => {
              if (data.success) {
                  transitionToConfirmResultsView();
              } else {
                  handleTournamentError({ data }, endRoundEarlyBtn, defaultText);
              }
          })
          .catch(error => {
              handleTournamentError(error, endRoundEarlyBtn, defaultText);
              endRoundEarlyBtn.textContent = defaultText;
              endRoundEarlyBtn.disabled = false;
          });
      });
  }
  
  // New confirm results button handler
  const confirmResultsBtn = document.getElementById('confirmResultsBtn');
  if (confirmResultsBtn) {
      confirmResultsBtn.addEventListener('click', () => {
          // Validate before proceeding
          if (!validateAllSelectionsComplete()) {
              return;
          }
          
          const defaultText = confirmResultsBtn.textContent;
          confirmResultsBtn.textContent = 'Processing...';
          confirmResultsBtn.disabled = true;
          
          // Save results and complete the round
          saveResults()
          .then(data => {
              if (!data.success) {
                  handleTournamentError({ data }, confirmResultsBtn, defaultText);
                  return;
              }
              
              return fetch(`/tournament/${tournamentId}/complete_round`, {
                  method: 'POST',
                  headers: {
                      'Content-Type': 'application/json',
                  },
                  body: JSON.stringify({
                      match_results: collectMatchResults()
                  })
              })
              .then(response => {
                  if (!response.ok) {
                      throw response;
                  }
                  return response.json();
              })
              .then(data => {
                  if (data.success) {
                      // Reload to show the completed round state
                      window.location.href = `/tournament/${tournamentId}`;
                  } else {
                      handleTournamentError({ data }, confirmResultsBtn, defaultText);
                  }
              });
          })
          .catch(error => {
              handleTournamentError(error, confirmResultsBtn, defaultText);
          });
      });
  }
  
  const proceedNextRoundBtn = document.getElementById('proceedNextRoundBtn');
  if (proceedNextRoundBtn) {
      proceedNextRoundBtn.addEventListener('click', () => {
          const defaultText = proceedNextRoundBtn.textContent;
          proceedNextRoundBtn.textContent = 'Processing...';
          proceedNextRoundBtn.disabled = true;
          
          // Results should already be saved at this point, just navigate to the next round
          fetch(`/tournament/${tournamentId}/next_round`, {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
              }
          })
          .then(response => {
              if (!response.ok) {
                  throw response;
              }
              return response.json();
          })
          .then(data => {
              if (data.success) {
                  window.location.reload();
              } else {
                  handleTournamentError({ data }, proceedNextRoundBtn, defaultText);
              }
          })
          .catch(error => {
              handleTournamentError(error, proceedNextRoundBtn, defaultText);
          });
      });
  }
  
  const saveExitBtn = document.getElementById('saveExitBtn');
  if (saveExitBtn) {
      saveExitBtn.addEventListener('click', () => {
          const defaultText = saveExitBtn.textContent;
          saveExitBtn.textContent = 'Saving...';
          saveExitBtn.disabled = true;
          
          saveResults()
          .then(data => {
              if (data.success) {
                  window.location.href = '/tournaments';
              } else {
                  handleTournamentError({ data }, saveExitBtn, defaultText);
              }
          })
          .catch(error => {
              handleTournamentError(error, saveExitBtn, defaultText);
          });
      });
  }
  
  // Helper functions
  function saveResults() {
      return fetch(`/tournament/${tournamentId}/save_results`, {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify({
              match_results: collectMatchResults()
          })
      })
      .then(response => {
          if (!response.ok) {
              throw response;
          }
          return response.json();
      });
  }
  
  function collectMatchResults() {
      const results = [];
      document.querySelectorAll('.match-row').forEach(row => {
          const matchId = row.dataset.matchId;
          const player1Id = row.dataset.player1Id;
          const player2Id = row.dataset.player2Id;
          const isBye = row.dataset.isBye === 'true';
          
          let winnerId = null;
          
          if (isBye) {
              // For bye matches, player1 automatically wins
              winnerId = player1Id;
          } else {
              // For regular matches, check which radio button is selected
              const player1Radio = row.querySelector(`input[name="winner${matchId}"][value="player1"]`);
              const player2Radio = row.querySelector(`input[name="winner${matchId}"][value="player2"]`);
              
              if (player1Radio && player1Radio.checked) {
                  winnerId = player1Id;
              } else if (player2Radio && player2Radio.checked) {
                  winnerId = player2Id;
              }
          }
          
          if (winnerId) {
              results.push({
                  match_id: matchId,
                  winner_id: winnerId
              });
          }
      });
      
      return results;
  }

  // Completed Tournament Page
  // Round tabs functionality
  const roundTabs = document.querySelectorAll('.round-tab');
  roundTabs.forEach(tab => {
      tab.addEventListener('click', function() {
          // Remove active class from all tabs
          roundTabs.forEach(t => t.classList.remove('active'));
          
          // Add active class to clicked tab
          this.classList.add('active');
          
          // Hide all round content
          const roundContents = document.querySelectorAll('.round-content');
          roundContents.forEach(content => {
              content.style.display = 'none';
          });
          
          // Show selected round content
          const roundNum = this.getAttribute('data-round');
          document.getElementById(`round-content-${roundNum}`).style.display = 'block';
      });
  });
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

  // Game‐type filtering + pie‐chart rendering
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

  // Standings modal
  document.querySelectorAll('#adminStatcards .view-tourney')
    .forEach(link => {
      link.addEventListener('click', e => {
        e.preventDefault();
        const id     = link.dataset.tourneyId;
        const tourney= window.recentTournaments.find(t => t.id == id);
        if (!tourney) return;

        document.getElementById('modalTitle').textContent = tourney.title;
        const info  = document.querySelectorAll('.modal-info .info-item .regular4');
        info[0].textContent = tourney.format;
        info[1].textContent = tourney.game_type;
        info[2].textContent = tourney.round_time_minutes + ' Minutes';
        document.querySelector('.modal-date .regular4').textContent = tourney.date;

        const tbody = document.querySelector('.table-wrapper tbody');
        tbody.innerHTML = '';
        tourney.standings.forEach((p,i) => {
          tbody.insertAdjacentHTML('beforeend', `
            <tr>
              <td>${i+1}</td>
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
  if (limitSelector) {
    limitSelector.addEventListener('change', function() {
      const params = new URLSearchParams(window.location.search);
      params.set('limit', this.value);
      params.set('view',  viewSelector.value);   // preserve current tab
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
  initTournamentManager();
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