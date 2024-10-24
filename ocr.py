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

# Configurações do Gemini

def preprocess_image(image):
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    _, image = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY)
    return Image.fromarray(image)

def save_response_to_file(response_text, pdf_filename):
    base_name = os.path.splitext(pdf_filename)[0]
    output_filename = f"{base_name}_relatorio.txt"
    with open(output_filename, 'w', encoding='utf-8') as file:
        file.write(response_text)

def analyze_text_with_gemini(ocr_text, pdf_filename):
    # response = model.generate_content(f"Análise o texto e faça um resumo com 5 linhas, esse texto deve conter as pessoas envolvidas e o cpf delas, {ocr_text}")

    print("ENTROU")
    regex_cpf = r'\b\d{3}[\.\s]?\d{3}[\.\s]?\d{3}[-]?\d{2}\b'
    regex_cnpj = r'\b\d{2}[\.\s]?\d{3}[\.\s]?\d{3}\/\d{4}[-]?\d{2}\b'

    cpfs = re.findall(regex_cpf, ocr_text)
    cnpj = re.findall(regex_cnpj, ocr_text)

    print(cpfs)
    print(cpfs)
    print(cnpj)

    # save_response_to_file(response.text, pdf_filename)

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
    analyze_text_with_gemini(full_text, os.path.basename(pdf_path))
    
    # Deletar o PDF após o processamento
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

if __name__ == "__main__":
    caminho_pdf = "pdfs_finalizados/"
    monitor_folder(caminho_pdf)
