import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
import Database

class AdminPanel(tb.Window):
    def __init__(self):
        super().__init__(themename="cosmo")
        self.title("Admin Panel - User Management")
        self.geometry("900x500")
        self.resizable(False, False)
        self.configure(bg="#f5f6fa")
        self.create_widgets()

    def create_widgets(self):
        # Title
        tb.Label(self, text="User Management", font=("Roboto", 22, "bold"), bootstyle=PRIMARY).pack(pady=20)
        main_frame = tb.Frame(self, bootstyle=LIGHT)
        main_frame.pack(fill="both", expand=True, padx=30, pady=10)

        # Left: Create User
        left_frame = tb.Frame(main_frame, bootstyle=LIGHT)
        left_frame.pack(side="left", fill="y", padx=(0, 30))
        tb.Label(left_frame, text="Create New User", font=("Roboto", 16, "bold"), bootstyle=INFO).pack(pady=10)
        tb.Label(left_frame, text="Username:", font=("Roboto", 12)).pack(anchor="w", padx=10)
        self.username_entry = tb.Entry(left_frame, font=("Roboto", 12), width=25)
        self.username_entry.pack(padx=10, pady=5)
        tb.Label(left_frame, text="Password:", font=("Roboto", 12)).pack(anchor="w", padx=10)
        self.password_entry = tb.Entry(left_frame, font=("Roboto", 12), show="*", width=25)
        self.password_entry.pack(padx=10, pady=5)
        tb.Label(left_frame, text="Confirm Password:", font=("Roboto", 12)).pack(anchor="w", padx=10)
        self.confirm_entry = tb.Entry(left_frame, font=("Roboto", 12), show="*", width=25)
        self.confirm_entry.pack(padx=10, pady=5)
        self.is_admin_var = tb.IntVar()
        tb.Checkbutton(left_frame, text="Is Admin", variable=self.is_admin_var, bootstyle=SUCCESS).pack(anchor="w", padx=10, pady=5)
        tb.Button(left_frame, text="Create User", bootstyle=SUCCESS, command=self.create_user_action).pack(pady=15)

        # Right: User Table
        right_frame = tb.Frame(main_frame, bootstyle=LIGHT)
        right_frame.pack(side="left", fill="both", expand=True)
        tb.Label(right_frame, text="All Users", font=("Roboto", 16, "bold"), bootstyle=INFO).pack(pady=10)
        self.user_table = tb.Treeview(right_frame, columns=("Id", "Username", "Is Admin"), show="headings", bootstyle=INFO, height=15)
        self.user_table.heading("Id", text="Id")
        self.user_table.heading("Username", text="Username")
        self.user_table.heading("Is Admin", text="Is Admin")
        self.user_table.column("Id", width=60)
        self.user_table.column("Username", width=180)
        self.user_table.column("Is Admin", width=100)
        self.user_table.pack(fill="both", expand=True, padx=10)
        self.refresh_user_table()
        rmbtn=tb.Button(right_frame, text="Remove Selected User", bootstyle=DANGER, command=self.remove_user_action)
        rmbtn.pack(pady=10)

    def create_user_action(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm = self.confirm_entry.get().strip()
        is_admin = self.is_admin_var.get()
        if not username or not password:
            messagebox.showerror("Error", "Username and password required!")
            return
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match!")
            return
        try:
            Database.create_user(username, password, is_admin)
            messagebox.showinfo("Success", f"User '{username}' created successfully!")
            self.username_entry.delete(0, 'end')
            self.password_entry.delete(0, 'end')
            self.confirm_entry.delete(0, 'end')
            self.is_admin_var.set(0)
            self.refresh_user_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh_user_table(self):
        for row in self.user_table.get_children():
            self.user_table.delete(row)
        import sqlite3
        conn = sqlite3.connect("student_management.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, is_admin FROM users")
        users = cursor.fetchall()
        conn.close()
        for user in users:
            self.user_table.insert("", "end", values=(user[0], user[1], "Yes" if user[2] else "No"))

    def remove_user_action(self):
        selected = self.user_table.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a user to remove.")
            return
        user_id = self.user_table.item(selected, "values")[0]
        try:
            Database.remove_user(user_id)
            messagebox.showinfo("Success", f"User with ID {user_id} removed successfully!")
            self.refresh_user_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = AdminPanel()
    app.mainloop()


