import requests
from bs4 import BeautifulSoup
import re
import json
import os
from urllib.parse import urljoin
import camelot

# Configuration
FACULTY_URL = "https://kultart.lnu.edu.ua/academics/bachelor"
FACULTY_NAME = "Факультет культури та мистецтв"

## @param url - The link to bachelors or masters degree page should be pasted as in FACULTY_URL
## @return json string with the ${FACULTY_NAME}:
## {
##   {
##      "spec_name": specialty_name1,
##       "courses": {
##          "subj1": {
##             "lecturers": [...]
##             "emails": [...]
##             "department": " .. "
##             "link_to_syllabus": " ... "
##             "link_to_course": " ... "
##             "literature": [ ... ]
##             "number_of_lit": "..."
##             "number_of_ukrainian": "..."
##             "number_of_moscowian": "..."
##         },
##         ......
##      }
##    },
##   {
##      "spec_name": specialty_name2,
##       "courses": {
##          "subj1": {
##             "lecturers": [...]
##             "emails": [...]
##             "department": " .. "
##             "link_to_syllabus": " ... "
##             "link_to_course": " ... "
##             "literature": [ ... ]
##             "number_of_lit": "..."
##             "number_of_ukrainian": "..."
##             "number_of_moscowian": "..."
##         },
##         .....
##      }
##    },
##    .....
## }
def fetch_faculty(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    specialties = soup.find_all('section', class_='specialization')  # Adapt to find specialty links
    specialty_links = [url + spec.find('h3', class_='title').find('a')['href'] for spec in specialties]

    faculty_data = []
    for link in specialty_links:
        specialty_data = fetch_specialty(link)
        faculty_data.append(specialty_data)

    return json.dumps({FACULTY_NAME: faculty_data}, ensure_ascii=False, indent=4)

## @param url – The link to one specialty
## @return json formatted string:
## {
##      "name": specialty_name
##      "courses": {
##         "subj1": {
##            "lecturers": [...]
##            "emails": [...]
##            "department": " .. "
##            "link_to_syllabus": " ... "
##            "link_to_course": " ... "
##            "literature": [ ... ]
##             "number_of_lit": "..."
##             "number_of_ukrainian": "..."
##             "number_of_moscowian": "..."
##      }
##    }
## }
def fetch_specialty(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    course_links = [a['href'] for a in soup.select('td.title a') if 'course' in a['href']] # Find the actual course links
    specialty_name = soup.find('h3', class_='title').find('a').text.strip()

    courses_data = {}
    for link in course_links:
        course_name, course_details = extract_course_details(link)
        courses_data[course_name] = course_details

    return {"spec_name": specialty_name, "courses": courses_data}

## @param url – The link to each course in a certain specialty
## @return json formatted string:
## {
##    "subj1": {
##       "lecturers": [...]
##       "emails": [...]
##       "department": " .. "
##       "link_to_syllabus": " ... "
##       "link_to_course": " ... "
##       "literature": [ ... ]
##        "number_of_lit": "..."
##        "number_of_ukrainian": "..."
##        "number_of_moscowian": "..."
##     },
##     "subj2": {
##       "lecturers": [...]
##       "emails": [...]
##       "department": " .. "
##       "link_to_syllabus": " ... "
##       "link_to_course": " ... "
##       "literature": [ ... ]
##        "number_of_lit": "..."
##        "number_of_ukrainian": "..."
##        "number_of_moscowian": "..."
##     },
##     .....
## }
def extract_course_details(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    # Example: Extract faculty, department, and literature as arrays
    faculty = soup.find(...)  # Adapt based on actual HTML structure
    department = soup.find(...)
    literature = soup.find_all(...)
    pdf_link = soup.find('a', href=True, text=re.compile("syllabus", re.IGNORECASE))['href']

    # Download syllabus PDF
    pdf_filename = f"{faculty}.pdf"
    download_pdf(pdf_link, pdf_filename)

    # Extract information from PDF
    # Adapt based on your needs, whether tables or text
    tables = camelot.read_pdf(pdf_filename, pages='all', flavor='lattice')
    syllabus_info = [table.df for table in tables]

    # Append or process PDF info as needed
    # ...

    os.remove(pdf_filename)  # Clean up downloaded PDF

    return {
        "faculty": faculty,
        "department": department,
        "literature": literature,
        "syllabus_info": syllabus_info
    }


## Removes duplicates for each specialty
## because we parse website for literature and PDF, so it can be duplicated
def remove_duplicates(data):
    # Implement deduplication logic based on your data structure
    # This might involve converting lists to sets or using pandas for DataFrame deduplication
    return data

## Downloads PDF from ${pdf_url} into file named ${filename}
def download_pdf(pdf_url, filename):
    response = requests.get(pdf_url)
    with open(filename, 'wb') as f:
        f.write(response.content)


def main():
    faculty_details = fetch_faculty(FACULTY_URL)
    # faculty_details = remove_duplicates()

    # Write to JSON file
    with open('course_data.json', 'w', encoding='utf-8') as f:
        json.dump(faculty_details, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
