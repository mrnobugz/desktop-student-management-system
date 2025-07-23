
import sqlite3
from tkinter import messagebox
import requests
import json

def db_connect():
    conn = sqlite3.connect("student_management.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        dob TEXT NOT NULL,
                        gender TEXT NOT NULL,
                        student_class TEXT NOT NULL,
                        parent_name TEXT,
                        parent_phone TEXT,
                        parent_nationality TEXT
                        )''')
    # Create users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        is_admin INTEGER DEFAULT 0
                    )''')
    # Ensure default admin exists
    cursor.execute("SELECT * FROM users WHERE username=?", ("admin",))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)", ("admin", "admin123", 1))
    conn.commit()
    conn.close()

# User management functions
def create_user(username, password, is_admin=0):
    conn = sqlite3.connect("student_management.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)", (username, password, is_admin))
        conn.commit()
        messagebox.showinfo("Success", f"User '{username}' created successfully!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", f"Username '{username}' already exists!")
    finally:
        conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect("student_management.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

def is_admin(username):
    conn = sqlite3.connect("student_management.db")
    cursor = conn.cursor()
    cursor.execute("SELECT is_admin FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result and result[0] == 1

def insert(name, dob, gender, student_class, parent_name, parent_phone, parent_nationality):
    conn = sqlite3.connect("student_management.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO students (name, dob, gender, student_class, parent_name, parent_phone, parent_nationality) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (name, dob, gender, student_class, parent_name, parent_phone, parent_nationality)
    )
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Student record added successfully!")

def update(student_id, name, dob, gender, student_class, parent_name, parent_phone, parent_nationality):
    conn = sqlite3.connect("student_management.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE students SET name=?, dob=?, gender=?, student_class=?, parent_name=?, parent_phone=?, parent_nationality=? WHERE id=?",
        (name, dob, gender, student_class, parent_name, parent_phone, parent_nationality, student_id)
    )
    conn.commit()
    conn.close()


def delete(student_id):
    conn = sqlite3.connect("student_management.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id=?", (student_id,))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Student record deleted successfully!")

# Remove user by username
def remove_user(username):
    conn = sqlite3.connect("student_management.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username=?", (username,))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", f"User '{username}' removed successfully!")

def delete_all():
    conn = sqlite3.connect("student_management.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students")
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "All student records have been deleted!")

def searchFunction(search_value=""):
    conn = sqlite3.connect("student_management.db")
    cursor = conn.cursor()
    if search_value:
        cursor.execute(
            "SELECT * FROM students WHERE name LIKE ? OR parent_name LIKE ?",
            ('%' + search_value + '%', '%' + search_value + '%')
        )
    else:
        cursor.execute("SELECT * FROM students")
    records = cursor.fetchall()
    conn.close()
    return records

# Search students by class
def search_by_class(student_class):
    conn = sqlite3.connect("student_management.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE student_class=?", (student_class,))
    records = cursor.fetchall()
    conn.close()
    return records

def save():
    # Confirm with user before backup
    from customtkinter import CTkToplevel, CTkProgressBar, CTkLabel
    import threading
    import time
    root = None
    try:
        # Try to get the main window
        import tkinter as tk
        root = tk._default_root
    except Exception:
        pass
    if not messagebox.askyesno("Confirm Backup", "Do you want to backup all student records to the online server?"):
        return

    # Progress bar window
    progress_win = CTkToplevel(root)
    progress_win.title("Backing Up Data")
    progress_win.geometry("350x120")
    progress_win.resizable(False, False)
    CTkLabel(progress_win, text="Uploading data to server...", font=("roboto", 16)).pack(pady=10)
    progress_bar = CTkProgressBar(progress_win, width=300)
    progress_bar.pack(pady=10)
    progress_bar.set(0)

    def do_backup():
        try:
            conn = sqlite3.connect("student_management.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students")
            records = cursor.fetchall()
            conn.close()
            columns = ["id", "name", "dob", "gender", "student_class", "parent_name", "parent_phone", "parent_nationality"]
            data = [dict(zip(columns, row)) for row in records]
            url = "https://your-server.com/backup"  # <-- Replace with your actual endpoint
            # Simulate progress
            for i in range(1, 6):
                time.sleep(0.2)
                progress_bar.set(i/6)
            response = requests.post(url, json={"students": data})
            progress_bar.set(1)
            time.sleep(0.3)
            progress_win.destroy()
            if response.status_code == 200:
                messagebox.showinfo("Backup Success", "Data backed up to online server successfully!")
            else:
                messagebox.showerror("Backup Failed", f"Server error: {response.status_code}\n{response.text}")
        except Exception as e:
            progress_win.destroy()
            messagebox.showerror("Backup Error", str(e))

    threading.Thread(target=do_backup, daemon=True).start()

db_connect()
