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
    username: window.currentUserUsername || "" 
  };

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

  // Functions
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
    emailError.className = 'field-error regular4 display-none mt-1';
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
          player.guest_name = `${currentUser.firstName} ${currentUser.lastName}`.trim();
          player.email = currentUser.email;
          
          // Track the email for duplicate detection
          if (currentUser.email) {
            usedEmails.push(currentUser.email.toLowerCase());
          }
        } else {
          // User will be matched by username in the backend
          player.guest_name = username; // Use username as guest name until matched
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
        
        // Check for duplicate email in the tournament
        if (email && email.trim() !== '') {
          if (usedEmails.includes(email.toLowerCase())) {
            const emailError = document.getElementById(`emailError${i}`);
            if (emailError) {
              emailError.textContent = `Email '${email}' is already used in this tournament`;
              emailError.style.display = 'block';
              activatePlayer(i);
            }
            validPlayers = false;
            continue;
          }
          usedEmails.push(email.toLowerCase());
        }
        
        player.guest_name = `${firstName} ${lastName}`.trim();
        player.email = email;
      }
      
      playerData.push(player);
    }
    
    return validPlayers ? playerData : null;
  }

  function handleSaveTournament() {
    // Collect tournament data
    const tournamentData = {
      title: document.getElementById('tournamentName').value,
      format: document.getElementById('tournamentType').value,
      game_type: document.getElementById('gameType').value,
      include_creator_as_player: isCompetitorCheckbox.checked,
      is_draft: true,  // Always save as draft initially
      created_by: currentUser.id
    };
    
    // Validate core tournament data
    if (!tournamentData.title || tournamentData.title.trim() === '') {
      showError('Please enter a tournament name');
      return;
    }
    
    if (!tournamentData.format || tournamentData.format === '') {
      showError('Please select a tournament type');
      return;
    }
    
    // Get number of players
    const playerCount = parseInt(competitorCountSelect.value);
    if (isNaN(playerCount) || playerCount < 2) {
      showError('Please select a valid number of competitors');
      return;
    }
    
    // Validate player data
    const playerData = validatePlayerData(playerCount);
    if (!playerData) {
      return; // Validation failed, errors already shown
    }
    
    // Add validated player data to tournament data
    tournamentData.players = playerData;
    
    // Show loading state
    saveTournamentBtn.disabled = true;
    saveTournamentBtn.textContent = 'Saving...';
    
    // Send data to server
    fetch('/save_tournament', {
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
        alert('Tournament saved successfully!');
        window.location.href = '/dashboard';  // Redirect to dashboard
      } else {
        showError('Error: ' + data.message);
      }
    })
    .catch(error => {
      console.error('Error:', error);
      
      // Reset button state
      saveTournamentBtn.disabled = false;
      saveTournamentBtn.textContent = 'Save Tournament';
      
      // Display specific error messages based on server response
      if (error.data) {
        if (error.data.invalid_usernames) {
          // Display username errors
          error.data.invalid_usernames.forEach(username => {
            const playerIndex = playerData.findIndex(player => player.username === username);
            if (playerIndex !== -1) {
              const playerNumber = playerIndex + 1;
              const usernameError = document.getElementById(`usernameError${playerNumber}`);
              if (usernameError) {
                usernameError.textContent = `User '${username}' does not exist`;
                usernameError.style.display = 'block';
                
                // Activate the player tab with the error
                activatePlayer(playerNumber);
              }
            }
          });
          
          showError('One or more TourneyPro usernames are invalid. Please correct them and try again.');
        } 
        else if (error.data.emails_with_accounts) {
          // Display email errors
          error.data.emails_with_accounts.forEach(email => {
            // Find which player has this email
            for (let i = 1; i <= playerCount; i++) {
              const playerEmail = document.getElementById(`email${i}`).value;
              if (playerEmail === email) {
                const emailError = document.getElementById(`emailError${i}`);
                if (emailError) {
                  emailError.textContent = `A TourneyPro Account has been created using the email address '${email}'`;
                  emailError.style.display = 'block';
                  
                  // Activate the player tab with the error
                  activatePlayer(i);
                }
                break;
              }
            }
          });
          
          showError('One or more emails are already linked to TourneyPro accounts. Please correct them and try again.');
        }
        else {
          showError(error.data.message || 'Failed to save tournament. Please try again.');
        }
      } else {
        showError('Failed to save tournament. Please try again.');
      }
    })
    .finally(() => {
      // Reset button state
      saveTournamentBtn.disabled = false;
      saveTournamentBtn.textContent = 'Save Tournament';
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
  const viewSelector = document.getElementById('viewSelector');
  const playerView = document.getElementById('playerView');
  const adminView = document.getElementById('adminView');
  const gameTypeSelector = document.getElementById('gameTypeSelector');

  if (!viewSelector) return;

  // Game type selector functionality
  if (gameTypeSelector) {
    gameTypeSelector.addEventListener('change', () => {
      const selectedGame = gameTypeSelector.value;
      const statSections = document.querySelectorAll('.game-stat');

      statSections.forEach((section) => {
        if (section.dataset.game === selectedGame) {
          section.style.display = 'block';
          const canvas = section.querySelector('canvas');
          if (canvas && !canvas.dataset.rendered) {
            const wins = parseInt(section.querySelector('.total-stat:nth-child(1) .title2').textContent);
            const games = parseInt(section.querySelector('.total-stat:nth-child(2) .title2').textContent);
            const losses = games - wins;
            renderPieChart(canvas.id, wins, losses);
            canvas.dataset.rendered = 'true';
          }
        } else {
          section.style.display = 'none';
        }
      });
    });

    // Run filter once on page load to show default
    gameTypeSelector.dispatchEvent(new Event('change'));
  }

  // View selector functionality
  viewSelector.addEventListener('change', function() {
    const isPlayer = this.value === 'player';
    if (playerView) playerView.style.display = isPlayer ? 'block' : 'none';
    if (adminView) adminView.style.display = isPlayer ? 'none' : 'block';
    
    // Show game type selector only in player view
    if (gameTypeSelector) {
      gameTypeSelector.style.display = isPlayer ? 'block' : 'none';
    }
  });
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
});