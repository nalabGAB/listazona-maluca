import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import requests
from bs4 import BeautifulSoup
from AnilistPython import Anilist

#region api

# Crie uma instância da biblioteca AnilistPython
anilist = Anilist()

# Autenticar a API
scope = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/spreadsheets'
]
current_dir = os.path.dirname(__file__)  # Diretório atual do script
file_path = os.path.join(current_dir, 'listona-maluca-7a5e52a565e4.json')
creds = ServiceAccountCredentials.from_json_keyfile_name(file_path, scope)
client = gspread.authorize(creds)

# Abrir a planilha existente
spreadsheet_id = '1ilIl6v5xpZClswdsszJZHWlLMA7ftyls0ubo3UVUvBU'
spreadsheet = client.open_by_key(spreadsheet_id)

#endregion

sheet = spreadsheet.sheet1  # Acessa a página da planilha

url = "https://www.anroll.net"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

animes = soup.find_all("div", class_="anime")

for anime in animes:
    # Extrair as informações relevantes do anime
    nome = anime.find("h2").text.strip()
    avaliacao = anime.find("span", class_="rating").text.strip()

    # Criar um dicionário com as informações do anime
    anime_info = {
        'Nome': nome,
        'Avaliação': avaliacao
    }

    # Adicionar o anime à planilha
    sheet.append_row(anime_info)