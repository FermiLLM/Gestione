import subprocess
import sys
import os
import time
import threading

def pulisci_schermo():
    os.system('cls' if os.name == 'nt' else 'clear')

def leggi_file(percorso_file):
    try:
        with open(percorso_file, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Errore: Il file '{percorso_file}' non è stato trovato.")
        sys.exit(1)

def cerca_nel_file(domanda, contenuto_file):
    parole_chiave = domanda.lower().split()
    righe_rilevanti = []

    for riga in contenuto_file.splitlines():
        if any(parola in riga.lower() for parola in parole_chiave):
            righe_rilevanti.append(riga)

    return "\n".join(righe_rilevanti)[:1000]

def mostra_caricamento():
    """Mostra un effetto di caricamento con trattini."""
    global loading_active
    while loading_active:
        for i in range(7):  # Usa 7 per il ciclo di animazione (0-6)
            if not loading_active:
                break
            sys.stdout.write("\rCaricamento" + "-" * i + " " * (6 - i))  # Rimuovi le lineette precedenti
            sys.stdout.flush()
            time.sleep(0.5)

def invia_a_ollama_interattivo(prompt):
    global loading_active
    loading_active = True

    # Avvia la funzione di caricamento
    caricamento_thread = threading.Thread(target=mostra_caricamento)
    caricamento_thread.start()

    try:
        comando = f'echo "{prompt}" | ollama run llama3.2:1b'
        processo = subprocess.Popen(comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        print("\rOllama: ", end='', flush=True)
        
        while True:
            riga = processo.stdout.readline()
            if riga == '' and processo.poll() is not None:
                break
            if riga.strip():
                # Cancella l'effetto di caricamento e mostra l'output
                loading_active = False
                print("\r" + " " * 30, end='\r')  # Cancella l'effetto di caricamento
                print("\rOllama: " + riga.strip(), flush=True)

        processo.wait()

    except subprocess.CalledProcessError as e:
        print(f"Errore nell'esecuzione di Ollama: {e.stderr}")
    except Exception as e:
        print(f"Errore inaspettato: {e}")

def chat_interattiva(percorso_file):
    pulisci_schermo()
    print("Chat con Ollama avviata! Digita 'esci' per terminare.\n")
    
    contenuto_file = leggi_file(percorso_file)
    
    while True:
        try:
            domanda_utente = input("Tu: ")
            
            if domanda_utente.strip().lower() == 'esci':
                print("Chat terminata.")
                pulisci_schermo()
                break
            
            informazioni_rilevanti = cerca_nel_file(domanda_utente, contenuto_file)
            
            if informazioni_rilevanti:
                prompt_finale = f"Usa le seguenti informazioni per rispondere alla domanda: {informazioni_rilevanti}\nDomanda: {domanda_utente}\nRisposta finale:"
                invia_a_ollama_interattivo(prompt_finale)
            else:
                invia_a_ollama_interattivo(domanda_utente)

        except KeyboardInterrupt:
            print("\nChat terminata dall'utente.")
            pulisci_schermo()
            break
        except EOFError:
            print("\nChat terminata dall'utente.")
            pulisci_schermo()
            break

if __name__ == "__main__":
    percorso_file = "/home/info.txt"
    loading_active = False  # Variabile per controllare il caricamento
    
    chat_interattiva(percorso_file)
