#script email log

import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
import os

def envoyer_alerte(email_parent, mot_detecte):
    msg = MIMEMultipart()
    msg['From'] = 'test@scryptoura.com'
    msg['To'] = email_parent
    msg['Subject'] = 'Alerte: Mot Inapproprié Détecté'
    
    message = f"Le mot '{mot_detecte}' a été détecté dans le fichier de log."
    msg.attach(MIMEText(message, 'plain'))
    
    try:
        server = smtplib.SMTP_SSL('mail.scryptoura.com', 465) 
        server.login('test@scryptoura.com', 'MamanPapa*1')  
        text = msg.as_string()
        server.sendmail('test@scryptoura.com', email_parent, text)
        server.quit()
        print(f"Alerte envoyée à {email_parent}")
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'alerte : {e}")

def verifier_log(log_file, mots_inappropries, email_parent):
    if os.path.exists(log_file):
        # Essayer avec un encodage différent
        try:
            with open(log_file, 'r', encoding='ISO-8859-1') as f:
                contenu_log = f.read()
                for mot in mots_inappropries:
                    if mot in contenu_log:
                        print(f"Mot détecté : {mot}")
                        envoyer_alerte(email_parent, mot)
                        break
        except UnicodeDecodeError:
            print("Erreur de décodage du fichier de log avec l'encodage ISO-8859-1.")
    else:
        print(f"Le fichier {log_file} n'existe pas.")

log_file_path = r"C:\path\to\log.htm"
mots_file_path = r"C:\path\to\mot.csv"
email_parent = "utilisateur@exemple.com"

def surveiller_fichier_log(log_file_path, mots_file_path, email_parent)
    log_file = r"C:\Users\vraica\Downloads\log.htm"
    
    mots_file = r"C:\Users\vraica\Downloads\mot.csv"
    
    mots_df = pd.read_csv(mots_file, header=None)
    mots_inappropries = mots_df[0].tolist()
    
    email_parent = "mathiasduret@hotmail.fr"
    
    while True:
        verifier_log(log_file, mots_inappropries, email_parent)
        time.sleep(300) 

surveiller_fichier_log()