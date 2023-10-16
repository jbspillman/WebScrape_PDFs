"""
Notes:
2023.10.15  - Start to evaluate the project scope.
            UpWork Job URL: > https://www.upwork.com/jobs/~01e042f1d122da0721
            Site to Scrape: >
"""
import os
import time
import datetime
import bs4
import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

current_time_stamp = datetime.datetime.now()
date_stamp = current_time_stamp.strftime("%Y%m%d")
script_path = os.path.dirname(os.path.realpath(__file__))
data_folder = os.path.join('data')
pdfs_html_folder = os.path.join(data_folder, 'pdf_lists')
docs_folder = os.path.join(data_folder, 'ipo-docs')
os.makedirs(data_folder, exist_ok=True)
os.makedirs(pdfs_html_folder, exist_ok=True)
os.makedirs(docs_folder, exist_ok=True)

web_base = "https://search.ipindia.gov.in"
web_pdfs = "/IPOJournal/Journal/Patent"
web_get = "/IPOJournal/Journal/ViewJournal"
pdf_page = web_base + web_pdfs


def get_pdf_urls(web_url):
    print("Entered:".ljust(30), "get_pdf_urls")
    today_pdf_list = os.path.join(pdfs_html_folder, date_stamp + "_pdf_listing.txt")
    if not os.path.exists(today_pdf_list):
        html_page = requests.get(web_url, verify=False).content
        soup_page = bs4.BeautifulSoup(html_page, features="html.parser")
        with open(today_pdf_list, 'w', encoding="utf-8") as f:
            for pdf_link in soup_page.find_all("input"):
                the_pdf = str(pdf_link).replace('<input name="FileName" type="hidden" value="', '').replace('"/>', '')
                f.write(the_pdf + "\n")

    """ file is downloaded, read the file in and send back. """
    with open(today_pdf_list, 'r', encoding="utf-8") as f:
        input_lines = f.read()
    return input_lines


def download_pdfs(data):
    print("Entered:".ljust(30), "download_pdfs")

    x = 0
    files = 0
    for line in data.split("\n"):
        x += 1
        pdf_name = ""
        local_folder = ""
        for item in line.split("\\"):
            if ".pdf" not in item:
                local_folder += item + os.sep
            else:
                pdf_name = item
        local_folder = local_folder.rstrip(os.sep)
        save_to = os.path.join(data_folder, local_folder)
        out_pdf = os.path.join(save_to, pdf_name)
        if not os.path.exists(out_pdf):
            print("Get.".ljust(30), pdf_name.ljust(70))
            os.makedirs(save_to, exist_ok=True)
            post_url = web_base + web_get
            fd = {
                "FileName": line
            }
            t0 = time.time()
            r = requests.post(post_url, data=fd, verify=False)
            if r.status_code == 200:
                with open(out_pdf, 'wb') as f:
                    f.write(r.content)
                elapsed = time.time() - t0

                file_stats = os.stat(out_pdf)
                size_mb = round(file_stats.st_size / (1024 * 1024), 2)
                print(" Wrote.".ljust(30), pdf_name.ljust(70), elapsed, "Secs.".ljust(10), str(size_mb).rjust(20), "MB")
                files += 1
            else:
                print("ERROR:".ljust(30), r.status_code)
                print("ERROR:".ljust(30), r.text)
                time.sleep(24)

        else:
            file_stats = os.stat(out_pdf)
            size_mb = round(file_stats.st_size / (1024 * 1024), 2)
            files += 1
            print("Exists.".ljust(30), pdf_name.ljust(70), 0, "Secs.".ljust(10), str(size_mb).rjust(20), "MB")

    print("Created:", files, "from list of:", x)


def main():

    pdf_links = get_pdf_urls(pdf_page)  # gets the pdf links on the page.
    download_pdfs(pdf_links)  # download pdfs to folders.


if __name__ == '__main__':
    main()
