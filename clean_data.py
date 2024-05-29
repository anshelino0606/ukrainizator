import csv
import os
from dotenv import load_dotenv

load_dotenv()

CSV_COURSES = os.getenv("CSV_COURSES")
CSV_DEPARTMENTS = os.getenv("CSV_DEPARTMENTS")
FACULTY_NAME = os.getenv("FACULTY_NAME")


def clean_lecturer_name(name):
    titles = [
        "професор", "проф.", "доцент", "доц.", "доцент,",
        "ст. наук. співробітник", "професор,", "проф.,", "доц.,",
        "ст. наук. співробітник,", ","
    ]
    clean_name = name
    for title in titles:
        clean_name = clean_name.replace(title, "")  # Remove the title from the name
    clean_name = clean_name.replace("\N{NBSP}", " ")
    return clean_name.strip()  # Trim whitespace and return


def clean_csv_lecturer_names(input_filename, output_filename):
    with open(input_filename, mode='r', encoding='utf-8') as infile, \
            open(output_filename, mode='w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile)
        fields = reader.fieldnames
        writer = csv.DictWriter(outfile, fieldnames=fields)
        writer.writeheader()

        for row in reader:
            # Assuming the lecturer's name is under the 'Lecturers' column
            if 'Lecturers' in row:
                row['Lecturers'] = clean_lecturer_name(row['Lecturers'])
            writer.writerow(row)


if __name__ == "__main__":
    input1_csv = f'departments_{CSV_DEPARTMENTS}.csv'
    input2_csv = f'courses_{CSV_COURSES}.csv'
    output1_csv = f'{CSV_DEPARTMENTS}.csv'
    output2_csv = f'{CSV_COURSES}.csv'
    clean_csv_lecturer_names(input1_csv, output1_csv)
    clean_csv_lecturer_names(input2_csv, output2_csv)
