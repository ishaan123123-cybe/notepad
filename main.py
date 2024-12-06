
import sys
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import pygame
from mutagen import File as MutagenFile
import enchant
#half of feautres dont work anymore, like saving. Sorry
import sys
import webbrowser

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import nltk

import pyttsx3
import markovify
import random
import base64
from autocorrect import Speller


import tkinter as tk
from tkinter import scrolledtext
import threading
from sympy import sympify

def start_chat():
    # Dictionary for friendly responses
    friendly_responses = {
        "greeting": "Hello! I'm your friendly calculator bot. Feel free to ask me any math question.",
        "farewell": "Goodbye! Have a great day!",
        "error": "Oops! Something went wrong. Please try again.",
    }

    def process_input():
        user_input = entry.get().replace("x", "*")  # Replace "x" with "*"
        threading.Thread(target=calculate_response, args=(user_input,)).start()

    def calculate_response(user_input):
        try:
            result = sympify(user_input)
            response = f"The answer is {result}"
        except Exception as e:
            response = friendly_responses["error"]
        update_chat_log(user_input, response=response)

    def update_chat_log(user_input, response=None):
        chat_log.config(state=tk.NORMAL)
        if user_input:
            chat_log.insert(tk.END, f"You: {user_input}\n", "user")
        if response:
            chat_log.insert(tk.END, "Robot: " + response + "\n", "bot")
        chat_log.config(state=tk.DISABLED)
        chat_log.see(tk.END)

    # GUI setup
    root = tk.Tk()
    root.title("Friendly AI Calculator")

    chat_log = scrolledtext.ScrolledText(root, width=50, height=20, wrap=tk.WORD)
    chat_log.tag_config("user", foreground="blue")
    chat_log.tag_config("bot", foreground="green")
    chat_log.pack()

    entry = tk.Entry(root, width=40)
    entry.pack(side=tk.LEFT)

    calculate_button = tk.Button(root, text="Calculate", command=process_input)
    calculate_button.pack(side=tk.RIGHT)

    def close_window():
        update_chat_log("", friendly_responses["farewell"])
        entry.config(state="disabled")
        calculate_button.config(state="disabled")
        root.after(2000, root.destroy)  # Close the window after 2 seconds

    root.protocol("WM_DELETE_WINDOW", close_window)  # Override the close button

    # Greet the user
    update_chat_log("", friendly_responses["greeting"])

    root.mainloop()





def hide_startup_message():
    startup_frame.pack_forget()


def animate_startup_message(fade_in=True):
    global startup_label, startup_frame
    alpha = 0 if fade_in else 1
    startup_frame.config(bg="#000" if fade_in else "#fff")
    startup_frame.pack(side="top", pady=10, fill="both", expand=True)
    startup_label.config(fg="#000" if fade_in else "#fff")
    if fade_in:
        alpha_delta = 0.05
        alpha_target = 1
    else:
        alpha_delta = -0.05
        alpha_target = 0

    def update_alpha():
        nonlocal alpha
        alpha += alpha_delta
        startup_label.config(fg="#{:02x}{:02x}{:02x}".format(int(alpha * 255), int(alpha * 255), int(alpha * 255)))
        if (alpha_delta > 0 and alpha >= alpha_target) or (alpha_delta < 0 and alpha <= alpha_target):
            if fade_in:
                root.after(1000, lambda: animate_startup_message(False))
            else:
                root.after(1000, hide_startup_message)
        else:
            root.after(100, update_alpha)

    update_alpha()


spell_checker = Speller(lang='en')


class ClickableText(tk.Text):
    def __init__(self, master, **kwargs):
        tk.Text.__init__(self, master, **kwargs)
        self.tag_configure("hyperlink", foreground="blue", underline=1)
        self.bind("<Button-1>", self.on_click)
        self.selected_text = ""

    def insert_link(self, link):
        if self.selected_text:
            self.insert("insert", self.selected_text, "hyperlink")
            self.tag_bind("hyperlink", "<Enter>", lambda event: self.tag_config("hyperlink", foreground="red"))
            self.tag_bind("hyperlink", "<Leave>", lambda event: self.tag_config("hyperlink", foreground="blue"))
            self.tag_bind("hyperlink", "<Button-1>", lambda event, url=link: self.on_link_click(url))

    def on_click(self, event):
        if self.tag_ranges(tk.SEL):
            self.selected_text = self.get(tk.SEL_FIRST, tk.SEL_LAST)

    def on_link_click(self, url):
        webbrowser.open_new(url)


def import_tasks():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        try:
            with open(file_path, "r") as file:
                tasks = file.readlines()
                for task in tasks:
                    task_list.insert(tk.END, task.strip())
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import tasks: {e}")


def export_tasks():
    tasks = task_list.get(0, tk.END)
    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        try:
            with open(file_path, "w") as file:
                for task in tasks:
                    file.write(task + "\n")
            messagebox.showinfo("Success", "Tasks exported successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export tasks: {e}")


def add_task():
    task_text = entry.get()
    if task_text.strip():  # Check if the task text is not empty
        task_list.insert(tk.END, f"- [ ] {task_text}")
        entry.delete(0, tk.END)  # Clear the entry field


def correct_word(event):
    if "spell_error" in text_area.tag_names("current"):
        word = text_area.get("current linestart", "current lineend")
        corrected_word = spell_checker(word)
        text_area.delete("current linestart", "current lineend")
        text_area.insert("current linestart", corrected_word)


def toggle_task(event):
    selected_item = task_list.curselection()
    if selected_item:
        current_text = task_list.get(selected_item)
        if "[ ]" in current_text:
            new_text = current_text.replace("[ ]", "[x]")  # Mark as completed
        else:
            new_text = current_text.replace("[x]", "[ ]")  # Mark as incomplete
        task_list.delete(selected_item)
        task_list.insert(selected_item, new_text)


def speak_text(text):
    engine.say(text)
    engine.runAndWait()


engine = pyttsx3.init()

nltk.download('punkt')


def read_text():
    text_content = text_area.get("1.0", "end-1c")
    speak_text(text_content)


def summarize_text():
    text_content = text_area.get("1.0", "end-1c")  # Get the content of the text area

    # Initialize Sumy summarizer with LSA algorithm
    summarizer = LsaSummarizer()
    summarizer = LsaSummarizer()
    parser = PlaintextParser.from_string(text_content, Tokenizer("english"))

    # Summarize the text
    summary = summarizer(parser.document, sentences_count=2)

    # Convert the summary sentences to a single string
    summary_text = ' '.join(map(str, summary))

    if summary_text:  # Check if a summary is generated
        messagebox.showinfo("Summary", summary_text)  # Display the summary in a messagebox
    else:
        messagebox.showinfo("Summary", "No summary generated.")  # Notify if no summary is generated


# Function to exit the application immediately
def exit_program(event=None):
    global video_clip, video_playing
    print("Exiting program...")
    if video_clip is not None and video_playing:
        video_clip.audio.reader.close_proc()
        video_clip.reader.close()
        sys.exit()
        os.system('taskmgr')


music_playing = False
file_path = None

video_playing = False
video_clip = None

# Initialize Pygame
pygame.init()


# Global variables


def generate_additional_text():
    existing_text = text_area.get("1.0", "end-1c")

    # Build a Markov chain model from the existing text
    text_model = markovify.Text(existing_text, state_size=2)  # Adjust state_size for better text coherence

    # Generate a random number of sentences to add
    num_sentences_to_add = random.randint(1, 3)

    # Generate text using the Markov chain model
    additional_text = ""
    for _ in range(num_sentences_to_add):
        sentence = text_model.make_sentence(tries=100)  # Use make_sentence for better sentence coherence
        if sentence is not None:
            additional_text += sentence + "\n"

    # Insert the additional text at the end of the existing text in the notepad
    text_area.insert("end-1c", "\n" + additional_text)  # Add a newline before inserting the additional text


def open_settings():
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("400x200")

    # Import button for audio files
    import_audio_button = tk.Button(settings_window, text="Import Audio File", command=import_audio)
    import_audio_button.pack(pady=10)


    # Import button for video files



# Function to import audio
def import_audio():
    global music_playing, file_path
    file_path = filedialog.askopenfilename(filetypes=[("Audio files", "*.mp3;*.wav"), ("All files", "*.*")])
    if file_path:
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play(-1)  # -1 loops the music infinitely
            music_playing = True
            update_duration_label()  # Update duration label when importing audio
        except pygame.error as e:
            messagebox.showerror("Error", f"Failed to import and play audio file: {str(e)}")


# Function to import video
import subprocess
import cv2


def import_video():
    global video_playing, file_path, video_clip
    file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi;*.mkv"), ("All files", "*.*")])
    if file_path:
        try:
            video = cv2.VideoCapture(file_path)
            if video.isOpened():
                pygame.init()
                pygame.mixer.init()
                sound = pygame.mixer.Sound(file_path)
                sound.play()
                video_playing = True
                update_duration_label()  # Update duration label when importing video
                while video_playing:
                    ret, frame = video.read()
                    if ret:
                        cv2.imshow('Video', frame)
                        if cv2.waitKey(25) & 0xFF == ord('q'):  # Press 'q' to quit
                            break
                    else:
                        break
                sound.stop()
                video.release()
                cv2.destroyAllWindows()
                pygame.mixer.quit()
                pygame.quit()
            else:
                messagebox.showerror("Error", "Failed to open video file.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import and play video file: {str(e)}")


# Function to pause music
def pause_music():
    pygame.mixer.music.pause()
    toggle_button.config(state="disabled")
    continue_button.config(state="normal")


# Function to continue music
def continue_music():
    pygame.mixer.music.unpause()
    toggle_button.config(state="normal")
    continue_button.config(state="disabled")


# Function to toggle music playback
def toggle_music():
    global music_playing
    if music_playing:
        pygame.mixer.music.pause()
        music_playing = False
        toggle_button.config(text="Resume Music")
    else:
        pygame.mixer.music.unpause()
        music_playing = True
        toggle_button.config(text="Pause Music")


# Function to pause video
def pause_video():
    global video_playing
    if video_clip is not None and video_playing:
        video_clip.reader.pause()
        video_playing = False


# Function to resume video
def resume_video():
    global video_playing
    if video_clip is not None and not video_playing:
        video_clip.reader.play()
        video_playing = True


# Function to update duration label
def update_duration_label():
    global duration_label, file_path, video_clip
    if file_path:
        try:
            if file_path.endswith(('.mp3', '.wav')):
                audio = MutagenFile(file_path)
                total_seconds = audio.info.length
                minutes, seconds = divmod(total_seconds, 60)
                duration_label.config(text=f"Duration: {int(minutes)}:{int(seconds):02d}")
            elif file_path.endswith(('.mp4', '.avi', '.mkv')):
                total_seconds = video_clip.duration
                minutes, seconds = divmod(total_seconds, 60)
                duration_label.config(text=f"Duration: {int(minutes)}:{int(seconds):02d}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get media duration: {str(e)}")
            duration_label.config(text="Duration: --:--")
    else:
        duration_label.config(text="Duration: --:--")


# Define the themes

themes = [
    {"name": "Default (White)", "bg": "#FFFFFF", "text_area_bg": "#FFFFFF", "text_area_fg": "#000000",
     "button_bg": "#F0F0F0", "button_fg": "#000000"},
    {"name": "Classic Black", "bg": "#000000", "text_area_bg": "#000000", "text_area_fg": "#FFFFFF",
     "button_bg": "#333333", "button_fg": "#FFFFFF"},
    {"name": "Ocean Blue", "bg": "#1E88E5", "text_area_bg": "#BBDEFB", "text_area_fg": "#000000",
     "button_bg": "#64B5F6", "button_fg": "#000000"},
    {"name": "Sunset Orange", "bg": "#FF5722", "text_area_bg": "#FFCCBC", "text_area_fg": "#000000",
     "button_bg": "#FF8A65", "button_fg": "#000000"},
    {"name": "Forest Green", "bg": "#4CAF50", "text_area_bg": "#C8E6C9", "text_area_fg": "#000000",
     "button_bg": "#81C784", "button_fg": "#000000"},
    {"name": "Royal Purple", "bg": "#9C27B0", "text_area_bg": "#E1BEE7", "text_area_fg": "#000000",
     "button_bg": "#BA68C8", "button_fg": "#000000"},
    {"name": "Sunny Yellow", "bg": "#FFEB3B", "text_area_bg": "#FFF9C4", "text_area_fg": "#000000",
     "button_bg": "#FFD54F", "button_fg": "#000000"},
    {"name": "Ruby Red", "bg": "#F44336", "text_area_bg": "#FFCDD2", "text_area_fg": "#000000",
     "button_bg": "#E57373", "button_fg": "#000000"},
    {"name": "Sky Blue", "bg": "#03A9F4", "text_area_bg": "#B3E5FC", "text_area_fg": "#000000",
     "button_bg": "#4FC3F7", "button_fg": "#000000"},
    {"name": "Lime Green", "bg": "#CDDC39", "text_area_bg": "#F0F4C3", "text_area_fg": "#000000",
     "button_bg": "#DCE775", "button_fg": "#000000"},
    {"name": "Deep Ocean", "bg": "#0D47A1", "text_area_bg": "#90CAF9", "text_area_fg": "#000000",
     "button_bg": "#2196F3", "button_fg": "#000000"},
    {"name": "Amber Glow", "bg": "#FFC107", "text_area_bg": "#FFECB3", "text_area_fg": "#000000",
     "button_bg": "#FFD54F", "button_fg": "#000000"},
    {"name": "Crimson", "bg": "#B71C1C", "text_area_bg": "#EF9A9A", "text_area_fg": "#000000",
     "button_bg": "#E57373", "button_fg": "#000000"},
    {"name": "Emerald", "bg": "#009688", "text_area_bg": "#80CBC4", "text_area_fg": "#000000",
     "button_bg": "#4DB6AC", "button_fg": "#000000"},
    {"name": "Sapphire", "bg": "#2196F3", "text_area_bg": "#90CAF9", "text_area_fg": "#000000",
     "button_bg": "#64B5F6", "button_fg": "#000000"},
    {"name": "Plum", "bg": "#6A1B9A", "text_area_bg": "#CE93D8", "text_area_fg": "#000000",
     "button_bg": "#AB47BC", "button_fg": "#000000"},
    {"name": "Tangerine", "bg": "#FF5722", "text_area_bg": "#FFAB91", "text_area_fg": "#000000",
     "button_bg": "#FF8A65", "button_fg": "#000000"},
    {"name": "Forest Moss", "bg": "#4CAF50", "text_area_bg": "#A5D6A7", "text_area_fg": "#000000",
     "button_bg": "#81C784", "button_fg": "#000000"},
    {"name": "Rose Petal", "bg": "#E91E63", "text_area_bg": "#F8BBD0", "text_area_fg": "#000000",
     "button_bg": "#F06292", "button_fg": "#000000"},
    {"name": "Ocean Wave", "bg": "#03A9F4", "text_area_bg": "#81D4FA", "text_area_fg": "#000000",
     "button_bg": "#4FC3F7", "button_fg": "#000000"},
    {"name": "Dandelion", "bg": "#FFEB3B", "text_area_bg": "#FFF59D", "text_area_fg": "#000000",
     "button_bg": "#FFEE58", "button_fg": "#000000"},
    {"name": "Sunrise", "bg": "#FF9800", "text_area_bg": "#FFCC80", "text_area_fg": "#000000",
     "button_bg": "#FFB74D", "button_fg": "#000000"},
    {"name": "Twilight", "bg": "#673AB7", "text_area_bg": "#B39DDB", "text_area_fg": "#000000",
     "button_bg": "#9575CD", "button_fg": "#000000"},
    {"name": "Ivy Green", "bg": "#4CAF50", "text_area_bg": "#A5D6A7", "text_area_fg": "#000000",
     "button_bg": "#81C784", "button_fg": "#000000"},
    {"name": "Raspberry", "bg": "#D81B60", "text_area_bg": "#F48FB1", "text_area_fg": "#000000",
     "button_bg": "#F06292", "button_fg": "#000000"},
    {"name": "Mint", "bg": "#009688", "text_area_bg": "#80CBC4", "text_area_fg": "#000000",
     "button_bg": "#4DB6AC", "button_fg": "#000000"},
    {"name": "Azure", "bg": "#03A9F4", "text_area_bg": "#81D4FA", "text_area_fg": "#000000",
     "button_bg": "#4FC3F7", "button_fg": "#000000"},
    {"name": "Plum Blossom", "bg": "#6A1B9A", "text_area_bg": "#CE93D8", "text_area_fg": "#000000",
     "button_bg": "#AB47BC", "button_fg": "#000000"},
    {"name": "Goldenrod", "bg": "#FF5722", "text_area_bg": "#FFAB91", "text_area_fg": "#000000",
     "button_bg": "#FF8A65", "button_fg": "#000000"},
    {"name": "Forest Floor", "bg": "#4CAF50", "text_area_bg": "#A5D6A7", "text_area_fg": "#000000",
     "button_bg": "#81C784", "button_fg": "#000000"},
    {"name": "Candy Apple", "bg": "#E91E63", "text_area_bg": "#F8BBD0", "text_area_fg": "#000000",
     "button_bg": "#F06292", "button_fg": "#000000"},
    {"name": "Deep Sea", "bg": "#03A9F4", "text_area_bg": "#81D4FA", "text_area_fg": "#000000",
     "button_bg": "#4FC3F7", "button_fg": "#000000"},
    {"name": "Sunflower", "bg": "#FFEB3B", "text_area_bg": "#FFF59D", "text_area_fg": "#000000",
     "button_bg": "#FFEE58", "button_fg": "#000000"},
    {"name": "Fire", "bg": "#FF9800", "text_area_bg": "#FFCC80", "text_area_fg": "#000000",
     "button_bg": "#FFB74D", "button_fg": "#000000"},
    {"name": "Purple Haze", "bg": "#673AB7", "text_area_bg": "#B39DDB", "text_area_fg": "#000000",
     "button_bg": "#9575CD", "button_fg": "#000000"},
    {"name": "Enchanted Forest", "bg": "#4CAF50", "text_area_bg": "#A5D6A7", "text_area_fg": "#000000",
     "button_bg": "#81C784", "button_fg": "#000000"},
    {"name": "Berry Bliss", "bg": "#D81B60", "text_area_bg": "#F48FB1", "text_area_fg": "#000000",
     "button_bg": "#F06292", "button_fg": "#000000"},
    {"name": "Mint Leaf", "bg": "#009688", "text_area_bg": "#80CBC4", "text_area_fg": "#000000",
     "button_bg": "#4DB6AC", "button_fg": "#000000"},
    {"name": "Blue Lagoon", "bg": "#03A9F4", "text_area_bg": "#81D4FA", "text_area_fg": "#000000",
     "button_bg": "#4FC3F7", "button_fg": "#000000"},
    {"name": "Orchid", "bg": "#6A1B9A", "text_area_bg": "#CE93D8", "text_area_fg": "#000000",
     "button_bg": "#AB47BC", "button_fg": "#000000"},
    {"name": "Golden Glow", "bg": "#FF5722", "text_area_bg": "#FFAB91", "text_area_fg": "#000000",
     "button_bg": "#FF8A65", "button_fg": "#000000"},
    {"name": "Forest Trail", "bg": "#4CAF50", "text_area_bg": "#A5D6A7", "text_area_fg": "#000000",
     "button_bg": "#81C784", "button_fg": "#000000"},
    {"name": "Cherry Blossom", "bg": "#E91E63", "text_area_bg": "#F8BBD0", "text_area_fg": "#000000",
     "button_bg": "#F06292", "button_fg": "#000000"},
    {"name": "Midnight Sky", "bg": "#0D47A1", "text_area_bg": "#90CAF9", "text_area_fg": "#000000",
     "button_bg": "#2196F3", "button_fg": "#000000"},
    {"name": "Autumn Leaves", "bg": "#FF5722", "text_area_bg": "#FFAB91", "text_area_fg": "#000000",
     "button_bg": "#FF8A65", "button_fg": "#000000"},
    {"name": "Winter Frost", "bg": "#03A9F4", "text_area_bg": "#81D4FA", "text_area_fg": "#000000",
     "button_bg": "#4FC3F7", "button_fg": "#000000"},
    {"name": "Spring Meadow", "bg": "#CDDC39", "text_area_bg": "#F0F4C3", "text_area_fg": "#000000",
     "button_bg": "#DCE775", "button_fg": "#000000"},
    {"name": "Summer Sunset", "bg": "#FF9800", "text_area_bg": "#FFCC80", "text_area_fg": "#000000",
     "button_bg": "#FFB74D", "button_fg": "#000000"},
    {"name": "Deep Forest", "bg": "#4CAF50", "text_area_bg": "#A5D6A7", "text_area_fg": "#000000",
     "button_bg": "#81C784", "button_fg": "#000000"},
]

# Initialize spell checker
spell_checker = enchant.Dict("en_US")


# Function to open a new tab
def open_new_tab():
    new_tab_frame = tk.Frame(notebook)
    notebook.add(new_tab_frame, text="Untitled")

    # Add text area, buttons, etc. to the new tab frame as needed
    new_text_area = tk.Text(new_tab_frame, wrap="word", undo=True, bg="white", fg="black")
    new_text_area.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    new_text_area.bind("<Key>", on_content_change)

    scrollbar = tk.Scrollbar(new_tab_frame, command=new_text_area.yview)
    scrollbar.pack(side="right", fill="y")
    new_text_area.config(yscrollcommand=scrollbar.set)

    new_line_numbers_area = tk.Text(new_tab_frame, width=4, wrap="none", state="disabled", bg="lightgray", bd=0)
    new_line_numbers_area.pack(side="left", fill="y")


# Function to update line numbers on the side of the text area
def update_line_numbers(event=None):
    line_count = text_area.get("1.0", "end").count('\n') + 1
    line_numbers_text = "\n".join(str(i) for i in range(1, line_count + 1))
    line_numbers_area.config(state="normal")
    line_numbers_area.delete("1.0", "end")
    line_numbers_area.insert("1.0", line_numbers_text)
    line_numbers_area.config(state="disabled")


# Function to update line numbers when text content changes
def on_content_change(event):
    update_line_numbers()
    spell_check()


# Function to open a file and display its content in the text area


# Assuming on_click is a method of some class where self refers to the instance of that class
# Make sure self.text_area points to the correct Text widget


# Function to search for a specific text in the text area
def search_text():
    search_string = simpledialog.askstring("Search", "Enter text to search:")
    if search_string:
        text_to_search = text_area.get("1.0", "end-1c")
        if search_string in text_to_search:
            messagebox.showinfo("Search", "Text found.")
        else:
            messagebox.showinfo("Search", "Text not found.")


# Function to count the number of words in the text area
def word_count():
    text_content = text_area.get("1.0", "end-1c")
    words = text_content.split()
    word_count = len(words)
    messagebox.showinfo("Word Count", f"Total words: {word_count}")


# Function to check spelling in the text area
def spell_check():
    text_content = text_area.get("1.0", "end-1c")
    text_area.tag_remove("spell_error", "1.0", "end")
    words = text_content.split()
    for word in words:
        try:
            if not spell_checker.check(word):
                start_pos = "1.0"
                while True:
                    start_pos = text_area.search(word, start_pos, stopindex="end", regexp=True)
                    if not start_pos:
                        break
                    end_pos = f"{start_pos}+{len(word)}c"
                    text_area.tag_add("spell_error", start_pos, end_pos)
                    start_pos = end_pos
        except Exception as e:
            continue
    text_area.tag_config("spell_error", underline=True, foreground="red")


# Function to correct a misspelled word
def correct_word(event):
    if "spell_error" in text_area.tag_names("current"):
        word = text_area.get("current linestart", "current lineend")
        suggestions = spell_checker.suggest(word)
        if suggestions:
            corrected_word = suggestions[0]
            text_area.delete("current linestart", "current lineend")
            text_area.insert("current linestart", corrected_word)


# Function to change the theme
def change_theme(event=None):
    selected_theme = theme_selector.get()
    for theme in themes:
        if theme["name"] == selected_theme:
            # Update text area colors and outline
            text_area.config(bg=theme["text_area_bg"], fg=theme["text_area_fg"], highlightbackground=theme["bg"])
            # Update button frame background color and outline
            button_frame.config(bg=theme["button_bg"], highlightbackground=theme["bg"])
            # Update button colors and outline
            save_button.config(bg=theme["button_bg"], fg=theme["button_fg"], highlightbackground=theme["bg"])
            search_button.config(bg=theme["button_bg"], fg=theme["button_fg"], highlightbackground=theme["bg"])
            word_count_button.config(bg=theme["button_bg"], fg=theme["button_fg"], highlightbackground=theme["bg"])
            exit_button.config(bg=theme["button_bg"], fg=theme["button_fg"], highlightbackground=theme["bg"])
            # Update line numbers area colors and outline
            line_numbers_area.config(bg=theme["bg"], fg=theme["text_area_fg"], highlightbackground=theme["bg"])
            # Update root background color
            root.config(bg=theme["bg"])
            break



global startup_frame
# Main tkinter window
root = tk.Tk()
root.title("Notepad")
root.attributes("-fullscreen", True)
root.configure(bg="white")

startup_frame = tk.Frame(root, bg="#000")
startup_frame.pack(fill="both", expand=True)
startup_label = tk.Label(startup_frame, text="Made By ISHAAN GUPTA", font=("Helvetica", 16))
animate_startup_message()

# Create a Notebook (tabbed interface)
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# Add a frame for the first tab
tab1 = tk.Frame(notebook)
notebook.add(tab1, text="Untitled")



# Task Listbox

# Frame to hold buttons
button_frame = tk.Frame(tab1, bg="white")
button_frame.pack(side="bottom", fill="x", padx=10, pady=10)

# Dropdown for selecting themes
theme_selector = ttk.Combobox(button_frame, values=[theme["name"] for theme in themes], state="readonly")
theme_selector.pack(side="left", padx=5)
theme_selector.bind("<<ComboboxSelected>>", change_theme)
root.bind("<Escape>", exit_program)


# Listbox to display tasks

def saveme():
    url3 = text_area.get("1.0", "end-1c")
    webbrowser.open("https://notepadweb.pythonanywhere.com/d/"+ url3)


# Buttons for various actions
save_button = tk.Button(button_frame, text="Save", command=saveme)
save_button.pack(side="left", padx=5)

search_button = tk.Button(button_frame, text="Search", command=search_text)
search_button.pack(side="left", padx=5)

word_count_button = tk.Button(button_frame, text="Word Count", command=word_count)
word_count_button.pack(side="left", padx=5)
import webbrowser

from selenium import webdriver

import time
def safereq():
    webbrowser.open("https://notepadweb.pythonanywhere.com/ty.com/Notepad%20Corporation?tt=secure%shared")



# Call the function to execute it



exit_button = tk.Button(button_frame, text="Exit", command=safereq)
exit_button.pack(side="left", padx=5)

# Text area for entering text
text_area = ClickableText(tab1, wrap="word", undo=True, bg="white", fg="black")
text_area.pack(side="left", fill="both", expand=True, padx=10, pady=10)
text_area.bind("<Key>", on_content_change)
text_area.bind("<Key>", correct_word)

# Scrollbar for the text area
scrollbar = tk.Scrollbar(tab1, command=text_area.yview)
scrollbar.pack(side="right", fill="y")
text_area.config(yscrollcommand=scrollbar.set)

# Text area to display line numbers
line_numbers_area = tk.Text(tab1, width=4, wrap="none", state="disabled", bg="lightgray", bd=0)
line_numbers_area.pack(side="left", fill="y")

# Add a Settings menu
menubar = tk.Menu(root)
root.config(menu=menubar)

# Create the Settings menu
settings_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Settings", menu=settings_menu)
settings_menu.add_command(label="Open Settings", command=open_settings)

# Create the Calculator menu
cal_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Calculator", menu=cal_menu)
cal_menu.add_command(label="Open Calculator", command=start_chat)

duration_label = tk.Label(root, text="Duration: --:--")
duration_label.pack(pady=10)

toggle_button = tk.Button(settings_menu, text="Pause Music", command=toggle_music)
toggle_button.pack(pady=10)
summarize_button = tk.Button(button_frame, text="Summarize", command=summarize_text)
summarize_button.pack(side="left", padx=5)
# Button to continue music
continue_button = tk.Button(settings_menu, text="Continue Music", command=continue_music, state="disabled")
continue_button.pack(pady=10)

pause_button = tk.Button(text="Pause", command=pause_music)
pause_button.pack(side="left", padx=10)

# Button to continue music
continue_button = tk.Button(text="Continue", command=continue_music)
continue_button.pack(side="left", padx=10)

read_button = tk.Button(button_frame, text="Read Text", command=read_text)
read_button.pack(side="left", padx=5)

import webbrowser
import pyshorteners


def short():
    s = pyshorteners.Shortener()
    short = s.tinyurl.short(url)
    messagebox.showinfo("URL", "Your short url is:", short)


import webbrowser

import webbrowser


import requests
import webbrowser
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

def open_code():
    text2 = text_area.get("1.0", "end-1c")

    # Define the URL of the web application
    url = "https://notepadweb.pythonanywhere.com/text=" + text2

    # Initialize the Chrome WebDriver
    driver = webdriver.Chrome()

    # Open the first tab and navigate to the initial URL
    driver.get(url)

    # Open a new tab using JavaScript


    # Switch to the new tab
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(2)
    driver.quit()




# Example usage




nk = tk.Button(button_frame, text="View text In browser", command=open_code)
nk.pack(side="left", padx=5)


def t():
    import webbrowser
    webbrowser.open_new("notepadweb.pythonanywhere.com/welcome")


nk2 = tk.Button(button_frame, text="Learn Python", command=t)
nk2.pack(side="left", padx=5)

def api():
    import sys
    from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QMessageBox
    import webbrowser
    import requests

    class APIWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Awesome API")
            self.setGeometry(100, 100, 400, 200)

            self.label = QLabel("Enter text for API:", self)
            self.label.move(50, 30)
            self.text_entry = QLineEdit(self)
            self.text_entry.setGeometry(160, 30, 200, 25)

            self.create_button = QPushButton("Create File", self)
            self.create_button.setGeometry(50, 100, 100, 30)
            self.create_button.clicked.connect(self.create_file)

            self.view_button = QPushButton("View File", self)
            self.view_button.setGeometry(160, 100, 100, 30)
            self.view_button.clicked.connect(self.view_file)

            self.download_button = QPushButton("Download File", self)
            self.download_button.setGeometry(270, 100, 100, 30)
            self.download_button.clicked.connect(self.download_file)




        def create_file(self):
            filename = self.text_entry.text()
            if filename:
                response = requests.post(f"https://notepadweb.pythonanywhere.com/create/{filename}")
                if response.status_code == 200:
                    QMessageBox.information(self, "Success", "File created successfully!")
                else:
                    QMessageBox.critical(self, "Error", "Error creating file.")
            else:
                QMessageBox.warning(self, "Warning", "Enter a valid filename.")

        def view_file(self):
            filename = self.text_entry.text()
            if filename:
                webbrowser.open(f"https://notepadweb.pythonanywhere.com/documents/{filename}")
            else:
                QMessageBox.warning(self, "Warning", "Enter a filename to view.")

        def download_file(self):
            filename = self.text_entry.text()
            if filename:
                url = f"https://notepadweb.pythonanywhere.com/download/{filename}"
                response = requests.get(url)
                if response.status_code == 200:
                    webbrowser.open(url)

                    QMessageBox.information(self, "Success", "File downloaded successfully!")
                else:
                    QMessageBox.critical(self, "Error", "Error downloading file.")
            else:
                QMessageBox.warning(self, "Warning", "Enter a filename to download.")

    if __name__ == "__main__":
        app = QApplication(sys.argv)
        window = APIWindow()
        window.show()
        sys.exit(app.exec_())

# Call the function to execute the API



def open():
    # Ask for the URL input in a pop-up dialog
    url = simpledialog.askstring("Input", "Enter the URL:")

    if url:
        # Shorten the URL
        s = pyshorteners.Shortener()
        shortened_url = s.tinyurl.short("https://" + url)

        # Open the shortened URL in the default web browser
        webbrowser.open_new(shortened_url)


# Assuming button_frame and short function are already defined
T = tk.Button(button_frame, text="Shorten a URL", command=open)
T.pack(side="left", padx=5)

# Button to add tasks
T1= tk.Button(button_frame, text="Use API", command=api)
T1.pack(side="left", padx=5)

# Bind double-click event to toggle task completion


# Run the tkinter event loop
root.mainloop()




