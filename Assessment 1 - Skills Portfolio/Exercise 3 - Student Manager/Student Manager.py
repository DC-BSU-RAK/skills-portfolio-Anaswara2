import customtkinter as ctk
from tkinter import ttk, messagebox
import tkinter as tk
import os
from PIL import Image, ImageTk

# CONFIGURATION
# Setting up the look and feel. I prefer Dark mode, looks cleaner.
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Grab the folder where this script lives so we can find our files easily
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_NAME = os.path.join(SCRIPT_DIR, "studentMarks.txt")
# Switching to a static image for the background to avoid video loading issues
BG_IMAGE_PATH = os.path.join(SCRIPT_DIR, "bluebg.jpg")

# DATA MODEL
class Student:
    """
    Simple class to hold student info. 
    Using a class makes it way easier to handle sorting and calculations later.
    """
    def __init__(self, code, name, c1, c2, c3, exam):
        self.code = str(code).strip() # Clean up any accidental spaces
        self.name = name.strip()
        self.c1 = int(c1)
        self.c2 = int(c2)
        self.c3 = int(c3)
        self.exam = int(exam)

    @property
    def coursework_total(self):
        # Just summing up the three coursework marks
        return self.c1 + self.c2 + self.c3

    @property
    def total_score(self):
        # Max possible score is 160 (60 for coursework + 100 for exam)
        return self.coursework_total + self.exam

    @property
    def percentage(self):
        # Calculating the percentage based on the max score of 160
        return (self.total_score / 160) * 100

    @property
    def grade(self):
        # Standard grading boundaries. 
        # Using a property here means we don't have to recalculate it manually every time.
        p = self.percentage
        if p >= 70: return 'A'
        elif p >= 60: return 'B'
        elif p >= 50: return 'C'
        elif p >= 40: return 'D'
        else: return 'F'

# MAIN APPLICATION 
class StudentApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Basic window setup
        self.title("Student Data Analyser")
        self.geometry("1100x700")

        # Creating a label to hold our background image.
        # We'll place it later in the welcome screen function.
        self.bg_label = tk.Label(self, bg="black")
        
        # We need to keep a reference to the image object, otherwise Python's 
        # garbage collector throws it away and the image vanishes!
        self.bg_image_ref = None

        # Initialize our list of students and load data from the file immediately
        self.students = []
        self.ensure_file_exists() # Make sure we don't crash if the file is missing
        self.load_data()

        # Placeholders for our main UI sections
        self.sidebar = None
        self.content = None
        
        # This list keeps track of buttons/text on the welcome screen so we can delete them easily
        self.welcome_widgets = []

        # Configure the main grid so things stretch properly
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Kick things off by showing the welcome page
        self.show_welcome_screen()

    # BACKGROUND IMAGE
    def update_background_image(self, event=None):
        """
        This handles resizing the background image when the window size changes.
        """
        # Get the current size of the app window
        width = self.winfo_width()
        height = self.winfo_height()
        
        # Avoid doing work if the window is tiny (like during startup)
        if width < 2 or height < 2:
            return

        # Check if the background file is actually there
        if not os.path.exists(BG_IMAGE_PATH):
            print(f"Error: Background image not found at {BG_IMAGE_PATH}")
            self.bg_label.configure(image="", bg="#1a1a1a") # Fallback to dark grey
            return

        try:
            # Open the image with Pillow
            pil_image = Image.open(BG_IMAGE_PATH)
            
            # Resize it to match the window. LANCZOS gives the best quality for this.
            resized_image = pil_image.resize((width, height), Image.Resampling.LANCZOS)
            
            # Convert it to a format Tkinter understands
            self.bg_image_ref = ImageTk.PhotoImage(resized_image)
            
            # Update the label
            self.bg_label.configure(image=self.bg_image_ref, bg="black")

        except Exception as e:
            print(f"Error loading background image: {e}")
            # Just use a solid color if something breaks
            self.bg_label.configure(image="", bg="#1a1a1a")


    def show_background(self):
        # Stretch the label to fill the whole screen and send it to the back
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_label.lower()
        
        # Trigger an immediate update so we don't see a blank screen
        self.update_background_image()
        
        # Whenever the user resizes the window, update the image size
        self.bind("<Configure>", self.update_background_image)

    def hide_background(self):
        # Stop listening for resize events and hide the label
        self.unbind("<Configure>")
        self.bg_label.place_forget()

    # WELCOME SCREEN
    def show_welcome_screen(self):
        # Turn on the fancy background
        self.show_background()
        
        # If the dashboard was open, hide it
        if self.sidebar: self.sidebar.grid_forget()
        if self.content: self.content.grid_forget()

        # Placing widgets directly on the root window (self) instead of a frame
        # This fixes issues where frames might have weird background colors blocking the image
        
        # Main Title
        lbl1 = ctk.CTkLabel(self, text="STUDENT ANALYTICS", font=("Arial Black", 40), text_color="white")
        lbl1.place(relx=0.5, rely=0.4, anchor="center")
        self.welcome_widgets.append(lbl1) # Add to list so we can clear it later

        # Subtitle
        lbl2 = ctk.CTkLabel(self, text="Data Processing System", font=("Arial", 16), text_color="#ddd")
        lbl2.place(relx=0.5, rely=0.48, anchor="center")
        self.welcome_widgets.append(lbl2)

        # The big button to enter the app
        btn = ctk.CTkButton(self, text="LOAD DATA", font=("Arial", 15, "bold"), height=50, width=200, corner_radius=25,
                            fg_color="white", text_color="black", hover_color="#ddd",
                            command=self.enter_app)
        btn.place(relx=0.5, rely=0.6, anchor="center")
        self.welcome_widgets.append(btn)

    def enter_app(self):
        # Transitioning to the main app
        self.hide_background()
        
        # Clean up all the text/buttons from the welcome screen
        for w in self.welcome_widgets:
            w.destroy()
        self.welcome_widgets.clear()
        
        # Create the main layout frames if they don't exist yet
        if not self.sidebar: self.create_sidebar()
        if not self.content: self.content = ctk.CTkFrame(self, corner_radius=0, fg_color="#1a1a1a")

        # Show the dashboard layout
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.content.grid(row=0, column=1, sticky="nsew")
        
        # Default view
        self.show_view_all()

    # NAVIGATION
    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#111111")
        
        # Making the sidebar scrollable in case we add tons of buttons later
        scroll_sidebar = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        scroll_sidebar.pack(fill="both", expand=True)
        
        ctk.CTkLabel(scroll_sidebar, text="MENU", font=("Arial Black", 20), text_color="#3B8ED0").pack(pady=(20, 20))

        # Core functionality buttons
        self.add_menu_btn(scroll_sidebar, "View All Records", self.show_view_all)
        self.add_menu_btn(scroll_sidebar, "Find Student", self.show_find_student)
        self.add_menu_btn(scroll_sidebar, "Highest Score", self.show_highest)
        self.add_menu_btn(scroll_sidebar, "Lowest Score", self.show_lowest)

        # Separator line for aesthetics
        ctk.CTkFrame(scroll_sidebar, height=2, fg_color="#333").pack(fill="x", padx=20, pady=10)
        
        # Extension/Edit buttons
        self.add_menu_btn(scroll_sidebar, "Sort Records", self.show_sort_menu)
        self.add_menu_btn(scroll_sidebar, "Add Student", lambda: self.show_student_form())
        self.add_menu_btn(scroll_sidebar, "Update Record", self.show_update_selection)
        self.add_menu_btn(scroll_sidebar, "Delete Record", self.show_delete_selection)

        # Exit button at the bottom
        ctk.CTkButton(self.sidebar, text="EXIT", fg_color="transparent", text_color="#ff5555",
                      hover_color="#2b1111", command=self.show_welcome_screen).pack(side="bottom", pady=20)

    def add_menu_btn(self, parent, text, cmd):
        # Helper to create consistent buttons without repeating code
        ctk.CTkButton(parent, text=text, command=cmd, fg_color="transparent", 
                      hover_color="#333", anchor="w", height=45, font=("Arial", 13, "bold")).pack(fill="x", padx=10, pady=5)

    def clear_content(self):
        # Wipes the main content area clean before showing a new page
        for w in self.content.winfo_children(): w.destroy()

    # CORE FEATURES
    def show_view_all(self, students_to_show=None):
        self.clear_content()
        
        # If specific students weren't passed (like from a sort), show everyone
        target_list = students_to_show if students_to_show is not None else self.students

        container = ctk.CTkFrame(self.content, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_text = "All Student Records" if students_to_show is None else "Sorted Records"
        ctk.CTkLabel(container, text=title_text, font=("Arial", 26, "bold"), text_color="white").pack(anchor="w", pady=(0, 20))

        # Using Treeview for the main table because it handles columns nicely
        style = ttk.Style()
        style.theme_use("clam")
        # Styling the treeview to match our dark theme
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", rowheight=35, borderwidth=0)
        style.configure("Treeview.Heading", background="#1f1f1f", foreground="white", relief="flat", font=("Arial", 11, "bold"))
        style.map("Treeview", background=[("selected", "#3B8ED0")])

        cols = ("Name", "Code", "Coursework", "Exam", "Percent", "Grade")
        tree_frame = ctk.CTkFrame(container, fg_color="#2b2b2b")
        tree_frame.pack(fill="both", expand=True)

        tree = ttk.Treeview(tree_frame, columns=cols, show="headings")
        
        # Add scrollbar just in case list is long
        sb = ctk.CTkScrollbar(tree_frame, command=tree.yview)
        sb.pack(side="right", fill="y")
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Define column headers
        tree.heading("Name", text="Student Name")
        tree.heading("Code", text="Number")
        tree.heading("Coursework", text="C-Work Total")
        tree.heading("Exam", text="Exam Mark")
        tree.heading("Percent", text="Overall %")
        tree.heading("Grade", text="Grade")

        # Set column widths and alignment
        tree.column("Name", width=200, anchor="w")
        tree.column("Code", width=100, anchor="center")
        tree.column("Coursework", width=120, anchor="center")
        tree.column("Exam", width=100, anchor="center")
        tree.column("Percent", width=100, anchor="center")
        tree.column("Grade", width=80, anchor="center")

        # Populate the table
        for s in target_list:
            tree.insert("", "end", values=(s.name, s.code, s.coursework_total, s.exam, f"{s.percentage:.1f}%", s.grade))
        
        # SUMMARY SECTION
        # Calculates totals and averages for the footer
        total_students = len(target_list)
        avg_percentage = sum(s.percentage for s in target_list) / total_students if total_students > 0 else 0

        summary_text = f"Total Students: {total_students}   |   Class Average: {avg_percentage:.1f}%"
        ctk.CTkLabel(container, text=summary_text, font=("Arial", 18, "bold"), text_color="#3B8ED0").pack(pady=(20, 0), anchor="e")

    def show_sort_menu(self):
        self.clear_content()
        container = ctk.CTkFrame(self.content, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(container, text="Sort Student Records", font=("Arial", 26, "bold"), text_color="white").pack(anchor="w", pady=(0, 20))

        options_frame = ctk.CTkFrame(container, fg_color="#2b2b2b")
        options_frame.pack(fill="x", pady=20)

        # Variables to hold user choices
        sort_var = tk.StringVar(value="Name")
        order_var = tk.BooleanVar(value=True)

        # Radio buttons for Criteria
        ctk.CTkLabel(options_frame, text="Sort By:", font=("Arial", 16, "bold")).pack(pady=10)
        ctk.CTkRadioButton(options_frame, text="Student Name", variable=sort_var, value="Name").pack(pady=5)
        ctk.CTkRadioButton(options_frame, text="Total Score", variable=sort_var, value="Score").pack(pady=5)
        ctk.CTkRadioButton(options_frame, text="Student Code", variable=sort_var, value="Code").pack(pady=5)

        # Radio buttons for Order
        ctk.CTkLabel(options_frame, text="Order:", font=("Arial", 16, "bold")).pack(pady=(20, 10))
        ctk.CTkRadioButton(options_frame, text="Ascending (A-Z, Low-High)", variable=order_var, value=True).pack(pady=5)
        ctk.CTkRadioButton(options_frame, text="Descending (Z-A, High-Low)", variable=order_var, value=False).pack(pady=5)

        def apply_sort():
            # Actually perform the sort when button is clicked
            reverse = not order_var.get()
            key = sort_var.get()
            sorted_list = []
            
            # Python's sort is stable, using lambdas to pick the attribute to sort by
            if key == "Name": sorted_list = sorted(self.students, key=lambda s: s.name.lower(), reverse=reverse)
            elif key == "Score": sorted_list = sorted(self.students, key=lambda s: s.total_score, reverse=reverse)
            elif key == "Code": sorted_list = sorted(self.students, key=lambda s: s.code, reverse=reverse)
            
            # Re-use the view all page to display the sorted result
            self.show_view_all(sorted_list)

        ctk.CTkButton(options_frame, text="Apply Sort", command=apply_sort, font=("Arial", 15, "bold"), height=40).pack(pady=30, padx=50, fill="x")

    def show_find_student(self):
        self.clear_content()
        container = ctk.CTkFrame(self.content, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(container, text="Find Student Record", font=("Arial", 26, "bold"), text_color="white").pack(anchor="w", pady=(0, 20))
        # Reusing the search UI builder, passing a callback to show the card when clicked
        self.build_search_ui(container, lambda s: self.create_student_card(container, s))

    def show_highest(self):
        # Use Python's max() to find the top student
        self.show_single_stat("Highest Performing Student", max)

    def show_lowest(self):
        # Use Python's min() to find the lowest
        self.show_single_stat("Lowest Performing Student", min)

    def show_single_stat(self, title, func):
        self.clear_content()
        container = ctk.CTkFrame(self.content, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(container, text=title, font=("Arial", 26, "bold"), text_color="white").pack(anchor="w", pady=(0, 40))
        
        if not self.students:
            ctk.CTkLabel(container, text="No data available.").pack()
            return
            
        # Determine the student based on total_score
        target_student = func(self.students, key=lambda s: s.total_score)
        
        card_container = ctk.CTkFrame(container, fg_color="transparent")
        card_container.pack(fill="x", padx=50)
        self.create_student_card(card_container, target_student, highlight=True)

    def show_student_form(self, student=None, index=None):
        """
        Shows a form. If 'student' is provided, it's an Edit. If None, it's an Add.
        """
        self.clear_content()
        container = ctk.CTkFrame(self.content, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        title = "Edit Student Record" if student else "Add New Student"
        ctk.CTkLabel(container, text=title, font=("Arial", 26, "bold"), text_color="white").pack(anchor="w", pady=(0, 20))

        form_frame = ctk.CTkFrame(container, fg_color="#2b2b2b")
        form_frame.pack(fill="both", expand=True, padx=50)

        entries = {}
        fields = [
            ("Student Code (1000-9999)", "code"),
            ("Student Name", "name"),
            ("Coursework 1 (Max 20)", "c1"),
            ("Coursework 2 (Max 20)", "c2"),
            ("Coursework 3 (Max 20)", "c3"),
            ("Exam Mark (Max 100)", "exam")
        ]

        # Pre-fill data if we are editing
        defaults = {
            "code": student.code if student else "",
            "name": student.name if student else "",
            "c1": str(student.c1) if student else "",
            "c2": str(student.c2) if student else "",
            "c3": str(student.c3) if student else "",
            "exam": str(student.exam) if student else ""
        }

        for label_text, key in fields:
            row = ctk.CTkFrame(form_frame, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=10)
            ctk.CTkLabel(row, text=label_text, width=200, anchor="w").pack(side="left")
            ent = ctk.CTkEntry(row)
            ent.insert(0, defaults[key])
            ent.pack(side="right", fill="x", expand=True)
            entries[key] = ent

        def save_record():
            try:
                # Get values and validate inputs
                code = entries["code"].get().strip()
                name = entries["name"].get().strip()
                
                if not (1000 <= int(code) <= 9999): raise ValueError("Code must be 1000-9999")
                if not name: raise ValueError("Name cannot be empty")
                
                c1, c2, c3 = int(entries["c1"].get()), int(entries["c2"].get()), int(entries["c3"].get())
                exam = int(entries["exam"].get())
                
                # Ensure marks are within valid ranges
                if any(x < 0 or x > 20 for x in [c1, c2, c3]): raise ValueError("Coursework marks must be 0-20")
                if not (0 <= exam <= 100): raise ValueError("Exam mark must be 0-100")

                new_student = Student(code, name, c1, c2, c3, exam)
                
                if index is not None:
                    # Update existing
                    self.students[index] = new_student
                    messagebox.showinfo("Success", "Record Updated Successfully")
                else:
                    # Append new
                    self.students.append(new_student)
                    messagebox.showinfo("Success", "Record Added Successfully")
                
                # Commit changes to file
                self.save_data_to_file()
                self.show_view_all()
                
            except ValueError as e: messagebox.showerror("Validation Error", str(e))
            except Exception as e: messagebox.showerror("Error", "Invalid Input")

        ctk.CTkButton(form_frame, text="SAVE RECORD", command=save_record, height=50, font=("Arial", 15, "bold")).pack(pady=30, padx=20, fill="x")

    def show_update_selection(self):
        # Lets user pick a student to edit
        self.clear_content()
        container = ctk.CTkFrame(self.content, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(container, text="Select Record to Update", font=("Arial", 26, "bold"), text_color="white").pack(anchor="w", pady=(0, 20))
        self.build_search_ui(container, lambda s: self.show_student_form(s, self.students.index(s)), action_text="Update")

    def show_delete_selection(self):
        # Lets user pick a student to remove
        self.clear_content()
        container = ctk.CTkFrame(self.content, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(container, text="Select Record to Delete", font=("Arial", 26, "bold"), text_color="white").pack(anchor="w", pady=(0, 20))
        
        def on_delete(s):
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {s.name}?"):
                self.students.remove(s)
                self.save_data_to_file()
                self.show_delete_selection()
        
        self.build_search_ui(container, on_delete, action_text="DELETE", action_color="#8a1c12")

    def build_search_ui(self, parent, callback, action_text="Select", action_color="#3B8ED0"):
        # Reusable search bar logic used for Find, Update, and Delete pages
        search_frame = ctk.CTkFrame(parent, fg_color="transparent")
        search_frame.pack(fill="x", pady=10)
        
        sv = tk.StringVar()
        entry = ctk.CTkEntry(search_frame, textvariable=sv, placeholder_text="Search by Name or ID...", height=45, font=("Arial", 14))
        entry.pack(fill="x")
        
        res_area = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        res_area.pack(fill="both", expand=True, pady=10)

        def perform_search(*args):
            # Clear previous results
            for w in res_area.winfo_children(): w.destroy()
            query = sv.get().lower()
            
            # Simple filtering logic
            matches = self.students if not query else [s for s in self.students if query in s.name.lower() or query in s.code]
            
            for s in matches:
                if action_text == "Select":
                    # Just viewing, show the full card
                    self.create_student_card(res_area, s)
                else:
                    # Action mode (Update/Delete), show a row with a button
                    row = ctk.CTkFrame(res_area, fg_color="#2b2b2b")
                    row.pack(fill="x", pady=5)
                    ctk.CTkLabel(row, text=f"{s.name} ({s.code})", font=("Arial", 14)).pack(side="left", padx=20)
                    ctk.CTkButton(row, text=action_text, width=100, fg_color=action_color, 
                                  command=lambda student=s: callback(student)).pack(side="right", padx=10, pady=10)
        
        # Update results live as user types
        sv.trace("w", perform_search)
        perform_search()

    def create_student_card(self, parent, s, highlight=False):
        # Creates a visual "Card" to display student stats
        color = "#3B8ED0" if highlight else "#2b2b2b"
        card = ctk.CTkFrame(parent, fg_color=color, corner_radius=10)
        card.pack(fill="x", pady=10)
        
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 5))
        ctk.CTkLabel(header, text=s.name, font=("Arial", 20, "bold"), text_color="white").pack(side="left")
        ctk.CTkLabel(header, text=f"ID: {s.code}", font=("Arial", 16), text_color="#e0e0e0").pack(side="right")
        
        # Separator
        ctk.CTkFrame(card, height=2, fg_color="#444").pack(fill="x", padx=10, pady=5)
        
        stats = ctk.CTkFrame(card, fg_color="transparent")
        stats.pack(fill="x", padx=20, pady=(5, 15))
        
        # Adding all the specific stats rows
        self.add_stat_row(stats, 0, "Coursework Total:", f"{s.coursework_total} / 60")
        self.add_stat_row(stats, 1, "Exam Mark:", f"{s.exam} / 100")
        self.add_stat_row(stats, 2, "Overall Percentage:", f"{s.percentage:.2f}%")
        self.add_stat_row(stats, 3, "Final Grade:", s.grade, is_grade=True)

    def add_stat_row(self, parent, row, label, value, is_grade=False):
        # Helper for consistent row styling in the student card
        ctk.CTkLabel(parent, text=label, font=("Arial", 14), text_color="#ccc", anchor="w").grid(row=row, column=0, sticky="w", pady=2)
        font = ("Arial", 18, "bold") if is_grade else ("Arial", 14, "bold")
        color = "#ffdd55" if is_grade else "white"
        ctk.CTkLabel(parent, text=value, font=font, text_color=color, anchor="e").grid(row=row, column=1, sticky="e", padx=(20,0), pady=2)
        parent.grid_columnconfigure(0, weight=1)

    # DATA MANAGEMENT
    def ensure_file_exists(self):
        # Creates dummy data if the file is missing so the app doesn't crash on first run
        if not os.path.exists(FILE_NAME):
            with open(FILE_NAME, 'w') as f:
                f.write("5\n")
                f.write("8439,Jake Hobbs,10,11,10,43\n")
                f.write("1023,Sarah Connor,20,19,20,85\n")
                f.write("9912,Mike Ross,8,12,9,30\n")
                f.write("5541,Rachel Green,18,18,19,90\n")
                f.write("3321,Walter White,20,20,20,98\n")

    def load_data(self):
        # Reads the text file and creates Student objects
        self.students = []
        try:
            with open(FILE_NAME, 'r') as f:
                lines = f.readlines()
                # Skip the first line since it's just the count
                data_lines = lines[1:] 
                for line in data_lines:
                    if ',' in line:
                        parts = line.strip().split(',')
                        if len(parts) == 6:
                            self.students.append(Student(*parts))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}")

    def save_data_to_file(self):
        # Overwrites the file with current memory state
        try:
            with open(FILE_NAME, 'w') as f:
                f.write(f"{len(self.students)}\n")
                for s in self.students:
                    f.write(f"{s.code},{s.name},{s.c1},{s.c2},{s.c3},{s.exam}\n")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save to file: {e}")

if __name__ == "__main__":
    app = StudentApp()
    app.mainloop()