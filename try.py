import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
import re

class Person:
    def __init__(self, user_id, password, name, email):
        self.user_id = user_id
        self.password = password
        self.name = name
        self.email = email
        self.is_active = True

class Teacher(Person):
    def __init__(self, user_id, password, name, email, subject):
        super().__init__(user_id, password, name, email)
        self.subject = subject

class Student(Person):
    def __init__(self, user_id, password, name, email, student_type):
        super().__init__(user_id, password, name, email)
        self.student_type = student_type

class AcademicUnit:
    def __init__(self):
        self.users = []
        self.login_attempts = {}

    def register_user(self, user_id, password, name, email, user_type, subject=None, student_type=None):
        if any(user.user_id == user_id for user in self.users if user.is_active):
            return False
        if self.is_valid_password(password):
            if user_type == "Teacher":
                user = Teacher(user_id, password, name, email, subject)
            elif user_type == "Student":
                user = Student(user_id, password, name, email, student_type)
            else:
                raise ValueError("Invalid user type")
            self.users.append(user)
            self.save_data()
            messagebox.showinfo("Registration", "User registered successfully.")

    def authenticate_user(self, user_id, password):
        if user_id not in self.login_attempts:
            self.login_attempts[user_id] = 0

        for user in self.users:
            if user.user_id == user_id and user.password == password and user.is_active:
                # Reset login attempts on successful login
                self.login_attempts[user_id] = 0
                return True
        # Increment login attempts and deactivate account after three wrong attempts
        self.login_attempts[user_id] += 1
        if self.login_attempts[user_id] >= 3:
            self.deactivate_account(user_id)
        return False

    def deactivate_account(self, user_id):
        for user in self.users:
            if user.user_id == user_id:
                user.is_active = False
                messagebox.showinfo("Account Deactivation", "Your account has been deactivated due to multiple incorrect login attempts.")
                break

    def update_user_profile(self, user_id, new_name, new_email):
        for user in self.users:
            if user.user_id == user_id:
                user.name = new_name
                user.email = new_email
                messagebox.showinfo("Update", "User profile updated successfully.")

    def deregister_user(self, user_id):
        for user in self.users:
            if user.user_id == user_id:
                user.is_active = False
                self.users.remove(user)
                messagebox.showinfo("Deregistration", "Deregistration request submitted. Your account will be deactivated.")

    def is_valid_password(self, password):
        if 8 <= len(password) <= 12 and any(c.isupper() for c in password) \
                and any(c.isdigit() for c in password) and any(c.islower() for c in password) \
                and any(c in "!@#$%&*" for c in password) and ' ' not in password:
            return True
        return False

    def is_valid_email(self, email):
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(pattern, email) is not None
    
    def save_data(self, filename='project.txt'):
        with open("project.txt", 'w') as file:
            for user in self.users:
                if isinstance(user, Teacher):
                    line = f"Teacher,{user.user_id},{user.password},{user.name},{user.email},{user.subject}\n"
                elif isinstance(user, Student):
                    line = f"Student,{user.user_id},{user.password},{user.name},{user.email},{user.student_type}\n"
                else:
                    line = f"Person,{user.user_id},{user.password},{user.name},{user.email}\n"
                file.write(line)

    def load_data(self, filename='project.txt'):
        try:
            with open(filename, 'r') as file:
                for line in file:
                    user_data = line.strip().split(',')
                    if len(user_data) >= 5:
                        user_type = user_data[0]
                        user_id = user_data[1]
                        password = user_data[2]
                        name = user_data[3]
                        email = user_data[4]

                        if user_type == "Teacher":
                            subject = user_data[5]
                            user = Teacher(user_id, password, name, email, subject)
                        elif user_type == "Student":
                            student_type = user_data[5]
                            user = Student(user_id, password, name, email, student_type)
                        else:
                            user = Person(user_id, password, name, email)

                        self.users.append(user)
        except FileNotFoundError:
            # Handle the case where the file is not found
            pass
class PersonTypeDialog(simpledialog.Dialog):
    def body(self, master):
        tk.Label(master, text="Select your person type:").grid(row=0, sticky=tk.W)
        self.person_type_var = tk.StringVar(value="Student")  # Default value
        tk.Checkbutton(master, text="Student", variable=self.person_type_var, onvalue="Student", offvalue="").grid(row=1)
        tk.Checkbutton(master, text="Teacher", variable=self.person_type_var, onvalue="Teacher", offvalue="").grid(row=2)

    def apply(self):
        self.result = self.person_type_var.get()
        self.destroy()
        # print("Selected Person Type:", self.result)

class App:
    def __init__(self, root):
        self.academic_unit = AcademicUnit()
        self.current_user_id = None
        self.root = root

        self.root.title("Academic Unit Management System")
        self.root.geometry("500x400")
        self.academic_unit.load_data()
        self.create_widgets()

    def create_widgets(self):
        self.frame = tk.Frame(self.root)
        font_tuple = ('Helvetica', 12, 'bold')
        self.frame.pack(expand=True, fill='both', padx=20, pady=20)

        tk.Label(self.frame, text="User ID",font=font_tuple).grid(row=0, column=0, padx=10, pady=10)
        tk.Label(self.frame, text="Password",font=font_tuple).grid(row=1, column=0, padx=10, pady=10)

        self.user_id_entry = tk.Entry(self.frame,width=30,borderwidth=3)
        self.password_entry = tk.Entry(self.frame, show='*',width=30,borderwidth=3)
        self.user_id_entry.grid(row=0, column=1, padx=10, pady=10)
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)
        self.show_password_var = tk.BooleanVar(value=False)
        tk.Checkbutton(self.frame, text="Show Password", variable=self.show_password_var, command=self.toggle_show_password).grid(row=1, column=2, columnspan=2, pady=10,sticky='E')
        # New "Show Password" button

        self.register_btn = tk.Button(self.frame, text="Register", command=self.register_user, bg="#80669d", fg="Black",font=('Helvetica', 12))
        self.sign_in_btn = tk.Button(self.frame, text="Sign In", command=self.sign_in, bg="#80669d", fg="Black",font=('Helvetica', 12))

        self.register_btn.grid(row=2, column=0, columnspan=2, pady=10)
        self.sign_in_btn.grid(row=3, column=0, columnspan=2, pady=10)

        self.update_btn = tk.Button(self.frame, text="Update Profile", command=self.update_profile, state=tk.DISABLED, bg="#80669d", fg="Black",font=('Helvetica', 12))
        self.update_btn.grid(row=4, column=0, columnspan=2, pady=10)
        self.deregister_btn = tk.Button(self.frame, text="Deregister", command=self.deregister_user, state=tk.DISABLED, bg="#80669d", fg="Black",font=('Helvetica', 12))
        self.deregister_btn.grid(row=5, column=0, columnspan=2, pady=10)

        self.print_btn = tk.Button(self.frame, text="Print Data", command=self.print_user_data, state=tk.DISABLED, bg="#80669d", fg="Black",font=('Helvetica', 12))
        self.print_btn.grid(row=8, column=0, columnspan=2, pady=10)
        
            
    def toggle_show_password(self):
        # Toggle the password visibility based on the state of the "Show Password" button
        show_password = self.show_password_var.get()
        self.password_entry["show"] = "" if show_password else "*"

    def register_user(self):
        user_id = self.user_id_entry.get()
        password = self.password_entry.get()

        if self.is_valid_email(user_id) and self.academic_unit.is_valid_password(password):
            # Check if User ID is unique
            if any(user.user_id == user_id for user in self.academic_unit.users):
                messagebox.showerror("Error", "User ID already exists. Please choose a different User ID.")
                return

            # Prompt the user for additional information using custom dialog
            person_type_dialog = PersonTypeDialog(self.root)
            person_type = person_type_dialog.result

            if person_type:
                name = simpledialog.askstring("Registration", "Enter your name:")
                email = simpledialog.askstring("Registration", "Enter your email:")
                if person_type.lower() == "teacher":
                    subject = simpledialog.askstring("Registration", "Enter your subject:")
                    # self.academic_unit.users[-1].subject = subject
                elif person_type.lower() == "student":
                    student_type = simpledialog.askstring("Registration", "Enter your student type (UG/PG):")
                    # self.academic_unit.users[-1].student_type = student_type
                # Attempt to register the user
                if self.academic_unit.register_user(user_id, password, name, email, person_type):
                    # Registration successful
                    if person_type.lower() == "teacher":
                        # subject = simpledialog.askstring("Registration", "Enter your subject:")
                        self.academic_unit.users[-1].subject = subject
                    elif person_type.lower() == "student":
                        # student_type = simpledialog.askstring("Registration", "Enter your student type (UG/PG):")
                        self.academic_unit.users[-1].student_type = student_type

                    messagebox.showinfo("Registration", "User registered successfully.")
                    # Clear the password entry after successful registration
                    self.password_entry.delete(0, tk.END)
            else:messagebox.showerror("Error", "Person type is required.")
        else:
            messagebox.showerror("Error", "Invalid email or password. Please enter valid values.")

    def sign_in(self):
        user_id = self.user_id_entry.get()
        password = self.password_entry.get()

        if self.academic_unit.authenticate_user(user_id, password):
            self.current_user_id = user_id
            messagebox.showinfo("Sign In", "Authentication successful.")
            self.enable_profile_buttons()
        else:
            messagebox.showerror("Error", "Authentication failed. Check your credentials.")

    def enable_profile_buttons(self):
        self.update_btn["state"] = tk.NORMAL
        self.print_btn["state"] = tk.NORMAL
        self.deregister_btn["state"] = tk.NORMAL
        self.register_btn["text"] = "New Registration"
        self.register_btn["command"] = self.new_registration

    def new_registration(self):
        self.disable_profile_buttons()
        self.register_btn["text"] = "Register"
        self.register_btn["command"] = self.register_user

    def update_profile(self):
        if self.current_user_id:
            new_name = simpledialog.askstring("Update Profile", "Enter new name:")
            new_email = simpledialog.askstring("Update Profile", "Enter new email:")

            if new_name and new_email:
                self.academic_unit.update_user_profile(self.current_user_id, new_name, new_email)
                self.academic_unit.save_data()
            else:
                messagebox.showerror("Error", "Name and email are required.")
        else:
            messagebox.showerror("Error", "Please sign in first.")

    def deregister_user(self):
        if self.current_user_id:
            response = messagebox.askquestion("Deregister", "Are you sure you want to deregister?")
            if response == "yes":
                self.academic_unit.deregister_user(self.current_user_id)
                self.current_user_id = None
                self.disable_profile_buttons()
                self.academic_unit.save_data()
                self.new_registration()
        else:
            messagebox.showerror("Error", "Please sign in first.")

    def disable_profile_buttons(self):
        self.update_btn["state"] = tk.DISABLED
        self.deregister_btn["state"] = tk.DISABLED
        self.print_btn["state"] = tk.DISABLED

    def is_valid_password(self, password):
        if 8 <= len(password) <= 12 and any(c.isupper() for c in password) \
                and any(c.isdigit() for c in password) and any(c.islower() for c in password) \
                and any(c in "!@#$%&*" for c in password) and ' ' not in password:
            return True
        return False

    def is_valid_email(self, email):
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(pattern, email) is not None

    def print_user_data(self):
        if self.current_user_id:
            # Create a new window for displaying user data
            top_window = tk.Toplevel(self.root)
            top_window.geometry("250x250")
            titlebar_frame = tk.Frame(top_window, bg="lightblue", height=30)
            titlebar_frame.pack(fill=tk.X)
            title_label = tk.Label(titlebar_frame, text="User Data", fg="purple", font=("Arial", 12, "bold"))
            title_label.pack(pady=5)
            top_window.title("User Data")

            # Find the current user in the academic unit
            current_user = next((user for user in self.academic_unit.users if user.user_id == self.current_user_id), None)


            if current_user:
                # Display user data in the new window
                tk.Label(top_window, text="User ID: " + current_user.user_id).pack()
                tk.Label(top_window, text="Name: " + current_user.name).pack()
                tk.Label(top_window, text="Email: " + current_user.email).pack()

                if hasattr(current_user, 'subject') and current_user.subject is not None:
                    tk.Label(top_window, text="Subject: " + current_user.subject).pack()
                    # Check if student_type attribute is not None before concatenating
                if hasattr(current_user, 'student_type') and current_user.student_type is not None:
                    tk.Label(top_window, text="Student Type: " + current_user.student_type).pack()
                # Additional details for teachers and students
            else:
                messagebox.showerror("Error", "User not found.")
        else:
            messagebox.showerror("Error", "Please sign in first.")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()

