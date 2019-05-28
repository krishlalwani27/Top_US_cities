from bs4 import BeautifulSoup
import requests
from unicodedata import normalize
import re

op = open('/Users/krish/Desktop/output.csv','w')
print('Name,State,Population,Area,Density,Timezone,Co-ordinates,Elevation',file=op)

# URL to the top US cities page
url = "https://en.wikipedia.org/wiki/List_of_United_States_cities_by_population"
res = requests.get(url).text

# BeautifulSoup used to parse the webpage
soup = BeautifulSoup(res,'lxml')

# Finds the required table to collect data from
cities_table = soup.find('table', {'class': 'wikitable sortable'})
cities = []

# Iterates over first 50 table rows (top 50 cities)
for tr in cities_table.findAll('tr')[:51]:

    city = []

    # Cleans and stores all table data cells in particular row
    trs = tr.findAll('td')
    for td in trs:
        city.append(re.sub('\[[a-zA-Z0-9 ]*\]', '', str(normalize("NFKD", td.text.strip('\n'))).lstrip(' ')))
    if not city:
        continue

    # Accesses the individual city page through its hyperlink
    city_url = "https://en.wikipedia.org" + trs[1].a.get('href')
    res = requests.get(city_url).text
    soup = BeautifulSoup(res, 'lxml')

    # Finds infobox table on individual city page
    city_table = soup.find('table',{'class':'infobox'})
    city_info = []

    # Finds coordinates of the city
    latitude = city_table.find('span',{'class':'latitude'})
    longitude = city_table.find('span', {'class': 'longitude'})
    coords = latitude.text + ' ' + longitude.text

    # Iterates over rows table to extract relevant data
    for trc in city_table.findAll('tr'):

        # Finds the elevation and time zone by checking the header
        if trc.th:
            header = str(trc.th.text).lower()

            if "elevation" in header:
                elev = str(normalize("NFKD", trc.td.text)).split(' ')[0].replace(',','')
            if "time zone" in header:
                timezone = trc.td.text

    # Removes commas so as to store in CSV easily
    name = city[1].replace(',',' ')
    state = city[2]
    population = city[3].replace(',', '')
    area = re.sub(' [a-zA-Z0-9]*', '', city[6].replace(',', ''))
    density = re.sub('/[a-zA-Z0-9 ]*', '', city[8]).replace(',', '')

    # Writes the scraped data to the CSV output file
    print(name,state,population,area,density,timezone,coords,elev,file=op,sep=',')

op.close()