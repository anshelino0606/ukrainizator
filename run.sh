#!/bin/bash

# Change it based on your needs and faculty list
faculty_names=("kultart" "mmf" "economic")
# shellcheck disable=SC2054
faculty_urls=("https://kultart.lnu.edu.ua/about/departments", "https://new.mmf.lnu.edu.ua/about/departments", "https://econom.lnu.edu.ua/about/departments")

length=${#faculty_names[@]}

for (( i=0; i<${length}; i++ )); do
    # Set environment variables
    echo "FACULTY_URL=\"${faculty_urls[$i]}\"" > .env
    echo "FACULTY_NAME=\"${faculty_names[$i]}\"" >> .env
    echo "CSV_DEPARTMENTS=\"${faculty_names[$i]}1.csv\"" >> .env
    echo "CSV_COURSES=\"${faculty_names[$i]}2.csv\"" >> .env

    # Execute the Python script for parsing data
    python pdf_parse.py

    departments_csv="departments_${faculty_names[$i]}1.csv"
    courses_csv="courses_${faculty_names[$i]}2.csv"

    while [[ ! -f "$departments_csv" || ! -f "$courses_csv" ]]; do
        echo "Waiting for $departments_csv and $courses_csv to be created..."
        sleep 1500
    done

    echo "CSV files found. Starting data cleaning..."

    # Execute the Python script for cleaning data
    python clean_data.py

    echo "Data cleaning completed for ${faculty_names[$i]}."
done

echo "Processing complete."