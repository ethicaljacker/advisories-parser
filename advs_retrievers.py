import requests
import re

from bs4 import BeautifulSoup
import pandas as pd

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

def get_all_advisories(urls) :
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
                        advisoryURL = baseURLAdvisory + advisory_number
                        page = requests.get(advisoryURL)
                        df_advisory_matrix=get_matrix_from_advisory_html(page.text)
                        df_advisory_matrix["Nummer"] = advisory_number
                        df_advisory_matrix["Versie"] = advisory_version_clean
                        df_all_advisories= pd.concat([df_all_advisories, df_advisory_matrix])
                else :
                        print(advisory_number + " already found")
                        
        return df_all_advisories

baseURLAdvisory = "https://advisories.ncsc.nl/advisory?bare=1&format=undefined&id="

urlsMH2023 = [
        "https://advisories.ncsc.nl/ajax/search?from=30-04-2023&to=31-05-2023&words=&prob[]=medium&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=31-03-2023&to=30-04-2023&words=&prob[]=medium&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-02-2023&to=31-03-2023&words=&prob[]=medium&dmg[]=high", 
        "https://advisories.ncsc.nl/ajax/search?from=01-01-2023&to=01-02-2023&words=&prob[]=medium&dmg[]=high"]


urlsMH2022 = [
        "https://advisories.ncsc.nl/ajax/search?from=01-12-2022&to=01-01-2023&words=&prob[]=medium&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-11-2022&to=01-12-2022&words=&prob[]=medium&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-10-2022&to=01-11-2022&words=&prob[]=medium&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-09-2022&to=01-10-2022&words=&prob[]=medium&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-08-2022&to=01-09-2022&words=&prob[]=medium&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-07-2022&to=01-08-2022&words=&prob[]=medium&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-06-2022&to=01-07-2022&words=&prob[]=medium&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-05-2022&to=01-06-2022&words=&prob[]=medium&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-04-2022&to=01-05-2022&words=&prob[]=medium&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-03-2022&to=01-04-2022&words=&prob[]=medium&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-02-2022&to=01-03-2022&words=&prob[]=medium&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-01-2022&to=01-02-2022&words=&prob[]=medium&dmg[]=high",
        ]

urlsMH2021 = [
        "https://advisories.ncsc.nl/ajax/search?from=01-12-2021&to=01-01-2022&words=&prob[]=medium&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-11-2021&to=01-12-2021&words=&prob[]=medium&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-10-2021&to=01-11-2021&words=&prob[]=medium&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-09-2021&to=01-10-2021&words=&prob[]=medium&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-08-2021&to=01-09-2021&words=&prob[]=medium&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-07-2021&to=01-08-2021&words=&prob[]=medium&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=15-06-2021&to=01-07-2021&words=&prob[]=medium&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-06-2021&to=15-06-2021&words=&prob[]=medium&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-05-2021&to=01-06-2021&words=&prob[]=medium&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=15-04-2021&to=01-05-2021&words=&prob[]=medium&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-04-2021&to=15-04-2021&words=&prob[]=medium&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-03-2021&to=01-04-2021&words=&prob[]=medium&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-02-2021&to=01-03-2021&words=&prob[]=medium&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-01-2021&to=01-02-2021&words=&prob[]=medium&dmg[]=high",
        ]       
 
urlsMH2020 = [
        "https://advisories.ncsc.nl/ajax/search?from=01-12-2020&to=01-01-2021&words=&prob[]=medium&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-11-2020&to=01-12-2020&words=&prob[]=medium&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-10-2020&to=01-11-2020&words=&prob[]=medium&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-09-2020&to=01-10-2020&words=&prob[]=medium&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-08-2020&to=01-09-2020&words=&prob[]=medium&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-07-2020&to=01-08-2020&words=&prob[]=medium&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-06-2020&to=01-07-2020&words=&prob[]=medium&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-05-2020&to=01-06-2020&words=&prob[]=medium&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-04-2020&to=01-05-2020&words=&prob[]=medium&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-03-2020&to=01-04-2020&words=&prob[]=medium&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-02-2020&to=01-03-2020&words=&prob[]=medium&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-01-2020&to=01-02-2020&words=&prob[]=medium&dmg[]=high",
        ]
    
urlsHH = [
        "https://advisories.ncsc.nl/ajax/search?from=01-01-2023&to=31-03-2023&words=&prob[]=high&dmg[]=high", 
        "https://advisories.ncsc.nl/ajax/search?from=01-10-2022&to=01-01-2023&words=&prob[]=high&dmg[]=high", 
        "https://advisories.ncsc.nl/ajax/search?from=01-07-2022&to=01-10-2022&words=&prob[]=high&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-04-2022&to=01-07-2022&words=&prob[]=high&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-01-2022&to=01-04-2022&words=&prob[]=high&dmg[]=high",        
        "https://advisories.ncsc.nl/ajax/search?from=01-10-2021&to=01-01-2022&words=&prob[]=high&dmg[]=high", 
        "https://advisories.ncsc.nl/ajax/search?from=01-07-2021&to=01-10-2021&words=&prob[]=high&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-04-2021&to=01-07-2021&words=&prob[]=high&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-01-2021&to=01-04-2021&words=&prob[]=high&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-10-2020&to=01-01-2021&words=&prob[]=high&dmg[]=high", 
        "https://advisories.ncsc.nl/ajax/search?from=01-07-2020&to=01-10-2020&words=&prob[]=high&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-04-2020&to=01-07-2020&words=&prob[]=high&dmg[]=high",
        "https://advisories.ncsc.nl/ajax/search?from=01-01-2020&to=01-04-2020&words=&prob[]=high&dmg[]=high"]
 
urls1 = ["https://advisories.ncsc.nl/ajax/search?from=20-03-2023&to=31-03-2023&words=&prob[]=medium&dmg[]=high"]


writer = pd.ExcelWriter("MHHH-2023.xlsx", engine='xlsxwriter')

""" df_all_MH_advsories_2020 = get_all_advisories(urlsMH2020)
print("Finished 2020")
df_all_MH_advsories_2021 = get_all_advisories(urlsMH2021)
print("Finished 2021")
df_all_MH_advsories_2022 = get_all_advisories(urlsMH2022)
print("Finished 2022") """
df_all_MH_advsories_2023 = get_all_advisories(urlsMH2023)
print("Finished 2023")

df_all_MH_advsories_2023.to_excel(writer, sheet_name="MH2023", index=False)

df_all_HH_advisories_2022_23 = get_all_advisories(urlsHH)
print("Finished HHs")

# df_all_MH_advsories_2020.to_excel(writer, sheet_name="MH2020", index=False)
# df_all_MH_advsories_2021.to_excel(writer, sheet_name="MH2021", index=False)
# df_all_MH_advsories_2022.to_excel(writer, sheet_name="MH2022", index=False)
df_all_HH_advisories_2022_23.to_excel(writer, sheet_name="HH", index=False)

writer.close()
        
