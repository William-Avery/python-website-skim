import requests, csv, json, sys
import urllib.parse
from bs4 import BeautifulSoup
from pandas import json_normalize

address_list = []
result_list = []
MAX_CHILD_LIMIT = 3 # Doing too many triggers antiscrape
uri = "https://www.truepeoplesearch.com/results?"

def ReadPageInfo(url):
    response = requests.get(url)
    # Parse webpage content
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Get Name
    name = soup.find_all('span', class_ = 'h2', )[0].get_text()
    
    # Loop through and get phones
    phones = []
    phone_rows = soup.find_all('a', {'data-link-to-more': "phone"})
    for phone in phone_rows:
        phones.append(phone.get_text())

    # Loop through emails and find data
    emails = []
    email_section = soup.find_all('div', class_ = 'col-12 col-sm-11')[4]
    email_results = email_section.find_all('div', class_ = "content-value")
    for email in email_results:
        value = email.get_text()
        emails.append(value.strip())
    
    # Create profile object
    profile = {
        "name": name,
        "phones": phones,
        "email": emails,
    }
    return profile
 
def ReadCSV():
    with open('input.csv', newline='') as csvfile:
        sheet = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in sheet:
            address_list.append(row)

def WriteCSV(data):
    df = json_normalize(data)
    df.to_csv("output.csv")

def GetResults():
    for address in address_list:
        City = address[1].lstrip()
        State = address[2].strip()
        CSZ = f'{City}, {State}'

        for i in range(MAX_CHILD_LIMIT):
            params = {
                "streetaddress": address[0],
                "citystatezip": CSZ,
                "rid": f'0x{i}'
            }

            url = uri + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
            profile = ReadPageInfo(url)
            profile["address"] = address[0]
            profile["city"] = City
            profile["state"] = State
            result_list.append(profile)

if __name__ == "__main__":
    print("Reading input.csv...")
    ReadCSV()
    print("Getting Results...")
    GetResults()
    print("Writing to output.csv...")
    WriteCSV(result_list)
    print("Done!")