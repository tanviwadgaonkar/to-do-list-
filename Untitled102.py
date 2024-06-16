#!/usr/bin/env python
# coding: utf-8

# In[7]:


import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime
import pyttsx3
import speech_recognition as sr

class TodoListApp:
    def __init__(self, master):
        self.master = master
        self.master.title("To-Do List")

        self.frame_tasks = tk.Frame(master)
        self.frame_tasks.pack(pady=10)

        self.listbox_tasks = tk.Listbox(self.frame_tasks, height=10, width=50, border=0)
        self.listbox_tasks.pack(side=tk.LEFT, fill=tk.BOTH)

        self.scrollbar_tasks = tk.Scrollbar(self.frame_tasks, orient=tk.VERTICAL, command=self.listbox_tasks.yview)
        self.scrollbar_tasks.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox_tasks.config(yscrollcommand=self.scrollbar_tasks.set)

        self.entry_task = tk.Entry(master, width=50)
        self.entry_task.pack(pady=5)

        self.frame_priority = tk.Frame(master)
        self.frame_priority.pack()

        self.radio_priority = tk.StringVar(value="non-important")
        self.radio_important = tk.Radiobutton(self.frame_priority, text="Important", variable=self.radio_priority, value="important")
        self.radio_important.pack(side=tk.LEFT)

        self.radio_non_important = tk.Radiobutton(self.frame_priority, text="Non-important", variable=self.radio_priority, value="non-important")
        self.radio_non_important.pack(side=tk.LEFT)

        self.frame_buttons = tk.Frame(master)
        self.frame_buttons.pack()

        self.buttons = [
            ("Add Task", self.add_task),
            ("Delete Task", self.delete_task),
            ("Clear All", self.clear_tasks),
            ("Voice Command", self.voice_command)
        ]

        for text, command in self.buttons:
            button = tk.Button(self.frame_buttons, text=text, width=15, command=command)
            button.pack(side=tk.LEFT, padx=5)

        self.load_tasks()

        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()

        self.master.after(60000, self.check_reminders)

    def add_task(self):
        task = self.entry_task.get().strip()
        priority = self.radio_priority.get()

        if not task:
            messagebox.showwarning("Warning", "Please enter a task.")
            return

        if priority == "important":
            reminder_time = simpledialog.askstring("Reminder", "Enter reminder time (format: HH:MM):")
            if not reminder_time:
                messagebox.showwarning("Warning", "Reminder time not set.")
                return
        else:
            reminder_time = None

        task_info = f"{task} - ({priority}) - {reminder_time if reminder_time else 'None'}"
        self.listbox_tasks.insert(tk.END, task_info)
        self.save_tasks()
        self.entry_task.delete(0, tk.END)
        messagebox.showinfo("Success", "Task added successfully.")

    def delete_task(self):
        try:
            index = self.listbox_tasks.curselection()[0]
            task_to_delete = self.listbox_tasks.get(index)
            confirmation = messagebox.askyesno("Confirmation", f"Are you sure you want to delete the task:\n{task_to_delete}")
            if confirmation:
                self.listbox_tasks.delete(index)
                self.save_tasks()
                messagebox.showinfo("Success", "Task deleted successfully.")
        except IndexError:
            messagebox.showwarning("Warning", "Please select a task to delete.")

    def clear_tasks(self):
        if messagebox.askyesno("Confirmation", "Are you sure you want to clear all tasks?"):
            self.listbox_tasks.delete(0, tk.END)
            self.save_tasks()
            messagebox.showinfo("Success", "All tasks cleared successfully.")

    def save_tasks(self):
        tasks = self.listbox_tasks.get(0, tk.END)
        try:
            with open("tasks.txt", "w") as f:
                for task in tasks:
                    f.write(task + "\n")
        except IOError as e:
            messagebox.showwarning("Warning", f"Failed to save tasks. {e}")

    def load_tasks(self):
        try:
            with open("tasks.txt", "r") as f:
                for line in f:
                    self.listbox_tasks.insert(tk.END, line.strip())
        except FileNotFoundError:
            pass
        except IOError as e:
            messagebox.showwarning("Warning", f"Failed to load tasks. {e}")

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def check_reminders(self):
        current_time = datetime.now().strftime("%H:%M")
        for index in range(self.listbox_tasks.size()):
            task_info = self.listbox_tasks.get(index)
            task_time = task_info.split("-")[-1].strip()
            if task_time and current_time == task_time:
                self.speak(f"Don't forget to complete {task_info.split('-')[0].strip()}")
        self.master.after(60000, self.check_reminders)

    def process_command(self, command):
        doc = command.lower()

        if "add task" in doc:
            try:
                task = doc.split('add task')[1].strip()

                priority = simpledialog.askstring("Priority", "Is this task important or non-important?")
                if priority.lower() == "important":
                    reminder_time = simpledialog.askstring("Reminder", "Enter reminder time (format: HH:MM):")
                    if not reminder_time:
                        messagebox.showwarning("Warning", "Reminder time not set.")
                        return
                else:
                    reminder_time = None

                task_info = f"{task} - ({priority}) - {reminder_time if reminder_time else 'None'}"
                self.listbox_tasks.insert(tk.END, task_info)
                self.save_tasks()
                messagebox.showinfo("Success", "Task added successfully.")
            except IndexError:
                messagebox.showwarning("Warning", "Could not extract task from command.")

        elif "delete task" in doc:
            task_to_delete = ""
            try:
                task_to_delete = doc.split('delete task')[1].strip()

                found = False
                for i in range(self.listbox_tasks.size()):
                    task_info = self.listbox_tasks.get(i)
                    task_description = task_info.split(" - ")[0].lower()

                    if task_to_delete.lower() == task_description:
                        self.listbox_tasks.delete(i)
                        self.save_tasks()
                        messagebox.showinfo("Success", "Task deleted successfully.")
                        found = True
                        break

                if not found:
                    # Try partial match search
                    for i in range(self.listbox_tasks.size()):
                        task_info = self.listbox_tasks.get(i)
                        if task_to_delete.lower() in task_info.lower():
                            self.listbox_tasks.delete(i)
                            self.save_tasks()
                            messagebox.showinfo("Success", "Task deleted successfully.")
                            found = True
                            break

                if not found:
                    messagebox.showwarning("Warning", f"No tasks containing '{task_to_delete}' found.")
            except IndexError:
                messagebox.showwarning("Warning", "Could not extract task from command.")

        elif "clear all" in doc:
            self.clear_tasks()
        else:
            messagebox.showwarning("Warning", "Command not recognized.")

    def voice_command(self):
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)
                self.speak("Listening for command...")
                print("Listening...")
                audio = self.recognizer.listen(source)

            command = self.recognizer.recognize_google(audio)
            self.speak(f"Command recognized: {command}")
            print(f"Command recognized: {command}")
            self.process_command(command)
        except sr.UnknownValueError:
            messagebox.showwarning("Warning", "Could not understand audio.")
        except sr.RequestError as e:
            messagebox.showwarning("Warning", f"Could not request results from Google Speech Recognition service; {e}")

    def main(self):
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.master.mainloop()

    def on_closing(self):
        self.master.destroy()


root = tk.Tk()
app = TodoListApp(root)
app.main()


# In[ ]:




