import tkinter as tk
import cv2
from PIL import Image, ImageTk
import random
import os
from tkinter import messagebox

#FILE PATHS
BASE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(BASE, "assets")
JOKES_FILE = os.path.join(BASE, "randomJokes.txt")

VIDEOS = [
    os.path.join(ASSETS, "1.mp4"),
    os.path.join(ASSETS, "2.mp4"),
    os.path.join(ASSETS, "3.mp4")
]

#JOKE MANAGEMENT
jokes_list = []
current_joke_index = -1
current_joke = None
current_bg_index = 1

def load_jokes():
    """
    Opens randomJokes.txt, reads each line, 
    and splits it into a (setup, punchline) tuple.
    """
    jokes = []
    if not os.path.exists(JOKES_FILE):
        messagebox.showerror("Error", f"Jokes file not found:\n{JOKES_FILE}")
        return jokes
    
    with open(JOKES_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "?" in line:
                setup, punch = line.split("?", 1)
                jokes.append((setup + "?", punch))
    return jokes

def show_joke_by_index(show_setup_after=0):
    """
    Displays the current joke on the labels.
    Has an optional delay to sync with video transitions.
    """
    global current_joke, current_joke_index, jokes_list

    if not jokes_list:
        return

    current_joke = jokes_list[current_joke_index]
    punchline_label.config(text="")

    if show_setup_after > 0:
        setup_label.config(text="")
        # root.after() runs a function after a specified delay in milliseconds
        root.after(show_setup_after, lambda: setup_label.config(text=current_joke[0]))
    else:
        setup_label.config(text=current_joke[0])

    # lift() ensures the text labels are drawn on top of the video
    setup_label.lift()
    punchline_label.lift()

#VIDEO PLAYER
cap = None  # Will hold the OpenCV VideoCapture object
after_id = None  # Stores the ID of the .after() loop so we can cancel it
app_is_exiting = False  # Flag to prevent crash on exit

def play_bg_video(path):
    """
    Stops any currently playing video and starts a new one.
    """
    global cap, after_id

    if after_id:  # Cancel any existing video loop
        root.after_cancel(after_id)
        after_id = None

    if cap:  # Release any open video file
        cap.release()

    cap = cv2.VideoCapture(path)

    if not cap.isOpened():
        messagebox.showerror("Video Error", f"Failed to open video file:\n{path}")
        cap = None
        return

    update_frame()  # Start the new video loop

def update_frame():
    """
    Reads one frame from the video, displays it on the label,
    and schedules itself to run again.
    """
    global cap, after_id, app_is_exiting

    # This is the "kill switch". If True, the exit function has been called.
    if app_is_exiting:
        return

    if cap is None:
        return

    ret, frame = cap.read()

    if not ret:  # 'ret' is False if the video has ended
        cap.release()
        cap = None
        return

    # Convert color from OpenCV's BGR to PIL's RGB
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # This try/except block prevents a race condition crash when exiting
    try:
        if not root.winfo_exists():
            return

        # Resize the frame to fit the current window size
        width = root.winfo_width()
        height = root.winfo_height()
        frame = cv2.resize(frame, (width, height))

        # Convert the OpenCV/numpy frame to a Tkinter-compatible image
        img = ImageTk.PhotoImage(Image.fromarray(frame))

        # Update the video label
        video_label.img = img  # Keep a reference to prevent garbage collection
        video_label.config(image=img)

        # Schedule this function to run again after 15ms
        if not app_is_exiting:
            after_id = video_label.after(15, update_frame)

    except (tk.TclError, RuntimeError):
        # This error happens if the window is destroyed mid-frame.
        # 'pass' silently stops the loop without crashing.
        pass

#PAGE SWITCH
def go_page1():
    """
    Sets up the main "Home" page. Shows start button, hides others.
    """
    play_bg_video(VIDEOS[0])
    setup_label.config(text="")
    punchline_label.config(text="")

    start_btn.place(relx=0.48, rely=0.72, anchor="center")
    show_btn.place_forget()
    next_btn.place_forget()
    home_btn.place_forget()

def go_page2():
    """
    Sets up the first "Joke" page.
    """
    global current_joke_index, current_bg_index
    current_joke_index = 0
    
    play_bg_video(VIDEOS[1])
    current_bg_index = 1
    start_btn.place_forget()

    next_btn.place(relx=0.55, rely=0.75, anchor="center")
    show_btn.place(relx=0.45, rely=0.75, anchor="center")
    home_btn.place(relx=0.02, rely=0.02, anchor="nw") 

    show_joke_by_index(show_setup_after=3000)

def go_page3():
    """
    Sets up all subsequent "Joke" pages, cycling videos and jokes.
    """
    global current_joke_index, jokes_list, current_bg_index
    current_joke_index += 1

    # If we've seen all jokes, shuffle and start over
    if current_joke_index >= len(jokes_list):
        random.shuffle(jokes_list)
        current_joke_index = 0
        messagebox.showinfo("Jokes Over", "You've seen them all! Starting over.")

    # Alternate the background video
    if current_bg_index == 1:
        play_bg_video(VIDEOS[2])
        current_bg_index = 2
    else:
        play_bg_video(VIDEOS[1])
        current_bg_index = 1

    start_btn.place_forget()
    show_btn.place(relx=0.45, rely=0.75, anchor="center")
    next_btn.place(relx=0.55, rely=0.75, anchor="center")
    home_btn.place(relx=0.02, rely=0.02, anchor="nw")

    show_joke_by_index(show_setup_after=3000)

#CLEAN EXIT
def on_exit():
    """
    Handles closing the window cleanly.
    This is called by the "Exit" button AND the window's "X" button.
    """
    global cap, after_id, app_is_exiting
    # 1. Set the flag to stop the video loop
    app_is_exiting = True 

    # 2. Cancel any pending .after() tasks
    if after_id:
        root.after_cancel(after_id)
    # 3. Release the video file
    if cap:
        cap.release()
    # 4. Destroy the window
    root.destroy()

#BUTTON STYLING
def on_enter(e):
    # This function is bound to the <Enter> (hover) event
    e.widget['background'] = '#666666' # Lighter color on hover

def on_leave(e):
    # This function is bound to the <Leave> (hover exit) event
    e.widget['background'] = '#444444' # Original color

#WINDOW
root = tk.Tk()
root.title("Alexa Joke Assistant")
root.state('zoomed') # Start maximized

# A dictionary to hold our shared button style for a consistent look
button_style = {
    "font": ("Poppins", 16),
    "fg": "white",
    "bg": "#444444",
    "activebackground": "#888888",
    "activeforeground": "white",
    "bd": 0,
    "highlightthickness": 0,
    "padx": 15,
    "pady": 5,
    "cursor": "hand2"
}

# Create the Exit button using the shared style
exit_btn = tk.Button(root, text="Exit", command=on_exit, **button_style)
exit_btn.place(relx=0.98, rely=0.02, anchor="ne")
exit_btn.bind("<Enter>", on_enter)
exit_btn.bind("<Leave>", on_leave)

# This protocol ensures the window's "X" button calls our on_exit function
root.protocol("WM_DELETE_WINDOW", on_exit)

# This label will hold the video frames
video_label = tk.Label(root)
video_label.place(x=0, y=0, relwidth=1, relheight=1)
video_label.lower() # Send it to the back

# Joke setup label
setup_label = tk.Label(root, text="", font=("Poppins", 32, "bold"),
                       fg="black", wraplength=1000, justify="center")
setup_label.place(relx=0.5, rely=0.45, anchor="center")

# Joke punchline label
punchline_label = tk.Label(root, text="", font=("Poppins", 30),
                           fg="black", wraplength=1000, justify="center")
punchline_label.place(relx=0.5, rely=0.55, anchor="center")

# BUTTONS
start_img_path = os.path.join(ASSETS, "start.png")
if os.path.exists(start_img_path):
    # If start.png exists, use it as the button
    start_img = Image.open(start_img_path)
    start_img = start_img.resize((250, 80), Image.Resampling.LANCZOS)
    start_photo = ImageTk.PhotoImage(start_img)
    
    start_btn = tk.Button(root, image=start_photo, borderwidth=0, highlightthickness=0,
                        command=go_page2)
else:
    # Otherwise, create a text-based "fallback" button
    messagebox.showerror("Error", f"Start button image not found:\n{start_img_path}")
    
    fallback_style = button_style.copy()
    fallback_style["font"] = ("Poppins", 40) 
    fallback_style["fg"] = "black" 
    
    start_btn = tk.Button(root, text="Start", command=go_page2, **fallback_style)
    start_btn.bind("<Enter>", on_enter)
    start_btn.bind("<Leave>", on_leave)

# Create the other buttons using the shared style
show_btn = tk.Button(root, text="Show",
                     command=lambda: punchline_label.config(text=current_joke[1]),
                     **button_style)
show_btn.bind("<Enter>", on_enter)
show_btn.bind("<Leave>", on_leave)

next_btn = tk.Button(root, text="Next", command=go_page3, **button_style)
next_btn.bind("<Enter>", on_enter)
next_btn.bind("<Leave>", on_leave)

home_btn = tk.Button(root, text="Home", command=go_page1, **button_style)
home_btn.bind("<Enter>", on_enter)
home_btn.bind("<Leave>", on_leave)

#STARTUP
jokes_list = load_jokes() # Load jokes into memory

if jokes_list:
    random.shuffle(jokes_list) # Shuffle them once at the start
    go_page1() # Show the home page
else:
    messagebox.showerror("Startup Error", "No jokes loaded. Exiting.")
    root.destroy()

# Start the main application loop
root.mainloop()