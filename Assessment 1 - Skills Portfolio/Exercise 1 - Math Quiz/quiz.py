#MATH QUIZ

import tkinter as tk
from PIL import Image, ImageTk
import cv2  # OpenCV for images/videos
import random
from tkinter import messagebox
from tkinter import font as tkfont
import os # Import os for path handling. images/videos wouldnt load without this

#ASSET PATH CONFIGURATION
#Get the directory of the currently executing script (quiz.py)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
#Define the path to the assets folder relative to the script's directory
ASSET_PATH = os.path.join(SCRIPT_DIR, "assets")

#GLOBAL WINDOW
root = tk.Tk()
root.state('zoomed') #to appear in full screen
root.title("Math Quiz")

#USING COMIC SANS AS CUSTOM FONT
try:
    custom_font = tkfont.Font(family="Comic Sans MS", size=16)
except:
    #"Arial" if "Comic Sans MS" is not available
    custom_font = tkfont.Font(family="Arial", size=16)

root.option_add("*Font", custom_font)
root.option_add("*Foreground", "#4b1c24")

#GLOBAL VARIABLES FOR QUIZ
quiz_score = 0
quiz_index = 0
quiz_attempt = 1
quiz_questions = []

#CLEAR WINDOW
def clear_window():
    for w in root.winfo_children():
        w.destroy()

#VIDEO UPDATE FUNCTION
def update_video(cap, video_label, loop=False):
    if not root.winfo_exists() or not video_label.winfo_exists():
        if cap and cap.isOpened():
            cap.release()
        return

    ret, frame = cap.read()
    if not ret:
        if loop:
            # It will restart video if looping
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            root.after(1, lambda: update_video(cap, video_label, loop))
        return

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    try:
        width = root.winfo_width()
        height = root.winfo_height()
        if width > 0 and height > 0:
            frame = cv2.resize(frame, (width, height))
        else:
            frame = cv2.resize(frame, (800, 600))
    except cv2.error as e:
        print(f"Error resizing frame: {e}")
        return

    img = ImageTk.PhotoImage(Image.fromarray(frame))
    video_label.config(image=img)
    video_label.image = img

    fps = cap.get(cv2.CAP_PROP_FPS)
    delay = int(1000 / fps) if fps > 0 else 33
    video_label.after(delay, lambda: update_video(cap, video_label, loop))

    for widget in root.winfo_children():
        if isinstance(widget, tk.Button) or isinstance(widget, tk.Label):
            widget.lift()

#BUTTON FADE-IN
def fade_in_button(btn, steps=20, step=0):
    if step > steps:
        return
    start_color = (107, 30, 30)  #6b1e1e
    end_color = (139, 46, 46)    #8b2e2e
    r = int(start_color[0] + (end_color[0]-start_color[0])*(step/steps))
    g = int(start_color[1] + (end_color[1]-start_color[1])*(step/steps))
    b = int(start_color[2] + (end_color[2]-start_color[2])*(step/steps))
    btn.config(bg=f"#{r:02x}{g:02x}{b:02x}")
    btn.lift()
    btn.after(50, lambda: fade_in_button(btn, steps, step+1))

#START SCREEN
def show_start_screen():
    clear_window()
    video_label = tk.Label(root)
    video_label.pack(fill="both", expand=True)

    video_file_name = "MATH QUIZ.mp4"
    video_file = os.path.join(ASSET_PATH, video_file_name) 

    #TO CHECK PATH 
    # The output will now show the full absolute path Python is trying to use.
    if not os.path.exists(video_file):
        print(f"DIAGNOSTIC: File NOT FOUND at path: {video_file}.")
    else:
        print(f"DIAGNOSTIC: File FOUND at path: {video_file}.")

    cap1 = None
    try:
        cap1 = cv2.VideoCapture(video_file)
        if not cap1.isOpened():
            # Error message suggests file found but failed to open (OpenCV/Codec issue)
            print(f"Error: Could not open video file: {video_file}. (Likely missing OpenCV codec or corrupted file).")
            video_label.config(text=f"Video Error: '{video_file_name}' not supported or corrupted.", fg="red", bg="black")
            cap1 = None
    except Exception as e:
        print(f"Error loading video: {e}")
        cap1 = None


    start_btn = tk.Button(root, text="START", font=("Comic Sans MS", 18, "bold"),
                          bg="#6b1e1e", fg="white", relief="flat", cursor="hand2",
                          command=lambda: (cap1.release() if cap1 and cap1.isOpened() else None, play_second_video()))
    start_btn.place(relx=0.5, rely=0.68, anchor="center")
    start_btn.lower()

    how_btn = tk.Button(root, text="HOW TO PLAY", font=("Comic Sans MS", 18, "bold"),
                        bg="#6b1e1e", fg="white", relief="flat", cursor="hand2",
                        command=show_how_to_play_video)
    how_btn.place(relx=0.5, rely=0.77, anchor="center")
    how_btn.lower()

    def fade_buttons():
        start_btn.lift()
        fade_in_button(start_btn)
        how_btn.lift()
        fade_in_button(how_btn)

    if cap1:
        root.after(2500, fade_buttons)
        update_video(cap1, video_label, loop=False)
    else:
        fade_buttons()

#SECOND VIDEO SCREEN (DIFFICULTY)
def play_second_video():
    clear_window()
    video_label = tk.Label(root)
    video_label.pack(fill="both", expand=True)

    cap2 = None
    video_file_name = "MATH QUIZ (1).mp4"
    video_file = os.path.join(ASSET_PATH, video_file_name)
    try:
        cap2 = cv2.VideoCapture(video_file)
        if not cap2.isOpened():
            print(f"Error: Could not open video file: {video_file}. (Likely missing OpenCV codec or corrupted file).")
            video_label.config(text=f"Video Error: '{video_file_name}' not supported or corrupted.", fg="red", bg="black")
            cap2 = None
    except Exception as e:
        print(f"Error loading video: {e}")
        cap2 = None

    if cap2:
        update_video(cap2, video_label, loop=False)

    buttons = []
    positions = [0.5, 0.6, 0.7]
    for i, name in enumerate(["EASY", "MEDIUM", "HARD"]):
        btn = tk.Button(root, text=name, font=("Comic Sans MS", 18, "bold"),
                        width=12, bg="#6b1e1e", fg="white", relief="flat", cursor="hand2",
                        command=lambda n=name: start_quiz(n))
        btn.place(relx=0.5, rely=positions[i], anchor="center")
        btn.lower()
        btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#8b2e2e"))
        btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#6b1e1e"))
        buttons.append(btn)

    def fade_all_buttons():
        for b in buttons:
            b.lift()
            fade_in_button(b)

    root.after(2000, fade_all_buttons)

    #BACK BUTTON IMAGE
    try:
        back_img_file = os.path.join(ASSET_PATH, "BACKBUTTON.png") # <--- ROBUST PATHING
        back_img = Image.open(back_img_file).resize((80, 80))
        back_photo = ImageTk.PhotoImage(back_img)
        root.back_photo_ref_2 = back_photo

        def back_command():
            if cap2 and cap2.isOpened():
                cap2.release()
            show_start_screen()

        back_btn = tk.Button(root, image=back_photo, bg="#6b1e1e", borderwidth=0,
                             activebackground="black", cursor="hand2",
                             command=back_command)
        back_btn.image = back_photo
        back_btn.place(relx=0.07, rely=0.1, anchor="center")
        root.after(2000, lambda: fade_in_button(back_btn))

    except FileNotFoundError:
        # Fallback text button if image is not found
        back_btn = tk.Button(root, text="BACK", font=("Comic Sans MS", 14, "bold"),
                             bg="#6b1e1e", fg="white", relief="flat", cursor="hand2",
                             command=lambda: (cap2.release() if cap2 else None, show_start_screen()))
        back_btn.place(relx=0.07, rely=0.1, anchor="center")
        back_btn.lift()
    except Exception as e:
        print(f"Error loading back button image: {e}")
        back_btn = tk.Button(root, text="BACK", font=("Comic Sans MS", 14, "bold"),
                             bg="#6b1e1e", fg="white", relief="flat", cursor="hand2",
                             command=lambda: (cap2.release() if cap2 else None, show_start_screen()))
        back_btn.place(relx=0.07, rely=0.1, anchor="center")
        back_btn.lift()


#START QUIZ
def start_quiz(level):
    global quiz_questions, quiz_index, quiz_attempt, quiz_score
    quiz_score = 0
    quiz_index = 0
    quiz_attempt = 1
    quiz_questions = generate_quiz_questions(level)
    display_quiz_question()

#TO GENERATE QUIZ QUESTIONS
def generate_quiz_questions(level):
    questions = []
    for _ in range(10):
        if level == "EASY":
            a = random.randint(0, 9)
            b = random.randint(0, 9)
        elif level == "MEDIUM":
            a = random.randint(10, 99)
            b = random.randint(10, 99)
        else:
            a = random.randint(1000, 9999)
            b = random.randint(1000, 9999)
        op = random.choice(["+", "-"])
        answer = a + b if op == "+" else a - b
        questions.append({"a": a, "b": b, "op": op, "answer": answer})
    return questions

#TO DISPLAY QUIZ QUESTION
def display_quiz_question():
    global quiz_index, quiz_attempt, quiz_score

    clear_window()

    #BACKGROUND FOR QUIZ
    bg_photo = None
    try:
        bg_image_file = os.path.join(ASSET_PATH, "BG.jpg") 
        # Use root.winfo_width() and height, but wrap in a check to ensure they are available
        width = root.winfo_width()
        height = root.winfo_height()
        bg_image = Image.open(bg_image_file).resize((width, height))
        bg_photo = ImageTk.PhotoImage(bg_image)
        root.bg_photo_ref = bg_photo
    except FileNotFoundError:
        root.config(bg="black")
    except Exception as e:
        print(f"Background image error: {e}")
        root.config(bg="black")

    canvas = tk.Canvas(root, width=root.winfo_width(), height=root.winfo_height(), highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    if bg_photo:
        canvas.create_image(0, 0, anchor="nw", image=bg_photo)

    #BACK BUTTON
    try:
        back_img_file = os.path.join(ASSET_PATH, "BACKBUTTON.png") 
        back_img = Image.open(back_img_file).resize((80, 80))
        back_photo = ImageTk.PhotoImage(back_img)
        root.back_photo_ref_3 = back_photo  

        def back_command():
            show_start_screen()

        back_btn = tk.Button(root, image=back_photo, bg="#6b1e1e", borderwidth=0,
                             activebackground="black", cursor="hand2",
                             command=back_command)
        back_btn.image = back_photo
        back_btn.place(relx=0.07, rely=0.1, anchor="center")
        fade_in_button(back_btn)

    except FileNotFoundError:
        # Fallback text button
        back_btn = tk.Button(root, text="BACK", font=("Comic Sans MS", 16, "bold"),
                             bg="#6b1e1e", fg="white", command=show_start_screen)
        back_btn.place(relx=0.07, rely=0.1, anchor="center")
        back_btn.lift()
    except Exception as e:
        print(f"Error loading back button image: {e}")
        back_btn = tk.Button(root, text="BACK", font=("Comic Sans MS", 16, "bold"),
                             bg="#6b1e1e", fg="white", command=show_start_screen)
        back_btn.place(relx=0.07, rely=0.1, anchor="center")
        back_btn.lift()

    #CHECK IF QUIZ ENDED
    if quiz_index >= len(quiz_questions):
        display_quiz_results()
        return

    q = quiz_questions[quiz_index]

    #QUIZ QUESTION DISPLAY
    canvas.create_text(root.winfo_width()//2, 100, text=f"Current Score: {quiz_score}",
                       font=("Comic Sans MS", 24, "bold"), fill="white")
    canvas.create_text(root.winfo_width()//2, 200, text=f"{q['a']} {q['op']} {q['b']} = ?",
                       font=("Comic Sans MS", 48, "bold"), fill="white")

    entry = tk.Entry(root, font=("Comic Sans MS", 24), justify="center")
    canvas.create_window(root.winfo_width()//2, 350, window=entry, width=200, height=50)
    entry.focus()

    feedback_text_id = canvas.create_text(root.winfo_width()//2, 550, text="", font=("Comic Sans MS", 24, "bold"), fill="white")

    def next_question():
        global quiz_index, quiz_attempt
        quiz_index += 1
        quiz_attempt = 1
        display_quiz_question()

    def submit_answer():
        global quiz_index, quiz_attempt, quiz_score
        try:
            user_ans = int(entry.get())
        except:
            canvas.itemconfig(feedback_text_id, text="Enter a number", fill="red")
            return

        correct = q['answer']
        if user_ans == correct:
            points = 10 if quiz_attempt == 1 else 5
            quiz_score += points
            canvas.itemconfig(feedback_text_id, text=f"Correct! +{points} points", fill="lightgreen")
            root.after(1000, next_question)
        else:
            if quiz_attempt == 1:
                canvas.itemconfig(feedback_text_id, text="Incorrect. Try once more.", fill="yellow")
                quiz_attempt = 2
            else:
                canvas.itemconfig(feedback_text_id, text=f"Wrong again! Correct answer: {correct}", fill="red")
                root.after(1500, next_question)

    submit_btn = tk.Button(root, text="Submit", font=("Comic Sans MS", 18, "bold"),
                           bg="#6b1e1e", fg="white", command=submit_answer)
    canvas.create_window(root.winfo_width()//2, 450, window=submit_btn, width=150, height=50)

#DISPLAY QUIZ RESULTS
def display_quiz_results():
    clear_window()
    video_label = tk.Label(root)
    video_label.pack(fill="both", expand=True)

    # Determine result video
    if quiz_score > 90:
        result_video_name = "excellent.mp4"
    elif quiz_score >= 50:
        result_video_name = "great_job.mp4"
    else:
        result_video_name = "good_luck_next_time.mp4"
    
    result_video = os.path.join(ASSET_PATH, result_video_name)

    def play_video(file, after_func=None):
        cap = cv2.VideoCapture(file)
        if not cap.isOpened():
            print(f"Error: Could not open {file}. (Likely missing OpenCV codec or corrupted file).")
            if after_func:
                after_func()
            return

        def update_frame():
            ret, frame = cap.read()
            if not ret:
                cap.release()
                if after_func:
                    after_func()
                return

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            try:
                width = root.winfo_width()
                height = root.winfo_height()
                frame = cv2.resize(frame, (width, height))
            except:
                frame = cv2.resize(frame, (800, 600))

            img = ImageTk.PhotoImage(Image.fromarray(frame))
            video_label.config(image=img)
            video_label.image = img

            fps = cap.get(cv2.CAP_PROP_FPS)
            delay = int(1000 / fps) if fps > 0 else 33
            video_label.after(delay, update_frame)

        update_frame()

    def overlay_results():
        tk.Label(root, text=f"Your Score: {quiz_score}/100",
                 font=("Comic Sans MS", 36, "bold"), fg="white", bg="#222578").place(relx=0.5, rely=0.5, anchor="center")
        rank = "A+" if quiz_score > 90 else "A" if quiz_score >= 75 else "B" if quiz_score >= 50 else "C"
        tk.Label(root, text=f"Rank: {rank}",
                 font=("Comic Sans MS", 28, "bold"), fg="white", bg="#222578").place(relx=0.5, rely=0.6, anchor="center")
        tk.Button(root, text="Play Again", font=("Comic Sans MS", 24, "bold"),
                  bg="#6b1e1e", fg="white", command=displayMenu).place(relx=0.5, rely=0.87, anchor="center", width=200, height=60)
        tk.Button(root, text="Exit", font=("Comic Sans MS", 24, "bold"),
                  bg="#6b1e1e", fg="white", command=root.quit).place(relx=0.5, rely=0.95, anchor="center", width=200, height=60)

    # Play confetti first, then result video
    confetti_file = os.path.join(ASSET_PATH, "confetti.mp4")
    def play_confetti_then_result():
        play_video(confetti_file, after_func=lambda: play_video(result_video, after_func=overlay_results))

    play_confetti_then_result()

#HOW TO PLAY
def show_how_to_play_video():
    clear_window()
    video_label = tk.Label(root)
    video_label.pack(fill="both", expand=True)

    video_file_name = "MATH QUIZ (2).mp4"
    video_file = os.path.join(ASSET_PATH, video_file_name) 
    cap3 = cv2.VideoCapture(video_file)
    if cap3.isOpened():
        update_video(cap3, video_label, loop=False)
    else:
        print(f"Error: Could not open video file: {video_file}. (Likely missing OpenCV codec or corrupted file).")


    try:
        back_img_file = os.path.join(ASSET_PATH, "BACKBUTTON.png")
        back_img = Image.open(back_img_file).resize((80, 80))
        back_photo = ImageTk.PhotoImage(back_img)
        root.back_photo_ref_3 = back_photo 

        def back_command():
            show_start_screen()

        back_btn = tk.Button(root, image=back_photo, bg="black", borderwidth=0,
                             activebackground="black", cursor="hand2",
                             command=back_command)
        back_btn.image = back_photo
        back_btn.place(relx=0.07, rely=0.1, anchor="center")
        fade_in_button(back_btn)

    except FileNotFoundError:
        # Fallback text button
        back_btn = tk.Button(root, text="BACK", font=("Comic Sans MS", 16, "bold"),
                             bg="#6b1e1e", fg="white", command=show_start_screen)
        back_btn.place(relx=0.07, rely=0.1, anchor="center")
        back_btn.lift()
    except Exception as e:
        print(f"Error loading back button image: {e}")
        back_btn = tk.Button(root, text="BACK", font=("Comic Sans MS", 16, "bold"),
                             bg="#6b1e1e", fg="white", command=show_start_screen)
        back_btn.place(relx=0.07, rely=0.1, anchor="center")
        back_btn.lift()


#DISPLAY MENU
def displayMenu():
    show_start_screen()

#MAIN
if __name__ == "__main__":
    root.state('zoomed')
    root.title("Math Quiz")
    show_start_screen()
    root.mainloop()