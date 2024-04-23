from tkinter import Listbox, Tk, Label, Entry, font as tkFont, messagebox, simpledialog
import requests
import webbrowser
from tkinter import ttk
import os
import subprocess
import sqlite3
from PIL import Image, ImageTk

def createTable():
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT)''')
    conn.commit()
    conn.close()

def insert_name(username):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (username) VALUES (?)", (username,))
    conn.commit()
    conn.close()

def get_last_users(num_users):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute("SELECT username FROM users ORDER BY ROWID DESC LIMIT ?", (num_users,))
    last_users = [row[0] for row in c.fetchall()]
    conn.close()
    return last_users  

class ConfigurationWindow: 
    def __init__ (self, title, resizable, width, height):
        self.title = title
        self.resizable = resizable
        self.width = width
        self.height = height

class ConfigurationLabel:
    def __init__(self, master, text, font=None):
        self.master = master
        self.text = text
        self.font = font

class ConfigurationEntry:
    def __init__ (self, master, width, font=None, default_text=None, height=None):  
        self.master = master
        self.width = width
        self.font = font
        self.default_text = default_text
        self.height = height  

class ConfigurationButton:
    def __init__(self, master, text, command=None, font=None):
        self.master = master
        self.text = text
        self.command = command
        self.font = font

def configuration_window(window, config):
    window.title(config.title)
    window.resizable(*config.resizable)
    window.geometry(f"{config.width}x{config.height}")

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    window.geometry(f"{width}x{height}+{x}+{y}")

def createLabel(config, textBold=False):
    label = Label(config.master, text=config.text, fg="white", bg="#333333")
    if config.font:
        label_font = tkFont.Font(family=config.font, size=14)  
        if textBold:
            label_font.config(weight="bold")
        label.config(font=label_font)
    return label

def createEntry(config):
    entry = Entry(config.master, width=config.width, bg="white")
    if config.font:
        entry_font = tkFont.Font(family=config.font, size=14)  
        entry.config(font=entry_font)
    if config.default_text:
        entry.insert(0, config.default_text)
    return entry 

def clearEntry(event):
    event.widget.delete(0, 'end')  

def getUsername():
    username = entry.get()
    if username:
        insert_name(username)
        url = f"https://api.github.com/users/{username}/repos"
        response = requests.get(url)
        if response.status_code == 200:
            repositories = response.json()
            showRepositories(repositories)
        else:
            print(f"Error: {response.status_code}")
            simpledialog.messagebox.showinfo("Error", f"User '{username}' not found.")

def showRepositories(repositories):
    for repo in repositories:
        tree.insert('', 'end', values=(repo["name"], "Go to Repo"), tags=("button",))

def on_btn_click(event):
    if tree.selection():
        item = tree.selection()[0]
        repo_name = tree.item(item, "values")[0]
        if messagebox.askyesno("Confirmation", f"Do you want to go to the repository '{repo_name}'?"):
            url = f"https://github.com/{entry.get()}/{repo_name}.git"
            webbrowser.open(url)
            print(f"Opening repository '{repo_name}'")
    else:
        return

def refreshRecentUsers():
    last_users_listbox.delete(0, 'end')  
    last_users = get_last_users(5)  
    if last_users:
        for user in last_users:
            last_users_listbox.insert("end", user)
    else:
        last_users_listbox.insert("end", "No users found.")

    
def refreshTable():
    entry.delete(0, 'end')

    for item in tree.get_children():
        tree.delete(item)

    username = entry.get()
    if username:
        url = f"https://api.github.com/users/{username}/repos"
        response = requests.get(url)
        if response.status_code == 200:
            repositories = response.json()
            showRepositories(repositories)
        else:
            print(f"Error: {response.status_code}")
    refreshRecentUsers()             

def cloningRepositories():
    if tree.selection():
        item = tree.selection()[0]
        repo_name = tree.item(item, "values")[0]
        username = entry.get()

        if username:
            git_url = f"https://github.com/{username}/{repo_name}.git"
            destination_dir = os.path.join("C:\\Github", repo_name) 

            if not os.path.exists(destination_dir):
                os.makedirs(destination_dir)
            
            subprocess.run(["git", "clone", git_url, destination_dir])
            print(f"Cloning repository '{repo_name}' to {destination_dir}")

            os.startfile(destination_dir)
        else:
            messagebox.showinfo("No Selection", "Please select a repository.")   

def on_listbox_double_click(event):
    selected_index = last_users_listbox.curselection()
    if selected_index:
        selected_user = last_users_listbox.get(selected_index[0])
        entry.delete(0, 'end')  
        entry.insert(0, selected_user)  

def clearRecentUsers():
    last_users_listbox.delete(0, 'end')

    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute("DELETE FROM users")
    conn.commit()
    conn.close()

def open_github(event):
    webbrowser.open("https://github.com/lucascampos04")

def main():
    global entry, tree, last_users_listbox

    width = 800
    height = 600 

    config = ConfigurationWindow("My Window", (False, False), width, height)

    window = Tk()
    configuration_window(window, config)
    center_window(window, width, height)

    # Imagem
    image = Image.open("github.png")  
    width, height = 40, 40
    resized_image = image.resize((width, height))  

    tk_image = ImageTk.PhotoImage(resized_image)

    image_label = Label(window, image=tk_image)
    image_label.place(x=755, y=1)

    # Título e entrada de usuário
    config_title_label = ConfigurationLabel(window, "Repositories", font="Arial") 
    titleLabel = createLabel(config_title_label, textBold=True)
    titleLabel.place(x=350, y=50)

    config_entry = ConfigurationEntry(window, width=25, font="Arial", default_text="Username here", height=22)  
    entry = createEntry(config_entry)
    entry.bind("<FocusIn>", clearEntry)  
    entry.place(x=200, y=101)

    image_label.bind("<Button-1>", open_github)
    # Botões
    config_button = ConfigurationButton(window, "Search", command=lambda: window.after(100, getUsername), font="Arial 17")  
    button = ttk.Button(config_button.master, text=config_button.text, command=config_button.command)
    button.place(x=550, y=100)

    refresh_button = ConfigurationButton(window, "Refresh", command=lambda: window.after(100, refreshTable), font="Arial")
    button_refresh = ttk.Button(refresh_button.master, text=refresh_button.text, command=refresh_button.command)
    button_refresh.place(x=710, y=190)
    
    clear_button = ConfigurationButton(window, "Clear Recents", command=lambda: window.after(100, clearRecentUsers), font="Arial")
    clear_refresh = ttk.Button(clear_button.master, text=clear_button.text, command=clear_button.command)
    clear_refresh.place(x=710, y=270)

    cloning_button = ConfigurationButton(window, "Cloning", command=lambda: window.after(100, cloningRepositories), font="Arial")
    cloning_refresh = ttk.Button(cloning_button.master, text=cloning_button.text, command=cloning_button.command)
    cloning_refresh.place(x=710, y=230)

    # Lista de usuários recentes
    last_users_frame = ttk.LabelFrame(window, text="Last Searched Users")
    last_users_frame.place(x=10, y=10, width=150, height=100)

    last_users_listbox = Listbox(last_users_frame, font=('Arial', 11), selectmode="single", borderwidth=0, border=None, bg="#f0f0f0")
    last_users_listbox.pack(fill="both", expand=True)

    last_users = get_last_users(5)
    if last_users:
        for user in last_users:
            last_users_listbox.insert("end", user)
    else:
        last_users_listbox.insert("end", "No users found.")  

    # Tabela de repositórios
    tree = ttk.Treeview(window, columns=("Repositories",), show="headings", height=20) 
    tree.heading("#1", text="Repositories")
    tree.column("#1", width=600)  
    tree.place(x=100, y=150)  

    # Estilo
    style = ttk.Style(window)
    style.configure("Treeview", font=('Arial', 12), background="#ffffff", foreground="#333333")  
    style.configure("Treeview.Heading", font=('Arial', 14, 'bold'), background="#eeeeee", foreground="#333333") 
    style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])  

    tree.tag_configure("button", foreground="blue", font=("Arial", 10, "underline"))
    tree.tag_bind("button", "<Button-1>", on_btn_click)

    style.configure("Custom.TButton", background="#007bff", foreground="black", padding=10)
    style.map("Custom.TButton", background=[("active", "#0056b3")])

    button.configure(style="Custom.TButton")
    last_users_listbox.bind("<Double-Button-1>", on_listbox_double_click)
    window.configure(bg="#f0f0f0")
    
    
    window.mainloop()
main()
