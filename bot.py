from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pyautogui
import os
from pdf2image import convert_from_path
from fpdf import FPDF
import sys

download_folder = os.path.join(os.getcwd(), "pdfs_baixados")
output_folder = os.path.join(os.getcwd(), "pdfs_finalizados")

def wait_for_downloads(download_folder):
    while any([f.endswith('.crdownload') for f in os.listdir(download_folder)]):
        time.sleep(1) 

def login(username, password, login_url):
    driver.get(login_url)

    wait.until(EC.visibility_of_element_located((By.ID, "userNameInput"))).send_keys(username)
    wait.until(EC.visibility_of_element_located((By.ID, "passwordInput"))).send_keys(password)
    driver.find_element(By.ID, "submitButton").click()
    time.sleep(5)


def capture_screenshot(index):
    screenshot = pyautogui.screenshot()
    screenshot_path = os.path.join(download_folder, f"screenshot_{index}.png")
    screenshot.save(screenshot_path)
    return screenshot_path

def criar_pdf_final(file_name, pdf_files):
    pdf_final = FPDF()

    for pdf_index, pdf in enumerate(pdf_files):
        pages = convert_from_path(pdf)

        for page_index, page in enumerate(pages):
            temp_image_path = os.path.join(download_folder,  f'temp_page_{pdf_index}_{page_index}.png')
            page.save(temp_image_path, "PNG")

            pdf_final.add_page()
            pdf_final.image(temp_image_path, x=10, y=10, w=180)

            os.remove(temp_image_path)

    pdf_output_path = os.path.join(output_folder, f"{file_name}.pdf")
    pdf_final.output(pdf_output_path)

    print(f"PDF consolidado salvo em {pdf_output_path}")

download_folder = os.path.join(os.getcwd(), "pdfs_baixados")
os.makedirs(download_folder, exist_ok=True)

chrome_options = webdriver.ChromeOptions()

prefs = {
    "download.default_directory": download_folder,
    "download.prompt_for_download": False,
    "plugins.always_open_pdf_externally": True
}
chrome_options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 10)
driver.maximize_window()

username="375410001.ALPEDRO"
password="A2l3e4x0*#!"

screenshot = []

login(username, password, "https://bccorreio.bcb.gov.br/bccorreio/Correio/CaixaDeEntrada.aspx")


while True: 
    time.sleep(3)
    rows = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//table[@id='ctl00_ctl00_ctl00_MainContent_ConteudoPlaceHolder_GridView1']/tbody/tr")))    

    try:
        button_ultima = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,"[title='Ir para a próxima página.']"))
        )

        if button_ultima.get_attribute("disabled"):
            print("finalizado")
            sys.exit()

    except Exception as e:
        print("Erro ao clicar no botão:", e)
    
    for index, row in enumerate(rows[1:]):  # Pulando a primeira linha de cabeçalho
        rows = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//table[@id='ctl00_ctl00_ctl00_MainContent_ConteudoPlaceHolder_GridView1']/tbody/tr")))
        row = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f"//table[@id='ctl00_ctl00_ctl00_MainContent_ConteudoPlaceHolder_GridView1']/tbody/tr[{index + 1}]")))
        
        file_name = f"{row.text.split(' ')[0]}"
        if "Lido/Recebido" in row.text:
            row.click()

            button2 = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "ctl00_ctl00_MainContent_ConteudoPlaceHolder_lnkVoltar"))
            )

            download_links = driver.find_elements(By.CSS_SELECTOR, "tr td.QuebraPalavra a.Anexo")
            pdf_files = []

            for link in download_links:
                link.click()
                time.sleep(2)
                wait_for_downloads(download_folder)

                dowloaded_pdf = max([os.path.join(download_folder, f) for f in os.listdir(download_folder)], key=os.path.getctime)
                pdf_files.append(dowloaded_pdf)

            time.sleep(1)
            criar_pdf_final(file_name, pdf_files)

            for pdf in pdf_files:
              os.remove(pdf)
            # os.remove(screenshot_file)

            button2.click()
            time.sleep(2)   

        if row == rows[10]:
            try:
                # Espera até que o elemento com a classe LinkSemSublinhado esteja presente e clicável
                button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "ctl00_ctl00_ctl00_MainContent_ConteudoPlaceHolder_GridView1_ctl13_UCPaginacao_ProximaLinkButton"))
                )

                # print(button.get_attribute("outerHTML"))
                button.click()

                time.sleep(2)
            except Exception as e:
                print("Erro ao clicar no botão:", e)