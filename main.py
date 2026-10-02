# CONFIGURAZIONE GENERALE
import os
import uuid
import base64
import asyncio
import re
import hashlib
import time
import random
import datetime
from cryptography.fernet import Fernet
import subprocess
import psutil
import shutil
from google_auth_oauthlib.flow import InstalledAppFlow
import platform
import sys
VERDE_MATRIX = "\033[38;2;0;255;65m"
ROSSO_MATRIX = "\033[38;2;255;0;0m"
import sys

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_CONFIG = {
    "installed": {
        "client_id": "681678497981-v4m0kq8fq663ffm1m8b3g6u5su59m853.apps.googleusercontent.com",
        "project_id": "italian-command-prompt",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "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",
        "redirect_uris": ["http://localhost"],
    }
}
account_google_path = os.path.join(BASE_DIR, "accounts_google.txt")
accounts_path = os.path.join(BASE_DIR, "accounts.txt")
chiave_crittografia_path = os.path.join(BASE_DIR, "chiave.key")
# Crea i due file vuoti al primo avvio se non esistono
for _percorso in (account_google_path, accounts_path, chiave_crittografia_path):
    try:
        if not os.path.exists(_percorso):
            open(_percorso, "a", encoding="utf-8").close()
    except OSError:
        pass
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
inizio = time.monotonic()
import shlex
import glob
import contextlib
try:
    import readline
except ImportError:
    readline = None  # su Windows: pip install pyreadline3 per avere cronologia e TAB

cronologia_path = os.path.join(BASE_DIR, "cronologia.txt")
CRONOLOGIA = []
ALIAS = {}
ULTIMO_CODICE = 0
CARTELLA_PRECEDENTE = None
_CACHE_ESEGUIBILI = None
COMANDI_CMD_WINDOWS = {"dir", "type", "copy", "del", "erase", "ren", "rename", "md", "mkdir",
                       "rd", "rmdir", "echo", "ver", "vol", "date", "time", "move", "mklink",
                       "assoc", "ftype", "path", "start", "title", "color"}
if os.name != "nt":
    ALIAS["ll"] = "ls -la"


class UscitaTerminale(Exception):
    pass


#-----------------------------------
#FUNZIONI, CUORE DEL FILE
#-----------------------------------
def percorso_attuale():
    time.sleep(1)
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        print(f"{VERDE_MATRIX}PERCORSO ATTUALE: {os.getcwd()}")
    except Exception:
        print(f"{ROSSO_MATRIX}ERRORE NELLA RICERCA DEL PERCORSO ATTUALE!")
def crea_cartella():
    time.sleep(1)
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        percorso = input(f"{VERDE_MATRIX}INSERIRE IL PERCORSO DOVE GENERARE LA CARTELLA, SEPARATORE: {os.sep}").strip()
        os.chdir(percorso)
        cartella = input(f"{VERDE_MATRIX}INSERIRE QUI IL NOME DELLA CARTELLA DA CREARE: ").strip()
        os.mkdir(cartella)
        print()
        print(f"{VERDE_MATRIX}CREAZIONE DELLA CARTELLA RIUSCITA")
    except Exception:
        print(f"{ROSSO_MATRIX}ERRORE NELLA CREAZIONE DELLA CARTELLA O ERRORE DI SCRITTURA DEL PERCORSO, SEPARATORE GIUSTO: {os.sep}")
def rimuovi_cartella_vuota():
    time.sleep(1)
    os.system('cls'if os.name == 'nt' else 'clear')
    try:
        percorso = input(f"{VERDE_MATRIX}INSERIRE IL PERCORSO DOVE È PRESENTE LA CARTELLA VUOTA  DA ELIMINARE, SEPARATORE: {os.sep}").strip()
        os.chdir(percorso)
        cartella = input(f"{VERDE_MATRIX}INSERIRE IL NOME DELLA CARTELLA DA ELIMINARE: ").strip()
        print()
        if os.path.exists(cartella):
            if os.path.isdir(cartella):
                os.rmdir(cartella)
                print(f"{VERDE_MATRIX}CARTELLA ELIMINATA CON SUCCESSO.")
            else:
                print(f"{ROSSO_MATRIX}ERRORE!! INSERIRE SOLO CARTELLA, NON FILE")
        else:
            print(f"{ROSSO_MATRIX}ERRORE!! CARTELLA NON ESISTENTE NEL PERCORSO")
    except Exception:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE PROBABILMENTE PER ERRORE DI SCRITTURA DI PERCORSO. SEPARATORE CORRETTO: {os.sep}")
def rimuovi_cartella():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        percorso = input(f"{VERDE_MATRIX}INSERIRE IL PERCORSO DOVE STA LA CARTELLA DA ELIMINARE: ").strip()
        os.chdir(percorso)
        cartella = input(f"{VERDE_MATRIX}NSERIRE NOME CARTELLA DA ELIMINARE: ").strip()
        print()
        if os.path.exists(cartella):
            if os.path.isdir(cartella):
                shutil.rmtree(cartella)
                print(f"{VERDE_MATRIX}FATTO!")
            else:
                print(f"{ROSSO_MATRIX}INSERIRE SOLO CARTELLA")
        else:
            print(f"{ROSSO_MATRIX}INSERIRE SOLO CARTELLA ESISTENTE")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE! {e}")
def sposta_file():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        percorso_di_origine = input(f"{VERDE_MATRIX}INSERIRE PERCORSO DI ORIGINE FILE: ").strip()
        percorso_di_destinazione = input(f"{VERDE_MATRIX}INSERIRE PERCORSO DI DESTINAZIONE FILE: ").strip()
        print()
        shutil.copy2(percorso_di_origine, percorso_di_destinazione)
        print(f"{VERDE_MATRIX}FATTO!")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE! {e}")
def sposta_cartella():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        percorso_di_origine = input(f"{VERDE_MATRIX}INSERIRE PERCORSO DI ORIGINE CARTELLA: ").strip()
        percorso_di_destinazione= input(f"{VERDE_MATRIX}INSERIRE PERCORSO DI DESTINAZIONE CARTELLA: ").strip()
        print()
        shutil.copytree(percorso_di_origine, percorso_di_destinazione)
        print(f"{VERDE_MATRIX}FATTO!")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE! {e}")
def statistiche_cpu():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{VERDE_MATRIX}CORE LOGICI: {psutil.cpu_count()}")
    print(f"{VERDE_MATRIX}CORE FISICI: {psutil.cpu_count(logical=False)}")
    print(f"{VERDE_MATRIX}FREQUENZA CPU: {psutil.cpu_freq()}")
    print(f"{VERDE_MATRIX}UTILIZZO CPU: {psutil.cpu_percent(interval=1)}")
    print(f"{VERDE_MATRIX}UTILIZZO DI TUTTI I CORE: {psutil.cpu_percent(percpu=True)}")
    print()
def statistiche_ram():
    os.system('cls' if os.name == 'nt' else 'clear')
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    print(f"{VERDE_MATRIX}MEMORIA RAM TOTALE: {mem.total}")
    print(f"{VERDE_MATRIX}MEMORIA RAM LIBERA: {mem.free}")
    print(f"{VERDE_MATRIX}MEMORIA RAM DISPONIBILE: {mem.available}")
    print(f"{VERDE_MATRIX}MEMORIA RAM USATA: {mem.used}")
    print(f"{VERDE_MATRIX}MEMORIA DI SWAP USATA: {swap.used}")
    print(f"{VERDE_MATRIX}MEMORIA DI SWAP TOTALE: {swap.total}")
    print(f"{VERDE_MATRIX}MEMORIA DI SWAP LIBERA: {swap.free}")
    print()
def utenti_loggati():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{VERDE_MATRIX}UTENTI LOGGATI: {psutil.users()}")
def tempo_di_boot():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{VERDE_MATRIX}TEMPO DI BOOT: {psutil.boot_time()}")


def avvia_python():
    time.sleep(1)
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        os.system("python")
    except Exception:
        print(f"{ROSSO_MATRIX}PYTHON NON INSTALLATO")
def esci():
    os.system("exit")
def time_up():
    time.sleep(1)
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("uptime")
def spegni_pc():
    os.system('shutdown -s -t 0' if os.name == 'nt' else 'shutdown -h now')
def riavvia_pc():
    os.system('shutdown -r -t 0' if os.name == 'nt' else 'reboot')
def rimuovi_file():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        percorso = input(f"{VERDE_MATRIX}INSERIRE IL PERCORSO DOVE STA IL FILE DA ELIMINARE, SEPARATORE: {os.sep}").strip()
        file = input(f"{VERDE_MATRIX}INSERIRE NOME FILE DA ELIMINARE: ").strip()
        print()
        os.chdir(percorso)
        if os.path.exists(file):
            if os.path.isfile(file):
                os.remove(file)
                print(f"{VERDE_MATRIX}FILE ELIMINATO CON SUCCESSO")
            else:
                print(f"{ROSSO_MATRIX}INSERIRE SOLO FILE.")
        else:
            print(f"{ROSSO_MATRIX}INSERIRE SOLO FILE ESISTENTE.")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERICO: {e}")

def rinomina_file():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        percorso = input(f"{VERDE_MATRIX}INSERIRE IL PERCORSO DOVE STA IL FILE DA RINOMINARE, SEPARATORE: {os.sep}").strip()
        os.chdir(percorso)
        file = input(f"{VERDE_MATRIX}INSERIRE NOME FILE ATTUALE: ").strip()
        nome = input(f"{VERDE_MATRIX}INSERIRE IL NOME CON CUI SARÀ RINOMINATO IL FILE: ").strip()
        print()
        if os.path.exists(file):
            if os.path.isfile(file):
                os.rename(file, nome)
                print(f"{VERDE_MATRIX}FILE RINOMINATO CON SUCCESSO")
            else:
                print(f"{ROSSO_MATRIX}INSERIRE SOLO FILE")
        else:
            print(f"{ROSSO_MATRIX}INSERIRE SOLO FILE ESISTENTE")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERICO: {e}")
def dimensione_file():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        percorso = input(f"{VERDE_MATRIX}INSERIRE IL PERCORSO DOVE STA IL FILE, SEPARATORE: {os.sep}").strip()
        os.chdir(percorso)
        file = input(f"{VERDE_MATRIX}INSERIRE NOME FILE: ").strip()
        print()
        if os.path.exists(file):
            if os.path.isfile(file):
                dimensione = os.path.getsize(file)
                print(f"{VERDE_MATRIX}DIMENSIONE FILE: {dimensione / (1024 * 1024):.2f} MB")
            else:
                print(f"{ROSSO_MATRIX}INSERIRE SOLO FILE")
        else:
            print(f"{ROSSO_MATRIX}INSERIRE SOLO FILE ESISTENTE")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERICO: {e}")
def thread_cpu():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{VERDE_MATRIX}THREADS_CPU: {os.cpu_count()}")
def dimensioni_terminale():
    os.system('cls' if os.name == 'nt' else 'clear')
    dimensioni = os.get_terminal_size()
    print(f"{VERDE_MATRIX}LINEE: {dimensioni.lines}\nCOLONNE: {dimensioni.columns}")
def avvia_file():
    try:
        os.system('cls')
        percorso = input(f"{VERDE_MATRIX}INSERIRE IL PERCORSO DOVE STA IL FILE DA AVVIARE, SEPARATORE: {os.sep}").strip()
        os.chdir(percorso)
        file = input(f"{VERDE_MATRIX}INSERIRE NOME FILE DA AVVIARE: ").strip()
        print()
        if os.path.exists(file):
            if os.path.isfile(file):
                if os.name == 'nt':
                    os.startfile(file)
                elif platform.system() == "Darwin":
                    subprocess.Popen(["open", file])
                else:
                    subprocess.Popen(["xdg-open", file])
            else:
                print(f"{ROSSO_MATRIX}INSERIRE SOLO FILE")
        else:
            print(f"{ROSSO_MATRIX}INSERIRE SOLO FILE ESISTENTE")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERICO: {e}")
def separatore_percorsi():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{VERDE_MATRIX}SEPARATORE PERCORSI: {os.sep}")
def separatore_path():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{VERDE_MATRIX}SEPARATORE PATH: {os.pathsep}")
def id_sistema():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{VERDE_MATRIX}ID SISTEMA OPERATIVO: {os.name}")
def entra_in_percorsi():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        primo_elemento = input(f"{VERDE_MATRIX}INSERIRE PRIMO ELEMENTO: ").strip()
        secondo_elemento = input(f"{VERDE_MATRIX}INSERIRE SECONDO ELEMENTO: ").strip()
        terzo_elemento = input(f"{VERDE_MATRIX}INSERIRE TERZO ELEMENTO: ").strip()
        percorso_unito = os.path.join(primo_elemento, secondo_elemento, terzo_elemento)
        print()
        print(f"{VERDE_MATRIX}PERCORSO UNITO: {percorso_unito}")
    except Exception as e:
        print()
        print(f"{ROSSO_MATRIX}ERRORE: {e}")
def secondi_passati_dal_1970():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{VERDE_MATRIX}SECONDI PASSATI DAL 1 GENNAIO 1970: {time.time()}")
def data_e_ora_attuale():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{VERDE_MATRIX}DATA E ORA ATTUALE: {datetime.datetime.now()}")


def ottieni_chiave_crittografia():
    # la chiave va generata UNA SOLA VOLTA e riletta sempre dopo:
    # è l'unico modo per cui cifrare e decifrare corrispondano davvero
    if os.path.exists(chiave_crittografia_path):
        with open(chiave_crittografia_path, "rb") as f:
            return f.read()
    else:
        nuova_chiave = Fernet.generate_key()
        with open(chiave_crittografia_path, "wb") as f:
            f.write(nuova_chiave)
        return nuova_chiave


def crittografia_testo():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        testo = input(f"{VERDE_MATRIX}INSERIRE TESTO DA CRIPTARE: ").strip()
        final = Fernet(ottieni_chiave_crittografia())
        print()
        print(f"{VERDE_MATRIX}TESTO CRIPTATO: {final.encrypt(testo.encode('utf-8')).decode('utf-8')}")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE, {e}")
def crittografia_file_di_testo():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        percorso = input(f"{VERDE_MATRIX}INSERIRE PERCORSO DOVE STA IL FILE DI TESTO, SEPARATORE: {os.sep}").strip()
        os.chdir(percorso)
        nome_file = input(f"{VERDE_MATRIX}INSERIRE IL NOME DEL FILE DI TESTO: ").strip()
        if os.path.exists(nome_file):
            if os.path.isfile(nome_file):
                if nome_file.endswith(".txt"):
                    with open(nome_file, mode="r", encoding="utf-8") as f:
                        righe = f.read().strip()
                        with open(nome_file, mode="wb") as f1:
                            final = Fernet(ottieni_chiave_crittografia())
                            f1.write(final.encrypt(righe.encode("utf-8")))
                            print()
                            print(f"{VERDE_MATRIX}FATTO!")
                else:
                    print(f"{ROSSO_MATRIX}SOLO FILE DI TESTO.")
            else:
                print(f"{ROSSO_MATRIX}INSERIRE SOLO FILE")
        else:
            print(f"{ROSSO_MATRIX}INSERIRE SOLO FILE ESISTENTE")
    except Exception as a:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE, {a}")
def decrittografia_testo():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        testo = input(f"{VERDE_MATRIX}INSERIRE TESTO DA DECRIPTARE: ").strip()
        final = Fernet(ottieni_chiave_crittografia())
        print()
        print(f"{VERDE_MATRIX}TESTO DECRIPTATO: {final.decrypt(testo.encode('utf-8')).decode('utf-8')}")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE, {e}")
def decrittografia_file_di_testo():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        percorso = input(f"{VERDE_MATRIX}INSERIRE PERCORSO DOVE STA IL FILE DI TESTO, SEPARATORE: {os.sep}").strip()
        os.chdir(percorso)
        nome_file = input(f"{VERDE_MATRIX}INSERIRE IL NOME DEL FILE DI TESTO: ").strip()
        if os.path.exists(nome_file):
            if os.path.isfile(nome_file):
                if nome_file.endswith(".txt"):
                    with open(nome_file, mode="rb") as f:
                        righe = f.read()
                        with open(nome_file, mode="w", encoding="utf-8") as f1:
                            final = Fernet(ottieni_chiave_crittografia())
                            f1.write(final.decrypt(righe).decode("utf-8"))
                            print()
                            print(f"{VERDE_MATRIX}FATTO!")
                else:
                    print(f"{ROSSO_MATRIX}SOLO FILE DI TESTO.")
            else:
                print(f"{ROSSO_MATRIX}INSERIRE SOLO FILE")
        else:
            print(f"{ROSSO_MATRIX}INSERIRE SOLO FILE ESISTENTE")
    except Exception as a:
            print(f"{ROSSO_MATRIX}ERRORE GENERALE, {a}")
def lista_cartella():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        percorso = input(f"{VERDE_MATRIX}INSERIRE PERCORSO DOVE STA LA CARTELLA: ").strip()
        cartella = input(f"{VERDE_MATRIX}INSERIRE NOME CARTELLA: ").strip()
        print()
        os.chdir(percorso)
        if os.path.exists(cartella):
            if os.path.isdir(cartella):
                print(f"{VERDE_MATRIX}CONTENUTO CARTELLA: {os.listdir()}")
            else:
                print(f"{ROSSO_MATRIX}INSERIRE SOLO CARTELLA")
        else:
            print(f"{ROSSO_MATRIX}INSERIRE SOLO CARTELLA ESISTENTE")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE!, {e}")
def secondi_passati_dall_avvio_del_programma():
    fine = time.monotonic()
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{VERDE_MATRIX}SECONDI PASSATI: {fine - inizio}")
def numero_casuale_tra_0_e_1():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{VERDE_MATRIX}NUMERO TRA 0 E 1: {random.random()}")
def esplorazione_cartella():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        percorso = input(f"{VERDE_MATRIX}INSERIRE IL PERCORSO DOVE STA LA CARTELLA: ").strip()
        os.chdir(percorso)
        cartella = input(f"{VERDE_MATRIX}INSERIRE NOME CARTELLA: ").strip()
        if os.path.exists(cartella):
            if os.path.isdir(cartella):
                for root, dirs, files in os.walk(cartella):
                    print()
                    print(f"{VERDE_MATRIX}ROOT: {root}")
                    print(f"{VERDE_MATRIX}DIRS: {dirs}")
                    print(f"{VERDE_MATRIX}FILES: {files}")
            else:
                print(f"{VERDE_MATRIX}INSERIRE SOLO CARTELLA")
        else:
            print(f"{ROSSO_MATRIX}INSERIRE SOLO CARTELLA ESISTENTE")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def scrivi_qualcosa_in_un_file():
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
        percorso = input(f"{VERDE_MATRIX}INSERIRE PERCORSO DOVE STA IL FILE: ").strip()
        file = input(f"{VERDE_MATRIX}INSERIRE NOME FILE: ").strip()
        testo = input(f"{VERDE_MATRIX}INSERIRE TESTO DA SCRIVERE NEL FILE: ").strip()
        os.chdir(percorso)
        if os.path.exists(file):
            if os.path.isfile(file):
                with open(file, mode="w") as f:
                    f.write(testo)
            else:
                print(f"{ROSSO_MATRIX}INSERIRE SOLO FILE")
        else:
            print(f"{ROSSO_MATRIX}INSERIRE SOLO FILE ESISTENTE")
    except Exception as a:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE! {a}")
def crea_file():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        nome = input(f"{VERDE_MATRIX}INSERIRE IL NOME CON CUI IL FILE VERRÀ CREATO: ").strip()
        with open(nome, mode="x") as c:
            c.close()
        print(f"{VERDE_MATRIX}FATTO!")
    except FileExistsError:
        print(f"{ROSSO_MATRIX}QUESTO FILE ESISTE GIA'!")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")
def pid_processo_python():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{VERDE_MATRIX}PID PROCESSO PYTHON: {os.getpid()}")
def genera_uuid_generico():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{VERDE_MATRIX}UUID GENERICO: {uuid.uuid4()}")
def genera_uuid_url():
    os.system("cls" if os.name == 'nt' else 'clear')
    name = input(f"{VERDE_MATRIX}INSERIRE LINK DEL SITO: ").strip()
    namespace = uuid.NAMESPACE_URL
    print()
    print(f"{VERDE_MATRIX}UUID LINK: {uuid.uuid5(namespace, name)}")
def uuid_vuoto():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{VERDE_MATRIX}UUID VUOTO: {uuid.MAX}")
def uuid_senza_trattini():
    os.system('cls' if os.name == 'nt' else 'clear')
    ids = uuid.uuid4()
    print(f"{VERDE_MATRIX}UUID SENZA TRATTINI: {ids.hex}")
def uuid_intero():
    os.system('cls' if os.name == 'nt' else 'clear')
    ids = uuid.uuid4()
    print(f"{VERDE_MATRIX}UUID RAPPRESENTATO COME INTERO: {ids.int}")
def uuid_bytes():
    os.system('cls' if os.name == 'nt' else 'clear')
    ids = uuid.uuid4()
    print(f"{VERDE_MATRIX}BYTES UUID: {ids.bytes}")
def fields_uuid():
    os.system('cls' if os.name == 'nt' else 'clear')
    ids = uuid.uuid1()
    print(f"{VERDE_MATRIX}STRUTTURA UUID: {ids.fields}")
def codifica_base64_testo():
    os.system('cls' if os.name == 'nt' else 'clear')
    testo = input(f"{VERDE_MATRIX}INSERIRE TESTO DA CODIFICARE: ").strip()
    codificato = base64.b64encode(testo.encode('utf-8')).decode('ascii')
    print()
    print(f"{VERDE_MATRIX}TESTO CODIFICATO: {codificato}")
def decodifica_base64_testo():
    os.system('cls' if os.name == 'nt' else 'clear')
    testo1 = input(f"{VERDE_MATRIX}INSERIRE TESTO: ").strip()
    decodificato = base64.b64decode(testo1.encode('utf-8')).decode('utf-8')
    print()
    print(f"{VERDE_MATRIX}TESTO DECODIFICATO: {decodificato}")
def codifica_base16_testo():
    os.system('cls' if os.name == 'nt' else 'clear')
    testo = input(f"{VERDE_MATRIX}INSERIRE TESTO DA CODIFICARE: ").strip()
    codificato = base64.b16encode(testo.encode('utf-8')).decode('ascii')
    print()
    print(f"{VERDE_MATRIX}TESTO CODIFICATO: {codificato}")
def decodifica_testo_base16():
    os.system('cls' if os.name == 'nt' else 'clear')
    testo = input(f"{VERDE_MATRIX}INSERIRE TESTO DA CODIFICARE: ").strip()
    decodificato = base64.b16decode(testo.encode('utf-8')).decode('utf-8')
    print()
    print(f"{VERDE_MATRIX}TESTO DECODIFICATO: {decodificato}")
def codifica_testo_base32():
    os.system('cls' if os.name == 'nt' else 'clear')
    testo = input(f"{VERDE_MATRIX}INSERIRE TESTO DA CODIFICARE: ").strip()
    codificato = base64.b32encode(testo.encode('utf-8')).decode('ascii')
    print()
    print(f"{VERDE_MATRIX}TESTO CODIFICATO: {codificato}")
def decodifica_testo_base32():
    os.system('cls' if os.name == 'nt' else 'clear')
    testo = input(f"{VERDE_MATRIX}INSERIRE TESTO DA CODIFICARE: ").strip()
    decodificato = base64.b32decode(testo.encode('utf-8')).decode('utf-8')
    print()
    print(f"{VERDE_MATRIX}TESTO DECODIFICATO: {decodificato}")
def codifica_testo_base85():
    os.system('cls' if os.name == 'nt' else 'clear')
    testo = input(f"{VERDE_MATRIX}INSERIRE TESTO DA CODIFICARE: ").strip()
    codificato = base64.b85encode(testo.encode('utf-8')).decode('ascii')
    print()
    print(f"{VERDE_MATRIX}TESTO CODIFICATO: {codificato}")
def decodifica_testo_base85():
    os.system('cls' if os.name == 'nt' else 'clear')
    testo = input(f"{VERDE_MATRIX}INSERIRE TESTO DA CODIFICARE: ").strip()
    decodificato = base64.b85decode(testo.encode('utf-8')).decode('utf-8')
    print()
    print(f"{VERDE_MATRIX}TESTO DECODIFICATO: {decodificato}")
def informazioni_sistema():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{VERDE_MATRIX}SISTEMA OPERATIVO: {platform.system()}")
    print(f"{VERDE_MATRIX}VERSIONE SISTEMA OPERATIVO: {platform.release()}")
    print(f"{VERDE_MATRIX}PROCESSORE: {platform.processor()}")
    print(f"{VERDE_MATRIX}TIPO DI ARCHITETTURA PC: {platform.machine()}")
    print(f"{VERDE_MATRIX}NOME HOST: {platform.node()}")
#-----------------------------------
# MAPPA DEI PROGRAMMI (nome programma -> funzioni apri / chiudi / chiudi forzato)
#-----------------------------------
def _costruisci_mappa(suffissi):
    # da nome -> suffisso ricava i nomi delle 3 funzioni (apri, chiudi, chiudi forzato)
    eccezioni = {'gestione_attività': 'gestione_attivita', 'utilità_di_pianificazione': 'utilita_di_pianificazione', 'inizializzatore_ISCSI': 'inizializzatore_iscsi'}
    mappa = {}
    for nome, suffisso in suffissi.items():
        s = eccezioni.get(suffisso, suffisso)
        mappa[nome] = ('apri_' + suffisso, 'termina_' + s, 'termina_forzatamente_' + s)
    return mappa

MAPPA_PROGRAMMI = {
    'windows': _costruisci_mappa({
        'Blocco Note': 'blocco_note',
        'Paint Classico': 'paint',
        'Calcolatrice Classica': 'calcolatrice',
        'WordPad / Write': 'wordpad',
        'Strumento di Cattura Classico': 'strumento_per_screenshot',
        'Registratore Azioni Utente': 'registrazoni_azioni_utente',
        'Note Adesive Classiche': 'note_adesive_classiche',
        'Mappa Caratteri': 'mappa_caratteri',
        'Connessione Telefonica Guidata': 'connessione_ytelefonica_guidatra',
        'Esplora File': 'esplora_file',
        'Gestione Attivita (Task Manager)': 'gestione_attività',
        'Prompt dei Comandi': 'cmd',
        'Windows PowerShell': 'powershell',
        'Editor del Registro di Sistema': 'registro_di_sistema',
        'Pannello di Controllo Classico': 'pannello_di_controllo',
        'System Information': 'informazioni_sistema',
        'Microsoft Management Console': 'microsoft_management_console',
        'Pulizia Disco': 'pulizia_disco',
        'Ripristino Configurazione di Sistema': 'ripristino_conf_di_sistema',
        'Utilita di Pianificazione': 'utilità_di_pianificazione',
        'Visualizzatore Eventi': 'visualizzatore_eventi',
        'Gestione dei Servizi': 'gestione_servizi',
        'Gestione Dispositivi': 'gestione_dispositivi',
        'Gestione Disco': 'gestione_dischi',
        'Gestione Computer': 'gestione_pc',
        'Gestione Stampa': 'gestione_stampa',
        'Strumento Diagnostica DirectX': 'strumento_diagnostica_directx',
        'Centro Sincronizzazione Periferiche': 'centro_sincronizzazione_periferiche',
        'Connessione Desktop Remoto': 'connessione_desktop_remoto',
        'Inizializzatore iSCSI': 'inizializzatore_ISCSI',
        'Windows Firewall Avanzato': 'windows_firewall_avanzato',
        'Opzioni Telefono e Modem': 'opzioni_telefono_e_modem',
        'Monitoraggio Affidabilita e Performance': 'monitoraggio_affidabilita_e_performance',
        'Monitoraggio Risorse': 'monitoraggio_risorse',
        'Configurazione di Sistema (MSConfig)': 'configurazione_di_sistema_msconfig',
        'Verifica Firma File': 'verifica_firma_file',
        'Driver Verifier Manager': 'driver_verifier_manager',
        'Informazioni Versione Windows': 'informazioni_versione_windows',
        'Strumento Rimozione Malware Microsoft': 'strumento_rimozione_malware_microsoft',
        'Backup e Ripristino Credenziali': 'backup_e_ripristino_credenziali',
        'Criteri di Sicurezza Locali': 'criteri_di_sicurezza_locali',
        'Editor dei Criteri di Gruppo Locali': 'editor_dei_criteri_di_gruppo_locali',
        'Programmi e Funzionalita (Disinstalla)': 'programmi_e_funzionalita_disinstalla',
        'Impostazioni Schermo Classiche': 'impostazioni_schermo_classiche',
        'Proprieta del Mouse': 'proprieta_del_mouse',
        'Impostazioni Audio (Suoni)': 'impostazioni_audio_suoni',
        'Proprieta del Sistema (Variabili Ambiente)': 'proprieta_del_sistema_variabili_ambiente',
        'Impostazioni Data e Ora': 'impostazioni_data_e_ora',
        'Opzioni Risparmio Energia': 'opzioni_risparmio_energia',
        'Opzioni Internazionali e Lingua': 'opzioni_internazionali_e_lingua',
        'Installazione Guidata Hardware Legacy': 'installazione_guidata_hardware_legacy',
        'Proprieta Internet': 'proprieta_internet',
        'Periferiche di Gioco (Controller)': 'periferiche_di_gioco_controller',
        'Centro Accessibilita Classico': 'centro_accessibilita_classico',
        'Impostazioni Generali': 'impostazioni_generali',
        'Windows Update': 'windows_update',
        'Stato della Rete e Wi-Fi': 'stato_della_rete_e_wi_fi',
        'Gestione Dispositivi Bluetooth': 'gestione_dispositivi_bluetooth',
        'Impostazioni Schermo Moderne': 'impostazioni_schermo_moderne',
        'Gestione Notifiche': 'gestione_notifiche',
        'Elenco App Installate': 'elenco_app_installate',
        'Applicazioni Predefinite': 'applicazioni_predefinite',
        'Personalizzazione e Sfondi': 'personalizzazione_e_sfondi',
        'Gestione dei Temi': 'gestione_dei_temi',
        'Schermata di Blocco': 'schermata_di_blocco',
        'Data e Ora Moderne': 'data_e_ora_moderne',
        'Lingua e Area Geografica': 'lingua_e_area_geografica',
        'Privacy Generale': 'privacy_generale',
        'Autorizzazioni Webcam': 'autorizzazioni_webcam',
        'Autorizzazioni Microfono': 'autorizzazioni_microfono',
        'Sicurezza di Windows (Defender)': 'sicurezza_di_windows_defender',
        'Opzioni di Ripristino (Recovery)': 'opzioni_di_ripristino_recovery',
        'Impostazioni Sviluppatori': 'impostazioni_sviluppatori',
        'Informazioni sul Sistema Moderne': 'informazioni_sul_sistema_moderne',
        'Orologio Sveglie e Timer': 'orologio_sveglie_e_timer',
        'Calendario di Windows': 'calendario_di_windows',
        'Posta di Windows': 'posta_di_windows',
        'Note Adesive Moderne': 'note_adesive_moderne',
        'Calcolatrice Moderna': 'calcolatrice_moderna',
        'Microsoft Whiteboard': 'microsoft_whiteboard',
        'Microsoft To Do': 'microsoft_to_do',
        'Foto di Windows': 'foto_di_windows',
        'Film e TV': 'film_e_tv',
        'Microsoft Store': 'microsoft_store',
        'Meteo di Windows': 'meteo_di_windows',
        'Microsoft News': 'microsoft_news',
        'Nuovo Paint Moderno / Paint 3D': 'nuovo_paint_moderno_paint_3d',
        'Nuovo Media Player': 'nuovo_media_player',
        'Microsoft Edge': 'microsoft_edge',
        'Richiesta Supporto': 'richiesta_supporto',
        'Centro Assistenza (Get Help)': 'centro_assistenza_get_help',
        'Contatti di Windows': 'contatti_di_windows',
        'Cattura e Annota (Screenshot)': 'cattura_e_annota_screenshot',
        'App Xbox': 'app_xbox',
        'Xbox Game Bar': 'xbox_game_bar',
        'Google Chrome': 'google_chrome',
        'Mozilla Firefox': 'mozilla_firefox',
        'Brave Browser': 'brave_browser',
        'Opera Browser': 'opera_browser',
        'Vivaldi Browser': 'vivaldi_browser',
        'Discord': 'discord',
        'WhatsApp Desktop': 'whatsapp_desktop',
        'Telegram Desktop': 'telegram_desktop',
        'Slack': 'slack',
        'Microsoft Teams': 'microsoft_teams',
        'Zoom Meetings': 'zoom_meetings',
        'Skype': 'skype',
        'Spotify': 'spotify',
        'Microsoft Word': 'microsoft_word',
        'Microsoft Excel': 'microsoft_excel',
        'Microsoft PowerPoint': 'microsoft_powerpoint',
        'Microsoft Outlook': 'microsoft_outlook',
        'Microsoft OneNote': 'microsoft_onenote',
        'Valve Steam': 'valve_steam',
        'Epic Games Launcher': 'epic_games_launcher',
        'EA App': 'ea_app',
        'Ubisoft Connect': 'ubisoft_connect',
        'Visual Studio Code': 'visual_studio_code',
        'VLC Media Player': 'vlc_media_player',
        'Adobe Photoshop': 'adobe_photoshop',
        'GIMP': 'gimp',
        'Blender': 'blender',
        'WinRAR': 'winrar',
        '7-Zip File Manager': '7_zip_file_manager',
        'OBS Studio': 'obs_studio',
        'Notepad++': 'notepad',
        'Utenti e Computer Active Directory': 'utenti_e_computer_active_directory',
        'Domini e Trust Active Directory': 'domini_e_trust_active_directory',
        'Siti e Servizi Active Directory': 'siti_e_servizi_active_directory',
        'Servizi Componenti DCOM': 'servizi_componenti_dcom',
        'Origini Dati ODBC 64-bit': 'origini_dati_odbc_64_bit',
        'Interfaccia Utente Stampante': 'interfaccia_utente_stampante',
        'Installazione Pacchetti Lingua MUI': 'installazione_pacchetti_lingua_mui',
        'WMI Object Browser (Tester)': 'wmi_object_browser_tester',
        'Registrazione DLL e ActiveX': 'registrazione_dll_e_activex',
        'IExpress Wizard (Creazione Installer)': 'iexpress_wizard_creazione_installer',
        'Utility Certificati e Hash File': 'utility_certificati_e_hash_file',
        'Compilatore MOF WMI': 'compilatore_mof_wmi',
        'Filter Manager Control': 'filter_manager_control',
        'Mixer Volume Classico': 'mixer_volume_classico',
        'Check Disk (Riparazione Disco)': 'check_disk_riparazione_disco',
        'Deframmentazione e Ottimizzazione': 'deframmentazione_e_ottimizzazione',
        'Partizionamento Dischi (Riga Comando)': 'partizionamento_dischi_riga_comando',
        'File System Utility (Parametri NTFS)': 'file_system_utility_parametri_ntfs',
        'Cifratura NTFS (Cipher)': 'cifratura_ntfs_cipher',
        'Gestore Copie Shadow Volume': 'gestore_copie_shadow_volume',
        'System File Checker (SFC /Scannow)': 'system_file_checker_sfc_scannow',
        'Deployment Image Servicing (DISM)': 'deployment_image_servicing_dism',
        'Diagnostica Memoria RAM (Mdsched)': 'diagnostica_memoria_ram_mdsched',
        'Arresto / Spegnimento Sistema': 'arresto_spegnimento_sistema',
        'Disconnessione Utente (Logoff)': 'disconnessione_utente_logoff',
        'Scollega Sessione Corrente': 'scollega_sessione_corrente',
        'Generazione Report Batteria HTML': 'generazione_report_batteria_html',
        'Diagnostica Sospensione (SleepStudy)': 'diagnostica_sospensione_sleepstudy',
        'Riga Comando Windows Defender': 'riga_comando_windows_defender',
        'Icona Area Notifica Sicurezza': 'icona_area_notifica_sicurezza',
        'Installatore Definizioni Malware': 'installatore_definizioni_malware',
        'Gestione BitLocker (Riga Comando)': 'gestione_bitlocker_riga_comando',
        'Ripristino Emergenza BitLocker': 'ripristino_emergenza_bitlocker',
        'Gestione Completa Driver (PnpUtil)': 'gestione_completa_driver_pnputil',
        'Windows Subsystem for Linux (WSL)': 'windows_subsystem_for_linux_wsl',
        'Gestione Macchine Virtuali Hyper-V': 'gestione_macchine_virtuali_hyper_v',
        'Windows Sandbox': 'windows_sandbox',
        'Ripristino Cache Microsoft Store': 'ripristino_cache_microsoft_store',
        'Update Session Orchestrator Client': 'update_session_orchestrator_client',
        'Gestione Log Eventi (WevtUtil)': 'gestione_log_eventi_wevtutil',
        'Windows Installer CleanUp Utility': 'windows_installer_cleanup_utility',
        "Editor dell'Editor dei Metodi di Input (IME)": 'editor_dell_editor_dei_metodi_di_input_ime',
        'Visualizzatore Clipboard di Sistema': 'visualizzatore_clipboard_di_sistema',
        'Utility di Configurazione del Carattere Privato': 'utility_di_configurazione_del_carattere_privato',
        'Procedura Autenticazione Avanzata (Netplwiz)': 'procedura_autenticazione_avanzata_netplwiz',
        'Verifica Driver di Terze Parti (Sigverif)': 'verifica_firma_file',
        'Gestione del Provider di Stampe': 'gestione_del_provider_di_stampe',
        'Utility Controllo Driver di Filtro Rete': 'utility_controllo_driver_di_filtro_rete',
        'Monitoraggio Attivita di Rete IP': 'monitoraggio_attivita_di_rete_ip',
        'Configurazione Componenti COM Locali': 'configurazione_componenti_com_locali',
        'Strumento Diagnostica Supporto Microsoft (MSDT)': 'strumento_diagnostica_supporto_microsoft_msdt',
        'Verifica Integrita Pacchetti AppX': 'verifica_integrita_pacchetti_appx',
        'Utility di Migrazione Stato Utente (USMT)': 'utility_di_migrazione_stato_utente_usmt',
        'Strumento Applicazione Immagini WIM': 'strumento_applicazione_immagini_wim',
        'Gestione Componenti Servizi Windows (Dism)': 'gestione_componenti_servizi_windows_dism',
        'Utility di Sincronizzazione Ora di Rete (W32tm)': 'utility_di_sincronizzazione_ora_di_rete_w32tm',
        'Visualizzatore dello Stato delle Licenze (Slmgr)': 'visualizzatore_dello_stato_delle_licenze_slmgr',
        'Gestore dei Criteri di Indicizzazione': 'gestore_dei_criteri_di_indicizzazione',
        'Strumento di Rimozione Appx Preinstallate': 'strumento_di_rimozione_appx_preinstallate',
        'Interprete Script Console Nativo': 'interprete_script_console_nativo',
        'Generatore Pacchetti di Provisioning Windows': 'generatore_pacchetti_di_provisioning_windows',
        'Strumento di Diagnostica Audio di Rete': 'strumento_di_diagnostica_audio_di_rete',
    }),
    'linux': _costruisci_mappa({
        'Gestore File (Nautilus/Files)': 'gestore_file_nautilus_files',
        'Terminale GNOME': 'terminale_gnome',
        'Terminale Universale (xterm)': 'terminale_universale_xterm',
        'Editor di Testo (Gedit)': 'editor_di_testo_gedit',
        'Calcolatrice GNOME': 'calcolatrice_gnome',
        'Visualizzatore Immagini (Eye of GNOME)': 'visualizzatore_immagini_eye_of_gnome',
        'Visualizzatore PDF (Evince)': 'visualizzatore_pdf_evince',
        'Gestore Archivi (File Roller)': 'gestore_archivi_file_roller',
        'Monitor di Sistema GNOME': 'monitor_di_sistema_gnome',
        'Impostazioni di Sistema GNOME': 'impostazioni_di_sistema_gnome',
        'Centro Software GNOME': 'centro_software_gnome',
        'Analizzatore Utilizzo Disco (Baobab)': 'analizzatore_utilizzo_disco_baobab',
        'Strumento di Cattura Schermo GNOME': 'strumento_di_cattura_schermo_gnome',
        'Editor Connessioni di Rete': 'editor_connessioni_di_rete',
        'LibreOffice Writer': 'libreoffice_writer',
        'LibreOffice Calc': 'libreoffice_calc',
        'LibreOffice Impress': 'libreoffice_impress',
        'GParted (Partizionamento Dischi)': 'gparted_partizionamento_dischi',
        'Lettore Musicale (Rhythmbox)': 'lettore_musicale_rhythmbox',
        'Lettore Video (Totem)': 'lettore_video_totem',
        'App Webcam (Cheese)': 'app_webcam_cheese',
        'Portachiavi e Password (Seahorse)': 'portachiavi_e_password_seahorse',
        'Visualizzatore Font GNOME': 'visualizzatore_font_gnome',
        'Utility Dischi GNOME': 'utility_dischi_gnome',
        'Client Torrent (Transmission)': 'client_torrent_transmission',
        'Gestore Macchine Virtuali (virt-manager)': 'gestore_macchine_virtuali_virt_manager',
        'GNOME Tweaks': 'gnome_tweaks',
        'Caratteri Speciali GNOME': 'caratteri_speciali_gnome',
        'Orologio GNOME': 'orologio_gnome',
        'Meteo GNOME': 'meteo_gnome',
    }),
    'macos': _costruisci_mappa({
        'Pages': 'pages_macos',
        'Numbers': 'numbers_macos',
        'Keynote': 'keynote_macos',
        'TextEdit': 'textedit_macos',
        'Anteprima (Preview)': 'anteprima_preview_macos',
        'Calcolatrice': 'calcolatrice_macos',
        'Calendario': 'calendario_macos',
        'Contatti': 'contatti_macos',
        'Note': 'note_macos',
        'Promemoria': 'promemoria_macos',
        'Note Adesive (Stickies)': 'note_adesive_stickies_macos',
        'Automator': 'automator_macos',
        'Editor di Script (Script Editor)': 'editor_di_script_script_editor_macos',
        'Comandi Rapidi (Shortcuts)': 'comandi_rapidi_shortcuts_macos',
        'Freeform': 'freeform_macos',
        'Dizionario': 'dizionario_macos',
        'Libro Font (Font Book)': 'libro_font_font_book_macos',
        'Terminale': 'terminale_macos',
        'Monitoraggio Attivita': 'monitoraggio_attivita_macos',
        'Console': 'console_macos',
        'Utility Disco': 'utility_disco_macos',
        'Informazioni di Sistema': 'informazioni_di_sistema_macos',
        'Assistente Migrazione': 'assistente_migrazione_macos',
        'Accesso Portachiavi (Keychain Access)': 'accesso_portachiavi_keychain_access_macos',
        'Screenshot': 'screenshot_macos',
        'Condivisione Schermo': 'condivisione_schermo_macos',
        'Misuratore Colore Digitale': 'misuratore_colore_digitale_macos',
        'Grapher': 'grapher_macos',
        'Scambio File Bluetooth': 'scambio_file_bluetooth_macos',
        'Configurazione Audio MIDI': 'configurazione_audio_midi_macos',
        'Utility ColorSync': 'utility_colorsync_macos',
        'Utility AirPort': 'utility_airport_macos',
        'Assistente Boot Camp': 'assistente_boot_camp_macos',
        'Utility VoiceOver': 'utility_voiceover_macos',
        'Diagnostica Wireless': 'diagnostica_wireless_macos',
        'Time Machine': 'time_machine_macos',
        'Impostazioni di Sistema': 'impostazioni_di_sistema_macos',
        'Finder': 'finder_macos',
        'Launchpad': 'launchpad_macos',
        'Mission Control': 'mission_control_macos',
        'Siri': 'siri_macos',
        'Acquisizione Immagini (Image Capture)': 'acquisizione_immagini_image_capture_macos',
        'App Store': 'app_store_macos',
        'Safari': 'safari_macos',
        'Mail': 'mail_macos',
        'Messaggi': 'messaggi_macos',
        'FaceTime': 'facetime_macos',
        "Dov'e (Find My)": 'dov_e_find_my_macos',
        'Mappe': 'mappe_macos',
        'Casa (Home)': 'casa_home_macos',
        'Google Chrome': 'google_chrome_macos',
        'Mozilla Firefox': 'mozilla_firefox_macos',
        'Microsoft Edge': 'microsoft_edge_macos',
        'Opera': 'opera_macos',
        'Brave Browser': 'brave_browser_macos',
        'Slack': 'slack_macos',
        'Zoom': 'zoom_macos',
        'Microsoft Teams': 'microsoft_teams_macos',
        'Discord': 'discord_macos',
        'WhatsApp': 'whatsapp_macos',
        'Telegram': 'telegram_macos',
        'Skype': 'skype_macos',
        'Musica (Music)': 'musica_music_macos',
        'TV': 'tv_macos',
        'Podcast': 'podcast_macos',
        'Foto (Photos)': 'foto_photos_macos',
        'Photo Booth': 'photo_booth_macos',
        'QuickTime Player': 'quicktime_player_macos',
        'Promemoria Vocali (Voice Memos)': 'promemoria_vocali_voice_memos_macos',
        'News': 'news_macos',
        'Libri (Books)': 'libri_books_macos',
        'Borsa (Stocks)': 'borsa_stocks_macos',
        'Scacchi (Chess)': 'scacchi_chess_macos',
        'Orologio (Clock)': 'orologio_clock_macos',
        'Spotify': 'spotify_macos',
        'VLC': 'vlc_macos',
        'IINA': 'iina_macos',
        'GarageBand': 'garageband_macos',
        'iMovie': 'imovie_macos',
        'Xcode': 'xcode_macos',
        'Visual Studio Code': 'visual_studio_code_macos',
        'Sublime Text': 'sublime_text_macos',
        'iTerm2': 'iterm2_macos',
        'Docker Desktop': 'docker_desktop_macos',
        'Adobe Photoshop': 'adobe_photoshop_macos',
        'Adobe Illustrator': 'adobe_illustrator_macos',
        'GIMP': 'gimp_macos',
        'Blender': 'blender_macos',
        'OBS Studio': 'obs_studio_macos',
        'Sketch': 'sketch_macos',
        'Figma': 'figma_macos',
        'Microsoft Word': 'microsoft_word_macos',
        'Microsoft Excel': 'microsoft_excel_macos',
        'Microsoft PowerPoint': 'microsoft_powerpoint_macos',
        'Microsoft Outlook': 'microsoft_outlook_macos',
        'Microsoft OneNote': 'microsoft_onenote_macos',
        'Notion': 'notion_macos',
        'Evernote': 'evernote_macos',
        '1Password': '1password_macos',
        'CleanMyMac X': 'cleanmymac_x_macos',
        'Steam': 'steam_macos',
        'Epic Games Launcher': 'epic_games_launcher_macos',
        'Battle.net': 'battle_net_macos',
        'Parallels Desktop': 'parallels_desktop_macos',
        'VMware Fusion': 'vmware_fusion_macos',
        'Transmission': 'transmission_macos',
        'The Unarchiver': 'the_unarchiver_macos',
        'Keka': 'keka_macos',
    }),
}
#-----------------------------------
# COMANDI RAPIDI DA TERMINALE - WINDOWS (os.system, come un vero cmd)
#-----------------------------------
def cmd_configurazione_rete():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("ipconfig")
def cmd_configurazione_rete_completa():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("ipconfig /all")
def cmd_prova_connessione():
    os.system('cls' if os.name == 'nt' else 'clear')
    indirizzo = input(f"{VERDE_MATRIX}INSERIRE INDIRIZZO O SITO DA CONTATTARE (es. google.com): ").strip()
    os.system(f"ping {indirizzo}")
def cmd_percorso_di_rete():
    os.system('cls' if os.name == 'nt' else 'clear')
    indirizzo = input(f"{VERDE_MATRIX}INSERIRE INDIRIZZO O SITO DA TRACCIARE (es. google.com): ").strip()
    os.system(f"tracert {indirizzo}")
def cmd_connessioni_di_rete_attive():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("netstat -ano")
def cmd_informazioni_dettagliate_sistema():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("systeminfo")
def cmd_elenco_processi_attivi():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("tasklist")
def cmd_nome_utente_attuale():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("whoami")
def cmd_nome_del_computer():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("hostname")
def cmd_contenuto_cartella_attuale():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("dir")
def cmd_versione_windows():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("ver")
def cmd_controllo_dischi():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("chkdsk")
def cmd_controllo_file_di_sistema():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("sfc /scannow")
def cmd_nome_del_processore():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("wmic cpu get name")
def cmd_elenco_dischi_e_spazio_libero():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("wmic logicaldisk get caption,description,freespace")
def cmd_elenco_utenti_del_pc():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("net user")
def cmd_orario_attuale():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("time /t")
def cmd_data_attuale():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("date /t")
def cmd_svuota_cache_dns():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("ipconfig /flushdns")

#-----------------------------------
# COMANDI RAPIDI DA TERMINALE - LINUX (os.system, come un vero terminale)
#-----------------------------------
def cmd_informazioni_sul_kernel():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("uname -a")
def cmd_nome_utente_attuale_linux():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("whoami")
def cmd_nome_del_computer_linux():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("hostname")
def cmd_configurazione_rete_linux():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("ip a")
def cmd_prova_connessione_linux():
    os.system('cls' if os.name == 'nt' else 'clear')
    indirizzo = input(f"{VERDE_MATRIX}INSERIRE INDIRIZZO O SITO DA CONTATTARE (es. google.com): ").strip()
    os.system(f"ping -c 4 {indirizzo}")
def cmd_spazio_sui_dischi():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("df -h")
def cmd_memoria_ram_disponibile():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("free -h")
def cmd_elenco_processi_attivi_linux():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("ps aux")
def cmd_elenco_dischi_e_partizioni():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("lsblk")
def cmd_dimensione_cartella_attuale():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("du -sh .")
def cmd_informazioni_distribuzione():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("cat /etc/os-release")
def cmd_connessioni_di_rete_attive_linux():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("netstat -tulnp")
def cmd_utenti_collegati_ora():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("who")
def cmd_contenuto_cartella_attuale_linux():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("ls -la")
def cmd_cronologia_comandi():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("history")
def cmd_variabile_path():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("echo $PATH")
def cmd_pacchetti_installati():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("apt list --installed")

#-----------------------------------
# COMANDI RAPIDI DA TERMINALE - MACOS (os.system, come un vero terminale)
#-----------------------------------
def cmd_informazioni_hardware_mac():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("system_profiler SPHardwareDataType")
def cmd_versione_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("sw_vers")
def cmd_nome_utente_attuale_mac():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("whoami")
def cmd_nome_del_computer_mac():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("scutil --get ComputerName")
def cmd_configurazione_rete_mac():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("ifconfig")
def cmd_prova_connessione_mac():
    os.system('cls' if os.name == 'nt' else 'clear')
    indirizzo = input(f"{VERDE_MATRIX}INSERIRE INDIRIZZO O SITO DA CONTATTARE (es. google.com): ").strip()
    os.system(f"ping -c 4 {indirizzo}")
def cmd_spazio_sui_dischi_mac():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("df -h")
def cmd_elenco_processi_attivi_mac():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("ps aux")
def cmd_elenco_dischi_mac():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("diskutil list")
def cmd_stato_batteria():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("pmset -g batt")
def cmd_utenti_collegati_ora_mac():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("who")
def cmd_contenuto_cartella_attuale_mac():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("ls -la")
def cmd_connessioni_di_rete_attive_mac():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("netstat -an")
def cmd_cronologia_comandi_mac():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("history")
def cmd_variabile_path_mac():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("echo $PATH")
def cmd_tempo_di_attivita_mac():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("uptime")
def cmd_informazioni_processore_mac():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("sysctl -n machdep.cpu.brand_string")
def cmd_svuota_cache_dns_mac():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("sudo dscacheutil -flushcache")


def apri_blocco_note():
    os.system('cls' if os.name == 'nt' else 'clear')
    sistema = input(f"{VERDE_MATRIX}INSERIRE NOME SISTEMA OPERATIVO: ").strip().lower()
    if sistema == "windows":
        subprocess.Popen("notepad.exe")
def apri_calcolatrice():
    os.system('cls' if os.name == 'nt' else 'clear')
    sistema = input(f"{VERDE_MATRIX}INSERIRE NOME SISTEMA OPERATIVO: ").strip().lower()
    if sistema == "windows":
        subprocess.Popen("calc.exe")
def apri_paint():
    subprocess.Popen("mspaint.exe")
def apri_wordpad():
    subprocess.Popen("write.exe")
def apri_strumento_per_screenshot():
    subprocess.Popen("snippingtool.exe")
def apri_registrazoni_azioni_utente():
    subprocess.Popen("psr.exe")
def apri_mappa_caratteri():
    subprocess.Popen("charmap.exe")
def apri_connessione_ytelefonica_guidatra():
    subprocess.Popen("dialer.exe")
def apri_esplora_file():
    subprocess.Popen("explorer.exe")
def apri_gestione_attività():
    subprocess.Popen("taskmgr.exe")
def apri_cmd():
    subprocess.Popen("cmd.exe")
def apri_powershell():
    subprocess.Popen("powershell.exe")
def apri_registro_di_sistema():
    subprocess.Popen("regedit.exe")
def apri_pannello_di_controllo():
    subprocess.Popen("control.exe")
def apri_informazioni_sistema():
    subprocess.Popen("msinfo32.exe")
def apri_microsoft_management_console():
    subprocess.Popen("mmc.exe")
def apri_pulizia_disco():
    subprocess.Popen("cleanmgr.exe")
def apri_ripristino_conf_di_sistema():
    subprocess.Popen("rstrui.exe")
def apri_utilità_di_pianificazione():
    subprocess.Popen("taskschd.msc")
def apri_visualizzatore_eventi():
    subprocess.Popen("eventvwr.msc")
def apri_gestione_servizi():
    subprocess.Popen("services.msc")
def apri_gestione_dispositivi():
    subprocess.Popen("devmgmt.msc")
def apri_gestione_dischi():
    subprocess.Popen("diskmgmt.msc")
def apri_gestione_pc():
    subprocess.Popen("compmgmt.msc")
def apri_gestione_stampa():
    subprocess.Popen("printmanagement.msc")
def apri_strumento_diagnostica_directx():
    subprocess.Popen("dxdiag.exe")
def apri_centro_sincronizzazione_periferiche():
    subprocess.Popen("mobsync.exe")
def apri_connessione_desktop_remoto():
    subprocess.Popen("mstsc.exe")
def apri_inizializzatore_ISCSI():
    subprocess.Popen("iscsicpl.exe")
def apri_windows_firewall_avanzato():
    subprocess.Popen("wf.msc")
def apri_opzioni_telefono_e_modem():
    subprocess.Popen("telephon.cpl")

#-----------------------------------
# FUNZIONI DI APERTURA AGGIUNTIVE (generate da LISTA_COMANDI)
#-----------------------------------
def apri_note_adesive_classiche():
    subprocess.Popen("stikynot.exe")

def apri_monitoraggio_affidabilita_e_performance():
    subprocess.Popen("perfmon.exe")

def apri_monitoraggio_risorse():
    subprocess.Popen("resmon.exe")

def apri_configurazione_di_sistema_msconfig():
    subprocess.Popen("msconfig.exe")

def apri_verifica_firma_file():
    subprocess.Popen("sigverif.exe")

def apri_driver_verifier_manager():
    subprocess.Popen("verifier.exe")

def apri_informazioni_versione_windows():
    subprocess.Popen("winver.exe")

def apri_strumento_rimozione_malware_microsoft():
    subprocess.Popen("mrt.exe")

def apri_backup_e_ripristino_credenziali():
    subprocess.Popen("credwiz.exe")

def apri_criteri_di_sicurezza_locali():
    subprocess.Popen("secpol.msc")

def apri_editor_dei_criteri_di_gruppo_locali():
    subprocess.Popen("gpedit.msc")

def apri_programmi_e_funzionalita_disinstalla():
    subprocess.Popen("appwiz.cpl")

def apri_impostazioni_schermo_classiche():
    subprocess.Popen("desk.cpl")

def apri_proprieta_del_mouse():
    subprocess.Popen("main.cpl")

def apri_impostazioni_audio_suoni():
    subprocess.Popen("mmsys.cpl")

def apri_proprieta_del_sistema_variabili_ambiente():
    subprocess.Popen("sysdm.cpl")

def apri_impostazioni_data_e_ora():
    subprocess.Popen("timedate.cpl")

def apri_opzioni_risparmio_energia():
    subprocess.Popen("powercfg.cpl")

def apri_opzioni_internazionali_e_lingua():
    subprocess.Popen("intl.cpl")

def apri_installazione_guidata_hardware_legacy():
    subprocess.Popen("hdwwiz.cpl")

def apri_proprieta_internet():
    subprocess.Popen("inetcpl.cpl")

def apri_periferiche_di_gioco_controller():
    subprocess.Popen("joy.cpl")

def apri_centro_accessibilita_classico():
    subprocess.Popen("access.cpl")

def apri_impostazioni_generali():
    subprocess.Popen("ms-settings:")

def apri_windows_update():
    subprocess.Popen("ms-settings:windowsupdate")

def apri_stato_della_rete_e_wi_fi():
    subprocess.Popen("ms-settings:network")

def apri_gestione_dispositivi_bluetooth():
    subprocess.Popen("ms-settings:bluetooth")

def apri_impostazioni_schermo_moderne():
    subprocess.Popen("ms-settings:display")

def apri_gestione_notifiche():
    subprocess.Popen("ms-settings:notifications")

def apri_elenco_app_installate():
    subprocess.Popen("ms-settings:appsfeatures")

def apri_applicazioni_predefinite():
    subprocess.Popen("ms-settings:defaultapps")

def apri_personalizzazione_e_sfondi():
    subprocess.Popen("ms-settings:personalization")

def apri_gestione_dei_temi():
    subprocess.Popen("ms-settings:themes")

def apri_schermata_di_blocco():
    subprocess.Popen("ms-settings:lockscreen")

def apri_data_e_ora_moderne():
    subprocess.Popen("ms-settings:dateandtime")

def apri_lingua_e_area_geografica():
    subprocess.Popen("ms-settings:regionlanguage")

def apri_privacy_generale():
    subprocess.Popen("ms-settings:privacy")

def apri_autorizzazioni_webcam():
    subprocess.Popen("ms-settings:privacy-webcam")

def apri_autorizzazioni_microfono():
    subprocess.Popen("ms-settings:privacy-microfone")

def apri_sicurezza_di_windows_defender():
    subprocess.Popen("ms-settings:windowsdefender")

def apri_opzioni_di_ripristino_recovery():
    subprocess.Popen("ms-settings:recovery")

def apri_impostazioni_sviluppatori():
    subprocess.Popen("ms-settings:developers")

def apri_informazioni_sul_sistema_moderne():
    subprocess.Popen("ms-settings:about")

def apri_orologio_sveglie_e_timer():
    subprocess.Popen("ms-clock:")

def apri_calendario_di_windows():
    subprocess.Popen("outlookcal:")

def apri_posta_di_windows():
    subprocess.Popen("outlookmail:")

def apri_note_adesive_moderne():
    subprocess.Popen("ms-stickynotes:")

def apri_calcolatrice_moderna():
    subprocess.Popen("ms-calculator:")

def apri_microsoft_whiteboard():
    subprocess.Popen("ms-whiteboard:")

def apri_microsoft_to_do():
    subprocess.Popen("ms-todo:")

def apri_foto_di_windows():
    subprocess.Popen("ms-photos:")

def apri_film_e_tv():
    subprocess.Popen("mswindowsvideo:")

def apri_microsoft_store():
    subprocess.Popen("ms-windows-store:")

def apri_meteo_di_windows():
    subprocess.Popen("bingweather:")

def apri_microsoft_news():
    subprocess.Popen("bingnews:")

def apri_nuovo_paint_moderno_paint_3d():
    subprocess.Popen("ms-paint:")

def apri_nuovo_media_player():
    subprocess.Popen("ms-mediaplayer:")

def apri_microsoft_edge():
    subprocess.Popen("microsoft-edge:")

def apri_richiesta_supporto():
    subprocess.Popen("ms-contact-support:")

def apri_centro_assistenza_get_help():
    subprocess.Popen("ms-get-help:")

def apri_contatti_di_windows():
    subprocess.Popen("ms-people:")

def apri_cattura_e_annota_screenshot():
    subprocess.Popen("ms-screenclip:")

def apri_app_xbox():
    subprocess.Popen("xbox:")

def apri_xbox_game_bar():
    subprocess.Popen("ms-gamebar:")

def apri_google_chrome():
    subprocess.Popen("chrome")

def apri_mozilla_firefox():
    subprocess.Popen("firefox")

def apri_brave_browser():
    subprocess.Popen("brave")

def apri_opera_browser():
    subprocess.Popen("opera")

def apri_vivaldi_browser():
    subprocess.Popen("vivaldi")

def apri_discord():
    subprocess.Popen("discord:")

def apri_whatsapp_desktop():
    subprocess.Popen("whatsapp:")

def apri_telegram_desktop():
    subprocess.Popen("tg:")

def apri_slack():
    subprocess.Popen("slack:")

def apri_microsoft_teams():
    subprocess.Popen("teams:")

def apri_zoom_meetings():
    subprocess.Popen("zoommtg:")

def apri_skype():
    subprocess.Popen("skype:")

def apri_spotify():
    subprocess.Popen("spotify:")

def apri_microsoft_word():
    subprocess.Popen("winword")

def apri_microsoft_excel():
    subprocess.Popen("excel")

def apri_microsoft_powerpoint():
    subprocess.Popen("powerpnt")

def apri_microsoft_outlook():
    subprocess.Popen("outlook")

def apri_microsoft_onenote():
    subprocess.Popen("onenote")

def apri_valve_steam():
    subprocess.Popen("steam:")

def apri_epic_games_launcher():
    subprocess.Popen("com.epicgames.launcher:")

def apri_ea_app():
    subprocess.Popen("ea:")

def apri_ubisoft_connect():
    subprocess.Popen("ubisoftconnect:")

def apri_visual_studio_code():
    subprocess.Popen("code")

def apri_vlc_media_player():
    subprocess.Popen("vlc")

def apri_adobe_photoshop():
    subprocess.Popen("photoshop")

def apri_gimp():
    subprocess.Popen("gimp")

def apri_blender():
    subprocess.Popen("blender")

def apri_winrar():
    subprocess.Popen("winrar")

def apri_7_zip_file_manager():
    subprocess.Popen("7zFM.exe")

def apri_obs_studio():
    subprocess.Popen("obs")

def apri_notepad():
    subprocess.Popen("notepad++")

def apri_utenti_e_computer_active_directory():
    subprocess.Popen("dsa.msc")

def apri_domini_e_trust_active_directory():
    subprocess.Popen("domain.msc")

def apri_siti_e_servizi_active_directory():
    subprocess.Popen("dssite.msc")

def apri_servizi_componenti_dcom():
    subprocess.Popen("dcomcnfg.exe")

def apri_origini_dati_odbc_64_bit():
    subprocess.Popen("odbcad64.exe")

def apri_interfaccia_utente_stampante():
    subprocess.Popen("printui.exe")

def apri_installazione_pacchetti_lingua_mui():
    subprocess.Popen("lpksetup.exe")

def apri_wmi_object_browser_tester():
    subprocess.Popen("wbemtest.exe")

def apri_registrazione_dll_e_activex():
    subprocess.Popen("regsvr32.exe")

def apri_iexpress_wizard_creazione_installer():
    subprocess.Popen("iexpress.exe")

def apri_utility_certificati_e_hash_file():
    subprocess.Popen("certutil.exe")

def apri_compilatore_mof_wmi():
    subprocess.Popen("mofcomp.exe")

def apri_filter_manager_control():
    subprocess.Popen("fltmc.exe")

def apri_mixer_volume_classico():
    subprocess.Popen("sndvol.exe")

def apri_check_disk_riparazione_disco():
    subprocess.Popen("chkdsk.exe")

def apri_deframmentazione_e_ottimizzazione():
    subprocess.Popen("defrag.exe")

def apri_partizionamento_dischi_riga_comando():
    subprocess.Popen("diskpart.exe")

def apri_file_system_utility_parametri_ntfs():
    subprocess.Popen("fsutil.exe")

def apri_cifratura_ntfs_cipher():
    subprocess.Popen("cipher.exe")

def apri_gestore_copie_shadow_volume():
    subprocess.Popen("vssadmin.exe")

def apri_system_file_checker_sfc_scannow():
    subprocess.Popen("sfc.exe")

def apri_deployment_image_servicing_dism():
    subprocess.Popen("dism.exe")

def apri_diagnostica_memoria_ram_mdsched():
    subprocess.Popen("mdsched.exe")

def apri_arresto_spegnimento_sistema():
    subprocess.Popen("shutdown.exe")

def apri_disconnessione_utente_logoff():
    subprocess.Popen("logoff.exe")

def apri_scollega_sessione_corrente():
    subprocess.Popen("tsdiscon.exe")

def apri_generazione_report_batteria_html():
    subprocess.Popen("powercfg.exe /batteryreport")

def apri_diagnostica_sospensione_sleepstudy():
    subprocess.Popen("powercfg.exe /sleepstudy")

def apri_riga_comando_windows_defender():
    subprocess.Popen("MpCmdRun.exe")

def apri_icona_area_notifica_sicurezza():
    subprocess.Popen("SecurityHealthSystray.exe")

def apri_installatore_definizioni_malware():
    subprocess.Popen("MpSigStub.exe")

def apri_gestione_bitlocker_riga_comando():
    subprocess.Popen("manage-bde.exe")

def apri_ripristino_emergenza_bitlocker():
    subprocess.Popen("repair-bde.exe")

def apri_gestione_completa_driver_pnputil():
    subprocess.Popen("pnputil.exe")

def apri_windows_subsystem_for_linux_wsl():
    subprocess.Popen("wsl.exe")

def apri_gestione_macchine_virtuali_hyper_v():
    subprocess.Popen("virtmgmt.msc")

def apri_windows_sandbox():
    subprocess.Popen("WindowsSandbox.exe")

def apri_ripristino_cache_microsoft_store():
    subprocess.Popen("wsreset.exe")

def apri_update_session_orchestrator_client():
    subprocess.Popen("usoclient.exe")

def apri_gestione_log_eventi_wevtutil():
    subprocess.Popen("wevtutil.exe")

def apri_windows_installer_cleanup_utility():
    subprocess.Popen("msiexec.exe")

def apri_editor_dell_editor_dei_metodi_di_input_ime():
    subprocess.Popen("imepad.exe")

def apri_visualizzatore_clipboard_di_sistema():
    subprocess.Popen("clipbrd.exe")

def apri_utility_di_configurazione_del_carattere_privato():
    subprocess.Popen("eudcedit.exe")

def apri_procedura_autenticazione_avanzata_netplwiz():
    subprocess.Popen("netplwiz.exe")

def apri_verifica_driver_di_terze_parti_sigverif():
    subprocess.Popen("sigverif.exe")

def apri_gestione_del_provider_di_stampe():
    subprocess.Popen("localspl.dll")

def apri_utility_controllo_driver_di_filtro_rete():
    subprocess.Popen("netcfg.exe")

def apri_monitoraggio_attivita_di_rete_ip():
    subprocess.Popen("pktmon.exe")

def apri_configurazione_componenti_com_locali():
    subprocess.Popen("comexp.msc")

def apri_strumento_diagnostica_supporto_microsoft_msdt():
    subprocess.Popen("msdt.exe")

def apri_verifica_integrita_pacchetti_appx():
    subprocess.Popen("appxsysprep.exe")

def apri_utility_di_migrazione_stato_utente_usmt():
    subprocess.Popen("scanstate.exe")

def apri_strumento_applicazione_immagini_wim():
    subprocess.Popen("imagex.exe")

def apri_gestione_componenti_servizi_windows_dism():
    subprocess.Popen("dism.exe /online /get-features")

def apri_utility_di_sincronizzazione_ora_di_rete_w32tm():
    subprocess.Popen("w32tm.exe")

def apri_visualizzatore_dello_stato_delle_licenze_slmgr():
    subprocess.Popen("slmgr.vbs")

def apri_gestore_dei_criteri_di_indicizzazione():
    subprocess.Popen("searchindexingconfig.exe")

def apri_strumento_di_rimozione_appx_preinstallate():
    subprocess.Popen("remove-appxpackage")

def apri_interprete_script_console_nativo():
    subprocess.Popen("cscript.exe")

def apri_generatore_pacchetti_di_provisioning_windows():
    subprocess.Popen("icd.exe")

def apri_strumento_di_diagnostica_audio_di_rete():
    subprocess.Popen("audiodg.exe")

#-----------------------------------
# FUNZIONI DI TERMINAZIONE (normale)
#-----------------------------------
def termina_blocco_note():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "notepad.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: notepad.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_calcolatrice():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "calc.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: calc.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_paint():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "mspaint.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: mspaint.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_wordpad():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "write.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: write.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_strumento_per_screenshot():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "snippingtool.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: snippingtool.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_registrazoni_azioni_utente():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "psr.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: psr.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_mappa_caratteri():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "charmap.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: charmap.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_connessione_ytelefonica_guidatra():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "dialer.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: dialer.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_esplora_file():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "explorer.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: explorer.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_gestione_attivita():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "taskmgr.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: taskmgr.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_cmd():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "cmd.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: cmd.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_powershell():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "powershell.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: powershell.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_registro_di_sistema():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "regedit.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: regedit.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_pannello_di_controllo():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "control.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: control.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_informazioni_sistema():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "msinfo32.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: msinfo32.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_microsoft_management_console():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "mmc.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: mmc.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_pulizia_disco():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "cleanmgr.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: cleanmgr.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_ripristino_conf_di_sistema():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "rstrui.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: rstrui.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_utilita_di_pianificazione():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "taskschd.msc"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: taskschd.msc")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_visualizzatore_eventi():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "eventvwr.msc"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: eventvwr.msc")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_gestione_servizi():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "services.msc"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: services.msc")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_gestione_dispositivi():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "devmgmt.msc"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: devmgmt.msc")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_gestione_dischi():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "diskmgmt.msc"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: diskmgmt.msc")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_gestione_pc():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "compmgmt.msc"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: compmgmt.msc")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_gestione_stampa():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "printmanagement.msc"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: printmanagement.msc")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_strumento_diagnostica_directx():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "dxdiag.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: dxdiag.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_centro_sincronizzazione_periferiche():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "mobsync.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: mobsync.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_connessione_desktop_remoto():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "mstsc.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: mstsc.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_inizializzatore_iscsi():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "iscsicpl.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: iscsicpl.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_windows_firewall_avanzato():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "wf.msc"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: wf.msc")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_opzioni_telefono_e_modem():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "telephon.cpl"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: telephon.cpl")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_note_adesive_classiche():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "stikynot.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: stikynot.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_monitoraggio_affidabilita_e_performance():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "perfmon.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: perfmon.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_monitoraggio_risorse():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "resmon.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: resmon.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_configurazione_di_sistema_msconfig():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "msconfig.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: msconfig.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_verifica_firma_file():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "sigverif.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: sigverif.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_driver_verifier_manager():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "verifier.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: verifier.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_informazioni_versione_windows():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "winver.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: winver.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_strumento_rimozione_malware_microsoft():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "mrt.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: mrt.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_backup_e_ripristino_credenziali():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "credwiz.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: credwiz.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_criteri_di_sicurezza_locali():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "secpol.msc"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: secpol.msc")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_editor_dei_criteri_di_gruppo_locali():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "gpedit.msc"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: gpedit.msc")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_programmi_e_funzionalita_disinstalla():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "appwiz.cpl"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: appwiz.cpl")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_impostazioni_schermo_classiche():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "desk.cpl"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: desk.cpl")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_proprieta_del_mouse():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "main.cpl"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: main.cpl")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_impostazioni_audio_suoni():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "mmsys.cpl"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: mmsys.cpl")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_proprieta_del_sistema_variabili_ambiente():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "sysdm.cpl"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: sysdm.cpl")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_impostazioni_data_e_ora():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "timedate.cpl"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: timedate.cpl")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_opzioni_risparmio_energia():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "powercfg.cpl"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: powercfg.cpl")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_opzioni_internazionali_e_lingua():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "intl.cpl"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: intl.cpl")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_installazione_guidata_hardware_legacy():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "hdwwiz.cpl"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: hdwwiz.cpl")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_proprieta_internet():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "inetcpl.cpl"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: inetcpl.cpl")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_periferiche_di_gioco_controller():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "joy.cpl"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: joy.cpl")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_centro_accessibilita_classico():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "access.cpl"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: access.cpl")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_impostazioni_generali():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "ms-settings:"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: ms-settings:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_windows_update():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "ms-settings:windowsupdate"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: ms-settings:windowsupdate")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_stato_della_rete_e_wi_fi():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "ms-settings:network"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: ms-settings:network")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_gestione_dispositivi_bluetooth():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "ms-settings:bluetooth"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: ms-settings:bluetooth")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_impostazioni_schermo_moderne():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "ms-settings:display"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: ms-settings:display")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_gestione_notifiche():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "ms-settings:notifications"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: ms-settings:notifications")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_elenco_app_installate():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "ms-settings:appsfeatures"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: ms-settings:appsfeatures")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_applicazioni_predefinite():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "ms-settings:defaultapps"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: ms-settings:defaultapps")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_personalizzazione_e_sfondi():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "ms-settings:personalization"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: ms-settings:personalization")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_gestione_dei_temi():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "ms-settings:themes"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: ms-settings:themes")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_schermata_di_blocco():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "ms-settings:lockscreen"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: ms-settings:lockscreen")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_data_e_ora_moderne():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "ms-settings:dateandtime"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: ms-settings:dateandtime")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_lingua_e_area_geografica():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "ms-settings:regionlanguage"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: ms-settings:regionlanguage")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_privacy_generale():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "ms-settings:privacy"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: ms-settings:privacy")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_autorizzazioni_webcam():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "ms-settings:privacy-webcam"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: ms-settings:privacy-webcam")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_autorizzazioni_microfono():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "ms-settings:privacy-microfone"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: ms-settings:privacy-microfone")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_sicurezza_di_windows_defender():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "ms-settings:windowsdefender"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: ms-settings:windowsdefender")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_opzioni_di_ripristino_recovery():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "ms-settings:recovery"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: ms-settings:recovery")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_impostazioni_sviluppatori():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "ms-settings:developers"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: ms-settings:developers")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_informazioni_sul_sistema_moderne():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "ms-settings:about"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: ms-settings:about")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_orologio_sveglie_e_timer():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "ms-clock:"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: ms-clock:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_calendario_di_windows():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "outlookcal:"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: outlookcal:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_posta_di_windows():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "outlookmail:"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: outlookmail:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_note_adesive_moderne():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "ms-stickynotes:"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: ms-stickynotes:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_calcolatrice_moderna():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "ms-calculator:"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: ms-calculator:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_microsoft_whiteboard():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "ms-whiteboard:"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: ms-whiteboard:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_microsoft_to_do():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "ms-todo:"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: ms-todo:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_foto_di_windows():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "ms-photos:"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: ms-photos:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_film_e_tv():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "mswindowsvideo:"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: mswindowsvideo:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_microsoft_store():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "ms-windows-store:"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: ms-windows-store:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_meteo_di_windows():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "bingweather:"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: bingweather:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_microsoft_news():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "bingnews:"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: bingnews:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_nuovo_paint_moderno_paint_3d():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "ms-paint:"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: ms-paint:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_nuovo_media_player():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "ms-mediaplayer:"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: ms-mediaplayer:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_microsoft_edge():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "microsoft-edge:"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: microsoft-edge:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_richiesta_supporto():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "ms-contact-support:"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: ms-contact-support:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_centro_assistenza_get_help():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "ms-get-help:"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: ms-get-help:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_contatti_di_windows():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "ms-people:"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: ms-people:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_cattura_e_annota_screenshot():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "ms-screenclip:"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: ms-screenclip:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_app_xbox():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "xbox:"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: xbox:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_xbox_game_bar():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "ms-gamebar:"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: ms-gamebar:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_google_chrome():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "chrome.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: chrome.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_mozilla_firefox():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "firefox.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: firefox.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_brave_browser():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "brave.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: brave.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_opera_browser():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "opera.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: opera.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_vivaldi_browser():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "vivaldi.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: vivaldi.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_discord():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "discord:"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: discord:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_whatsapp_desktop():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "whatsapp:"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: whatsapp:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_telegram_desktop():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "tg:"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: tg:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_slack():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "slack:"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: slack:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_microsoft_teams():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "teams:"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: teams:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_zoom_meetings():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "zoommtg:"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: zoommtg:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_skype():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "skype:"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: skype:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_spotify():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "spotify:"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: spotify:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_microsoft_word():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "winword.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: winword.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_microsoft_excel():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "excel.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: excel.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_microsoft_powerpoint():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "powerpnt.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: powerpnt.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_microsoft_outlook():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "outlook.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: outlook.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_microsoft_onenote():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "onenote.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: onenote.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_valve_steam():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "steam:"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: steam:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_epic_games_launcher():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "com.epicgames.launcher:"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: com.epicgames.launcher:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_ea_app():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "ea:"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: ea:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_ubisoft_connect():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "ubisoftconnect:"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: ubisoftconnect:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_visual_studio_code():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "code.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: code.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_vlc_media_player():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "vlc.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: vlc.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_adobe_photoshop():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "photoshop.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: photoshop.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_gimp():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "gimp.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: gimp.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_blender():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "blender.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: blender.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_winrar():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "winrar.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: winrar.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_7_zip_file_manager():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "7zFM.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: 7zFM.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_obs_studio():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "obs.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: obs.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_notepad():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "notepad++.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: notepad++.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_utenti_e_computer_active_directory():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "dsa.msc"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: dsa.msc")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_domini_e_trust_active_directory():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "domain.msc"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: domain.msc")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_siti_e_servizi_active_directory():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "dssite.msc"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: dssite.msc")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_servizi_componenti_dcom():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "dcomcnfg.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: dcomcnfg.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_origini_dati_odbc_64_bit():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "odbcad64.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: odbcad64.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_interfaccia_utente_stampante():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "printui.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: printui.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_installazione_pacchetti_lingua_mui():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "lpksetup.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: lpksetup.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_wmi_object_browser_tester():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "wbemtest.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: wbemtest.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_registrazione_dll_e_activex():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "regsvr32.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: regsvr32.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_iexpress_wizard_creazione_installer():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "iexpress.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: iexpress.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_utility_certificati_e_hash_file():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "certutil.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: certutil.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_compilatore_mof_wmi():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "mofcomp.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: mofcomp.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_filter_manager_control():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "fltmc.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: fltmc.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_mixer_volume_classico():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "sndvol.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: sndvol.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_check_disk_riparazione_disco():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "chkdsk.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: chkdsk.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_deframmentazione_e_ottimizzazione():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "defrag.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: defrag.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_partizionamento_dischi_riga_comando():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "diskpart.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: diskpart.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_file_system_utility_parametri_ntfs():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "fsutil.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: fsutil.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_cifratura_ntfs_cipher():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "cipher.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: cipher.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_gestore_copie_shadow_volume():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "vssadmin.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: vssadmin.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_system_file_checker_sfc_scannow():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "sfc.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: sfc.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_deployment_image_servicing_dism():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "dism.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: dism.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_diagnostica_memoria_ram_mdsched():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "mdsched.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: mdsched.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_arresto_spegnimento_sistema():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "shutdown.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: shutdown.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_disconnessione_utente_logoff():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "logoff.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: logoff.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_scollega_sessione_corrente():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "tsdiscon.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: tsdiscon.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_generazione_report_batteria_html():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "powercfg.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: powercfg.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_diagnostica_sospensione_sleepstudy():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "powercfg.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: powercfg.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_riga_comando_windows_defender():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "MpCmdRun.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: MpCmdRun.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_icona_area_notifica_sicurezza():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "SecurityHealthSystray.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: SecurityHealthSystray.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_installatore_definizioni_malware():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "MpSigStub.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: MpSigStub.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_gestione_bitlocker_riga_comando():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "manage-bde.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: manage-bde.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_ripristino_emergenza_bitlocker():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "repair-bde.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: repair-bde.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_gestione_completa_driver_pnputil():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "pnputil.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: pnputil.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_windows_subsystem_for_linux_wsl():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "wsl.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: wsl.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_gestione_macchine_virtuali_hyper_v():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "virtmgmt.msc"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: virtmgmt.msc")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_windows_sandbox():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "WindowsSandbox.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: WindowsSandbox.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_ripristino_cache_microsoft_store():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "wsreset.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: wsreset.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_update_session_orchestrator_client():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "usoclient.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: usoclient.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_gestione_log_eventi_wevtutil():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "wevtutil.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: wevtutil.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_windows_installer_cleanup_utility():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "msiexec.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: msiexec.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_editor_dell_editor_dei_metodi_di_input_ime():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "imepad.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: imepad.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_visualizzatore_clipboard_di_sistema():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "clipbrd.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: clipbrd.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_utility_di_configurazione_del_carattere_privato():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "eudcedit.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: eudcedit.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_procedura_autenticazione_avanzata_netplwiz():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "netplwiz.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: netplwiz.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_verifica_driver_di_terze_parti_sigverif():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "sigverif.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: sigverif.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_gestione_del_provider_di_stampe():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "localspl.dll"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: localspl.dll")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_utility_controllo_driver_di_filtro_rete():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "netcfg.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: netcfg.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_monitoraggio_attivita_di_rete_ip():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "pktmon.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: pktmon.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_configurazione_componenti_com_locali():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "comexp.msc"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: comexp.msc")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_strumento_diagnostica_supporto_microsoft_msdt():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "msdt.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: msdt.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_verifica_integrita_pacchetti_appx():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "appxsysprep.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: appxsysprep.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_utility_di_migrazione_stato_utente_usmt():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "scanstate.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: scanstate.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_strumento_applicazione_immagini_wim():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "imagex.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: imagex.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_gestione_componenti_servizi_windows_dism():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "dism.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: dism.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_utility_di_sincronizzazione_ora_di_rete_w32tm():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "w32tm.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: w32tm.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_visualizzatore_dello_stato_delle_licenze_slmgr():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "slmgr.vbs"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: slmgr.vbs")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_gestore_dei_criteri_di_indicizzazione():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "searchindexingconfig.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: searchindexingconfig.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_strumento_di_rimozione_appx_preinstallate():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "remove-appxpackage.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: remove-appxpackage.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_interprete_script_console_nativo():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "cscript.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: cscript.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_generatore_pacchetti_di_provisioning_windows():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "icd.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: icd.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_strumento_di_diagnostica_audio_di_rete():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/IM", "audiodg.exe"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: audiodg.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

#-----------------------------------
# FUNZIONI DI TERMINAZIONE FORZATA (kill)
#-----------------------------------
def termina_forzatamente_blocco_note():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "notepad.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: notepad.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_calcolatrice():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "calc.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: calc.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_paint():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "mspaint.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: mspaint.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_wordpad():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "write.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: write.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_strumento_per_screenshot():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "snippingtool.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: snippingtool.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_registrazoni_azioni_utente():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "psr.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: psr.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_mappa_caratteri():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "charmap.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: charmap.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_connessione_ytelefonica_guidatra():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "dialer.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: dialer.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_esplora_file():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "explorer.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: explorer.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_gestione_attivita():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "taskmgr.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: taskmgr.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_cmd():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "cmd.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: cmd.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_powershell():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "powershell.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: powershell.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_registro_di_sistema():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "regedit.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: regedit.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_pannello_di_controllo():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "control.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: control.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_informazioni_sistema():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "msinfo32.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: msinfo32.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_microsoft_management_console():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "mmc.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: mmc.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_pulizia_disco():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "cleanmgr.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: cleanmgr.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_ripristino_conf_di_sistema():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "rstrui.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: rstrui.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_utilita_di_pianificazione():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "taskschd.msc"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: taskschd.msc")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_visualizzatore_eventi():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "eventvwr.msc"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: eventvwr.msc")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_gestione_servizi():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "services.msc"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: services.msc")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_gestione_dispositivi():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "devmgmt.msc"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: devmgmt.msc")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_gestione_dischi():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "diskmgmt.msc"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: diskmgmt.msc")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_gestione_pc():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "compmgmt.msc"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: compmgmt.msc")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_gestione_stampa():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "printmanagement.msc"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: printmanagement.msc")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_strumento_diagnostica_directx():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "dxdiag.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: dxdiag.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_centro_sincronizzazione_periferiche():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "mobsync.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: mobsync.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_connessione_desktop_remoto():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "mstsc.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: mstsc.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_inizializzatore_iscsi():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "iscsicpl.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: iscsicpl.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_windows_firewall_avanzato():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "wf.msc"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: wf.msc")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_opzioni_telefono_e_modem():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "telephon.cpl"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: telephon.cpl")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_note_adesive_classiche():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "stikynot.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: stikynot.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_monitoraggio_affidabilita_e_performance():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "perfmon.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: perfmon.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_monitoraggio_risorse():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "resmon.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: resmon.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_configurazione_di_sistema_msconfig():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "msconfig.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: msconfig.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_verifica_firma_file():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "sigverif.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: sigverif.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_driver_verifier_manager():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "verifier.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: verifier.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_informazioni_versione_windows():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "winver.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: winver.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_strumento_rimozione_malware_microsoft():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "mrt.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: mrt.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_backup_e_ripristino_credenziali():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "credwiz.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: credwiz.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_criteri_di_sicurezza_locali():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "secpol.msc"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: secpol.msc")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_editor_dei_criteri_di_gruppo_locali():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "gpedit.msc"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: gpedit.msc")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_programmi_e_funzionalita_disinstalla():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "appwiz.cpl"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: appwiz.cpl")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_impostazioni_schermo_classiche():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "desk.cpl"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: desk.cpl")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_proprieta_del_mouse():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "main.cpl"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: main.cpl")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_impostazioni_audio_suoni():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "mmsys.cpl"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: mmsys.cpl")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_proprieta_del_sistema_variabili_ambiente():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "sysdm.cpl"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: sysdm.cpl")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_impostazioni_data_e_ora():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "timedate.cpl"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: timedate.cpl")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_opzioni_risparmio_energia():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "powercfg.cpl"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: powercfg.cpl")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_opzioni_internazionali_e_lingua():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "intl.cpl"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: intl.cpl")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_installazione_guidata_hardware_legacy():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "hdwwiz.cpl"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: hdwwiz.cpl")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_proprieta_internet():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "inetcpl.cpl"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: inetcpl.cpl")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_periferiche_di_gioco_controller():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "joy.cpl"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: joy.cpl")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_centro_accessibilita_classico():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "access.cpl"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: access.cpl")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_impostazioni_generali():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "ms-settings:"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: ms-settings:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_windows_update():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "ms-settings:windowsupdate"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: ms-settings:windowsupdate")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_stato_della_rete_e_wi_fi():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "ms-settings:network"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: ms-settings:network")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_gestione_dispositivi_bluetooth():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "ms-settings:bluetooth"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: ms-settings:bluetooth")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_impostazioni_schermo_moderne():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "ms-settings:display"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: ms-settings:display")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_gestione_notifiche():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "ms-settings:notifications"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: ms-settings:notifications")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_elenco_app_installate():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "ms-settings:appsfeatures"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: ms-settings:appsfeatures")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_applicazioni_predefinite():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "ms-settings:defaultapps"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: ms-settings:defaultapps")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_personalizzazione_e_sfondi():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "ms-settings:personalization"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: ms-settings:personalization")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_gestione_dei_temi():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "ms-settings:themes"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: ms-settings:themes")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_schermata_di_blocco():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "ms-settings:lockscreen"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: ms-settings:lockscreen")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_data_e_ora_moderne():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "ms-settings:dateandtime"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: ms-settings:dateandtime")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_lingua_e_area_geografica():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "ms-settings:regionlanguage"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: ms-settings:regionlanguage")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_privacy_generale():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "ms-settings:privacy"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: ms-settings:privacy")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_autorizzazioni_webcam():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "ms-settings:privacy-webcam"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: ms-settings:privacy-webcam")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_autorizzazioni_microfono():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "ms-settings:privacy-microfone"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: ms-settings:privacy-microfone")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_sicurezza_di_windows_defender():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "ms-settings:windowsdefender"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: ms-settings:windowsdefender")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_opzioni_di_ripristino_recovery():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "ms-settings:recovery"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: ms-settings:recovery")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_impostazioni_sviluppatori():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "ms-settings:developers"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: ms-settings:developers")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_informazioni_sul_sistema_moderne():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "ms-settings:about"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: ms-settings:about")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_orologio_sveglie_e_timer():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "ms-clock:"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: ms-clock:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_calendario_di_windows():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "outlookcal:"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: outlookcal:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_posta_di_windows():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "outlookmail:"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: outlookmail:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_note_adesive_moderne():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "ms-stickynotes:"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: ms-stickynotes:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_calcolatrice_moderna():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "ms-calculator:"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: ms-calculator:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_microsoft_whiteboard():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "ms-whiteboard:"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: ms-whiteboard:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_microsoft_to_do():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "ms-todo:"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: ms-todo:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_foto_di_windows():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "ms-photos:"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: ms-photos:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_film_e_tv():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "mswindowsvideo:"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: mswindowsvideo:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_microsoft_store():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "ms-windows-store:"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: ms-windows-store:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_meteo_di_windows():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "bingweather:"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: bingweather:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_microsoft_news():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "bingnews:"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: bingnews:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_nuovo_paint_moderno_paint_3d():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "ms-paint:"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: ms-paint:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_nuovo_media_player():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "ms-mediaplayer:"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: ms-mediaplayer:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_microsoft_edge():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "microsoft-edge:"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: microsoft-edge:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_richiesta_supporto():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "ms-contact-support:"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: ms-contact-support:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_centro_assistenza_get_help():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "ms-get-help:"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: ms-get-help:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_contatti_di_windows():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "ms-people:"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: ms-people:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_cattura_e_annota_screenshot():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "ms-screenclip:"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: ms-screenclip:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_app_xbox():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "xbox:"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: xbox:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_xbox_game_bar():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "ms-gamebar:"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: ms-gamebar:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_google_chrome():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "chrome.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: chrome.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_mozilla_firefox():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "firefox.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: firefox.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_brave_browser():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "brave.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: brave.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_opera_browser():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "opera.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: opera.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_vivaldi_browser():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "vivaldi.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: vivaldi.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_discord():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "discord:"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: discord:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_whatsapp_desktop():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "whatsapp:"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: whatsapp:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_telegram_desktop():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "tg:"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: tg:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_slack():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "slack:"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: slack:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_microsoft_teams():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "teams:"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: teams:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_zoom_meetings():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "zoommtg:"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: zoommtg:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_skype():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "skype:"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: skype:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_spotify():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "spotify:"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: spotify:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_microsoft_word():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "winword.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: winword.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_microsoft_excel():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "excel.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: excel.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_microsoft_powerpoint():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "powerpnt.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: powerpnt.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_microsoft_outlook():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "outlook.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: outlook.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_microsoft_onenote():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "onenote.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: onenote.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_valve_steam():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "steam:"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: steam:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_epic_games_launcher():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "com.epicgames.launcher:"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: com.epicgames.launcher:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_ea_app():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "ea:"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: ea:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_ubisoft_connect():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "ubisoftconnect:"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: ubisoftconnect:")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_visual_studio_code():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "code.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: code.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_vlc_media_player():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "vlc.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: vlc.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_adobe_photoshop():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "photoshop.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: photoshop.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_gimp():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "gimp.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: gimp.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_blender():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "blender.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: blender.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_winrar():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "winrar.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: winrar.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_7_zip_file_manager():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "7zFM.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: 7zFM.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_obs_studio():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "obs.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: obs.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_notepad():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "notepad++.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: notepad++.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_utenti_e_computer_active_directory():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "dsa.msc"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: dsa.msc")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_domini_e_trust_active_directory():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "domain.msc"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: domain.msc")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_siti_e_servizi_active_directory():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "dssite.msc"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: dssite.msc")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_servizi_componenti_dcom():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "dcomcnfg.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: dcomcnfg.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_origini_dati_odbc_64_bit():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "odbcad64.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: odbcad64.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_interfaccia_utente_stampante():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "printui.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: printui.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_installazione_pacchetti_lingua_mui():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "lpksetup.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: lpksetup.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_wmi_object_browser_tester():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "wbemtest.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: wbemtest.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_registrazione_dll_e_activex():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "regsvr32.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: regsvr32.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_iexpress_wizard_creazione_installer():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "iexpress.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: iexpress.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_utility_certificati_e_hash_file():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "certutil.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: certutil.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_compilatore_mof_wmi():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "mofcomp.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: mofcomp.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_filter_manager_control():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "fltmc.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: fltmc.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_mixer_volume_classico():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "sndvol.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: sndvol.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_check_disk_riparazione_disco():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "chkdsk.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: chkdsk.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_deframmentazione_e_ottimizzazione():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "defrag.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: defrag.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_partizionamento_dischi_riga_comando():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "diskpart.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: diskpart.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_file_system_utility_parametri_ntfs():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "fsutil.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: fsutil.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_cifratura_ntfs_cipher():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "cipher.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: cipher.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_gestore_copie_shadow_volume():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "vssadmin.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: vssadmin.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_system_file_checker_sfc_scannow():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "sfc.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: sfc.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_deployment_image_servicing_dism():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "dism.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: dism.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_diagnostica_memoria_ram_mdsched():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "mdsched.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: mdsched.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_arresto_spegnimento_sistema():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "shutdown.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: shutdown.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_disconnessione_utente_logoff():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "logoff.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: logoff.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_scollega_sessione_corrente():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "tsdiscon.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: tsdiscon.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_generazione_report_batteria_html():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "powercfg.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: powercfg.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_diagnostica_sospensione_sleepstudy():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "powercfg.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: powercfg.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_riga_comando_windows_defender():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "MpCmdRun.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: MpCmdRun.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_icona_area_notifica_sicurezza():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "SecurityHealthSystray.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: SecurityHealthSystray.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_installatore_definizioni_malware():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "MpSigStub.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: MpSigStub.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_gestione_bitlocker_riga_comando():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "manage-bde.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: manage-bde.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_ripristino_emergenza_bitlocker():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "repair-bde.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: repair-bde.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_gestione_completa_driver_pnputil():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "pnputil.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: pnputil.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_windows_subsystem_for_linux_wsl():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "wsl.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: wsl.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_gestione_macchine_virtuali_hyper_v():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "virtmgmt.msc"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: virtmgmt.msc")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_windows_sandbox():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "WindowsSandbox.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: WindowsSandbox.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_ripristino_cache_microsoft_store():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "wsreset.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: wsreset.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_update_session_orchestrator_client():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "usoclient.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: usoclient.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_gestione_log_eventi_wevtutil():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "wevtutil.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: wevtutil.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_windows_installer_cleanup_utility():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "msiexec.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: msiexec.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_editor_dell_editor_dei_metodi_di_input_ime():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "imepad.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: imepad.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_visualizzatore_clipboard_di_sistema():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "clipbrd.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: clipbrd.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_utility_di_configurazione_del_carattere_privato():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "eudcedit.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: eudcedit.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_procedura_autenticazione_avanzata_netplwiz():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "netplwiz.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: netplwiz.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_verifica_driver_di_terze_parti_sigverif():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "sigverif.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: sigverif.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_gestione_del_provider_di_stampe():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "localspl.dll"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: localspl.dll")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_utility_controllo_driver_di_filtro_rete():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "netcfg.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: netcfg.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_monitoraggio_attivita_di_rete_ip():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "pktmon.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: pktmon.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_configurazione_componenti_com_locali():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "comexp.msc"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: comexp.msc")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_strumento_diagnostica_supporto_microsoft_msdt():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "msdt.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: msdt.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_verifica_integrita_pacchetti_appx():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "appxsysprep.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: appxsysprep.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_utility_di_migrazione_stato_utente_usmt():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "scanstate.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: scanstate.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_strumento_applicazione_immagini_wim():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "imagex.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: imagex.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_gestione_componenti_servizi_windows_dism():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "dism.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: dism.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_utility_di_sincronizzazione_ora_di_rete_w32tm():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "w32tm.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: w32tm.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_visualizzatore_dello_stato_delle_licenze_slmgr():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "slmgr.vbs"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: slmgr.vbs")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_gestore_dei_criteri_di_indicizzazione():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "searchindexingconfig.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: searchindexingconfig.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_strumento_di_rimozione_appx_preinstallate():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "remove-appxpackage.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: remove-appxpackage.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_interprete_script_console_nativo():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "cscript.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: cscript.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_generatore_pacchetti_di_provisioning_windows():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "icd.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: icd.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_strumento_di_diagnostica_audio_di_rete():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["taskkill", "/F", "/IM", "audiodg.exe"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: audiodg.exe")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")




#-----------------------------------
# FUNZIONI PER APP GENERALI LINUX (MULTI-DISTRO) - set curato, non esaustivo
#-----------------------------------
def apri_gestore_file_nautilus_files():
    subprocess.Popen("nautilus", shell=True)

def apri_terminale_gnome():
    subprocess.Popen("gnome-terminal", shell=True)

def apri_terminale_universale_xterm():
    subprocess.Popen("xterm", shell=True)

def apri_editor_di_testo_gedit():
    subprocess.Popen("gedit", shell=True)

def apri_calcolatrice_gnome():
    subprocess.Popen("gnome-calculator", shell=True)

def apri_visualizzatore_immagini_eye_of_gnome():
    subprocess.Popen("eog", shell=True)

def apri_visualizzatore_pdf_evince():
    subprocess.Popen("evince", shell=True)

def apri_gestore_archivi_file_roller():
    subprocess.Popen("file-roller", shell=True)

def apri_monitor_di_sistema_gnome():
    subprocess.Popen("gnome-system-monitor", shell=True)

def apri_impostazioni_di_sistema_gnome():
    subprocess.Popen("gnome-control-center", shell=True)

def apri_centro_software_gnome():
    subprocess.Popen("gnome-software", shell=True)

def apri_analizzatore_utilizzo_disco_baobab():
    subprocess.Popen("baobab", shell=True)

def apri_strumento_di_cattura_schermo_gnome():
    subprocess.Popen("gnome-screenshot", shell=True)

def apri_editor_connessioni_di_rete():
    subprocess.Popen("nm-connection-editor", shell=True)

def apri_libreoffice_writer():
    subprocess.Popen("libreoffice --writer", shell=True)

def apri_libreoffice_calc():
    subprocess.Popen("libreoffice --calc", shell=True)

def apri_libreoffice_impress():
    subprocess.Popen("libreoffice --impress", shell=True)

def apri_gparted_partizionamento_dischi():
    subprocess.Popen("gparted", shell=True)

def apri_lettore_musicale_rhythmbox():
    subprocess.Popen("rhythmbox", shell=True)

def apri_lettore_video_totem():
    subprocess.Popen("totem", shell=True)

def apri_app_webcam_cheese():
    subprocess.Popen("cheese", shell=True)

def apri_portachiavi_e_password_seahorse():
    subprocess.Popen("seahorse", shell=True)

def apri_visualizzatore_font_gnome():
    subprocess.Popen("gnome-font-viewer", shell=True)

def apri_utility_dischi_gnome():
    subprocess.Popen("gnome-disks", shell=True)

def apri_client_torrent_transmission():
    subprocess.Popen("transmission-gtk", shell=True)

def apri_gestore_macchine_virtuali_virt_manager():
    subprocess.Popen("virt-manager", shell=True)

def apri_gnome_tweaks():
    subprocess.Popen("gnome-tweaks", shell=True)

def apri_caratteri_speciali_gnome():
    subprocess.Popen("gnome-characters", shell=True)

def apri_orologio_gnome():
    subprocess.Popen("gnome-clocks", shell=True)

def apri_meteo_gnome():
    subprocess.Popen("gnome-weather", shell=True)

#-----------------------------------
# TERMINAZIONE APP LINUX (pkill)
#-----------------------------------
def termina_gestore_file_nautilus_files():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "nautilus"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: nautilus")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_terminale_gnome():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "gnome-terminal"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: gnome-terminal")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_terminale_universale_xterm():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "xterm"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: xterm")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_editor_di_testo_gedit():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "gedit"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: gedit")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_calcolatrice_gnome():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "gnome-calculator"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: gnome-calculator")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_visualizzatore_immagini_eye_of_gnome():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "eog"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: eog")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_visualizzatore_pdf_evince():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "evince"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: evince")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_gestore_archivi_file_roller():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "file-roller"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: file-roller")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_monitor_di_sistema_gnome():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "gnome-system-monitor"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: gnome-system-monitor")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_impostazioni_di_sistema_gnome():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "gnome-control-center"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: gnome-control-center")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_centro_software_gnome():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "gnome-software"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: gnome-software")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_analizzatore_utilizzo_disco_baobab():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "baobab"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: baobab")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_strumento_di_cattura_schermo_gnome():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "gnome-screenshot"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: gnome-screenshot")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_editor_connessioni_di_rete():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "nm-connection-editor"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: nm-connection-editor")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_libreoffice_writer():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "libreoffice"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: libreoffice")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_libreoffice_calc():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "libreoffice"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: libreoffice")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_libreoffice_impress():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "libreoffice"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: libreoffice")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_gparted_partizionamento_dischi():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "gparted"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: gparted")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_lettore_musicale_rhythmbox():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "rhythmbox"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: rhythmbox")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_lettore_video_totem():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "totem"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: totem")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_app_webcam_cheese():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "cheese"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: cheese")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_portachiavi_e_password_seahorse():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "seahorse"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: seahorse")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_visualizzatore_font_gnome():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "gnome-font-viewer"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: gnome-font-viewer")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_utility_dischi_gnome():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "gnome-disks"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: gnome-disks")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_client_torrent_transmission():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "transmission-gtk"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: transmission-gtk")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_gestore_macchine_virtuali_virt_manager():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "virt-manager"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: virt-manager")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_gnome_tweaks():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "gnome-tweaks"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: gnome-tweaks")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_caratteri_speciali_gnome():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "gnome-characters"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: gnome-characters")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_orologio_gnome():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "gnome-clocks"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: gnome-clocks")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_meteo_gnome():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "gnome-weather"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: gnome-weather")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

#-----------------------------------
# TERMINAZIONE FORZATA APP LINUX (pkill -9)
#-----------------------------------
def termina_forzatamente_gestore_file_nautilus_files():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "-9", "nautilus"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: nautilus")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_terminale_gnome():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "-9", "gnome-terminal"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: gnome-terminal")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_terminale_universale_xterm():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "-9", "xterm"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: xterm")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_editor_di_testo_gedit():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "-9", "gedit"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: gedit")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_calcolatrice_gnome():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "-9", "gnome-calculator"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: gnome-calculator")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_visualizzatore_immagini_eye_of_gnome():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "-9", "eog"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: eog")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_visualizzatore_pdf_evince():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "-9", "evince"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: evince")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_gestore_archivi_file_roller():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "-9", "file-roller"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: file-roller")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_monitor_di_sistema_gnome():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "-9", "gnome-system-monitor"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: gnome-system-monitor")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_impostazioni_di_sistema_gnome():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "-9", "gnome-control-center"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: gnome-control-center")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_centro_software_gnome():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "-9", "gnome-software"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: gnome-software")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_analizzatore_utilizzo_disco_baobab():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "-9", "baobab"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: baobab")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_strumento_di_cattura_schermo_gnome():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "-9", "gnome-screenshot"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: gnome-screenshot")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_editor_connessioni_di_rete():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "-9", "nm-connection-editor"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: nm-connection-editor")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_libreoffice_writer():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "-9", "libreoffice"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: libreoffice")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_libreoffice_calc():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "-9", "libreoffice"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: libreoffice")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_libreoffice_impress():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "-9", "libreoffice"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: libreoffice")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_gparted_partizionamento_dischi():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "-9", "gparted"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: gparted")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_lettore_musicale_rhythmbox():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "-9", "rhythmbox"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: rhythmbox")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_lettore_video_totem():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "-9", "totem"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: totem")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_app_webcam_cheese():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "-9", "cheese"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: cheese")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_portachiavi_e_password_seahorse():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "-9", "seahorse"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: seahorse")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_visualizzatore_font_gnome():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "-9", "gnome-font-viewer"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: gnome-font-viewer")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_utility_dischi_gnome():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "-9", "gnome-disks"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: gnome-disks")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_client_torrent_transmission():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "-9", "transmission-gtk"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: transmission-gtk")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_gestore_macchine_virtuali_virt_manager():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "-9", "virt-manager"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: virt-manager")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_gnome_tweaks():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "-9", "gnome-tweaks"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: gnome-tweaks")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_caratteri_speciali_gnome():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "-9", "gnome-characters"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: gnome-characters")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_orologio_gnome():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "-9", "gnome-clocks"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: gnome-clocks")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_meteo_gnome():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["pkill", "-9", "gnome-weather"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: gnome-weather")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")


#-----------------------------------
# FUNZIONI PER APP MACOS (NATIVE + TERZE PARTI COMUNI)
# apertura: open -a "Nome App"  |  terminazione: killall "Nome Processo"
#-----------------------------------
def apri_pages_macos():
    subprocess.Popen(["open", "-a", "Pages"])

def apri_numbers_macos():
    subprocess.Popen(["open", "-a", "Numbers"])

def apri_keynote_macos():
    subprocess.Popen(["open", "-a", "Keynote"])

def apri_textedit_macos():
    subprocess.Popen(["open", "-a", "TextEdit"])

def apri_anteprima_preview_macos():
    subprocess.Popen(["open", "-a", "Preview"])

def apri_calcolatrice_macos():
    subprocess.Popen(["open", "-a", "Calculator"])

def apri_calendario_macos():
    subprocess.Popen(["open", "-a", "Calendar"])

def apri_contatti_macos():
    subprocess.Popen(["open", "-a", "Contacts"])

def apri_note_macos():
    subprocess.Popen(["open", "-a", "Notes"])

def apri_promemoria_macos():
    subprocess.Popen(["open", "-a", "Reminders"])

def apri_note_adesive_stickies_macos():
    subprocess.Popen(["open", "-a", "Stickies"])

def apri_automator_macos():
    subprocess.Popen(["open", "-a", "Automator"])

def apri_editor_di_script_script_editor_macos():
    subprocess.Popen(["open", "-a", "Script Editor"])

def apri_comandi_rapidi_shortcuts_macos():
    subprocess.Popen(["open", "-a", "Shortcuts"])

def apri_freeform_macos():
    subprocess.Popen(["open", "-a", "Freeform"])

def apri_dizionario_macos():
    subprocess.Popen(["open", "-a", "Dictionary"])

def apri_libro_font_font_book_macos():
    subprocess.Popen(["open", "-a", "Font Book"])

def apri_terminale_macos():
    subprocess.Popen(["open", "-a", "Terminal"])

def apri_monitoraggio_attivita_macos():
    subprocess.Popen(["open", "-a", "Activity Monitor"])

def apri_console_macos():
    subprocess.Popen(["open", "-a", "Console"])

def apri_utility_disco_macos():
    subprocess.Popen(["open", "-a", "Disk Utility"])

def apri_informazioni_di_sistema_macos():
    subprocess.Popen(["open", "-a", "System Information"])

def apri_assistente_migrazione_macos():
    subprocess.Popen(["open", "-a", "Migration Assistant"])

def apri_accesso_portachiavi_keychain_access_macos():
    subprocess.Popen(["open", "-a", "Keychain Access"])

def apri_screenshot_macos():
    subprocess.Popen(["open", "-a", "Screenshot"])

def apri_condivisione_schermo_macos():
    subprocess.Popen(["open", "-a", "Screen Sharing"])

def apri_misuratore_colore_digitale_macos():
    subprocess.Popen(["open", "-a", "Digital Color Meter"])

def apri_grapher_macos():
    subprocess.Popen(["open", "-a", "Grapher"])

def apri_scambio_file_bluetooth_macos():
    subprocess.Popen(["open", "-a", "Bluetooth File Exchange"])

def apri_configurazione_audio_midi_macos():
    subprocess.Popen(["open", "-a", "Audio MIDI Setup"])

def apri_utility_colorsync_macos():
    subprocess.Popen(["open", "-a", "ColorSync Utility"])

def apri_utility_airport_macos():
    subprocess.Popen(["open", "-a", "AirPort Utility"])

def apri_assistente_boot_camp_macos():
    subprocess.Popen(["open", "-a", "Boot Camp Assistant"])

def apri_utility_voiceover_macos():
    subprocess.Popen(["open", "-a", "VoiceOver Utility"])

def apri_diagnostica_wireless_macos():
    subprocess.Popen(["open", "-a", "Wireless Diagnostics"])

def apri_time_machine_macos():
    subprocess.Popen(["open", "-a", "Time Machine"])

def apri_impostazioni_di_sistema_macos():
    subprocess.Popen(["open", "-a", "System Settings"])

def apri_finder_macos():
    subprocess.Popen(["open", "-a", "Finder"])

def apri_launchpad_macos():
    subprocess.Popen(["open", "-a", "Launchpad"])

def apri_mission_control_macos():
    subprocess.Popen(["open", "-a", "Mission Control"])

def apri_siri_macos():
    subprocess.Popen(["open", "-a", "Siri"])

def apri_acquisizione_immagini_image_capture_macos():
    subprocess.Popen(["open", "-a", "Image Capture"])

def apri_app_store_macos():
    subprocess.Popen(["open", "-a", "App Store"])

def apri_safari_macos():
    subprocess.Popen(["open", "-a", "Safari"])

def apri_mail_macos():
    subprocess.Popen(["open", "-a", "Mail"])

def apri_messaggi_macos():
    subprocess.Popen(["open", "-a", "Messages"])

def apri_facetime_macos():
    subprocess.Popen(["open", "-a", "FaceTime"])

def apri_dov_e_find_my_macos():
    subprocess.Popen(["open", "-a", "Find My"])

def apri_mappe_macos():
    subprocess.Popen(["open", "-a", "Maps"])

def apri_casa_home_macos():
    subprocess.Popen(["open", "-a", "Home"])

def apri_google_chrome_macos():
    subprocess.Popen(["open", "-a", "Google Chrome"])

def apri_mozilla_firefox_macos():
    subprocess.Popen(["open", "-a", "Firefox"])

def apri_microsoft_edge_macos():
    subprocess.Popen(["open", "-a", "Microsoft Edge"])

def apri_opera_macos():
    subprocess.Popen(["open", "-a", "Opera"])

def apri_brave_browser_macos():
    subprocess.Popen(["open", "-a", "Brave Browser"])

def apri_slack_macos():
    subprocess.Popen(["open", "-a", "Slack"])

def apri_zoom_macos():
    subprocess.Popen(["open", "-a", "zoom.us"])

def apri_microsoft_teams_macos():
    subprocess.Popen(["open", "-a", "Microsoft Teams"])

def apri_discord_macos():
    subprocess.Popen(["open", "-a", "Discord"])

def apri_whatsapp_macos():
    subprocess.Popen(["open", "-a", "WhatsApp"])

def apri_telegram_macos():
    subprocess.Popen(["open", "-a", "Telegram"])

def apri_skype_macos():
    subprocess.Popen(["open", "-a", "Skype"])

def apri_musica_music_macos():
    subprocess.Popen(["open", "-a", "Music"])

def apri_tv_macos():
    subprocess.Popen(["open", "-a", "TV"])

def apri_podcast_macos():
    subprocess.Popen(["open", "-a", "Podcasts"])

def apri_foto_photos_macos():
    subprocess.Popen(["open", "-a", "Photos"])

def apri_photo_booth_macos():
    subprocess.Popen(["open", "-a", "Photo Booth"])

def apri_quicktime_player_macos():
    subprocess.Popen(["open", "-a", "QuickTime Player"])

def apri_promemoria_vocali_voice_memos_macos():
    subprocess.Popen(["open", "-a", "Voice Memos"])

def apri_news_macos():
    subprocess.Popen(["open", "-a", "News"])

def apri_libri_books_macos():
    subprocess.Popen(["open", "-a", "Books"])

def apri_borsa_stocks_macos():
    subprocess.Popen(["open", "-a", "Stocks"])

def apri_scacchi_chess_macos():
    subprocess.Popen(["open", "-a", "Chess"])

def apri_orologio_clock_macos():
    subprocess.Popen(["open", "-a", "Clock"])

def apri_spotify_macos():
    subprocess.Popen(["open", "-a", "Spotify"])

def apri_vlc_macos():
    subprocess.Popen(["open", "-a", "VLC"])

def apri_iina_macos():
    subprocess.Popen(["open", "-a", "IINA"])

def apri_garageband_macos():
    subprocess.Popen(["open", "-a", "GarageBand"])

def apri_imovie_macos():
    subprocess.Popen(["open", "-a", "iMovie"])

def apri_xcode_macos():
    subprocess.Popen(["open", "-a", "Xcode"])

def apri_visual_studio_code_macos():
    subprocess.Popen(["open", "-a", "Visual Studio Code"])

def apri_sublime_text_macos():
    subprocess.Popen(["open", "-a", "Sublime Text"])

def apri_iterm2_macos():
    subprocess.Popen(["open", "-a", "iTerm"])

def apri_docker_desktop_macos():
    subprocess.Popen(["open", "-a", "Docker"])

def apri_adobe_photoshop_macos():
    subprocess.Popen(["open", "-a", "Adobe Photoshop 2024"])

def apri_adobe_illustrator_macos():
    subprocess.Popen(["open", "-a", "Adobe Illustrator"])

def apri_gimp_macos():
    subprocess.Popen(["open", "-a", "GIMP"])

def apri_blender_macos():
    subprocess.Popen(["open", "-a", "Blender"])

def apri_obs_studio_macos():
    subprocess.Popen(["open", "-a", "OBS"])

def apri_sketch_macos():
    subprocess.Popen(["open", "-a", "Sketch"])

def apri_figma_macos():
    subprocess.Popen(["open", "-a", "Figma"])

def apri_microsoft_word_macos():
    subprocess.Popen(["open", "-a", "Microsoft Word"])

def apri_microsoft_excel_macos():
    subprocess.Popen(["open", "-a", "Microsoft Excel"])

def apri_microsoft_powerpoint_macos():
    subprocess.Popen(["open", "-a", "Microsoft PowerPoint"])

def apri_microsoft_outlook_macos():
    subprocess.Popen(["open", "-a", "Microsoft Outlook"])

def apri_microsoft_onenote_macos():
    subprocess.Popen(["open", "-a", "Microsoft OneNote"])

def apri_notion_macos():
    subprocess.Popen(["open", "-a", "Notion"])

def apri_evernote_macos():
    subprocess.Popen(["open", "-a", "Evernote"])

def apri_1password_macos():
    subprocess.Popen(["open", "-a", "1Password"])

def apri_cleanmymac_x_macos():
    subprocess.Popen(["open", "-a", "CleanMyMac X"])

def apri_steam_macos():
    subprocess.Popen(["open", "-a", "Steam"])

def apri_epic_games_launcher_macos():
    subprocess.Popen(["open", "-a", "Epic Games Launcher"])

def apri_battle_net_macos():
    subprocess.Popen(["open", "-a", "Battle.net"])

def apri_parallels_desktop_macos():
    subprocess.Popen(["open", "-a", "Parallels Desktop"])

def apri_vmware_fusion_macos():
    subprocess.Popen(["open", "-a", "VMware Fusion"])

def apri_transmission_macos():
    subprocess.Popen(["open", "-a", "Transmission"])

def apri_the_unarchiver_macos():
    subprocess.Popen(["open", "-a", "The Unarchiver"])

def apri_keka_macos():
    subprocess.Popen(["open", "-a", "Keka"])

#-----------------------------------
# TERMINAZIONE APP MACOS (killall)
#-----------------------------------
def termina_pages_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Pages"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Pages")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_numbers_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Numbers"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Numbers")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_keynote_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Keynote"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Keynote")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_textedit_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "TextEdit"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: TextEdit")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_anteprima_preview_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Preview"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Preview")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_calcolatrice_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Calculator"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Calculator")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_calendario_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Calendar"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Calendar")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_contatti_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Contacts"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Contacts")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_note_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Notes"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Notes")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_promemoria_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Reminders"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Reminders")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_note_adesive_stickies_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Stickies"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Stickies")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_automator_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Automator"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Automator")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_editor_di_script_script_editor_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Script Editor"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Script Editor")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_comandi_rapidi_shortcuts_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Shortcuts"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Shortcuts")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_freeform_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Freeform"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Freeform")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_dizionario_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Dictionary"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Dictionary")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_libro_font_font_book_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Font Book"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Font Book")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_terminale_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Terminal"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Terminal")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_monitoraggio_attivita_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Activity Monitor"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Activity Monitor")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_console_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Console"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Console")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_utility_disco_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Disk Utility"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Disk Utility")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_informazioni_di_sistema_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "System Information"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: System Information")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_assistente_migrazione_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Migration Assistant"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Migration Assistant")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_accesso_portachiavi_keychain_access_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Keychain Access"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Keychain Access")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_screenshot_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Screenshot"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Screenshot")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_condivisione_schermo_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Screen Sharing"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Screen Sharing")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_misuratore_colore_digitale_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Digital Color Meter"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Digital Color Meter")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_grapher_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Grapher"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Grapher")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_scambio_file_bluetooth_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Bluetooth File Exchange"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Bluetooth File Exchange")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_configurazione_audio_midi_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Audio MIDI Setup"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Audio MIDI Setup")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_utility_colorsync_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "ColorSync Utility"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: ColorSync Utility")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_utility_airport_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "AirPort Utility"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: AirPort Utility")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_assistente_boot_camp_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Boot Camp Assistant"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Boot Camp Assistant")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_utility_voiceover_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "VoiceOver Utility"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: VoiceOver Utility")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_diagnostica_wireless_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Wireless Diagnostics"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Wireless Diagnostics")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_time_machine_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Time Machine"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Time Machine")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_impostazioni_di_sistema_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "System Settings"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: System Settings")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_finder_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Finder"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Finder")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_launchpad_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Launchpad"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Launchpad")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_mission_control_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Mission Control"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Mission Control")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_siri_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Siri"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Siri")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_acquisizione_immagini_image_capture_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Image Capture"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Image Capture")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_app_store_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "App Store"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: App Store")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_safari_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Safari"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Safari")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_mail_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Mail"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Mail")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_messaggi_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Messages"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Messages")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_facetime_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "FaceTime"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: FaceTime")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_dov_e_find_my_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Find My"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Find My")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_mappe_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Maps"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Maps")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_casa_home_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Home"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Home")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_google_chrome_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Google Chrome"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Google Chrome")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_mozilla_firefox_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Firefox"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Firefox")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_microsoft_edge_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Microsoft Edge"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Microsoft Edge")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_opera_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Opera"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Opera")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_brave_browser_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Brave Browser"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Brave Browser")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_slack_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Slack"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Slack")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_zoom_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "zoom.us"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: zoom.us")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_microsoft_teams_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Microsoft Teams"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Microsoft Teams")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_discord_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Discord"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Discord")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_whatsapp_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "WhatsApp"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: WhatsApp")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_telegram_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Telegram"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Telegram")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_skype_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Skype"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Skype")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_musica_music_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Music"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Music")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_tv_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "TV"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: TV")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_podcast_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Podcasts"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Podcasts")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_foto_photos_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Photos"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Photos")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_photo_booth_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Photo Booth"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Photo Booth")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_quicktime_player_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "QuickTime Player"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: QuickTime Player")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_promemoria_vocali_voice_memos_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Voice Memos"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Voice Memos")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_news_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "News"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: News")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_libri_books_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Books"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Books")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_borsa_stocks_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Stocks"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Stocks")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_scacchi_chess_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Chess"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Chess")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_orologio_clock_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Clock"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Clock")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_spotify_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Spotify"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Spotify")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_vlc_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "VLC"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: VLC")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_iina_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "IINA"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: IINA")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_garageband_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "GarageBand"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: GarageBand")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_imovie_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "iMovie"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: iMovie")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_xcode_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Xcode"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Xcode")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_visual_studio_code_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Visual Studio Code"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Visual Studio Code")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_sublime_text_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Sublime Text"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Sublime Text")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_iterm2_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "iTerm"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: iTerm")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_docker_desktop_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Docker"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Docker")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_adobe_photoshop_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Adobe Photoshop 2024"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Adobe Photoshop 2024")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_adobe_illustrator_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Adobe Illustrator"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Adobe Illustrator")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_gimp_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "GIMP"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: GIMP")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_blender_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Blender"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Blender")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_obs_studio_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "OBS"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: OBS")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_sketch_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Sketch"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Sketch")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_figma_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Figma"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Figma")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_microsoft_word_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Microsoft Word"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Microsoft Word")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_microsoft_excel_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Microsoft Excel"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Microsoft Excel")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_microsoft_powerpoint_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Microsoft PowerPoint"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Microsoft PowerPoint")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_microsoft_outlook_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Microsoft Outlook"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Microsoft Outlook")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_microsoft_onenote_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Microsoft OneNote"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Microsoft OneNote")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_notion_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Notion"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Notion")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_evernote_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Evernote"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Evernote")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_1password_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "1Password"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: 1Password")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_cleanmymac_x_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "CleanMyMac X"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: CleanMyMac X")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_steam_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Steam"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Steam")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_epic_games_launcher_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Epic Games Launcher"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Epic Games Launcher")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_battle_net_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Battle.net"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Battle.net")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_parallels_desktop_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Parallels Desktop"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Parallels Desktop")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_vmware_fusion_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "VMware Fusion"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: VMware Fusion")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_transmission_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Transmission"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Transmission")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_the_unarchiver_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "The Unarchiver"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: The Unarchiver")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_keka_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "Keka"])
        print(f"{VERDE_MATRIX}RICHIESTA DI TERMINAZIONE INVIATA A: Keka")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

#-----------------------------------
# TERMINAZIONE FORZATA APP MACOS (killall -9)
#-----------------------------------
def termina_forzatamente_pages_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Pages"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Pages")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_numbers_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Numbers"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Numbers")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_keynote_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Keynote"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Keynote")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_textedit_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "TextEdit"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: TextEdit")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_anteprima_preview_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Preview"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Preview")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_calcolatrice_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Calculator"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Calculator")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_calendario_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Calendar"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Calendar")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_contatti_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Contacts"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Contacts")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_note_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Notes"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Notes")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_promemoria_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Reminders"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Reminders")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_note_adesive_stickies_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Stickies"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Stickies")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_automator_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Automator"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Automator")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_editor_di_script_script_editor_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Script Editor"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Script Editor")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_comandi_rapidi_shortcuts_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Shortcuts"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Shortcuts")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_freeform_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Freeform"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Freeform")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_dizionario_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Dictionary"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Dictionary")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_libro_font_font_book_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Font Book"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Font Book")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_terminale_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Terminal"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Terminal")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_monitoraggio_attivita_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Activity Monitor"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Activity Monitor")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_console_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Console"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Console")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_utility_disco_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Disk Utility"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Disk Utility")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_informazioni_di_sistema_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "System Information"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: System Information")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_assistente_migrazione_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Migration Assistant"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Migration Assistant")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_accesso_portachiavi_keychain_access_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Keychain Access"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Keychain Access")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_screenshot_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Screenshot"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Screenshot")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_condivisione_schermo_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Screen Sharing"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Screen Sharing")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_misuratore_colore_digitale_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Digital Color Meter"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Digital Color Meter")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_grapher_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Grapher"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Grapher")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_scambio_file_bluetooth_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Bluetooth File Exchange"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Bluetooth File Exchange")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_configurazione_audio_midi_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Audio MIDI Setup"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Audio MIDI Setup")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_utility_colorsync_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "ColorSync Utility"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: ColorSync Utility")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_utility_airport_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "AirPort Utility"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: AirPort Utility")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_assistente_boot_camp_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Boot Camp Assistant"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Boot Camp Assistant")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_utility_voiceover_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "VoiceOver Utility"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: VoiceOver Utility")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_diagnostica_wireless_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Wireless Diagnostics"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Wireless Diagnostics")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_time_machine_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Time Machine"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Time Machine")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_impostazioni_di_sistema_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "System Settings"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: System Settings")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_finder_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Finder"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Finder")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_launchpad_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Launchpad"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Launchpad")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_mission_control_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Mission Control"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Mission Control")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_siri_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Siri"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Siri")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_acquisizione_immagini_image_capture_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Image Capture"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Image Capture")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_app_store_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "App Store"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: App Store")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_safari_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Safari"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Safari")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_mail_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Mail"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Mail")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_messaggi_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Messages"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Messages")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_facetime_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "FaceTime"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: FaceTime")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_dov_e_find_my_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Find My"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Find My")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_mappe_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Maps"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Maps")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_casa_home_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Home"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Home")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_google_chrome_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Google Chrome"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Google Chrome")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_mozilla_firefox_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Firefox"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Firefox")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_microsoft_edge_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Microsoft Edge"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Microsoft Edge")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_opera_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Opera"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Opera")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_brave_browser_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Brave Browser"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Brave Browser")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_slack_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Slack"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Slack")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_zoom_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "zoom.us"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: zoom.us")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_microsoft_teams_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Microsoft Teams"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Microsoft Teams")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_discord_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Discord"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Discord")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_whatsapp_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "WhatsApp"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: WhatsApp")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_telegram_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Telegram"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Telegram")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_skype_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Skype"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Skype")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_musica_music_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Music"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Music")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_tv_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "TV"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: TV")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_podcast_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Podcasts"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Podcasts")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_foto_photos_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Photos"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Photos")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_photo_booth_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Photo Booth"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Photo Booth")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_quicktime_player_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "QuickTime Player"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: QuickTime Player")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_promemoria_vocali_voice_memos_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Voice Memos"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Voice Memos")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_news_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "News"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: News")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_libri_books_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Books"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Books")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_borsa_stocks_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Stocks"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Stocks")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_scacchi_chess_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Chess"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Chess")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_orologio_clock_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Clock"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Clock")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_spotify_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Spotify"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Spotify")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_vlc_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "VLC"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: VLC")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_iina_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "IINA"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: IINA")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_garageband_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "GarageBand"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: GarageBand")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_imovie_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "iMovie"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: iMovie")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_xcode_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Xcode"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Xcode")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_visual_studio_code_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Visual Studio Code"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Visual Studio Code")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_sublime_text_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Sublime Text"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Sublime Text")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_iterm2_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "iTerm"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: iTerm")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_docker_desktop_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Docker"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Docker")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_adobe_photoshop_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Adobe Photoshop 2024"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Adobe Photoshop 2024")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_adobe_illustrator_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Adobe Illustrator"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Adobe Illustrator")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_gimp_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "GIMP"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: GIMP")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_blender_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Blender"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Blender")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_obs_studio_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "OBS"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: OBS")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_sketch_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Sketch"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Sketch")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_figma_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Figma"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Figma")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_microsoft_word_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Microsoft Word"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Microsoft Word")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_microsoft_excel_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Microsoft Excel"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Microsoft Excel")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_microsoft_powerpoint_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Microsoft PowerPoint"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Microsoft PowerPoint")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_microsoft_outlook_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Microsoft Outlook"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Microsoft Outlook")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_microsoft_onenote_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Microsoft OneNote"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Microsoft OneNote")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_notion_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Notion"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Notion")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_evernote_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Evernote"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Evernote")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_1password_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "1Password"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: 1Password")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_cleanmymac_x_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "CleanMyMac X"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: CleanMyMac X")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_steam_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Steam"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Steam")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_epic_games_launcher_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Epic Games Launcher"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Epic Games Launcher")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_battle_net_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Battle.net"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Battle.net")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_parallels_desktop_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Parallels Desktop"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Parallels Desktop")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_vmware_fusion_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "VMware Fusion"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: VMware Fusion")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_transmission_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Transmission"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Transmission")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_the_unarchiver_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "The Unarchiver"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: The Unarchiver")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")

def termina_forzatamente_keka_macos():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        subprocess.Popen(["killall", "-9", "Keka"])
        print(f"{VERDE_MATRIX}TERMINAZIONE FORZATA INVIATA A: Keka")
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")
COMANDI_RAPIDI = {
    "windows": {
        "configurazione rete": "cmd_configurazione_rete",
        "configurazione rete completa": "cmd_configurazione_rete_completa",
        "prova connessione": "cmd_prova_connessione",
        "percorso di rete": "cmd_percorso_di_rete",
        "connessioni di rete attive": "cmd_connessioni_di_rete_attive",
        "informazioni dettagliate sistema": "cmd_informazioni_dettagliate_sistema",
        "elenco processi attivi": "cmd_elenco_processi_attivi",
        "nome utente attuale": "cmd_nome_utente_attuale",
        "nome del computer": "cmd_nome_del_computer",
        "contenuto cartella attuale": "cmd_contenuto_cartella_attuale",
        "versione windows": "cmd_versione_windows",
        "controllo dischi": "cmd_controllo_dischi",
        "controllo file di sistema": "cmd_controllo_file_di_sistema",
        "nome del processore": "cmd_nome_del_processore",
        "elenco dischi e spazio libero": "cmd_elenco_dischi_e_spazio_libero",
        "elenco utenti del pc": "cmd_elenco_utenti_del_pc",
        "orario attuale": "cmd_orario_attuale",
        "data attuale": "cmd_data_attuale",
        "svuota cache dns": "cmd_svuota_cache_dns",
    },
    "linux": {
        "informazioni sul kernel": "cmd_informazioni_sul_kernel",
        "nome utente attuale": "cmd_nome_utente_attuale_linux",
        "nome del computer": "cmd_nome_del_computer_linux",
        "configurazione rete": "cmd_configurazione_rete_linux",
        "prova connessione": "cmd_prova_connessione_linux",
        "spazio sui dischi": "cmd_spazio_sui_dischi",
        "memoria ram disponibile": "cmd_memoria_ram_disponibile",
        "elenco processi attivi": "cmd_elenco_processi_attivi_linux",
        "elenco dischi e partizioni": "cmd_elenco_dischi_e_partizioni",
        "dimensione cartella attuale": "cmd_dimensione_cartella_attuale",
        "informazioni distribuzione": "cmd_informazioni_distribuzione",
        "connessioni di rete attive": "cmd_connessioni_di_rete_attive_linux",
        "utenti collegati ora": "cmd_utenti_collegati_ora",
        "contenuto cartella attuale": "cmd_contenuto_cartella_attuale_linux",
        "cronologia comandi": "cmd_cronologia_comandi",
        "variabile path": "cmd_variabile_path",
        "pacchetti installati": "cmd_pacchetti_installati",
    },
    "macos": {
        "informazioni hardware": "cmd_informazioni_hardware_mac",
        "versione macos": "cmd_versione_macos",
        "nome utente attuale": "cmd_nome_utente_attuale_mac",
        "nome del computer": "cmd_nome_del_computer_mac",
        "configurazione rete": "cmd_configurazione_rete_mac",
        "prova connessione": "cmd_prova_connessione_mac",
        "spazio sui dischi": "cmd_spazio_sui_dischi_mac",
        "elenco processi attivi": "cmd_elenco_processi_attivi_mac",
        "elenco dischi": "cmd_elenco_dischi_mac",
        "stato batteria": "cmd_stato_batteria",
        "utenti collegati ora": "cmd_utenti_collegati_ora_mac",
        "contenuto cartella attuale": "cmd_contenuto_cartella_attuale_mac",
        "connessioni di rete attive": "cmd_connessioni_di_rete_attive_mac",
        "cronologia comandi": "cmd_cronologia_comandi_mac",
        "variabile path": "cmd_variabile_path_mac",
        "tempo di attivita": "cmd_tempo_di_attivita_mac",
        "informazioni processore": "cmd_informazioni_processore_mac",
        "svuota cache dns": "cmd_svuota_cache_dns_mac",
    },
}

FILE_COMANDI = {
    "percorso attuale": "percorso_attuale",
    "crea cartella": "crea_cartella",
    "rimuovi cartella vuota": "rimuovi_cartella_vuota",
    "rimuovi cartella": "rimuovi_cartella",
    "sposta file": "sposta_file",
    "sposta cartella": "sposta_cartella",
    "rimuovi file": "rimuovi_file",
    "rinomina file": "rinomina_file",
    "dimensione file": "dimensione_file",
    "lista cartella": "lista_cartella",
    "esplora cartella": "esplorazione_cartella",
    "scrivi in file": "scrivi_qualcosa_in_un_file",
    "crea file": "crea_file",
    "avvia file": "avvia_file",
    "entra in percorsi": "entra_in_percorsi",
    "separatore percorsi": "separatore_percorsi",
    "separatore path": "separatore_path",
}

TESTO_COMANDI = {
    "cripta testo": "crittografia_testo",
    "decripta testo": "decrittografia_testo",
    "cripta file": "crittografia_file_di_testo",
    "decripta file": "decrittografia_file_di_testo",
    "codifica base64": "codifica_base64_testo",
    "decodifica base64": "decodifica_base64_testo",
    "codifica base16": "codifica_base16_testo",
    "decodifica base16": "decodifica_testo_base16",
    "codifica base32": "codifica_testo_base32",
    "decodifica base32": "decodifica_testo_base32",
    "codifica base85": "codifica_testo_base85",
    "decodifica base85": "decodifica_testo_base85",
    "uuid generico": "genera_uuid_generico",
    "uuid da link": "genera_uuid_url",
    "uuid vuoto": "uuid_vuoto",
    "uuid senza trattini": "uuid_senza_trattini",
    "uuid intero": "uuid_intero",
    "uuid bytes": "uuid_bytes",
    "struttura uuid": "fields_uuid",
}

INFO_COMANDI = {
    "informazioni sistema": "informazioni_sistema",
    "statistiche cpu": "statistiche_cpu",
    "statistiche ram": "statistiche_ram",
    "utenti collegati": "utenti_loggati",
    "tempo di avvio sistema": "tempo_di_boot",
    "tempo di attivita": "time_up",
    "secondi dal 1970": "secondi_passati_dal_1970",
    "data e ora": "data_e_ora_attuale",
    "thread cpu": "thread_cpu",
    "dimensioni terminale": "dimensioni_terminale",
    "pid python": "pid_processo_python",
    "secondi passati programma": "secondi_passati_dall_avvio_del_programma",
    "numero casuale": "numero_casuale_tra_0_e_1",
    "id sistema operativo": "id_sistema",
    "spegni pc": "spegni_pc",
    "riavvia pc": "riavvia_pc",
}


#-----------------------------------
# MENU A PAROLE, SEMPLICE PER PRINCIPIANTI
#-----------------------------------
def mostra_lista_e_scegli(titolo, dizionario):
    # mostra tutte le voci del dizionario e fa scrivere all'utente il nome di
    # quella che vuole usare (parole, non numeri). scrivendo INDIETRO si torna
    # al menu precedente senza fare nulla
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{VERDE_MATRIX}{titolo}")
        print(f"{VERDE_MATRIX}--------------------------------------------------")
        for nome in sorted(dizionario.keys()):
            print(f"{VERDE_MATRIX}- {nome}")
        print(f"{VERDE_MATRIX}--------------------------------------------------")
        scelta = input(f"{VERDE_MATRIX}SCRIVI IL NOME DI QUELLO CHE VUOI FARE (oppure scrivi INDIETRO): ").strip().lower()
        if scelta == "indietro":
            return None
        for nome, valore in dizionario.items():
            if nome.lower() == scelta:
                return valore
        print(f"{ROSSO_MATRIX}NON HO CAPITO QUELLO CHE HAI SCRITTO, RIPROVA")
        time.sleep(1.5)


def menu_principale(sistema):
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{VERDE_MATRIX}IL TUO SISTEMA OPERATIVO: {sistema.upper()}")
        print()
        print(f"{VERDE_MATRIX}COSA VUOI FARE? SCRIVI UNA DI QUESTE PAROLE:")
        print(f"{VERDE_MATRIX}APRI             -> per aprire un programma")
        print(f"{VERDE_MATRIX}CHIUDI           -> per chiudere un programma")
        print(f"{VERDE_MATRIX}CHIUDI FORZATO   -> per chiudere forzatamente un programma")
        print(f"{VERDE_MATRIX}COMANDI          -> per i comandi rapidi del terminale")
        print(f"{VERDE_MATRIX}FILE             -> per gestire file e cartelle")
        print(f"{VERDE_MATRIX}TESTO            -> per testo, codifica e crittografia")
        print(f"{VERDE_MATRIX}INFORMAZIONI     -> per informazioni di sistema e altro")
        print(f"{VERDE_MATRIX}ESCI             -> per uscire dal programma")
        print(f"{VERDE_MATRIX}TERMINALE        -> per usare un terminale vero (scrivi i comandi che vuoi)")
        print()
        scelta = input(f"{VERDE_MATRIX}SCRIVI QUI: ").strip().lower()

        if scelta == "apri":
            try:
                programmi = MAPPA_PROGRAMMI[sistema]
                dizionario_apri = {nome: valori[0] for nome, valori in programmi.items()}
                funzione = mostra_lista_e_scegli("PROGRAMMI CHE PUOI APRIRE", dizionario_apri)
                if funzione:
                    globals()[funzione]()
                    input(f"{VERDE_MATRIX}PREMI INVIO PER CONTINUARE...")
            except Exception as e:
                pass


        elif scelta == "chiudi":
            try:
                programmi = MAPPA_PROGRAMMI[sistema]
                dizionario_chiudi = {nome: valori[1] for nome, valori in programmi.items() if valori[1]}
                funzione = mostra_lista_e_scegli("PROGRAMMI CHE PUOI CHIUDERE", dizionario_chiudi)
                if funzione:
                    globals()[funzione]()
                    input(f"{VERDE_MATRIX}PREMI INVIO PER CONTINUARE...")
            except Exception as a:
                pass


        elif scelta == "chiudi forzato":
            try:
                programmi = MAPPA_PROGRAMMI[sistema]
                dizionario_chiudi_forzato = {nome: valori[2] for nome, valori in programmi.items() if valori[2]}
                funzione = mostra_lista_e_scegli("PROGRAMMI CHE PUOI CHIUDERE FORZATAMENTE", dizionario_chiudi_forzato)
                if funzione:
                    globals()[funzione]()
                    input(f"{VERDE_MATRIX}PREMI INVIO PER CONTINUARE...")
            except Exception as g:
                pass


        elif scelta == "comandi":
            funzione = mostra_lista_e_scegli("COMANDI RAPIDI DEL TERMINALE", COMANDI_RAPIDI[sistema])
            if funzione:
                globals()[funzione]()
                input(f"{VERDE_MATRIX}PREMI INVIO PER CONTINUARE...")

        elif scelta == "file":
            funzione = mostra_lista_e_scegli("GESTIONE FILE E CARTELLE", FILE_COMANDI)
            if funzione:
                globals()[funzione]()
                input(f"{VERDE_MATRIX}PREMI INVIO PER CONTINUARE...")

        elif scelta == "testo":
            funzione = mostra_lista_e_scegli("TESTO, CODIFICA E CRITTOGRAFIA", TESTO_COMANDI)
            if funzione:
                globals()[funzione]()
                input(f"{VERDE_MATRIX}PREMI INVIO PER CONTINUARE...")

        elif scelta == "informazioni":
            funzione = mostra_lista_e_scegli("INFORMAZIONI DI SISTEMA E ALTRO", INFO_COMANDI)
            if funzione:
                globals()[funzione]()
                input(f"{VERDE_MATRIX}PREMI INVIO PER CONTINUARE...")
        elif scelta == "terminale":
            terminale()
        
        elif scelta == "esci":
            os.system('cls' if os.name == 'nt' else 'clear')
            
            
            print(f"{VERDE_MATRIX}A PRESTO!")
            break


        else:
            print(f"{ROSSO_MATRIX}NON HO CAPITO QUELLO CHE HAI SCRITTO, RIPROVA")
            time.sleep(1.5)



#-----------------------------------
# TERMINALE VERO: COMANDI INTERNI
#-----------------------------------
def interno_cd(args):
    global CARTELLA_PRECEDENTE
    if not args:
        destinazione = os.path.expanduser("~")
    elif args[0] == "-":
        destinazione = CARTELLA_PRECEDENTE or os.getcwd()
    else:
        destinazione = args[0]
    try:
        attuale = os.getcwd()
        os.chdir(destinazione)
        CARTELLA_PRECEDENTE = attuale
        return 0
    except Exception as e:
        print(f"{ROSSO_MATRIX}ERRORE: {e}")
        return 1
def interno_pwd(args):
    print(f"{VERDE_MATRIX}{os.getcwd()}")
    return 0
def interno_esci(args):
    raise UscitaTerminale()
def interno_cls(args):
    os.system('cls' if os.name == 'nt' else 'clear')
    return 0
def interno_cronologia(args):
    for numero, riga in enumerate(CRONOLOGIA, start=1):
        print(f"{VERDE_MATRIX}{numero}  {riga}")
    return 0
def interno_export(args):
    if not args:
        for nome, valore in os.environ.items():
            print(f"{VERDE_MATRIX}{nome}={valore}")
        return 0
    if len(args) == 2 and "=" not in args[0]:
        os.environ[args[0]] = args[1]
        return 0
    for voce in args:
        if "=" not in voce:
            print(f"{ROSSO_MATRIX}USA: export NOME=valore")
            return 1
        nome, valore = voce.split("=", 1)
        os.environ[nome] = valore
    return 0
def interno_unset(args):
    for nome in args:
        os.environ.pop(nome, None)
    return 0
def interno_alias(args):
    if not args:
        for nome, valore in ALIAS.items():
            print(f"{VERDE_MATRIX}{nome}={valore}")
        return 0
    for voce in args:
        if "=" not in voce:
            print(f"{ROSSO_MATRIX}USA: alias nome=comando")
            return 1
        nome, valore = voce.split("=", 1)
        ALIAS[nome] = valore
    return 0
def interno_unalias(args):
    for nome in args:
        ALIAS.pop(nome, None)
    return 0
def interno_dove(args):
    codice = 0
    for nome in args:
        if nome in COMANDI_INTERNI:
            print(f"{VERDE_MATRIX}{nome}: COMANDO INTERNO")
            continue
        percorso = shutil.which(nome)
        if percorso:
            print(f"{VERDE_MATRIX}{percorso}")
        else:
            print(f"{ROSSO_MATRIX}{nome}: NON TROVATO")
            codice = 1
    return codice
def interno_aiuto(args):
    print(f"{VERDE_MATRIX}COMANDI INTERNI: cd, pwd, cls/clear, cronologia/history, export/imposta, unset, alias, unalias, dove/which, aiuto/help, esci/exit")
    print(f"{VERDE_MATRIX}OPERATORI: |  >  >>  <  &&  ||  ;  &  $?  !!  ~  *")
    print(f"{VERDE_MATRIX}TAB = completa comandi e file | FRECCE SU/GIU = cronologia | CTRL+C = interrompe | CTRL+D = esce")
    return 0

COMANDI_INTERNI = {
    "cd": interno_cd, "pwd": interno_pwd, "esci": interno_esci, "exit": interno_esci,
    "cls": interno_cls, "clear": interno_cls, "cronologia": interno_cronologia,
    "history": interno_cronologia, "export": interno_export, "imposta": interno_export,
    "unset": interno_unset, "rimuovi_variabile": interno_unset, "alias": interno_alias,
    "unalias": interno_unalias, "which": interno_dove, "dove": interno_dove,
    "aiuto": interno_aiuto, "help": interno_aiuto,
}


#-----------------------------------
# TERMINALE VERO: LETTURA E INTERPRETAZIONE DELLA RIGA
#-----------------------------------
def dividi_riga(riga):
    lexer = shlex.shlex(riga, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    lexer.commenters = ""
    if os.name == "nt":
        lexer.escape = ""
    return list(lexer)
def espandi_argomento(gettone):
    gettone = os.path.expanduser(os.path.expandvars(gettone))
    if any(c in gettone for c in "*?["):
        trovati = sorted(glob.glob(gettone))
        if trovati:
            return trovati
    return [gettone]
def analizza_redirect(gettoni):
    args = []
    ridir = {}
    i = 0
    while i < len(gettoni):
        g = gettoni[i]
        if g in ("(", ")", "&"):
            raise ValueError(f"OPERATORE NON SUPPORTATO: {g}")
        if g in (">", ">>", "<"):
            if i + 1 >= len(gettoni):
                raise ValueError(f"MANCA IL FILE DOPO {g}")
            nome = os.path.expanduser(gettoni[i + 1])
            if g == "<":
                ridir["in"] = nome
            else:
                ridir["out"] = nome
                ridir["append"] = (g == ">>")
            i += 2
        else:
            args.extend(espandi_argomento(g))
            i += 1
    if not args:
        raise ValueError("COMANDO VUOTO")
    return args, ridir
def applica_alias(parti):
    if parti and parti[0] in ALIAS:
        try:
            return dividi_riga(ALIAS[parti[0]]) + parti[1:]
        except ValueError:
            return parti
    return parti
def prepara_comando(args):
    if os.name == "nt" and args[0].lower() in COMANDI_CMD_WINDOWS:
        return ["cmd", "/c"] + args
    percorso = shutil.which(args[0])
    if percorso:
        return [percorso] + args[1:]
    return args


#-----------------------------------
# TERMINALE VERO: ESECUZIONE
#-----------------------------------
def esegui_interno(args, ridir):
    funzione = COMANDI_INTERNI[args[0].lower()]
    file_out = None
    try:
        if ridir.get("out"):
            file_out = open(ridir["out"], "a" if ridir.get("append") else "w", encoding="utf-8")
            with contextlib.redirect_stdout(file_out):
                return funzione(args[1:])
        return funzione(args[1:])
    finally:
        if file_out:
            file_out.close()
def esegui_pipeline(stadi, sfondo):
    processi = []
    file_aperti = []
    precedente = None
    try:
        for i, (args, ridir) in enumerate(stadi):
            ultimo = (i == len(stadi) - 1)
            stdin = None
            stdout = None
            if precedente is not None:
                stdin = precedente.stdout
            elif ridir.get("in"):
                f = open(ridir["in"], "rb")
                file_aperti.append(f)
                stdin = f
            if ridir.get("out"):
                f = open(ridir["out"], "ab" if ridir.get("append") else "wb")
                file_aperti.append(f)
                stdout = f
            elif not ultimo:
                stdout = subprocess.PIPE
            p = subprocess.Popen(prepara_comando(args), stdin=stdin, stdout=stdout)
            if precedente is not None and precedente.stdout is not None:
                precedente.stdout.close()
            processi.append(p)
            precedente = p
    except OSError as e:
        for p in processi:
            try:
                p.kill()
            except OSError:
                pass
        if isinstance(e, FileNotFoundError):
            print(f"{ROSSO_MATRIX}NON TROVATO: {e.filename}")
            return 127
        if isinstance(e, PermissionError):
            print(f"{ROSSO_MATRIX}PERMESSO NEGATO: {e.filename}")
            return 126
        print(f"{ROSSO_MATRIX}ERRORE: {e}")
        return 1
    finally:
        for f in file_aperti:
            f.close()
    if sfondo:
        print(f"{VERDE_MATRIX}[IN SECONDO PIANO] PID {processi[-1].pid}")
        return 0
    try:
        for p in processi:
            p.wait()
    except KeyboardInterrupt:
        for p in processi:
            try:
                p.terminate()
            except OSError:
                pass
        print()
        return 130
    return processi[-1].returncode
def esegui_comando(parti):
    sfondo = False
    if parti and parti[-1] == "&":
        sfondo = True
        parti = parti[:-1]
    if not parti:
        return 0
    parti = applica_alias(parti)
    stadi_grezzi = []
    corrente = []
    for g in parti:
        if g == "|":
            stadi_grezzi.append(corrente)
            corrente = []
        else:
            corrente.append(g)
    stadi_grezzi.append(corrente)
    try:
        if any(not s for s in stadi_grezzi):
            raise ValueError("MANCA UN COMANDO PRIMA O DOPO |")
        stadi = [analizza_redirect(s) for s in stadi_grezzi]
    except ValueError as e:
        print(f"{ROSSO_MATRIX}ERRORE DI SINTASSI: {e}")
        return 2
    if len(stadi) == 1 and stadi[0][0][0].lower() in COMANDI_INTERNI:
        return esegui_interno(stadi[0][0], stadi[0][1])
    return esegui_pipeline(stadi, sfondo)
def esegui_riga(riga):
    global ULTIMO_CODICE
    if riga == "!!":
        if len(CRONOLOGIA) < 2:
            print(f"{ROSSO_MATRIX}NESSUN COMANDO PRECEDENTE")
            return 1
        riga = CRONOLOGIA[-2]
        print(f"{VERDE_MATRIX}{riga}")
    try:
        gettoni = dividi_riga(riga.replace("$?", str(ULTIMO_CODICE)))
    except ValueError as e:
        print(f"{ROSSO_MATRIX}ERRORE DI SINTASSI: {e}")
        return 2
    sequenze = []
    operatore = ";"
    corrente = []
    for g in gettoni:
        if g in (";", "&&", "||"):
            sequenze.append((operatore, corrente))
            corrente = []
            operatore = g
        else:
            corrente.append(g)
    sequenze.append((operatore, corrente))
    codice = ULTIMO_CODICE
    for operatore, parti in sequenze:
        if not parti:
            continue
        if operatore == "&&" and codice != 0:
            continue
        if operatore == "||" and codice == 0:
            continue
        codice = esegui_comando(parti)
    return codice


#-----------------------------------
# TERMINALE VERO: CRONOLOGIA, TAB E CICLO PRINCIPALE
#-----------------------------------
def elenca_eseguibili():
    global _CACHE_ESEGUIBILI
    if _CACHE_ESEGUIBILI is None:
        nomi = set(COMANDI_INTERNI) | set(ALIAS)
        for cartella in os.environ.get("PATH", "").split(os.pathsep):
            try:
                for voce in os.listdir(cartella):
                    percorso = os.path.join(cartella, voce)
                    if os.access(percorso, os.X_OK) and not os.path.isdir(percorso):
                        nomi.add(voce)
            except OSError:
                continue
        _CACHE_ESEGUIBILI = sorted(nomi)
    return _CACHE_ESEGUIBILI
def completatore(testo, stato):
    if stato == 0:
        prima = readline.get_line_buffer()[:readline.get_begidx()].rstrip()
        if prima == "" or prima.endswith(("|", "&&", "||", ";")):
            opzioni = [n for n in elenca_eseguibili() if n.startswith(testo)]
        else:
            opzioni = []
            for percorso in glob.glob(os.path.expanduser(testo) + "*"):
                opzioni.append(percorso + os.sep if os.path.isdir(percorso) else percorso)
        completatore.opzioni = sorted(opzioni)
    try:
        return completatore.opzioni[stato]
    except IndexError:
        return None
def carica_cronologia():
    if os.path.exists(cronologia_path):
        try:
            with open(cronologia_path, "r", encoding="utf-8") as f:
                for riga in f.read().splitlines():
                    if riga.strip():
                        CRONOLOGIA.append(riga)
                        if readline:
                            readline.add_history(riga)
        except Exception:
            pass
def salva_cronologia():
    try:
        with open(cronologia_path, "w", encoding="utf-8") as f:
            f.write("\n".join(CRONOLOGIA[-1000:]) + "\n")
    except Exception:
        pass
def prepara_readline():
    if readline is None:
        return
    readline.set_completer_delims(" \t\n|&;<>")
    readline.set_completer(completatore)
    if "libedit" in (readline.__doc__ or ""):
        readline.parse_and_bind("bind ^I rl_complete")
    else:
        readline.parse_and_bind("tab: complete")
def prompt_terminale():
    casa = os.path.expanduser("~")
    cartella = os.getcwd()
    if cartella.startswith(casa):
        cartella = "~" + cartella[len(casa):]
    colore = VERDE_MATRIX if ULTIMO_CODICE == 0 else ROSSO_MATRIX
    if readline and os.name != "nt":
        return f"\001{colore}\002{cartella} > "
    return f"{colore}{cartella} > "
def terminale():
    global ULTIMO_CODICE
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{VERDE_MATRIX}ITALIAN COMMAND PROMPT - TERMINALE. SCRIVI AIUTO PER I COMANDI, ESCI PER TORNARE AL MENU")
    print()
    carica_cronologia()
    prepara_readline()
    while True:
        try:
            riga = input(prompt_terminale()).strip()
        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            print()
            continue
        if not riga:
            continue
        CRONOLOGIA.append(riga)
        try:
            ULTIMO_CODICE = esegui_riga(riga)
        except UscitaTerminale:
            break
        except Exception as e:
            print(f"{ROSSO_MATRIX}ERRORE GENERALE: {e}")
            ULTIMO_CODICE = 1
    salva_cronologia()
def procedi():
    os.system('cls' if os.name == 'nt' else 'clear')
    scritta_icp = """
 ___  ____  ____  

|_ _||  _ \|  _ \ 
 | | | |   | |_) |
 | | | |   |  __/ 
|___||___| |_|    
"""

    print(f"{VERDE_MATRIX}{scritta_icp}")
    print()
    print(f"{VERDE_MATRIX}------------------------------------------------------------------------------------------------------------------")
    print()
    print(f"{VERDE_MATRIX}Italian Command Prompt, Tutti i diritti riservati. Dev by: Mari_Developer")
    print()

    sistema = ""
    while sistema not in ("windows", "linux", "macos"):
        sistema = input(f"{VERDE_MATRIX}SU CHE SISTEMA OPERATIVO SEI? (scrivi WINDOWS, LINUX o MACOS): ").strip().lower()
        if sistema not in ("windows", "linux", "macos"):
            print(f"{ROSSO_MATRIX}RISPOSTA NON VALIDA, SCRIVI SOLO WINDOWS, LINUX O MACOS")

    menu_principale(sistema)



def crea_account():
    os.system('cls' if os.name == 'nt' else 'clear')
    scelta1 = input(f"{VERDE_MATRIX}VUOI CREARE ACCOUNT  CON GOOGLE O CON EMAIL? (rispondere con google o email) ").strip().lower()
    if scelta1== "google":
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_CONFIG, scopes=["openid", "profile", "email"])
        flow.run_local_server(port=0, success_message="Grazie, continua sul terminale")
        user_info = flow.authorized_session().get("https://www.googleapis.com/oauth2/v3/userinfo").json()
        ids = uuid.uuid4()
        procedi()
        with open(account_google_path, mode="a", encoding="utf-8") as f:
            f.write(f"NOME: {user_info.get('name')}\nEMAIL: {user_info.get('email')}\n---------------------------------------------------------------------------\n")
    elif scelta1 == "email":
        print()
        email = input(f"{VERDE_MATRIX}INSERIRE EMAIL: ").strip()
        username = input(f"{VERDE_MATRIX}INSERIRE USERNAME: ").strip()
        if re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", email):
            with open(accounts_path, mode="r", encoding="utf-8") as a:
                righr = a.read().strip()
                if email and username not in righr:
                    with open(accounts_path, mode="a", encoding="utf-8") as f:
                        f.write(f"USERNAME: {username}\nEMAIL: {email}\n---------------------------------------------------------------------------------\n")
                        procedi()
                else:
                    print(f"{ROSSO_MATRIX}ACCOUNT GIA ESISTENTE!")
        else:
            print(f"{ROSSO_MATRIX}EMAIL NON VALIDA")
    else:
        print(f"{ROSSO_MATRIX}POSSIBILE FARE SOLO LOGIN CON GOOGLE O CON EMAIL")
def login():
    os.system('cls' if os.name == 'nt' else 'clear')
    scela1 = input(f"{VERDE_MATRIX}VUOI FARE LOGIN CON GOOGLE O CON EMAIL? (rispondere con google o con email) ").strip().lower()
    if scela1 == "google":
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_CONFIG, scopes=["openid", "profile", "email"])
        flow.run_local_server(port=0, success_message="Grazie per aver fatto il login! Continua sul temrinale")
        procedi()
    elif scela1 == "email":
        print()
        email = input(f"{VERDE_MATRIX}INSERIRE EMAIL: ").strip()
        username = input(f"{VERDE_MATRIX}INSERIRE USERNAME: ").strip()
        if re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", email):
            with open(accounts_path, mode="r", encoding="utf-8") as d:
                righe = d.read().strip()
                if email and username in righe:
                    procedi()
                else:
                    print(f"{ROSSO_MATRIX}ACCOUNT INESISTENTE")
        else:
            print(f"{ROSSO_MATRIX}EMAIL NON VALIDA")
    else:
        print(f"{ROSSO_MATRIX}LOGIN DISONIBILE SOLO CON GOOGLE E CON EMAIL")


os.system('cls' if os.name == 'nt' else 'clear')       
scelta = input(f"{VERDE_MATRIX}BENVENUTO, DIMMI SE VUOI CREARE UN ACCOUNT O FARE IL LOGIN NEL TERMINALE, (rispondere con crea account o login) ").strip().lower()
if scelta == "crea account":
    crea_account()
if scelta == "login":
    login()
