import json
import requests
from AdvancedHTMLParser import AdvancedHTMLParser
from modules.SharedConfig import SharedConfig
from zseilplan.model.OverrideContainer import OverrideContainer
from zseilplan.model.RawOverrideItem import RawOverrideItem


class HTMLOverrideProvider:
    def __init__(self, url: str):
        if not url.endswith("/"):
            url += "/"
        self.url = url
        self.teachermap = {}
        self.output = {}
        return None

    def teachermap_load_from_file(self, filename):
        with open(filename, "r", encoding="UTF-8") as f:
            self.teachermap = json.load(f)

        print(f"Using external teachermap: {filename}")
        return True

    def get_overrides_urls(self):
        r = requests.get(self.url, proxies=SharedConfig().requests_proxies)
        r.encoding = "UTF-8"
        
        if r.status_code != 200:
            return []

        listparser = AdvancedHTMLParser()
        listparser.parseStr(r.text)

        # FIXME: hack.
        panel = listparser.getElementById("panel_srodkowy_szerszy").getHTML()
        listparser = AdvancedHTMLParser()
        listparser.parseStr(panel)

        urls = []

        for li in listparser.getElementsByTagName("a"):
            url = f"{self.url}{li.href}"
            url = url.replace("\\", "/")  # Yes, this happened.

            if not url.endswith(".html"):
                print(f"Skipping: {url} (not a html file)")
                continue

            urls.append(url)

        return urls

    def download_single_override_file(self, url):
        r = requests.get(url, proxies=SharedConfig().requests_proxies)
        r.encoding = "UTF-8"

        if r.status_code != 200:
            print(f"Failed to download: {url} (HTTP {r.status_code})")
            return False

        return r.text

    def parse_single_override_file(self, url):
        date_fallback = url.split("/")[-1].split(".")[0].split("-")[:3]
        html_content = self.download_single_override_file(url)

        parser = AdvancedHTMLParser()
        parser.parseStr(html_content)

        for table in parser.getElementsByTagName("table"):
            self.parse_table(table.getChildren(), date_fallback)
            break  # BUG: Why?
        return

    def parse_table(self, table_elements, date_fallback):
        rows = table_elements.getElementsByTagName("tr")

        self.current_container = None

        for row in rows:
            is_date_header = len(row.getChildren().getElementsByTagName("th")) == 1
            is_column_header = len(row.getChildren().getElementsByTagName("th")) > 1
            is_data_row = not (is_date_header or is_column_header)

            if is_date_header:
                date_text = row.getChildren().getElementsByTagName("th")[0].innerText
                date_text = date_text.split(" ")[1].strip()
                self.current_container = OverrideContainer(date_text)

            elif is_data_row:
                raw_item = RawOverrideItem(row, teachermap=self.teachermap)
                dict_item = raw_item.parse()
                self.current_container.add_override(dict_item)

        # BUG: what if there is >1 OverrideContainer?
        self.output[
            self.current_container.date_text
        ] = self.current_container.get_json()

    def search(self):
        self.overrides_urls = self.get_overrides_urls()
        return True

    def parse(self):
        for url in self.overrides_urls:
            print(f"Parsing override: {url}")
            self.parse_single_override_file(url)

        return self.output