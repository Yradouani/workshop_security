import tkinter as tk
from tkinter import messagebox, simpledialog
import pandas as pd
import importlib.util
from PIL import Image, ImageTk
import os
import subprocess
   
def task_exists(task_name):
    try:
        # Exécute la commande et récupère le résultat
        result = subprocess.run(['schtasks', '/query', '/tn', task_name], capture_output=True, text=True)
        
        # Si le retour est 0, la tâche existe
        if result.returncode == 0:
            return True
        else:
            return False
    except Exception as e:
        print(f"Erreur lors de la vérification de la tâche : {e}")
        return False
    
def charger_configuration(fichier_config):
    config = {}
    with open(fichier_config, 'r') as f:
        for line in f:
            key, value = line.strip().split('=')
            config[key] = value
    return config

config = charger_configuration('config.txt')

def trigger_task(state):
    if state == "activate":
        print(config["path_to_script"])
        # Vérifiez si la tâche existe
        try:
            if task_exists("AnalyseLogTask"):
                print("La tâche existe déjà.")
            else:
                # Si la tâche n'existe pas, créez-la
                os.system(f'schtasks /create /tn "AnalyseLogTask" /tr "python ./script-analyse-log.py" /sc minute /mo 2')
                print("Tâche créée : AnalyseLogTask")

            # Lancer la tâche
            os.system('schtasks /run /tn "AnalyseLogTask"')
            print("Application activée, tâche lancée.")
        except Exception as e:
            print(f"Erreur lors de la vérification de la tâche : {str(e)}")
    else:
        try:
            os.system('schtasks /delete /tn "AnalyseLogTask" /f')
            print("Tâche supprimée : AnalyseLogTask")
        except Exception as e:
            print(f"Erreur lors de la suppression de la tâche : {str(e)}")
        print("Application désactivée.")

  
def toggle_app():
    if task_exists("AnalyseLogTask"):        
        activate_button.config(text="Activer l'application")
        print("Désactivation de l'application.")
        trigger_task("deactivate")
    else:        
        activate_button.config(text="Désactiver l'application")
        print("activation de l'application.")
        trigger_task("activate")
        
def load_emails():
    try:
        df = pd.read_csv('./mail.csv')
        return df['email'].tolist()
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible de charger les emails : {str(e)}")
        return []

# Fonction pour sauvegarder les mails dans le fichier CSV
def save_emails(emails):
    try:
        df = pd.DataFrame(emails, columns=['email'])
        df.to_csv('./mail.csv', index=False)
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible de sauvegarder les emails : {str(e)}")

# Fonction pour charger les mots depuis le fichier dictionnary.py
def load_categories():
    try:
        spec = importlib.util.spec_from_file_location("sensitive_words", "./dictionnary.py")
        dictionnary = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(dictionnary)
        return dictionnary.sensitive_words
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible de charger les catégories : {str(e)}")
        return {}

# Fonction pour mettre à jour l'affichage des emails
def update_email_display():
    email_list.delete(0, tk.END)
    email_list.insert(tk.END, "  " )
    for email in emails:
        email_list.insert(tk.END, "  " + email + "  ")

# Fonction pour ajouter un email
def add_email():
    new_email = simpledialog.askstring("Ajouter un email", "Entrez l'email à ajouter:")
    if new_email:
        emails.append(new_email)
        save_emails(emails)
        update_email_display()

# Fonction pour supprimer un email
def remove_email():
    selected_email = email_list.curselection()
    if selected_email:
        email_to_remove = emails[selected_email[0]]
        emails.remove(email_to_remove)
        save_emails(emails)
        update_email_display()
    else:
        messagebox.showwarning("Avertissement", "Sélectionnez un email à supprimer.")

# Fonction pour ajouter une catégorie
def add_category():
    new_category = simpledialog.askstring("Ajouter une catégorie", "Entrez le nom de la catégorie:")
    if new_category:
        if new_category not in categories:
            categories[new_category] = []
            update_category_display()
        else:
            messagebox.showwarning("Avertissement", "La catégorie existe déjà.")

# Fonction pour supprimer une catégorie
def remove_category():
    selected_category = category_list.curselection()
    if selected_category:
        category_to_remove = list(categories.keys())[selected_category[0]]
        del categories[category_to_remove]
        update_category_display()
    else:
        messagebox.showwarning("Avertissement", "Sélectionnez une catégorie à supprimer.")

def add_word():
    selected_category = category_list.curselection()
    if selected_category:
        category_name = list(categories.keys())[selected_category[0]]
        new_word = simpledialog.askstring("Ajouter un mot", "Entrez le mot à ajouter:")
        
        if new_word:
            normalized_new_word = new_word.lower()
            if normalized_new_word not in (word.lower() for word in categories[category_name]):
                categories[category_name].append(new_word)
                update_category_display()
            else:
                messagebox.showwarning("Avertissement", "Le mot existe déjà dans cette catégorie.")
    else:
        messagebox.showwarning("Avertissement", "Sélectionnez une catégorie pour ajouter un mot.")

# Fonction pour afficher les mots d'une catégorie
def show_words_in_category(event):
    selected_category = category_list.curselection()
    print(selected_category)
    if selected_category:
        category_index = selected_category[0] - 1  
        category_name = list(categories.keys())[category_index]
        words = categories[category_name]
        print(category_name)
        
        # Créer une nouvelle fenêtre pour afficher les mots
        words_window = tk.Toplevel(root)
        words_window.title(f"Mots dans la catégorie '{category_name}'")

        # Ajouter une scrollbar et une listbox
        words_frame = tk.Frame(words_window)
        words_frame.pack(padx=10, pady=10)

        words_listbox = tk.Listbox(words_frame, width=50, height=10)
        words_listbox.pack(side=tk.LEFT)

        # Ajout de la barre de défilement
        words_scrollbar = tk.Scrollbar(words_frame)
        words_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        words_listbox.config(yscrollcommand=words_scrollbar.set)
        words_scrollbar.config(command=words_listbox.yview)

        # Insérer les mots dans la listbox
        if words:
            for word in words:
                words_listbox.insert(tk.END, "  " + word)
        else:
            words_listbox.insert(tk.END, " Aucun mot dans cette catégorie.")

        words_listbox.bind("<Double-Button-1>", lambda event: manage_word(words_listbox, category_name))
    else:
        messagebox.showwarning("Avertissement", "Sélectionnez une catégorie.")

def manage_word(words_listbox, category_name):
    selected_word_index = words_listbox.curselection()
    if selected_word_index:
        word_to_manage = words_listbox.get(selected_word_index)

        # Créer une nouvelle fenêtre pour modifier ou supprimer le mot
        manage_window = tk.Toplevel(root)
        manage_window.title("Modifier ou Supprimer le mot")

        # Créer un label pour afficher le mot sélectionné
        label = tk.Label(manage_window, text=f"Voulez-vous modifier ou supprimer le mot '{word_to_manage}'?")
        label.pack(pady=10)

        # Bouton pour modifier le mot
        modify_button = tk.Button(manage_window, text="Modifier", command=lambda: modify_word(words_listbox, category_name, selected_word_index, manage_window, word_to_manage))
        modify_button.pack(side=tk.LEFT, padx=10, pady=10)

        # Bouton pour supprimer le mot
        delete_button = tk.Button(manage_window, text="Supprimer", command=lambda: delete_word(words_listbox, category_name, selected_word_index, manage_window))
        delete_button.pack(side=tk.RIGHT, padx=10, pady=10)

    else:
        messagebox.showwarning("Avertissement", "Sélectionnez un mot à gérer.")

# Fonction pour modifier un mot
def modify_word(words_listbox, category_name, selected_word_index, manage_window, old_word):
    new_word = simpledialog.askstring("Modifier le mot", "Entrez le nouveau mot:", initialvalue=old_word)
    if new_word:
        # Mettre à jour le mot dans la liste
        categories[category_name][selected_word_index[0]] = new_word
        update_category_display()
        words_listbox.delete(selected_word_index)  
        words_listbox.insert(selected_word_index, new_word)  
        save_categories()
        manage_window.destroy()  

# Fonction pour supprimer un mot
def delete_word(words_listbox, category_name, selected_word_index, manage_window):
    categories[category_name].remove(words_listbox.get(selected_word_index))
    update_category_display()
    words_listbox.delete(selected_word_index) 
    save_categories()
    manage_window.destroy()  
        
# Fonction pour mettre à jour l'affichage des catégories
def update_category_display():
    category_list.delete(0, tk.END)
    category_list.insert(tk.END, "  ")
    for category in categories.keys():
        category_list.insert(tk.END, "  " + category + "  ")
    save_categories()

def save_categories():
    try:
        with open('./dictionnary.py', 'w', encoding='utf-8') as f:
            f.write("sensitive_words = {\n")
            for category, words in categories.items():
                f.write(f'    "{category}": {words},\n')
            f.write("}\n")
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible de sauvegarder les catégories : {str(e)}")

# ----------------------------------------------------------------------------------------------------
root = tk.Tk()
root.title("Gestion des mails et catégories")
root.geometry("800x700")
root.configure(bg="white")

emails = load_emails()
categories = load_categories()

try:
    original_image = Image.open('SAP_Logo.png') 
    resized_image = original_image.resize((160, 150), resample=Image.LANCZOS) 
    logo_image = ImageTk.PhotoImage(resized_image)
    logo_label = tk.Label(root, image=logo_image, bg="white")
    logo_label.pack(pady=10)
except Exception as e:
    messagebox.showerror("Erreur", f"Impossible de charger le logo : {str(e)}")
    
# Liste des emails
email_frame = tk.Frame(root, width=300, height=500, bg="white")
email_frame.pack(side=tk.LEFT, ipadx=20, ipady=20, padx=10, pady=50)
email_frame.pack_propagate(False)
email_list = tk.Listbox(email_frame, width=30, height=15)
email_list.pack()
update_email_display()


def create_rounded_button(parent, text, command, bg, fg, width=20):
    button = tk.Button(parent, text=text, command=command, bg=bg, fg=fg, padx=15, pady=5, bd=1, relief="ridge", width=width, cursor="hand2")
    button.pack(pady=10, padx=10)
    return button

# Liste des catégories
category_frame = tk.Frame(root, width=300, height=500, bg="white")
category_frame.pack(side=tk.RIGHT, ipadx=20, ipady=20, padx=10, pady=50)
category_frame.pack_propagate(False)
category_list = tk.Listbox(category_frame, width=30, height=15)
category_list.pack()
update_category_display()

add_email_button = create_rounded_button(email_frame, "Ajouter un email", add_email, 'lightblue', 'black')
remove_email_button = create_rounded_button(email_frame, "Supprimer un email", remove_email, 'lightcoral', 'black')
add_category_button = create_rounded_button(category_frame, "Ajouter une catégorie", add_category, 'lightblue', 'black')
remove_category_button = create_rounded_button(category_frame, "Supprimer une catégorie", remove_category, 'lightcoral', 'black')
add_word_button = create_rounded_button(category_frame, "Ajouter un mot à la catégorie", add_word, 'lightgreen', 'black')

if task_exists("AnalyseLogTask"):
    activate_button = tk.Button(root, text="Désactiver l'application", command=toggle_app, bg='lightgreen', fg='black', padx=15, pady=5, bd=1, relief="ridge", width=50, cursor="hand2")
    activate_button.pack(pady=10, padx=10, fill='x')
else:
    activate_button = tk.Button(root, text="Activer l'application", command=toggle_app, bg='lightgreen', fg='black', padx=15, pady=5, bd=1, relief="ridge", width=50, cursor="hand2")
    activate_button.pack(pady=10, padx=10, fill='x')

# Lier le double clic à la fonction d'affichage des mots
category_list.bind("<Double-Button-1>", show_words_in_category)

root.mainloop()
