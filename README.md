# Task Manager

[![Python](https://img.shields.io/badge/python-3.x-blue)](https://www.python.org/) [![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)  

A simple command-line task manager that uses SQLite. Built to practice SQL and CRUD operations — a lightweight starting point for working with persistent data.

## Features

- Add, view, complete, and delete tasks  
- Assign priority: Hard (🔴), Medium (🟡), Easy (🟢)  
- Edit existing tasks (title and description)  
- Random uncompleted task selector ("Gamble")  
- View statistics (completed vs pending, counts by priority)  
- Search tasks by priority

## Requirements

- Python 3.x  
- Uses the standard library: `sqlite3`, `random`

## Installation & Run

1. Clone the repo:
   git clone https://github.com/madriLysh/your-repo.git
2. Change directory and run:
   cd your-repo
   python task_manager.py

(If you use a different filename, replace `task_manager.py` with your script name.)

## Usage

Run the script and choose an option from the menu:

```
=== TODO APP ===
1. Add task
2. View tasks
3. Complete task
4. Delete task
5. Add priority to task
6. Edit task
7. Gamble a task
8. View statistics
9. Search tasks by priority
10. Exit
```

Notes:
- Add task: title is required. If left empty, the program will reject it with: ❌ Task title cannot be empty!
- Default priority is ⚪ (no priority). Use the menu to assign 🔴 / 🟡 / 🟢.
- Gamble: randomly select one uncompleted task with options to confirm, reroll, or cancel.

## Example session

1) Add task: "Write README"  
2) View tasks — you’ll see the task with id, title, priority, and completed status.  
3) Complete task — mark it done and check statistics.

(You can paste a short sample console transcript here or include a screenshot.)

## Database structure

Table: `tasks`

| Column      | Type      | Description                                  |
|-------------|-----------|----------------------------------------------|
| id          | INTEGER   | Unique task ID (auto-increment)              |
| title       | TEXT      | Task name (required)                         |
| description | TEXT      | Task details (optional)                      |
| completed   | BOOLEAN   | 0 = not done, 1 = done                       |
| priority    | TEXT      | Emoji: 🔴 (hard), 🟡 (medium), 🟢 (easy)      |

## Contributing

Feel free to open issues or submit pull requests. Please keep changes small and focused, and include tests or a short demo if possible.

## License

This project is licensed under the MIT License — see the LICENSE file for details.

## Author

Anas Khan — Year 3, Computer Science Student at KAU  
GitHub: [madriLysh on GitHub](https://github.com/madriLysh)