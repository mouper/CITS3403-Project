# TourneyPro

Group project for CITS3403 - Agile Web Development

| Name      | Student ID | Github Username |
| ----------- | ----------- | ----------- |
| Keandria Hui En Ong | 23365164 | mouper |
| Jessie Gunawan | 24125314 | jessiecg |
| Kunning Shao | 23825311 | KunningShao |
| Aidan Hutchison | 23722738  | Lion-Rampant  |

---

## TourneyPro - Overview

TourneyPro is your new go-to web app for organising competitive tournaments with friends and analysing tournament statistics.

### Usage
1. Sign Up / Log In:
   - Create an account or login with existing credentials. 
   - If you have been invited as a guest to your friend's tournaments in the past, simply sign up with the same email and all of your existing tournament data will be linked automatically to your new account!

2. Dashboard:
    - View your active tournaments, create new ones, jump into ongoing events, add new friends or check out your friends profiles.

3. Tournament Management:
    - Add players, generate bracket pairings, and enter match outcomes. 
    - You can either add your friends on TourneyPro as players or invite guests using just their email and name. 
    - All tournament info can be viewed by TourneyPro users on their own pages, however, you can also send the round pairings and final tournament results to all players via email (so guests won't be left out!).

4. Analytics:
    - Track your tournament performance in different games and view any past tournaments you have hosted.

5. Requests:
    - Manage your friend requests.

6. My Account:
    - Update your profile picture, change your personal info or change the statistics visible to your friends when they view your profile.

### Design
- UI/UX: Designed on Figma.
- CSS Framework: Uses Tailwind Play CDN.
- Authentication: Uses Flask-Login to handle user sessions and access control.
- Email: Integrates Flask-Mail to send updates on tournaments.

---

## Running The Website

***WILL ONLY WORK ON LINUX (WSL ON WINDOWS) AND MAC***

1. Clone the repository:
```
git clone https://github.com/mouper/CITS3403-Project.git
```

2. Initial set up (from Project Directory):
```
cd src
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

3. Setting up the database
```
flask --app app db upgrade
```

4. Initialise the test database (optional):
```
python generate_test_db.py
```

5. Running the website:
```
flask run
```

6. Open the returned URL: http://127.0.0.1:5000

7. Leaving the virtual environment:
```
deactivate
```

---

## Testing
**STEPS 1-3 IN [Running The Website](#Running-The-Website) MUST FIRST BE COMPLETED:**

1. Running the unit tests:
```
python -m unittest tests/unitTests.py -v
```

2. Running the selenium tests:
```
python -m unittest tests/seleniumTests.py -v
```

---

## References

> AI tools (e.g. GitHub Copilot, chatGPT, Claude) were used in the development of this project. These tools were used to assist the team in correcting code logic, and optimising code efficiency in some instances.

## Note To Markers
Due to security concerns, we are not able to directly provide our .env file in the file submissions of this project. Since this file contains the credentials for the email address which is used to send the emails to users/guests, the functionality of these buttons will only work during our project demo. However, if needed these credentials can also be provided upon request.