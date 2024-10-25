import google.generativeai as genai
import os
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import re
import time
import cv2
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil
import schedule

# Configurações do Gemini
dados_cotistas = [
    {
        "nome": "GUILHERME AUGUSTO SCHMIDT",
        "cpf": ""
    },
    {
        "nome": "MANUELINA CÂNDIDA DE JESUS",
        "cpf": "24.348.947-12"
    },
    {
        "nome": "ADILSON FÉLIX DA SILVA",
        "cpf": "001.395.427-01"
    },
    {
        "nome": "Doloris Rossi",
        "cpf": ""
    },
    {
        "nome": "ODENIS DA SILVA COSTA ",
        "cpf": "69.439.402-87"
    },
    {
        "nome": "LUIZ CEZAR DA SILVA NEVES",
        "cpf": "494.509.569-87"
    }
]

def move_pdf(pdf_path, destination_folder):
    try:
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
        shutil.move(pdf_path, os.path.join(destination_folder, os.path.basename(pdf_path)))
    except Exception as e:
        print(f"Erro ao tentar mover o {pdf_path}: {e}")

def preprocess_image(image):
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    _, image = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY)
    return Image.fromarray(image)

def save_response_to_file(response_text, pdf_filename):
    base_name = os.path.splitext(pdf_filename)[0]
    output_filename = f"{base_name}_relatorio.txt"
    with open(output_filename, 'w', encoding='utf-8') as file:
        file.write(response_text)

def analyze_text_with_gemini(ocr_text, pdf_filename, pdf_path):
    regex_cpf = r'\b\d{3}[\.\s]?\d{3}[\.\s]?\d{3}[-]?\d{2}\b'
    regex_cnpj = r'\b\d{2}[\.\s]?\d{3}[\.\s]?\d{3}\/\d{4}[-]?\d{2}\b'

    cpfs = re.findall(regex_cpf, ocr_text)
    cnpj = re.findall(regex_cnpj, ocr_text)

    for cotista in dados_cotistas:
        if cotista['cpf'] in cpfs:
            print(cotista['nome'])
            move_pdf(pdf_path, "pdfs_clientes")
            return True
        if cotista['nome'] in ocr_text:
            print(cotista['nome'])
            print(pdf_path)            
            move_pdf(pdf_path, "pdfs_clientes")
            return True
    return False

def pdf_to_text(pdf_path):
    start = time.time()

    try:
        print(f"Processando: {pdf_path}")
        pages = convert_from_path(pdf_path, 200)
    except Exception as e:
        print(f"Erro ao converter PDF {pdf_path}: {e}")
        return

    full_text = ""

    for page in pages:  # Ignorar a última página
        text = pytesseract.image_to_string(page, lang="por")
        full_text += text + "\n"

    end = time.time()
    tempo = end - start
    print(f"{tempo:.2f} segundos")
    cotista = analyze_text_with_gemini(full_text, os.path.basename(pdf_path), pdf_path)
    
    if cotista == False:
        os.remove(pdf_path)

    print(f"PDF {pdf_path} deletado após processamento.")

class PDFEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.pdf'):
            pdf_to_text(event.src_path)

def monitor_folder(folder_path):
    event_handler = PDFEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path=folder_path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

schedule.every().day.at("16:23").do(monitor_folder)
schedule.every().day.at("17:00").do(monitor_folder)

if __name__ == "__main__":
    caminho_pdf = "pdfs_finalizados/"
    monitor_folder(caminho_pdf)
