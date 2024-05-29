# Faculty Data Processing Scripts

This repository contains scripts designed to parse and clean data from faculty department web pages. The scripts are organized to first parse data using `pdf_parse.py` and then clean the resulting CSV files using `clean_data.py`.

## Prerequisites

Before running the scripts, ensure you have Python installed on your machine along with the necessary Python libraries:
- aiohttp
- bs4 (BeautifulSoup)
- python-dotenv
- PyPDF2
- python-docx
- regex
- langdetect

You can install these dependencies via pip:

```bash
pip install aiohttp beautifulsoup4 python-dotenv PyPDF2 python-docx regex langdetect
```

For the case `pip` doesn't work:
```bash
pip3 install aiohttp beautifulsoup4 python-dotenv PyPDF2 python-docx regex langdetect 
```

## Configuration

1. **Environment Variables:** Before running the scripts, ensure that the `.env` file is correctly set up with the appropriate URLs and file paths that the scripts will reference. An example of the content of `.env` file is provided below:

    ```plaintext
    FACULTY_URL="https://example.com/about/departments"
    FACULTY_NAME="examplefaculty"
    CSV_DEPARTMENTS="${FACULTY_NAME}1.csv"
    CSV_COURSES="${FACULTY_NAME}2.csv"
    ```

2. **Edit the Bash script:** Modify the `faculty_names` and `faculty_urls` arrays in the `run.sh` script to match the faculties you wish to process.

## Usage

To use the scripts, follow these steps:

0. **Edit the `run.sh` file to include proper faculty names and URLs.**

1. **Make the script executable:**
   ```bash
   chmod +x run.sh
   ```

3. **Run the script:**
   ```bash
   ./run.sh
   ```

The script will execute `pdf_parse.py` for each faculty defined in the Bash script, wait for the necessary CSV files to be created, and then execute `clean_data.py` to clean the data. Progress updates will be printed to the console.

## Expected Output

After successful execution, you should find the following files in your directory:
- Two CSV files for each faculty (one from parsing, one cleaned) as specified in the `.env` file.
- Additional logs in the console regarding the execution status.

## Troubleshooting

- **Script Execution Takes Too Long:** If the scripts take longer than expected, check the console output for any errors or issues that might be occurring during the execution.
- **Missing Files:** If the expected CSV files are not being generated, ensure that the `pdf_parse.py` script is completing successfully and without errors. Check for correct URLs and valid HTML structures that the script expects.

---

Make sure to adjust the repository URL and any specific variables or paths as necessary for your actual setup. This README provides a clear, structured guide for users to get started with the scripts in your repository.