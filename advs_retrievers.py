import requests
import re
import utils
import argparse

from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

CURRENTMONTH= datetime.now().strftime('%m')
CURRENTYEAR = datetime.now().year
BASEURLADVISORY = "https://advisories.ncsc.nl/advisory?bare=1&format=undefined&id="

def get_matrix_from_advisory_html(adv_html) :
    
    soup = BeautifulSoup(adv_html, "html.parser")
    adv_name_header = soup.find("h1")
    adv_name = adv_name_header.text.strip()
    
    if len(adv_name_header.find_all("p")) > 0 :
            adv_name = adv_name_header.find("p").text.strip()
                      
    first_classification_element=soup.find("tr" , class_="release_lead")
    class_divs = first_classification_element.find_all("div")
    kans = class_divs[0].text.strip()
    schade = class_divs[1].text.strip()
    publish_date = "#N/A"
    
    # let's find the first release date
    release_lead_elements=soup.find_all("tr" , class_="release_lead")
    for rl_element in release_lead_elements :
        date_element = rl_element.find("td", class_="date")
        if date_element :
            publish_date = date_element.text.strip()
                
    prop_matrix = soup.find(id="probability_matrix")
    matrix_names = ["Advisory naam", "Kans", "Schade", "Datum eerste publicatie"]
    matrix_values = [adv_name, kans, schade, publish_date]
    
    tr_matrix_elements = prop_matrix.find_all("tr")
    for matrix_element in tr_matrix_elements :
        matrix_element_name = matrix_element["id"]
        matrix_element_value = matrix_element.find("td", class_="matrix_weight")
        matrix_names.append(matrix_element_name)
        matrix_value = matrix_element_value.text.strip()
        if matrix_element_name == "probability_total" :
            matrix_value = matrix_value.replace("∑\xa0=\xa0", "")
        
        matrix_values.append(matrix_value)


            
    data=[]
    data.append(matrix_values)
    matrix = pd.DataFrame(data, columns=matrix_names)
    return matrix

def get_all_advisories_for_urls(urls) :
        list_advisories = []
        list_adv_numbers = []

        for url in urls:
                resp = requests.get(url=url)
                data=resp.json()
                if data["limited"] > 0:
                        print("Result of request was limited! ", url)
                list_advisories.extend(data['results'])

        df_all_advisories = pd.DataFrame(columns=['Nummer', 'Versie'])

        for advisory in list_advisories :
                advisory_number = advisory[0:14]
                if not advisory_number in list_adv_numbers:
                        list_adv_numbers.append(advisory_number)
                        advisory_version = (re.search(r'\[.*?\]', advisory))[0]
                        advisory_version_clean = advisory_version.replace("[", "").replace("]", "")
                        advisoryURL = BASEURLADVISORY + advisory_number
                        page = requests.get(advisoryURL)
                        df_advisory_matrix=get_matrix_from_advisory_html(page.text)
                        df_advisory_matrix["Nummer"] = advisory_number
                        df_advisory_matrix["Versie"] = advisory_version_clean
                        df_all_advisories= pd.concat([df_all_advisories, df_advisory_matrix])
                else :
                        print(advisory_number + " already found")
                        
        return df_all_advisories

def get_all_advisories(prmMonth=None, prmYear=CURRENTYEAR, prmProb="medium", prmDmg="high") :
        URLs = []
        if prmYear > CURRENTYEAR :
               print("only current year or older (starting 2014)!")
               return URLs
        
        if prmMonth :
                URLs = utils.createURLsForMonth(prmYear, int(prmMonth), prmProb, prmDmg)
        else :
                URLs = utils.createURLsForYear(prmYear, prmProb, prmDmg)
        
        return get_all_advisories_for_urls(URLs)

def createSheetAdvisoriesForMonth(prmExcelFilename, prmSheetName, prmMonth=None, prmYear=CURRENTYEAR, prmProb="medium", prmDmg="high"):
        writer = pd.ExcelWriter(prmExcelFilename, engine='xlsxwriter')
        df_advisories = get_all_advisories(prmMonth, prmYear, prmProb, prmDmg)
        df_advisories.to_excel(writer, prmSheetName, index=False)
        writer.close()
        return "%s successfull created." % (prmExcelFilename)

def getCSVText_all_advisories(prmMonth=None, prmYear=CURRENTYEAR, prmProb="medium", prmDmg="high"):
        return(get_all_advisories(prmMonth, prmYear, prmProb, prmDmg).to_csv())

#little test code
#createSheetAdvisoriesForMonth("mytestsheetMH.xlsx", "MHs")
#createSheetAdvisoriesForMonth("mytestsheetHH.xlsx", "HHs", prmProb="high", prmDmg="high")

parser = argparse.ArgumentParser("Get an Excelsheet with an overview of all the NCSC advisories for a certain period and a certain classification.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--filename", default=None, type=str, help="The name of the Excelsheet to be created. Should have the '.xls(x)' extension. Existing file will be overwritten! If omitted a comma separated text string will be returned.")
parser.add_argument("--sheetname", default="wks1", type=str)
parser.add_argument("--year", default=CURRENTYEAR, type=int, help="The year for which you want the overview")
parser.add_argument("--month", default=None, type=int, help="The month (as an integer) for which you want the overview. If not provided you will the whole year.")
parser.add_argument("--probability", default='medium', type=str, help="The probability classification for which you want the overview")
parser.add_argument("--damage", default='high', type=str, help="The damage classification for which you want the overview")

args=parser.parse_args()

if (args.filename) :
        print(createSheetAdvisoriesForMonth(args.filename, args.sheetname, args.month, args.year, args.probability, args.damage))
else :
        print(getCSVText_all_advisories(prmMonth=args.month, prmYear=args.year, prmProb=args.probability, prmDmg=args.damage))
