# CITS3403-Project
Group project for CITS3403 - Agile Web Development

| Name      | Student ID | Github Username |
| ----------- | ----------- | ----------- |
| Keandria Hui En Ong | 23365164 | mouper |
| Jessie Gunawan | 24125314 | jessiecg |
| Kunning Shao | 23825311 | KunningShao |
| Aidan Hutchison | 23722738  | Lion-Rampant  |


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
*** THE ABOVE STEPS 1-3 MUST BE COMPLETED: ***

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