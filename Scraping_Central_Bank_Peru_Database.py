######################################################
#
#  WEB SCRAPING CENTRAL RESERVE BANK OF PERU DATABASE
#
######################################################

from bs4 import BeautifulSoup
import requests
import pandas as pd

#Write one of the following options:
# monthly
# quarterly
# annual

x = input()
print('Downloanding data:', x.upper())

if x == 'monthly':
    link = 'https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales'
elif x == 'quarterly':
    link = 'https://estadisticas.bcrp.gob.pe/estadisticas/series/trimestrales'
else:
    link = 'https://estadisticas.bcrp.gob.pe/estadisticas/series/anuales'

page = requests.get(link, verify=False)
content = BeautifulSoup(page.content, 'html.parser')
tables = content.find_all(class_='series')
number_tables = len(tables)

code = []
name = []
start = []
end = []

for x in range(0, number_tables):
    tr = tables[x].select('tr')
    for y in range(1,len(tr)):
        td=tr[y].select('td')
        code.append(td[1].get_text())
        name.append(td[2].get_text())
        start.append(td[3].get_text())
        end.append(td[4].get_text())
        
table = pd.DataFrame({
        "codes" : code,
        "names" : name,
        "start" : start,
        "end" : end})

##
# MONTHLY, QUARTERLY OR ANNUAL VARIABLES
##

if 'mensuales' in link or 'trimestrales' in link:
    table['start_year'] = table['start'].str.split('-', expand=True)[1]
    table['end_year'] = table['end'].str.split('-', expand=True)[1]
    table['initial_date'] = table['start'].str.split('-', expand=True)[0]
    table['final_date'] = table['end'].str.split('-', expand=True)[0]
    i=1
    if 'mensuales' in link:
        period = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago',
         'Sep', 'Oct', 'Nov', 'Dic']
    elif 'trimestrales' in link:
        period = ['T1','T2','T3','T4']
    for x in period:
        table.initial_date[table.initial_date == x] = i
        table.final_date[table.final_date == x] = i
        i +=1

    start_date = []
    end_date = []

    for x in range(0, len(table)):
        i1,i2 = table.start_year[x], table.initial_date[x]
        start_date.append(i1 + '-' + str(i2))
        i1,i2 = table.end_year[x], table.final_date[x]
        end_date.append(i1 + '-' + str(i2))
    
    table['start_date'] = start_date
    table['end_date'] = end_date
    table = table[['codes','start_date','end_date', 'names']]
elif 'anuales' in link:
    table = table[['codes','start','end', 'names']]
    table.rename(columns={'start':'start_date','end':'end_date'}, inplace=True)
        
##
# DOWNLOANDING
##

total_data = pd.DataFrame(columns = ['name', 'date', 'value'] )

series = {}

for x in range(0, len(table)):
    print('Total of tables: ', len(table)-1)
    print('Downloading table: ', x)
    url = str('https://estadisticas.bcrp.gob.pe/estadisticas/series/api/') + \
    table.codes[x] + str('/') + str('html') + str('/') + table.start_date[x] + \
    str('/') + table.end_date[x]
    page1 = requests.get(url, verify=False)
    content1 = BeautifulSoup(page1.content, 'html.parser')
    cabecera = content1.find_all(class_='cabecera')
    periodo = content1.find_all(class_='periodo')
    dato = content1.find_all(class_='dato')
    name = []
    date = []
    value= []
    try:
        for y in range(0, len(periodo)):
            name.append(cabecera[1].get_text())
            date.append(periodo[y].get_text().replace('\n','').replace(' ',''))
            value.append(pd.to_numeric(dato[y].get_text().replace('\n','').replace(' ',''), errors='ignore'))
        serie = pd.DataFrame({'name': name,
                      'date':date,
                      'value':value})
        total_data = total_data.append(serie)
    except:
        pass
        
total_data.to_csv('data_total.txt', sep = '|')

