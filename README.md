# CITS3403-Project
Group project for CITS3403 - Agile Web Development

| Name      | Student ID | Github Username |
| ----------- | ----------- | ----------- |
| Keandria Ong | 23365164 | mouper |
| Jessie Gunawan | 24125314 | jessiecg |
| Kunning Shao | 23825311 | Kunning Shao |
| Aidan Hutchison | 23722738  | Lion-Rampant  |


---


## Set Up
```
*ONLY WORKS ON LINUX (WSL ON WINDOWS) AND MAC*

Initial Set Up:
    cd src
    python3 -m venv env
    source env/bin/activate
    pip install -r requirements.txt
    python init_db.py
    flask run

After Set Up Has Been Completed Once:
    source env/bin/activate
    flask run

If you want to leave the environment:
    deactivate
```
Site can now be viewed from [http://127.0.0.1:5000](http://127.0.0.1:5000)


---


## Issue Creation Guidelines

To keep our workflow organized and efficient, please follow these conventions when creating a new issue:


### Use Present Tense in the Title

Write issue titles in **present tense**, using a verb that describes the action.

- Good: `Create navbar component`  
- Bad: `Created navbar component`, `Navbar was created`


### Add an Image of the Design

Include a **screenshot or link** to the relevant design (e.g., from Figma) to give visual context for the task.


### List Reusable Components and Styles

If the issue involves building **reusable components or styles**, list them out clearly.

#### Example List:
- components/Navbar.tsx
- components/Button.tsx

### Reporting a Bug
Start the issue with 'Bug:'
- e.g. Bug: Save button broken

---


## Branch Naming Convention
This project follows a consistent branch naming strategy to improve collaboration and maintain clarity across development activities.

### Branch Types

- **`feature/`**  
  Used for adding, refactoring, or removing a feature.

- **`bugfix/`**  
  Used for fixing a bug.

- **`test/`**  
  Used for experimenting or prototyping outside of a specific ticket or issue.

### Reference

After the branch category, include the **reference** to the issue or ticket you're working on. If there's no reference, use `no-ref`.

#### Example Branch Name
`feature/issue-42/create-new-button-component` 


---


## Commit Message Convention

Commit messages should be clear, concise, and follow a structured format to communicate changes effectively.

### Categories

Start your commit message with one of the following categories:

- **`feat`** — Adding a new feature  
- **`fix`** — Fixing a bug  
- **`refactor`** — Improving code for performance or readability, without changing behavior  
- **`chore`** — Maintenance tasks (e.g. documentation, formatting, tests, cleanup)

### Format

Each commit message should follow this pattern:
**`<category>: statement`**
- The **category** is followed by a colon `:` and a space
- Each **statement** is a short, imperative verb phrase
- Separate multiple statements with a **semicolon `;`**

#### Example Commit Message
`feat: add button component` 


---


## Link To View Figma Design File:
[https://www.figma.com/design/n3Yytb0iObtMeXQxszi8NE/TourneyPro?node-id=0-1&t=dwzOMW01yCNLIZJ2-1](https://www.figma.com/design/n3Yytb0iObtMeXQxszi8NE/TourneyPro?node-id=0-1&t=dwzOMW01yCNLIZJ2-1)
