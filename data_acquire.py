import requests
from bs4 import BeautifulSoup
# import re
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

    # title_tag = [spec.find('h3', class_='title').find('a') for spec in course_links]

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

    # Extract course name
    course_name = soup.find('h1', class_='page-title').text.strip()

    # Extract department
    department_tag = soup.find('span', string="Кафедра:")
    department = department_tag.find_next(
        'a').text.strip() if department_tag else "Department information not available"

    # Extract lecturers and emails (assuming emails could be found on their profile page, if needed)
    lecturers = []

    lecturer_links_practical = soup.select('section.practical .teachers a')
    lecturer_links_lectures = soup.select('section.lectures .lecturer a')
    all_lecturer_links = lecturer_links_practical + lecturer_links_lectures

    for link in all_lecturer_links:
        lecturers.append({
            "name": link.text.strip(),
            "profile": urljoin(url, link['href'])
        })

    # Extract recommended literature
    literature_section = soup.find('section', class_='materials')
    literature = []
    if literature_section:
        literature_texts = literature_section.find_all('p')
        for lit in literature_texts:
            literature.append(lit.text.strip())

    # Find syllabus link(s) and download
    syllabus_links = soup.select('section.attachments a[href$=".pdf"]')
    syllabus_info = []
    for slink in syllabus_links:
        syllabus_url = urljoin(url, slink['href'])
        pdf_filename = slink.text.strip() + ".pdf"
        download_pdf(syllabus_url, pdf_filename)
        pdf_data = fetch_pdf(pdf_filename)
        syllabus_info.append({slink, pdf_data})
        os.remove(pdf_filename)  # Clean up downloaded PDF after processing

    return {
        "name": course_name,
        "department": department,
        "lecturers": [lect["name"] for lect in lecturers],
        "lecturer_links": [lect["profile"] for lect in lecturers],
        "syllabus_info": syllabus_info,
        "link_to_course": url,
        "literature": literature
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

## Fetches info from PDF for extracting to course
import pandas as pd

def fetch_pdf(filename):
    tables = camelot.read_pdf(filename, pages='all', flavor='lattice')

    if len(tables) == 0:
        # If no tables found, try 'stream' mode
        tables = camelot.read_pdf(filename, pages='all', flavor='stream')

    all_tables_data = []
    # Process extracted tables
    for table in tables:
        # Convert table to a pandas DataFrame
        table_data = table.df

        # If the table contains NaN values, drop them before writing to CSV
        if table_data.isnull().values.any():
            table_data = table_data.dropna()

        # Convert the DataFrame to a CSV string and save it to the CSV file
        csv_string = table_data.to_csv(index=False, header=not all_tables_data)
        with open(f"{filename}_parsed.csv", 'a', encoding='utf-8') as f:
            f.write(csv_string)

        all_tables_data.append(table_data.to_dict('records'))

    # literature_entries = process_literature(all_tables_data)

    # os.remove(f"{filename}_parsed.json")

    # return literature_entries

## NLP processing of literature to identify language
## for each literature entry in an array
def nlp_literature(literature):

    return {
        "literature": literature,
        "all_entries": 0,
        "ukrainian_entries": 0,
        "moscowian_entries": 0
    }

def process_literature_tables(tables):
    literature_entries = []  # To store concatenated literature entries
    in_literature_section = False  # Flag to track whether we're processing a literature section

    for table in tables:
        df = table.df
        for index, row in df.iterrows():
            if ("Література для вивчення дисципліни" in row[0]):
                in_literature_section = True  # We've entered a literature section
                literature_entries.extend(row[1:].dropna().tolist())  # Add initial entries, ignoring NaNs
            elif in_literature_section and row[0].strip() == "":
                # We're in a literature continuation section
                literature_entries.extend(row[1:].dropna().tolist())  # Append continuation entries
            else:
                in_literature_section = False  # We've exited the literature section

    return literature_entries

def extract_tables_from_pdf_to_literature_list(filename):
    # Extract tables from the PDF
    tables = camelot.read_pdf(filename, pages='all', flavor='stream', split_text=True)

    # Process the extracted tables to consolidate literature entries
    literature_list = process_literature_tables(tables)

    return literature_list
def analyze_string_by_lang(string):
    return 0


import pandas as pd

import csv


def process_literature_from_csv(csv_path):
    literature_started = False
    literature_entries = []
    processed_entries = []

    with open(csv_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if "Література для вивчення дисципліни" in row[0]:
                literature_started = True
                literature_entries.append(row[1:])
                continue

            if literature_started:
                if row[0].strip() == "" and len(row) > 1:
                    # This is a continuation of literature entries, append directly
                    literature_entries.append(row[1:])
                elif row[0].strip() != "":
                    # This signals the end of literature section if it's not a continuation row
                    literature_started = False

    # Assuming literature entries may contain numerical prefixes like "1. ..."
    for entry in literature_entries:
        # Splitting each entry by known patterns, e.g., "\n\d+\." for newline followed by a number and a dot
        # This requires flattening the list if `entry` itself contains multiple items
        if isinstance(entry, list):
            for sub_entry in entry:
                split_entries = re.findall(r'\d+\..+', sub_entry)
                processed_entries.extend(split_entries)
        else:
            split_entries = re.findall(r'\d+\..+', entry)
            processed_entries.extend(split_entries)

    return processed_entries


def main():
    faculty_details = fetch_faculty(FACULTY_URL)
    # faculty_details = remove_duplicates()

    # Write to JSON file
    with open(f'{FACULTY_NAME}.json', 'w', encoding='utf-8') as f:
        json.dump(faculty_details, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    # filename = "discrete.pdf"
    # fetch_pdf(filename)
    # print(literature_entries)
    csv_file_path = 'discrete.pdf_parsed.csv'
    literature_list = process_literature_from_csv(csv_file_path)
    for entry in literature_list:
        print(entry)
