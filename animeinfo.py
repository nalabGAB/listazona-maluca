import requests
from bs4 import BeautifulSoup
import csv
import os.path

base_url = 'https://www.anroll.net' # powered by AnimesROLL

# Defina uma função para verificar se o título do anime já existe no arquivo CSV
def verificar_existencia_titulo(titulo):
    with open('animes.csv', mode='r', encoding='utf-8', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[1] == titulo:  # Compara o título do anime com cada linha do arquivo CSV
                return True
    return False

# Defina uma função para escrever os dados em um arquivo CSV
def escrever_csv(data):
    titulo = data[1]
    if not verificar_existencia_titulo(titulo):
        with open('animes.csv', mode='a', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            data[5] = str(data[5]).replace('.', ',')  # Converte a nota para uma string e substitui '.' por ','
            writer.writerow(data)

# Defina uma função para verificar as informações já presentes no aqruivo CSV
def atualizar_csv(data):
    with open('animes.csv', mode='r', encoding='utf-8', newline='') as file:
        reader = csv.reader(file)
        rows = list(reader)

    for i, row in enumerate(rows):
        if row[1] == data[1]:  # Verifica se o título do anime já existe no CSV
            # Atualiza as informações se necessário
            if row != data:
                rows[i] = data
            break
    else:
        rows.append(data)

    with open('animes.csv', mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        data[5] = str(data[5]).replace('.', ',')  # Converte a nota para uma string e substitui '.' por ','
        writer.writerows(rows)

#region econtrar informações
def lista(url):
    response = requests.get(url) # Fazendo a solicitação HTTP para a página
    if response.status_code == 200: # Verifica se a solicitação foi bem-sucedida
        soup = BeautifulSoup(response.content, 'html.parser') # Converte o conteúdo da página em um objeto BeautifulSoup

        infos = soup.find_all('article')
        tags = []
        for info in infos:
            details = info.find_all('div', class_='details')
            for detail in details:
                numscore = str(''.join(filter(str.isdigit, detail.get_text(strip=True))))[:-4]
                if numscore != '':
                    score = int(numscore)/10
                    ano = str(''.join(filter(str.isdigit, detail.get_text(strip=True))))[2:] # esse aqui ta dificil, ele pega o texto de detail (detail.get_text) e filtra para checar se é um número (str.isdigit) e depois retorna se os dois primeiros números ([2:]), isso porque os dois primeiros dígitos seriam o score
                else:
                    score = "??"
                    ano = str(''.join(filter(str.isdigit, detail.get_text(strip=True))))
                    if detail == '' or detail is None:
                        detail = "??"
                infogeneros = detail.find_all('div', id='generos')
                for infoshref in infogeneros:
                    infotags = infoshref.find_all('a')
                    for infotag in infotags:
                        if infotag.find('div', class_=lambda c: c and 'generostag' in c):
                            tags.append(infotag.find('div', class_=lambda c: c and 'generostag' in c).text.strip())
            titulo = soup.find('h2').text.strip()
            if titulo == '' or titulo is None:
                titulo = "??"
            textoeps = soup.find('button', class_=lambda c: c and 'buttontabitem' in c)
            if textoeps == '' or textoeps is None:
                eps = "??"
            else:
                eps = ''.join(filter(str.isdigit, textoeps.get_text(strip=True)))

        return titulo, eps, tags, ano, score, url
    else:
        print('Erro ao fazer a solicitação HTTP (2)')

#endregion

if os.path.exists('animes.csv'):
    usar_funcao = atualizar_csv
else:
    usar_funcao = escrever_csv

#region encontrar link

response = requests.get(f'{base_url}/animes')
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    container = soup.find_all('ul', class_='animePagination')
    paginas = container[0].find_all('li')
    totalpaginas = []
    for pagina in paginas:
        totalpaginas.append((pagina.text.strip()))
else:
    print('Erro ao fazer a solicitação HTTP')
    
maxpaginas = int(totalpaginas[-2])
contadoranimes = 0

for paginaatual in range(1, maxpaginas+1):
    # Constrói a URL da página atual
    url_pagina = f'{base_url}/animes?page={paginaatual}'
    response = requests.get(url_pagina) # Fazendo a solicitação HTTP para a página

    try:
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser') # Converte o conteúdo da página em um objeto BeautifulSoup
        animes = soup.find_all('li', class_=lambda c: c and 'itemlistanime' in c) # encontra todos os elementos da lista de anime (a class é só um idzao maluco)

        for animeindice in range(0, len(animes)):
            contadoranimes += 1
            anime_href = animes[animeindice].find('a')['href']
            if anime_href is None:
                break
            url_anime = (f'{base_url}{anime_href}')
            info = lista(url_anime)
            titulo = info[0]
            eps = info[1]
            tags = ', '.join(info[2])  # Transforma a lista de tags em uma string separada por vírgulas
            ano = info[3]
            score = info[4]
            link = info[5]
            if info is None or titulo is None:
                break

            data = [contadoranimes-1, titulo, eps, tags, ano, score, link]
            usar_funcao(data)
            print(f'--------------ANIME {contadoranimes}--------------')
            print("Título:", titulo)
            print("Eps:", eps)
            print("Categorias:", tags)
            print("Ano:", ano)
            print("Nota:", score)
            print("Link:", link)
            print("--------------===--------------")
        
            if not animes:
                print("not animes")
                break

    except requests.exceptions.HTTPError as err:
        print(f'Erro ao fazer a solicitação HTTP: {err}')
else:
    print('__Execução Concluída__')
        
#endregion