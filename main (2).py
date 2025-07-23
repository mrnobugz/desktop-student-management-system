from customtkinter import *
import customtkinter as ctk
from tkinter import messagebox, IntVar, filedialog

from tkcalendar import DateEntry
import Database
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas



try:
    import pywhatkit
except ImportError:
    pywhatkit = None

# Ensure database and tables are initialized before login
Database.db_connect()

# Search by name
# search_entry initialization moved below after fram is defined


# --- LOGIN FORM ---
def show_main_window():
    win.deiconify()

def authenticate():
    username = username_entry.get()
    password = password_entry.get()
    user = Database.authenticate_user(username, password)
    if user:
        login_win.destroy()
        show_main_window()
        global current_user
        current_user = username
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")


# Create login window using customtkinter
login_win = ctk.CTk()
login_win.title("Admin Login")
login_win.geometry("400x300")
login_win.configure(fg_color="lightblue")

login_frame = ctk.CTkFrame(login_win, fg_color="white", width=350, height=250)
login_frame.place(relx=0.5, rely=0.5, anchor="center")

ad_lebel=ctk.CTkLabel(login_frame, text="Admin Login", font=("roboto", 20, "bold"), text_color="blue").pack(pady=15)
user_lebel=ctk.CTkLabel(login_frame, text="Username:", font=("roboto", 14)).pack()
username_entry = ctk.CTkEntry(login_frame, font=("roboto", 14), width=200)
username_entry.pack(pady=5)
pas_lebel=ctk.CTkLabel(login_frame, text="Password:", font=("roboto", 14)).pack()
password_entry = ctk.CTkEntry(login_frame, font=("roboto", 14), show="*", width=200)
password_entry.pack(pady=5)
log_btn=ctk.CTkButton(login_frame, text="Login", font=("roboto", 14, "bold"), fg_color="#0080ff", text_color="white", command=authenticate)
log_btn.pack(pady=15)


 # Hide main window until login
win = ctk.CTk()
win.withdraw()
current_user = None


def menu():
    global count
    count += 1
    if count %2 == 1:
        frame_menu = ctk.CTkFrame(fram, width=300, height=500)
        frame_menu.place(x=1000, y=60)
        # Add Admin Panel button to menu frame if user is admin
        if current_user and Database.is_admin(current_user):
            adminbtn = ctk.CTkButton(frame_menu,
                text="Admin Panel",
                text_color="white",
                fg_color='#3333ff',
                font=("italic", 15, "bold"),
                command=penel)
            adminbtn.place(x=50, y=50)
        # Add WhatsApp Broadcast button to menu frame
        broadcast_btn = ctk.CTkButton(frame_menu,
            text="WhatsApp Broadcast",
            text_color="white",
            fg_color='#25D366',
            width=170,
            font=("italic", 15, "bold"),
            command=broadcast_whatsapp_message
        )
        broadcast_btn.place(x=50, y=120)
    else:
        for widget in fram.winfo_children():
            if isinstance(widget, ctk.CTkFrame) and widget.winfo_width() == 300 and widget.winfo_height() == 500:
                # Cancel any pending after events for child widgets
                for child in widget.winfo_children():
                    try:
                        # If child has any after events, cancel them
                        if hasattr(child, '_after_id') and child._after_id:
                            child.after_cancel(child._after_id)
                    except Exception:
                        pass
                widget.destroy()
    # print(count) removed for cleaner code


# ...existing code...

fram = ctk.CTkFrame(win, fg_color='#0080ff', bg_color="#0080ff", width=1350, height=630)
fram.place(x=10, y=70,)


search_type_combo = ctk.CTkComboBox(fram, values=["Name", "Class", "Id"], width=120)
search_type_combo.set("Name")
search_type_combo.place(x=600, y=30)

search_entry = ctk.CTkEntry(fram, width=200)
search_entry.place(x=720, y=30)

def searchFunction():
    search_type = search_type_combo.get()
    search_value = search_entry.get().strip()
    if search_type == "Name":
        records = Database.searchFunction(search_value)
    elif search_type == "Class":
        records = Database.search_by_class(search_value)
    elif search_type == "Id":
        try:
            id_val = int(search_value)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid numeric Id.")
            return
        records = [r for r in Database.searchFunction() if r[0] == id_val]
    else:
        records = []
    for row in tree.get_children():
        tree.delete(row)
    for record in records:
        tree.insert("", "end", values=record)

searchbtn = CTkButton(fram,
                    text="Search",
                    width=90,
                    text_color="white",
                    fg_color='#00ff00',
                    font=("italic", 15, "bold"),
                    command=searchFunction)
searchbtn.place(x=800, y=30)

# Search by class
class_list = ['1', '2', '3', '4', '5', '6', '7']
search_class_entry = ctk.CTkComboBox(fram, values=class_list, width=120)
search_class_entry.set("none")
search_class_entry.place(x=400, y=30)

def search_by_class():
    selected_class = search_class_entry.get()
    if selected_class == "none":
        messagebox.showerror("Error", "Please select a class to search.")
        return
    records = Database.search_by_class(selected_class)
    for row in tree.get_children():
        tree.delete(row)
    for record in records:
        tree.insert("", "end", values=record)

search_class_btn = CTkButton(fram,
    text="Class",
    width=50,
    text_color="white",
    fg_color='#00ccff',
    font=("italic", 15, "bold"),
    command=search_by_class)
search_class_btn.place(x=540, y=30)

def searchFunction():
    search_value = search_entry.get()
    records = Database.searchFunction(search_value)
    for row in tree.get_children():
        tree.delete(row)
    for record in records:
        tree.insert("", "end", values=record)

def add():
    if ebox1.get() == "" or ebox2.get() == "" or parent_name.get() == "" or phone_no.get() == "" or nation.get() == "":
        messagebox.showerror(title="error", message="all fields are required")
    else:
        Database.db_connect()
        Database.insert(
            ebox1.get(), ebox2.get(), radio1.get(), class_sel.get(),
            parent_name.get(), phone_no.get(), nation.get()
        )
        searchFunction()  # Refresh table

def update():
    selected = tree.focus()
    if not selected:
        messagebox.showerror("Error", "No record selected")
        return
    values = tree.item(selected, "values")
    student_id = values[0]
    Database.update(
        student_id,
        ebox1.get(), ebox2.get(), radio1.get(), class_sel.get(),
        parent_name.get(), phone_no.get(), nation.get()
    )
    searchFunction()

def delete():
    selected = tree.focus()
    if not selected:
        messagebox.showerror("Error", "No record selected")
        return
    values = tree.item(selected, "values")
    student_id = values[0]
    Database.delete(student_id)
    searchFunction()

def delete_all_records():
    if messagebox.askyesno("Confirm", "Are you sure you want to delete ALL student records?"):
        Database.delete_all()
        searchFunction()  # Refresh the table

def save():
    Database.save()

def export_treeview():
    columns = [tree.heading(col)["text"] for col in tree["columns"]]
    data = [tree.item(child)["values"] for child in tree.get_children()]

    excel_file = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx")],
        title="Save as Excel"
    )
    if excel_file:
        df = pd.DataFrame(data, columns=columns)
        df.to_excel(excel_file, index=False)

    pdf_file = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
        title="Save as PDF"
    )
    if pdf_file:
        c = canvas.Canvas(pdf_file, pagesize=letter)
        width, height = letter

        x_offsets = [30, 70, 170, 250, 320, 400, 500, 600]
        y = height - 50
        for i, col in enumerate(columns):
            c.drawString(x_offsets[i], y, str(col))

        y -= 20
        for row in data:
            for i, item in enumerate(row):
                c.drawString(x_offsets[i], y, str(item))
            y -= 20
            if y < 50:
                c.showPage()
                y = height - 50
                for i, col in enumerate(columns):
                    c.drawString(x_offsets[i], y, str(col))
                y -= 20

        c.save()

    if excel_file or pdf_file:
        messagebox.showinfo("Export", f"Data exported to:\n{excel_file}\n{pdf_file}")

def on_tree_select(event):
    selected = tree.focus()
    if not selected:
        return
    values = tree.item(selected, "values")
    if values:
        ebox1.delete(0, 'end')
        ebox1.insert(0, values[1])
        # Safely set date, handle invalid date format
        try:
            ebox2.set_date(values[2])
        except Exception:
            ebox2.set_date('')
        radio1.set(values[3])
        class_sel.set(values[4])
        parent_name.delete(0, 'end')
        parent_name.insert(0, values[5])
        phone_no.delete(0, 'end')
        phone_no.insert(0, values[6])
        nation.set(values[7])



win.title("STA")
win.geometry("1500x800")
win.config(background="lightblue")

class_list = ['1', '2', '3', '4', '5', '6', '7']
var = IntVar()
count = 0

head = ctk.CTkLabel(win,
                  text="RUTABO STUDENT MANAGMENT SYSTEM",
                  font=("roboto", 20, "bold"),
                  text_color="blue",
                  fg_color="lightblue")
head.place(x=500, y=40,)

fram = ctk.CTkFrame(win, fg_color='#0080ff', bg_color="#0080ff", width=1350, height=630)
fram.place(x=10, y=70,)

# Search
search_entry = ctk.CTkEntry(fram, width=200)
search_entry.place(x=900, y=30)

searchbtn = CTkButton(fram,
                    text="search",
                    width=90,
                    text_color="white",
                    fg_color='#00ff00',
                    font=("italic", 15, "bold"),
                    command=searchFunction)
searchbtn.place(x=800, y=30)

# Menu
menubtn = CTkButton(fram, text="menu", width=70, text_color="white", font=("italic", 15, "bold"), command=menu)
menubtn.place(x=1220, y=30)

# Student credentials frame
frame1 = ctk.CTkFrame(fram, fg_color='#8080ff', bg_color='#8080ff', width=500, height=300)
frame1.place(x=50, y=60)

head1 = ctk.CTkLabel(frame1, text="STUDENT CREDINTIALS", text_color="white", font=("roboto", 20, "bold"))
head1.place(x=120, y=10)

ctk.CTkLabel(frame1, text="Student name:", text_color="white", font=("roboto", 15, "bold")).place(x=10, y=40)
ctk.CTkLabel(frame1, text="Date of birth:", text_color="white", font=("roboto", 15, "bold")).place(x=10, y=90)
ctk.CTkLabel(frame1, text="Gender:", text_color="white", font=("roboto", 15, "bold")).place(x=10, y=150)
ctk.CTkLabel(frame1, text="Class:", text_color="white", font=("roboto", 15, "bold")).place(x=10, y=210)

ebox1 = ctk.CTkEntry(frame1, width=200)
ebox1.place(x=200, y=40)

# Use only supported options for DateEntry
ebox2 = DateEntry(frame1, width=18, date_pattern='yyyy-mm-dd')
ebox2.place(x=200, y=90)

radio1 = ctk.CTkComboBox(frame1, values=["male", "female"])
radio1.place(x=200, y=150)

class_sel = ctk.CTkComboBox(frame1, variable=var, values=class_list)
class_sel.set("none")
class_sel.place(x=200, y=210)

# Parent details frame
frame2 = ctk.CTkFrame(fram, fg_color='#8080ff', bg_color='#8080ff', width=500, height=200)
frame2.place(x=50, y=400)

head2 = ctk.CTkLabel(frame2, text="Parent details", text_color="white", font=("roboto", 20, "bold"))
head2.place(x=120, y=10)

ctk.CTkLabel(frame2, text="Parent name:", text_color="white", font=("roboto", 15, "bold")).place(x=10, y=40)
ctk.CTkLabel(frame2, text="phone number:", text_color="white", font=("roboto", 15, "bold")).place(x=10, y=90)
ctk.CTkLabel(frame2, text="Nationality:", text_color="white", font=("roboto", 15, "bold")).place(x=10, y=150)

parent_name = ctk.CTkEntry(frame2, width=200)
parent_name.place(x=200, y=40)
phone_no = ctk.CTkEntry(frame2, width=200)
phone_no.place(x=200, y=90)
nation = ctk.CTkComboBox(frame2, values=["TANZANIA"])
nation.place(x=200, y=150)


# Buttons
addbtn = ctk.CTkButton(fram, text="add",
                 text_color="white",
                 fg_color='#8080ff',
                 bg_color='#8080ff',
                 font=("italic", 15, "bold"),
                 command=add)
addbtn.place(x=600, y=590)

updatebtn = ctk.CTkButton(fram,
                    text="update",
                    text_color="white",
                    fg_color='#4bf5d3',
                    font=("italic", 15, "bold"),
                    command=update)
updatebtn.place(x=750, y=590)

deletebtn = ctk.CTkButton(fram,
                    text="delete",
                    text_color="white",
                    fg_color='#003c3c',
                    font=("italic", 15, "bold"),
                    command=delete)
deletebtn.place(x=900, y=590)

deleteallbtn = ctk.CTkButton(
    fram,
    text="delete all",
    text_color="white",
    fg_color='#ff3333',
    width=90,
    font=("italic", 15, "bold"),
    command=delete_all_records
)
deleteallbtn.place(x=1200, y=590)

savebtn = ctk.CTkButton(fram,
                  text="save",
                  text_color="white",
                  fg_color='#59a672',
                  font=("italic", 15, "bold"),
                  command=save)
savebtn.place(x=1050, y=590)

exportbtn = ctk.CTkButton(
    fram,
    text="Export",
    text_color="white",
    fg_color='#ff9900',
    width=90,
    font=("italic", 15, "bold"),
    command=export_treeview
)
exportbtn.place(x=1120, y=30)

menubtn = ctk.CTkButton(fram, text="menu", width=70, text_color="white", font=("italic", 15, "bold"), command=menu)
menubtn.place(x=1220, y=30)

def broadcast_whatsapp_message():
    if pywhatkit is None:
        messagebox.showerror("Error", "pywhatkit is not installed. Please run 'pip install pywhatkit' in your terminal.")
        return
    # Get all phone numbers from treeview
    data = [tree.item(child)["values"] for child in tree.get_children()]
    phone_numbers = [str(row[6]) for row in data if row[6]]
    if not phone_numbers:
        messagebox.showerror("Error", "No phone numbers found.")
        return
    # Prompt for message
    msg_win = ctk.CTkToplevel(win)
    msg_win.title("Broadcast WhatsApp Message")
    msg_win.geometry("400x200")
    ctk.CTkLabel(msg_win, text="Enter message to broadcast:", font=("roboto", 14)).pack(pady=10)
    msg_entry = ctk.CTkEntry(msg_win, font=("roboto", 14), width=300)
    msg_entry.pack(pady=10)
    def send_messages():
        message = msg_entry.get().strip()
        if not message:
            messagebox.showerror("Error", "Message cannot be empty.")
            return
        msg_win.destroy()
        failed = []
        for number in phone_numbers:
            # Format number for WhatsApp (with country code, e.g. +255...)
            num = number.replace(" ","").replace("-","")
            if not num.startswith("+"):
                num = "+255" + num.lstrip("0")
            try:
                pywhatkit.sendwhatmsg_instantly(num, message, wait_time=10, tab_close=True)
            except Exception as e:
                failed.append(num)
        if failed:
            messagebox.showerror("WhatsApp Error", f"Failed for: {', '.join(failed)}")
        else:
            messagebox.showinfo("Broadcast", "Message sent to all numbers!")
    ctk.CTkButton(msg_win, text="Send", font=("roboto", 14, "bold"), fg_color="#25D366", text_color="white", command=send_messages).pack(pady=10)

# WhatsApp Broadcast Button (place after all other buttons)
broadcast_btn = ctk.CTkButton(fram,
    text="WhatsApp Broadcast",
    text_color="white",
    fg_color='#25D366',
    width=170,
    font=("italic", 15, "bold"),
    command=broadcast_whatsapp_message
)
broadcast_btn.place(x=950, y=70)

# Admin Panel button (only for admin)
def penel():
    if current_user and Database.is_admin(current_user):
    
        # Add user management functionality here
        import ad  # Import the admin module to handle user management
        ad.AdminPanel() # Call the admin panel function


# Treeview for displaying students
frame3 = ctk.CTkFrame(fram, fg_color='#8080ff', bg_color="#0080ff", width=730, height=490)
frame3.place(x=600, y=70)


import ttkbootstrap as tb
tree = tb.Treeview(
    frame3,
    columns=["Id", "student name", "date of birth", "gender", "class", "parent name", "parent phone", "parent nationality"],
    show="headings",
    height=40,
    bootstyle="info",
    selectmode="extended"
)
tree.heading("Id", text="Id")
tree.heading("student name", text="Student name")
tree.heading("date of birth", text="Date of birth")
tree.heading("gender", text="Gender")
tree.heading("class", text="Class")
tree.heading("parent name", text="Parent Name")
tree.heading("parent phone", text="Parent Phone")
tree.heading("parent nationality", text="Parent Nationality")

tree.column("Id", width=50)
tree.column("student name", width=200)
tree.column("date of birth", width=100)
tree.column("gender", width=80)
tree.column("class", width=60)
tree.column("parent name", width=200)
tree.column("parent phone", width=100)
tree.column("parent nationality", width=120)


tree.place(x=10, y=10, width=700, height=400)  # Treeview smaller than total columns

# Vertical scrollbar (customtkinter)
scrollbar_y = ctk.CTkScrollbar(frame3, orientation="vertical", height=400, command=tree.yview)
scrollbar_y.place(x=710, y=10)  # Only set height here
tree.config(yscrollcommand=scrollbar_y.set)

# Horizontal scrollbar (customtkinter)
scrollbar_x = ctk.CTkScrollbar(frame3, orientation="horizontal", command=tree.xview,width=700)
scrollbar_x.place(x=10, y=460)   # Only set width here
tree.config(xscrollcommand=scrollbar_x.set)

# Bind after tree is created
tree.bind("<<TreeviewSelect>>", on_tree_select)

# Show all data on startup
searchFunction()

# Patch show_main_window to call admin panel button after window is visible
def show_main_window():
    win.deiconify()

# Start login window mainloop
login_win.mainloop()

def broadcast_whatsapp_message():
    if pywhatkit is None:
        messagebox.showerror("Error", "pywhatkit is not installed. Please run 'pip install pywhatkit' in your terminal.")
        return
    # Get all phone numbers from treeview
    data = [tree.item(child)["values"] for child in tree.get_children()]
    phone_numbers = [str(row[6]) for row in data if row[6]]
    if not phone_numbers:
        messagebox.showerror("Error", "No phone numbers found.")
        return
    # Prompt for message
    msg_win = ctk.CTkToplevel(win)
    msg_win.title("Broadcast WhatsApp Message")
    msg_win.geometry("400x200")
    ctk.CTkLabel(msg_win, text="Enter message to broadcast:", font=("roboto", 14)).pack(pady=10)
    msg_entry = ctk.CTkEntry(msg_win, font=("roboto", 14), width=300)
    msg_entry.pack(pady=10)
    def send_messages():
        message = msg_entry.get().strip()
        if not message:
            messagebox.showerror("Error", "Message cannot be empty.")
            return
        msg_win.destroy()
        failed = []
        for number in phone_numbers:
            # Format number for WhatsApp (with country code, e.g. +255...)
            num = number.replace(" ","").replace("-","")
            if not num.startswith("+"):
                num = "+255" + num.lstrip("0")
            try:
                pywhatkit.sendwhatmsg_instantly(num, message, wait_time=10, tab_close=True)
            except Exception as e:
                failed.append(num)
        if failed:
            messagebox.showerror("WhatsApp Error", f"Failed for: {', '.join(failed)}")
        else:
            messagebox.showinfo("Broadcast", "Message sent to all numbers!")
    ctk.CTkButton(msg_win, text="Send", font=("roboto", 14, "bold"), fg_color="#25D366", text_color="white", command=send_messages).pack(pady=10)
