# This script...

import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import StaleElementReferenceException
import os
from glob import glob
import time
import unidecode

# global variables
menus = {
    'presidente': 'Eleccion Presidente',
    'participacion': 'Participacion',
    # 'senadores': '...',
}    
modes = {
    'total': 'renderMenuTotal',
    'chile': 'renderMenuChile',
    'extranjero': 'renderMenuExtranjero',
    'region': 'renderMenuGeografica',
}
candidates = ["BORIC","KAST","PROVOSTE","SICHEL","ARTES","ENRIQUEZ-OMINAMI","PARISI"]
vote_types = ["Emitidos","Nulos","Blanco","Total"]

def parse_table(candidates, vote_types, table):
    """
    Parses data...
    Returns...
    """
    data_report = {
        "Type": [],
        "Votes": [],
        "Percentage": [],
    }

    data_votes = {
        "Candidate": [],
        "Votes": [],
        "Percentage": [],
    }

    for row in table.find_elements_by_tag_name("tr"):
        line = row.text
        if line != '':
            #
            if any(a in line for a in candidates):
                name = [a for a in candidates if a in line][0]
                if name in ["BORIC", "KAST"]:
                    count = int(''.join(line.split(None)[-3].split('.')))
                    percen = float(line.split(None)[-2][:-1].replace(',', '.'))
                else:
                    count = int(''.join(line.split(None)[-2].split('.')))
                    percen = float(line.split(None)[-1][:-1].replace(',', '.'))
                #
                data_votes["Candidate"].append(name)
                data_votes["Votes"].append(count)
                data_votes["Percentage"].append(percen)
            #
            if any(a in line for a in vote_types):
                # print(f"test {line}")
                name = [a for a in vote_types if a in line][0]
                count = int(''.join(line.split(None)[-2].split('.')))
                percen = float(line.split(None)[-1][:-1].replace(',', '.'))
                data_report["Type"].append(name)
                data_report["Votes"].append(count)
                data_report["Percentage"].append(percen)
    #
    return data_report, data_votes

def select_element(wait, tag, click=False):
    """
    Select element...
    """
    if 'render' in tag:
        elem = wait.until(EC.presence_of_element_located((
            By.CSS_SELECTOR, f"li[ng-show={tag}]"))
        )
        if click: elem.click()
    if 'sel' in tag:
        elem = wait.until(EC.presence_of_element_located((
            By.CSS_SELECTOR, f"select[id={tag}]"))
        )
        if click: elem.click()
        options = elem.text.split('\n')[1:]
        return elem, options
    if tag in menus:
        elems = wait.until(EC.presence_of_all_elements_located((
            By.CLASS_NAME, "ng-binding"))
        )
        elem = [e for e in elems if unidecode.unidecode(e.text) == menus[tag]][0]
        if click: elem.click()
        return elem

def get_table(wait):
    """
    Returns table...
    """
    table = wait.until(EC.presence_of_element_located((
        By.ID, "divVotacion"))
    )
    return table

def shorten_region(region):
    """
    Returns short region name...
    """
    shorten_regions = {
        "DE ARICA Y PARINACOTA": "ARICA",
        "DE TARAPACA": "TARAPACA",
        "DE ANTOFAGASTA": "ANTOFAGASTA",
        "DE ATACAMA": "ATACAMA",
        "DE COQUIMBO": "COQUIMBO",
        "DE VALPARAISO": "VALPARAISO",
        "METROPOLITANA DE SANTIAGO": "METROPOLITANA",
        "DEL LIBERTADOR GENERAL BERNARDO O'HIGGINS": "OHIGGINS",
        "DEL MAULE": "MAULE",
        "DE ÑUBLE": "ÑUBLE",
        "DEL BIOBIO": "BIOBIO",
        "DE LA ARAUCANIA": "ARAUCANIA",
        "DE LOS RIOS": "LOS_RIOS",
        "DE LOS LAGOS": "LOS_LAGOS",
        "DE AYSEN DEL GENERAL CARLOS IBAÑEZ DEL CAMPO": "AYSEN",
        "DE MAGALLANES Y DE LA ANTARTICA CHILENA": "MAGALLES",
    }
    return shorten_regions[region]

# TODO: update
def create_dataframe(data, mode, save='csv'):
    """
    Returns dataframe...
    """
    # TODO: update as done with mode = 'region'
    if mode in ['total', 'chile']:
        df_votes = pd.DataFrame.from_dict(data['votes'])
        df_report = pd.DataFrame.from_dict(data['report'])
        if save == 'csv':
            df_votes.to_csv(f"data/votes_{mode}.csv", index=False)
            df_report.to_csv(f"data/report_{mode}.csv", index=False)
    if mode == 'region':
        #
        Region, City = [], []
        Boric, Kast, Provoste, Sichel = [], [], [], []
        Artes, Enriquez, Parisi = [], [], []
        Emitidos, Nulos, Blancos, Total = [], [], [], []
        Boric_per, Kast_per, Provoste_per, Sichel_per = [], [], [], []
        Artes_per, Enriquez_per, Parisi_per = [], [], []
        Emitidos_per, Nulos_per, Blancos_per, Total_per = [], [], [], []
        #
        for k in data:
            for l in data[k]:
                votes = data[k][l]['votes']['Votes']
                votes_per = data[k][l]['votes']['Percentage']
                report = data[k][l]['report']['Votes']
                report_per = data[k][l]['report']['Percentage']
                #
                Boric.append(votes[0])
                Kast.append(votes[1])
                Provoste.append(votes[2])
                Sichel.append(votes[3])
                Artes.append(votes[4])
                Enriquez.append(votes[5])
                Parisi.append(votes[6])
                Emitidos.append(report[0])
                Nulos.append(report[1])
                Blancos.append(report[2])
                Total.append(report[3])
                #
                Boric_per.append(votes_per[0])
                Kast_per.append(votes_per[1])
                Provoste_per.append(votes_per[2])
                Sichel_per.append(votes_per[3])
                Artes_per.append(votes_per[4])
                Enriquez_per.append(votes_per[5])
                Parisi_per.append(votes_per[6])
                Emitidos_per.append(report_per[0])
                Nulos_per.append(report_per[1])
                Blancos_per.append(report_per[2])
                Total_per.append(report_per[3])
                # Region.append(shorten_region(k))
                #
                Region.append(k)
                City.append(l)
        #
        df_votes = pd.DataFrame.from_dict({
            'Region': Region,
            'City': City,
            'Boric': Boric,
            'Kast': Kast,
            'Provoste': Provoste,
            'Sichel': Sichel,
            'Artes': Artes,
            'Enriquez': Enriquez,
            'Parisi': Parisi,
            'Votos_Emitidos': Emitidos,
            'Votos_Nulos': Nulos,
            'Votos_Blancos': Blancos,
            'Votos_Total': Total,
            'Boric_per': Boric_per,
            'Kast_per': Kast_per,
            'Provoste_per': Provoste_per,
            'Sichel_per': Sichel_per,
            'Artes_per': Artes_per,
            'Enriquez_per': Enriquez_per,
            'Parisi_per': Parisi_per,
            'Votos_Emitidos_per': Emitidos_per,
            'Votos_Nulos_per': Nulos_per,
            'Votos_Blancos_per': Blancos_per,
            'Votos_Total_per': Total_per,
        })
        if save == 'csv':
            df_votes.to_csv("data/votes_region.csv", index=False)
            # df_report.to_csv(f"data/report_region.csv", index=False)

def run_parsing(wait, mode, menu):
    """
    Parses data...
    Returns...
    """
    select_element(wait, menu, click=True)    
    
    if menu == "presidente":
        parse_election_president(wait, mode, menu)
    elif menu == "participacion":
        parse_election_participation(wait, mode)        

def parse_election_participation(wait, mode):
    """
    Parses data...
    Returns...
    """
    if mode in ['total', 'chile']:
        select_element(wait, modes[mode], click=True)
        table = get_table(wait)
        report, votes = parse_table_participation(table)
        # create_dataframe(report, votes)
        data = {
            'votes': votes,
        }
        create_dataframe(data, mode)
    if mode == 'region':
        select_element(wait, modes['chile'], click=True)
        select_element(wait, modes[mode], click=True)
        #
        # iterate over regions, parsing votes by city
        data = {}
        elem_region, regions = select_element(wait, 'selRegion', click=False)
        for region in regions:
            print(f"Parsing region: {region}...")   
            elem_region.send_keys(region)
            time.sleep(1.)
            table = get_table(wait)
            votes = parse_table_participation(table)     
            if region not in data:
                data[region] = {}
            data[region] = {
                'votes': votes,
            }
        #
        # create dataframe
        create_dataframe_participation(data, mode, save='csv')            

def create_dataframe_participation(data, mode, save='csv'):
    """
    Returns dataframe...
    """
    # TODO: update as done with mode = 'region'
    # if mode in ['total', 'chile']:
    #     df_votes = pd.DataFrame.from_dict(data['votes'])
    #     if save == 'csv':
    #         df_votes.to_csv(f"data/votes_{mode}.csv", index=False)
    if mode == 'region':
        Region, City = [], []
        pa_mesas, pa_electors = [], []
        pa_votes, pa_percentage = [], []               
        #
        for k in data:
            votes = data[k]['votes']  
            # iterate first on the element (Total), then the remaining cities            
            ll = [-1]+list(range(len(votes['Mesas'])-1))
            for l in ll:
                pa_mesas.append(votes['Mesas'][l])
                pa_electors.append(votes['Electors'][l])                               
                pa_votes.append(votes['Votes'][l])
                pa_percentage.append(votes['Percentage'][l])
                Region.append(k)
                City.append(votes['Cities'][l])                
        #
        df_votes = pd.DataFrame.from_dict({
            'Region': Region,
            'City': City,
            'Participa_mesas': pa_mesas,
            'Participa_electors': pa_electors,
            'Participa_votes': pa_votes,
            'Participa_percentage': pa_percentage,
        })
        if save == 'csv':
            df_votes.to_csv("data/participacion_region.csv", index=False)

def parse_table_participation(table):
    """
    Parses data...
    Returns...
    """
    data_votes = {
        "Mesas": [],
        "Electors": [],
        "Votes": [],
        "Percentage": [],
        "Cities": [],       
    }
    #
    for row in table.find_elements_by_tag_name("tr"):
        line = row.text
        if line == '':
            continue
        if "Total Mesas" in line:
            continue
        #
        percen = float(line.split(None)[-1].replace(',', '.'))
        votes = int(''.join(line.split(None)[-2].split('.')))
        electors = int(''.join(line.split(None)[-3].split('.')))
        mesas = int(''.join(line.split(None)[-4].split('.'))) 
        cities = ' '.join(line.split(None)[:-4])             
        #
        data_votes["Cities"].append(cities)        
        data_votes["Mesas"].append(mesas)
        data_votes["Electors"].append(electors)        
        data_votes["Votes"].append(votes)
        data_votes["Percentage"].append(percen)
    #
    return data_votes

# TODO: update
def parse_election_president(candidates, vote_types, wait, mode, menu):
    """
    Parses data...
    Returns...
    """        
    if mode in ['total', 'chile']:
        select_element(wait, modes[mode], click=True)
        table = get_table(wait)
        report, votes = parse_table(candidates, vote_types, table)
        # create_dataframe(report, votes)
        data = {
            'votes': votes,
            'report': report,
        }
        create_dataframe(candidates, vote_types, data, mode)
    if mode == 'region':
        select_element(wait, modes['chile'], click=True)
        select_element(wait, modes[mode], click=True)
        #
        # iterate over regions
        data = {}
        elem_region, regions = select_element(wait, 'selRegion', click=False)
        for region in regions:
            print(f"Parsing region: {region}...")
            elem_region.send_keys(region)
            time.sleep(1.)
            table = get_table(wait)
            report, votes = parse_table(candidates, vote_types, table)
            # while True:
            #     try:
            #         report, votes = parse_table(candidates, vote_types, table)
            #         break
            #     except StaleElementReferenceException:
            #         pass
            if region not in data:
                data[region] = {}
            data[region]['total'] = {
                'votes': votes,
                'report': report,
            }
            #
            # iterate over cities
            elem_comuna, comunas = select_element(wait, 'selComunas', click=False)
            for comuna in comunas:
                print(f"Parsing comuna: {comuna}...")
                # elem_comuna, comunas = select_element(wait, 'selComunas', click=False)
                elem_comuna.send_keys(comuna)
                time.sleep(1.)
                table = get_table(wait)
                # print(table.text)
                report, votes = parse_table(candidates, vote_types, table)
                # while True:
                #     try:
                #         report, votes = parse_table(candidates, vote_types, table)
                #         break
                #     except StaleElementReferenceException:
                #         time.sleep(2.)
                #         continue
                if comuna not in data[region]:
                    data[region][comuna] = {}
                data[region][comuna]['votes'] = votes
                data[region][comuna]['report'] = report
        #
        # create dataframe
        create_dataframe(data, mode, save='csv')

def main():
    """
    Runs...
    """
    url_init = 'https://www.servelelecciones.cl/'
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(url_init)
    wait = WebDriverWait(driver, 10)
    #
    menu = 'participacion'
    mode = 'total'
    run_parsing(candidates, vote_types, wait, mode, menu)

if __name__ == '__main__':
    main()
