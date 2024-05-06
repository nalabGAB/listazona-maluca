from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

current_dir = os.path.dirname(__file__)  # Diretório atual do script

# Caminho para o arquivo CSV que você deseja fazer o upload
caminho_arquivo_csv = os.path.join(current_dir, 'animes.csv')

# Credenciais da API do Google Drive
file_path_drive = os.path.join(current_dir, 'listona-maluca-7a5e52a565e4.json')

# ID da pasta de destino no Google Drive
id_pasta_destino = '1mpABO-W0ayJjyNz-y-OrR-IKLtmst47v'

# Nome do arquivo no Google Drive
nome_arquivo_drive = 'animes.csv'

try:
    credenciais = service_account.Credentials.from_service_account_file(
        file_path_drive,
        scopes=['https://www.googleapis.com/auth/drive']
    )

    # Criando o cliente da API do Google Drive
    cliente_drive = build('drive', 'v3', credentials=credenciais)

    # Verificando se o arquivo já existe no Google Drive
    response = cliente_drive.files().list(q=f"name='{nome_arquivo_drive}' and '{id_pasta_destino}' in parents",
                                           fields='files(id)').execute()
    arquivos = response.get('files', [])

    if arquivos:  # Se o arquivo já existe, substitui
        arquivo_id = arquivos[0]['id']
        arquivo = cliente_drive.files().update(
            fileId=arquivo_id,
            media_body=caminho_arquivo_csv,
            fields='id'
        ).execute()
    else:  # Se o arquivo não existe, cria um novo
        arquivo_metadata = {'name': nome_arquivo_drive, 'parents': [id_pasta_destino]}
        media = {'media': caminho_arquivo_csv}

        arquivo = cliente_drive.files().create(
            body=arquivo_metadata,
            media_body=caminho_arquivo_csv,
            fields='id'
        ).execute()

    print('Arquivo enviado com sucesso! ID:', arquivo.get('id'))

except Exception as e:
    print('Ocorreu um erro durante o upload do arquivo:', e)
