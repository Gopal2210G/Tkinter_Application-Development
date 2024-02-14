import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from tkinter import simpledialog
import re

from styles import *

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
            
            CTkMessagebox(title="Registration", message="User registered successfully.", icon="check", button_color=button_color, width=pop_up_width, 
                          button_hover_color=button_hover_color, icon_size=(icon_size, icon_size), font=(font, font_size), sound=pop_up_sound_on)

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
                CTkMessagebox(title="Account Deactivation", message="Your account has been deactivated due to multiple incorrect login attempts.", icon="warning", button_color=button_color, width=pop_up_width, 
                              button_hover_color=button_hover_color, icon_size=(icon_size, icon_size), font=(font, font_size), sound=pop_up_sound_on)
                break

    def update_user_profile(self, user_id, new_name, new_email):
        for user in self.users:
            if user.user_id == user_id:
                user.name = new_name
                user.email = new_email
                CTkMessagebox(title="Update", message="User profile updated successfully.", icon="check", button_color=button_color, width=pop_up_width, 
                              button_hover_color=button_hover_color, icon_size=(icon_size, icon_size), font=(font, font_size), sound=pop_up_sound_on)

    def deregister_user(self, user_id):
        for user in self.users:
            if user.user_id == user_id:
                user.is_active = False
                self.users.remove(user)
                CTkMessagebox(title="Deregistration", message="Deregistration request submitted. Your account will be deactivated.", icon="info", button_color=button_color, width=pop_up_width, 
                              button_hover_color=button_hover_color, icon_size=(icon_size, icon_size), font=(font, font_size), sound=pop_up_sound_on)

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
        ctk.CTkLabel(master, text="What's your role:", text_color="black").grid(row=0, sticky=ctk.W)
        self.person_type_var = ctk.StringVar(value="Student")  # Default value
        ctk.CTkCheckBox(master, text="Student", variable=self.person_type_var, onvalue="Student", offvalue="", text_color="black").grid(row=1)
        ctk.CTkCheckBox(master, text="Teacher", variable=self.person_type_var, onvalue="Teacher", offvalue="", text_color="black").grid(row=2)

    def apply(self):
        self.result = self.person_type_var.get()
        self.destroy()
        # print("Selected Person Type:", self.result)

class App:
    def __init__(self, root):
        self.academic_unit = AcademicUnit()
        self.current_user_id = None
        self.root = root
        self.options_shwon = False

        self.root.title("Academic Unit Management System")
        self.root.geometry("500x500")
        self.academic_unit.load_data()
        self.create_widgets()

    def create_widgets(self):
        self.frame = ctk.CTkFrame(self.root)
        self.frame.grid_propagate(False)
        self.frame.pack(expand=True, fill='both', padx=20, pady=20)

        self.user_id_entry = ctk.CTkEntry(self.frame,width=200, text_color="White", placeholder_text="User ID", font=(font, font_size*1.3), height=font_size*2.5)
        self.password_entry = ctk.CTkEntry(self.frame,width=200, show="*", text_color="White", placeholder_text="Password", font=(font, font_size*1.3), height=font_size*2.5)
        self.user_id_entry.grid(row=0, column=1, padx=10, pady=10)
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)
        self.show_password_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(self.frame, text="Show Password", fg_color=button_color, hover_color=button_hover_color, variable=self.show_password_var, command=self.toggle_show_password).grid(row=2, column=1, columnspan=2, pady=10)
        # New "Show Password" CTkButton

        self.register_btn = ctk.CTkButton(self.frame, text="Register", command=self.register_user, fg_color=button_color, hover_color=button_hover_color,font=('Helvetica', 12), text_color="White")
        self.sign_in_btn = ctk.CTkButton(self.frame, text="Sign In", command=self.sign_in, fg_color=button_color, hover_color=button_hover_color, font=('Helvetica', 12), text_color="White")

        self.register_btn.grid(row=3, column=1, columnspan=2, pady=10)
        self.sign_in_btn.grid(row=4, column=1, columnspan=2, pady=10)

        self.more_options_btn = ctk.CTkButton(self.frame, text="more options", text_color=button_color, hover=False, fg_color="transparent", bg_color="transparent", command=self.show_options)
        self.more_options_btn.grid(row=5, column=1, columnspan=2, pady=5)


        self.update_btn = ctk.CTkButton(self.frame, text="Update Profile", command=self.update_profile, state=ctk.DISABLED, fg_color=button_color,  hover_color=button_hover_color,font=('Helvetica', 12), text_color="White")
        self.update_btn.grid(row=6, column=1, columnspan=2, pady=10)

        self.deregister_btn = ctk.CTkButton(self.frame, text="Deregister", command=self.deregister_user, state=ctk.DISABLED, fg_color=button_color, hover_color=button_hover_color,font=('Helvetica', 12), text_color="White")
        self.deregister_btn.grid(row=7, column=1, columnspan=2, pady=10)

        self.print_btn = ctk.CTkButton(self.frame, text="Print Data", command=self.print_user_data, state=ctk.DISABLED, fg_color=button_color, hover_color=button_hover_color,font=('Helvetica', 12), text_color="White")
        self.print_btn.grid(row=8, column=1, columnspan=2, pady=10)

        self.update_btn.grid_forget()
        self.deregister_btn.grid_forget()
        self.print_btn.grid_forget()

    
    def show_options(self):
        if not self.options_shwon:
            self.options_shwon = True
            self.update_btn.grid(row=6, column=1, columnspan=2, pady=10)
            self.deregister_btn.grid(row=7, column=1, columnspan=2, pady=10)
            self.print_btn.grid(row=8, column=1, columnspan=2, pady=10)
        
        else:
            self.options_shwon = False
            self.update_btn.grid_forget()
            self.deregister_btn.grid_forget()
            self.print_btn.grid_forget()

            
    def toggle_show_password(self):
        # Toggle the password visibility based on the state of the "Show Password" CTkButton
        show_password = self.show_password_var.get()
        if show_password:
            self.password_entry.configure(show="")
        else:
            self.password_entry.configure(show="*")

    def register_user(self):
        user_id = self.user_id_entry.get()
        password = self.password_entry.get()

        if self.is_valid_email(user_id) and self.academic_unit.is_valid_password(password):
            # Check if User ID is unique
            if any(user.user_id == user_id for user in self.academic_unit.users):
                CTkMessagebox(title="Error", message="User ID already exists. Please choose a different User ID.", icon="cancel", button_color=button_color, width=pop_up_width, 
                              button_hover_color=button_hover_color, icon_size=(icon_size, icon_size), font=(font, font_size), sound=pop_up_sound_on)
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

                    CTkMessagebox(title="Registration", message="User registered successfully.", icon="check", button_color=button_color, width=pop_up_width, 
                                  button_hover_color=button_hover_color, icon_size=(icon_size, icon_size), font=(font, font_size), sound=pop_up_sound_on)
                    # Clear the password CTkEntry after successful registration
                    self.password_entry.delete(0, ctk.END)
            else:
                CTkMessagebox(title="Error", message="Role is required.", icon="cancel", button_color=button_color, 
                              button_hover_color=button_hover_color, icon_size=(icon_size, icon_size), font=(font, font_size), sound=pop_up_sound_on, width=pop_up_width)
        else:
            CTkMessagebox(title="Error", message="Invalid email or password. Please enter valid values.", icon="cancel", button_color=button_color, 
                          button_hover_color=button_hover_color, icon_size=(icon_size, icon_size), font=(font, font_size), sound=pop_up_sound_on, width=pop_up_width)

    def sign_in(self):
        user_id = self.user_id_entry.get()
        password = self.password_entry.get()

        if self.academic_unit.authenticate_user(user_id, password):
            self.current_user_id = user_id
            CTkMessagebox(title="Sign In", message="Authentication successful.", icon="check", button_color=button_color, width=pop_up_width, 
                          button_hover_color=button_hover_color, icon_size=(icon_size, icon_size), font=(font, font_size), sound=pop_up_sound_on)
            self.enable_profile_buttons()
        else:
            CTkMessagebox(title="Error", message="Authentication failed. Check your credentials.", icon="cancel", button_color=button_color, width=pop_up_width, 
                          button_hover_color=button_hover_color, icon_size=(icon_size, icon_size), font=(font, font_size), sound=pop_up_sound_on)

    def enable_profile_buttons(self):
        self.update_btn["state"] = ctk.NORMAL
        self.print_btn["state"] = ctk.NORMAL
        self.deregister_btn["state"] = ctk.NORMAL
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
                CTkMessagebox(title="Error", message="Name and email are required.", icon="cancel", button_color=button_color, width=pop_up_width, 
                              button_hover_color=button_hover_color, icon_size=(icon_size, icon_size), font=(font, font_size), sound=pop_up_sound_on)
        else:
            CTkMessagebox(title="Error", message="Please sign in first.", icon="cancel", button_color=button_color, width=pop_up_width, 
                          button_hover_color=button_hover_color, icon_size=(icon_size, icon_size), font=(font, font_size), sound=pop_up_sound_on)

    def deregister_user(self):
        if self.current_user_id:
            response = CTkMessagebox(title="Deregister", message="Are you sure you want to deregister?.", icon="info", button_color=button_color, width=pop_up_width, 
                                     button_hover_color=button_hover_color, icon_size=(icon_size, icon_size), font=(font, font_size), sound=pop_up_sound_on, option_1="no", option_2="yes")
            if response.get() == "yes":
                self.academic_unit.deregister_user(self.current_user_id)
                self.current_user_id = None
                self.disable_profile_buttons()
                self.academic_unit.save_data()
                self.new_registration()
        else:
            CTkMessagebox(title="Error", message="Please sign in first.", icon="cancel", button_color=button_color, width=pop_up_width, 
                          button_hover_color=button_hover_color, icon_size=(icon_size, icon_size), font=(font, font_size), sound=pop_up_sound_on)

    def disable_profile_buttons(self):
        self.update_btn["state"] = ctk.DISABLED
        self.deregister_btn["state"] = ctk.DISABLED
        self.print_btn["state"] = ctk.DISABLED

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
            top_window = ctk.Toplevel(self.root)
            top_window.geometry("250x250")
            titlebar_frame = ctk.CTkFrame(top_window, fg_color="lightblue", height=30)
            titlebar_frame.pack(fill=ctk.X)
            title_label = ctk.CTkLabel(titlebar_frame, text="User Data", bg_color="purple", font=("Arial", 12, "bold"))
            title_label.pack(pady=5)
            top_window.title("User Data")

            # Find the current user in the academic unit
            current_user = next((user for user in self.academic_unit.users if user.user_id == self.current_user_id), None)


            if current_user:
                # Display user data in the new window
                ctk.CTkLabel(top_window, text="User ID: " + current_user.user_id).pack()
                ctk.CTkLabel(top_window, text="Name: " + current_user.name).pack()
                ctk.CTkLabel(top_window, text="Email: " + current_user.email).pack()

                if hasattr(current_user, 'subject') and current_user.subject is not None:
                    ctk.CTkLabel(top_window, text="Subject: " + current_user.subject).pack()
                    # Check if student_type attribute is not None before concatenating
                if hasattr(current_user, 'student_type') and current_user.student_type is not None:
                    ctk.CTkLabel(top_window, text="Student Type: " + current_user.student_type).pack()
                # Additional details for teachers and students
            else:
                CTkMessagebox(title="Error", message="User not found.", icon="cancel", button_color=button_color, width=pop_up_width, 
                              button_hover_color=button_hover_color, icon_size=(icon_size, icon_size), font=(font, font_size), sound=pop_up_sound_on)
        else:
            CTkMessagebox(title="Error", message="Please sign in first.", icon="cancel", button_color=button_color, width=pop_up_width, 
                          button_hover_color=button_hover_color, icon_size=(icon_size, icon_size), font=(font, font_size), sound=pop_up_sound_on)


if __name__ == "__main__":
    root = ctk.CTk()
    app = App(root)
    root.mainloop()

