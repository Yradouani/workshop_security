import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
import os
import emails_config
import dictionnary
from interface import load_emails

# Fonction pour envoyer un email
def envoyer_alerte(theme, mot_detecte):
    mail_file = load_emails()
    print(mail_file)
    for mail_address in mail_file:
        
        msg = MIMEMultipart()
        msg['From'] = 'test@scryptoura.com'
        msg['To'] = mail_address
        msg['Subject'] = emails_config.emails_par_theme[theme]['Objet']

        message = emails_config.emails_par_theme[theme]['Contenu']
        msg.attach(MIMEText(message, 'plain'))

        # Envoyer l'email via SMTP sécurisé (SSL)
        try:
            server = smtplib.SMTP_SSL('mail.scryptoura.com', 465)  
            server.login('test@scryptoura.com', 'MamanPapa*1') 
            text = msg.as_string()
            server.sendmail('test@scryptoura.com', mail_address, text)
            server.quit()
            print(f"Alerte envoyée à {mail_address} pour le mot '{mot_detecte}' dans le thème '{theme}'")
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'alerte : {e}")

mots_detectes = set()

def verifier_log(log_file, sensitive_words):
    if os.path.exists(log_file):
        print(f"Le fichier {log_file} existe.")
        try:
            with open(log_file, 'r', encoding='ISO-8859-1') as f:
                contenu_log = f.read().lower() 
                print("Contenu du fichier de log chargé.")
                
                for theme, mots in sensitive_words.items():
                    print(f"Vérification des mots pour le thème '{theme}'.")
                    for mot in mots:
                        mot = mot.lower() 
                        if mot in contenu_log and mot not in mots_detectes:
                            print(f"Mot détecté : {mot} dans le thème {theme}")
                            envoyer_alerte(theme, mot)
                            mots_detectes.add(mot)  
                            break
        except UnicodeDecodeError:
            print("Erreur de décodage du fichier de log.")
    else:
        print(f"Le fichier {log_file} n'existe pas.")

    
log_file = r"log.htm"
verifier_log(log_file, dictionnary.sensitive_words)