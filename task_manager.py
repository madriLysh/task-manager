#!/usr/bin/env python3
"""
Task Manager (command-line) — SQLite-backed TODO app.
Refactored version: uses sqlite3.Row for named column access, fixes indexing bugs,
adds small input validation and friendlier prompts.
"""
import sqlite3
import random
from typing import List, Optional


class TodoApp:
    def __init__(self, db_path: str = "todo.db"):
        # Use Row factory so we can access columns by name instead of numeric indexes
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.create_table()

    # ---------------- Core DB Methods ----------------
    def create_table(self) -> None:
        """Create tasks table if it doesn't exist"""
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                completed INTEGER DEFAULT 0,
                priority TEXT
            )
            """
        )
        self.conn.commit()

    def get_all_tasks(self) -> List[sqlite3.Row]:
        """Fetch all tasks from database (returns list of Row objects)"""
        self.cursor.execute("SELECT * FROM tasks ORDER BY id")
        return self.cursor.fetchall()

    def update_task_column(self, task_id: int, column: str, value) -> None:
        """Update a specific column for a task (whitelisted columns only)."""
        allowed_columns = {"title", "description", "completed", "priority"}
        if column not in allowed_columns:
            raise ValueError(f"Invalid column: {column}")
        # Use parameterized query to avoid injection
        self.cursor.execute(f"UPDATE tasks SET {column} = ? WHERE id = ?", (value, task_id))
        self.conn.commit()

    # ---------------- Utility Methods ----------------
    def is_empty(self, tasks: List[sqlite3.Row]) -> bool:
        """Return True and print message if tasks list is empty."""
        if not tasks:
            print("📋 No tasks yet!")
            return True
        return False

    def print_tasks(self, tasks: List[sqlite3.Row]) -> None:
        """Print tasks in a readable format (id, status, title, priority, description)."""
        if self.is_empty(tasks):
            return

        print("\n📋 Your Tasks:")
        print("-" * 60)
        for task in tasks:
            status = "✅" if task["completed"] else "⬜"
            priority = task["priority"] or "⚪"
            print(f"{status} [{task['id']}] {task['title']} {priority}")
            if task["description"]:
                print(f"    Description: {task['description']}")
        print("-" * 60)

    def choose_task(self, tasks: List[sqlite3.Row]) -> Optional[sqlite3.Row]:
        """Let the user pick a task by number from the provided list (1-based)."""
        for i, task in enumerate(tasks, start=1):
            print(f"{i}- [{task['id']}] {task['title']}")
        try:
            num_str = input("Enter the number: ").strip()
            num = int(num_str)
            return tasks[num - 1]
        except (ValueError, IndexError):
            print("❌ Invalid choice!")
            return None

    # ---------------- Task Methods ----------------
    def add_task(self, title: str, description: str = "") -> None:
        """Add a new task to the database (title required)."""
        title = title.strip()
        if not title:
            raise ValueError("Task title cannot be empty")
        self.cursor.execute("INSERT INTO tasks (title, description) VALUES (?, ?)", (title, description))
        self.conn.commit()
        print(f"✅ Task added: {title}")

    def view_tasks(self) -> None:
        tasks = self.get_all_tasks()
        self.print_tasks(tasks)

    def complete_task(self, task_id: int) -> None:
        """Mark a task as completed (1)."""
        self.update_task_column(task_id, "completed", 1)
        print(f"✅ Task {task_id} marked as completed!")

    def delete_task(self, task_id: int) -> None:
        self.cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.conn.commit()
        print(f"🗑️ Task {task_id} deleted!")

    def set_priority(self) -> None:
        """Assign a priority (hard/medium/easy) to a selected task."""
        tasks = self.get_all_tasks()
        if self.is_empty(tasks):
            return

        print("Which task do you want to add a priority for?")
        task = self.choose_task(tasks)
        if not task:
            return

        color = input("Difficulty (hard, medium, easy): ").strip().lower()
        if color not in ("hard", "medium", "easy"):
            print("❌ Invalid priority. Choose: hard, medium, or easy.")
            return

        color_icon = {"hard": "🔴", "medium": "🟡", "easy": "🟢"}[color]
        self.update_task_column(task["id"], "priority", color_icon)
        print(f"✅ Priority {color_icon} set for task {task['id']}.")

    def edit_task(self) -> None:
        """Edit title or description of a task."""
        tasks = self.get_all_tasks()
        if self.is_empty(tasks):
            return

        task = self.choose_task(tasks)
        if not task:
            return

        field = input("What to change (title or description): ").strip().lower()
        if field not in ("title", "description"):
            print("❌ Invalid field! Only 'title' or 'description' allowed.")
            return

        new_value = input(f"Enter new {field}: ").rstrip()
        if field == "title" and not new_value:
            print("❌ Title cannot be empty!")
            return

        self.update_task_column(task["id"], field, new_value)
        print(f"✅ Task {task['id']} {field} updated.")

    def gamble_task(self) -> None:
        """Randomly pick an incomplete task and offer to accept/reroll/cancel."""
        tasks = self.get_all_tasks()
        if self.is_empty(tasks):
            return

        incomplete = [t for t in tasks if t["completed"] == 0]
        if not incomplete:
            print("🎉 All tasks are completed! Nothing to gamble.")
            return

        while True:
            task = random.choice(incomplete)
            print(f"\n🎲 You got: {task['title']}")
            choice = input("Accept this task? (yes / no / cancel): ").strip().lower()

            if choice == "yes":
                print(f"✅ Selected: {task['title']}")
                return
            elif choice == "no":
                continue  # re-roll
            elif choice == "cancel":
                print("❌ Gamble canceled.")
                return
            else:
                print("❌ Invalid choice. Type: yes, no, or cancel.")

    def search_tasks(self) -> None:
        """Filter tasks by priority (hard, medium, easy)."""
        difficulty = input("What is the difficulty (hard, medium, easy): ").strip().lower()
        if difficulty not in ("hard", "medium", "easy"):
            print("❌ Invalid priority. Choose: hard, medium, or easy.")
            return

        priority_map = {"hard": "🔴", "medium": "🟡", "easy": "🟢"}
        target = priority_map[difficulty]

        self.cursor.execute("SELECT * FROM tasks WHERE priority = ?", (target,))
        results = self.cursor.fetchall()
        if not results:
            print(f"📋 No {difficulty} tasks found!")
            return

        print(f"\n{target} {difficulty.upper()} Tasks:")
        self.print_tasks(results)

        print("\nSelect a task:")
        task = self.choose_task(results)
        if task:
            print(f"✅ You selected: {task['title']}")
        else:
            print("❌ No task selected.")

    def statistics(self) -> None:
        """Display task counts and percentages."""
        self.cursor.execute("SELECT COUNT(*) FROM tasks")
        total = self.cursor.fetchone()[0]
        if total == 0:
            print("📋 No tasks yet!")
            return

        self.cursor.execute("SELECT COUNT(*) FROM tasks WHERE completed = 1")
        completed = self.cursor.fetchone()[0]
        pending = total - completed
        completed_pct = (completed / total) * 100 if total else 0.0
        pending_pct = 100.0 - completed_pct

        print("\n=== STATISTICS ===")
        print(f"Total Tasks: {total}")
        print(f"Completed: {completed} ({completed_pct:.1f}%)")
        print(f"Pending: {pending} ({pending_pct:.1f}%)\n")

        # By priority
        self.cursor.execute("SELECT COUNT(*) FROM tasks WHERE priority IS NULL OR priority = ''")
        no_priority = self.cursor.fetchone()[0]
        if no_priority:
            print(f"⚪ No Priority: {no_priority} tasks")

        self.cursor.execute("SELECT COUNT(*) FROM tasks WHERE priority = '🔴'")
        hard = self.cursor.fetchone()[0]
        print(f"🔴 Hard: {hard} tasks")

        self.cursor.execute("SELECT COUNT(*) FROM tasks WHERE priority = '🟡'")
        medium = self.cursor.fetchone()[0]
        print(f"🟡 Medium: {medium} tasks")

        self.cursor.execute("SELECT COUNT(*) FROM tasks WHERE priority = '🟢'")
        easy = self.cursor.fetchone()[0]
        print(f"🟢 Easy: {easy} tasks")

    def close(self) -> None:
        """Close the DB connection."""
        if self.conn:
            self.conn.close()


# ---------------- Main Program ----------------

def main() -> None:
    app = TodoApp()
    try:
        while True:
            print("\n=== TODO APP ===")
            print("1. Add task")
            print("2. View tasks")
            print("3. Complete task")
            print("4. Delete task")
            print("5. Add priority to task")
            print("6. Edit task")
            print("7. Gamble a task")
            print("8. View statistics")
            print("9. Search tasks by priority")
            print("10. Exit")

            choice = input("\nChoose option (1-10): ").strip()

            if choice == "1":
                title = input("Task title: ").strip()
                if not title:
                    print("❌ Task title cannot be empty!")
                    continue
                description = input("Description (optional): ").strip()
                try:
                    app.add_task(title, description)
                except Exception as e:
                    print(f"❌ Error adding task: {e}")

            elif choice == "2":
                app.view_tasks()

            elif choice == "3":
                app.view_tasks()
                task_id = input("Enter task ID to complete: ").strip()
                if not task_id.isdigit():
                    print("❌ Please enter a valid number!")
                    continue
                task_id = int(task_id)
                app.cursor.execute("SELECT 1 FROM tasks WHERE id = ?", (task_id,))
                if not app.cursor.fetchone():
                    print(f"❌ Task {task_id} not found!")
                    continue
                app.complete_task(task_id)

            elif choice == "4":
                app.view_tasks()
                task_id = input("Enter task ID to delete: ").strip()
                if not task_id.isdigit():
                    print("❌ Please enter a valid number!")
                    continue
                task_id = int(task_id)
                app.cursor.execute("SELECT 1 FROM tasks WHERE id = ?", (task_id,))
                if not app.cursor.fetchone():
                    print(f"❌ Task {task_id} not found!")
                    continue
                app.delete_task(task_id)

            elif choice == "5":
                app.set_priority()

            elif choice == "6":
                app.edit_task()

            elif choice == "7":
                app.gamble_task()

            elif choice == "8":
                app.statistics()

            elif choice == "9":
                app.search_tasks()

            elif choice == "10":
                print("👋 Goodbye!")
                break

            else:
                print("❌ Invalid choice!")
    finally:
        app.close()

if __name__ == "__main__":
    main()