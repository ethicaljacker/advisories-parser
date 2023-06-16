from bs4 import BeautifulSoup
import pandas as pd

def get_matrix_from_advisory_html(adv_html) :
    
    soup = BeautifulSoup(adv_html, "html.parser")
    adv_name_header = soup.find("h1")
    adv_name = adv_name_header.text.strip()
    print(adv_name)
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

strEx = open('example_advisory.html', 'r').read()

print(get_matrix_from_advisory_html(strEx))