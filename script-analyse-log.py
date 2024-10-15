import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
import os
import json

from dictionnary import sensitive_words 


def charger_contenu_emails(emails_config):
    with open(emails_config, 'r', encoding='utf-8') as f:
        return json.load(f)
        print(contenu_emails.columns)

def envoyer_alerte(email_parent, thématique, contenu_emails):
    email_data = contenu_emails[contenu_emails['thématique'] == thématique].iloc[0]
    
    msg = MIMEMultipart()
    msg['From'] = 'test@scryptoura.com'
    msg['To'] = email_parent
    msg['Subject'] = email_data['objet']

    message_complet = f"{email_data['message']}\n\n{email_data['ressources']}"
    msg.attach(MIMEText(message_complet, 'plain'))

    try:
        server = smtplib.SMTP_SSL('mail.scryptoura.com', 465)
        server.login('test@scryptoura.com', 'MamanPapa*1')  
        text = msg.as_string()
        server.sendmail('test@scryptoura.com', email_parent, text)
        server.quit()
        print(f"Alerte envoyée à {email_parent} pour la thématique {thématique}")
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'alerte : {e}")

def verifier_log(log_file, email_parent, contenu_emails):
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='ISO-8859-1') as f:
                contenu_log = f.read()

                for thématique, mots in sensitive_words.items():
                    for mot in mots:
                        if mot in contenu_log:
                            print(f"Mot détecté : {mot} dans la thématique {thématique}")
                            envoyer_alerte(email_parent, thématique, contenu_emails)
                            return 
        except UnicodeDecodeError:
            print("Erreur de décodage du fichier de log.")
    else:
        print(f"Le fichier {log_file} n'existe pas.")

# Fonction pour surveiller le fichier log
def surveiller_fichier_log(log_file, email_parent, fichier_emails):
    contenu_emails = charger_contenu_emails(fichier_emails)
    while True:
        verifier_log(log_file, email_parent, contenu_emails)
        time.sleep(300)  

def charger_configuration(fichier_config):
    config = {}
    with open(fichier_config, 'r') as f:
        for line in f:
            key, value = line.strip().split('=')
            config[key] = value
    return config

config = charger_configuration('config.txt')
surveiller_fichier_log(config['logs_file'], config['email_parent'], config['emails_config'])