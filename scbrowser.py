from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse, urljoin
from tkinter import Tk, Label, messagebox, Entry, Button, PhotoImage, Listbox
import threading
import os
import requests

class SimpleBrowser:
    def __init__(self, master):
        self.master = master
        master.title("scbrowser")

        self.text = Label(master, font=("Helvetica", 12), wraplength=500, justify="left")
        self.text.pack(expand=True, fill="both")
        self.url_entry = Entry(master, font=("Helvetica", 12), name="entry")
        self.url_entry.pack(fill="x")
        self.url_entry.bind("<Return>", self.load_url)
        self.browser_parser = None

    def load_url(self, event):
        url = self.url_entry.get()
        threading.Thread(target=self.load_url_thread, args=(url,)).start()

    def load_url_thread(self, url):
        self.browser_parser = BrowserParser()
        if not self.browser_parser.is_allowed(url):
            messagebox.showwarning("경고", "robots.txt에 의해 차단됨. code: 3")
            return

        try:
            req = Request(url, headers={'User-Agent': "scbrowser/0.1.0-build-1"})
            response = urlopen(req)
            main_site = urlparse(url)
            self.browser_parser.main_site = f"{main_site.scheme}://{main_site.netloc}"
            html_content = response.read().decode("utf-8")

            self.master.after(0, self.display_html(html_content))
        except Exception as e:
           messagebox.showerror("경고", f"연결 실패: {str(e)} code: 1")

    def display_html(self, html_content):
        self.browser_parser.parse_html(html_content)
        for child in root.winfo_children():
            if child != self.url_entry:
                child.destroy()

        self.master.after(0, lambda: self.browser_parser.display_tags(root))


class BrowserParser:
    def __init__(self, main_site="https://example.com"):
        self.soup = None
        self.main_site = main_site
        self.robot_parser = None

    def is_allowed(self, url):
        if self.robot_parser is None:
            self.robot_parser = RobotFileParser()
            self.robot_parser.set_url(urljoin(self.main_site, '/robots.txt'))
            self.robot_parser.read()

        return self.robot_parser.can_fetch("*", url)

    def get_tag_info(self, tag):
        tag_attrs = tag.attrs
        return tag_attrs

    def parse_html(self, html_content):
        self.soup = BeautifulSoup(html_content, 'html.parser')

    def display_tag_(self, parent, tag2):
        for tag in tag2.find_all():
            if tag.name == "h1":
                Label(parent, text=f'{tag.text}', font=("Helvetica", 24)).pack()
            elif tag.name == "div":
                self.display_tag_(parent, tag)
            elif tag.name == 'img':
                img_src = tag['src']
                local_path = self.download_and_cache_image(img_src)
                if local_path:
                    self.display_image(parent, local_path)
            elif tag.name == 'script':
                messagebox.showwarning("경고", f"경고: {tag}가 차단됐습니다 code: 2")
            elif tag.name == 'a':
                attrs = self.get_tag_info(tag)
                Button(parent, text=attrs["href"]).pack()
            elif tag.name == 'ul':
                listbox = Listbox(parent)
                num = 0
                for tag3 in tag.find_all():
                    listbox.insert(num, tag3.text)
                    num += 1
                listbox.pack()

    def download_and_cache_image(self, img_src):
        image_url = urljoin(self.main_site, img_src)
        local_path = os.path.join("image_cache", urlparse(image_url).netloc, f"{os.path.basename(urljoin(self.main_site, img_src))}.jpg")

        if os.path.exists(local_path):
            return local_path

        try:
            response = requests.get(image_url)
            response.raise_for_status()

            with open(local_path, 'wb') as file:
                file.write(response.content)

            return local_path
        except requests.exceptions.RequestException as e:
            return None

        except FileNotFoundError:
            os.makedirs(os.path.join("image_cache", urlparse(image_url).netloc))
            response = requests.get(image_url)
            response.raise_for_status()

            with open(local_path, 'wb') as file:
                file.write(response.content)

    def display_image(self, parent, local_path):
        img_label = Label(parent)
        img_label.image = PhotoImage(file=local_path)
        img_label.configure(image=img_label.image)
        img_label.pack()

    def display_tags(self, parent):
        for tag in self.soup.find_all():
            if tag.name == "h1":
                Label(parent, text=f'{tag.text}', font=("Helvetica", 24)).pack()
            elif tag.name == "div":
                self.display_tag_(parent, tag)
            elif tag.name == 'img':
                img_src = tag['src']
                local_path = self.download_and_cache_image(img_src)
                if local_path:
                    self.display_image(parent, local_path)
            elif tag.name == 'script':
                messagebox.showwarning("경고", f"경고: {tag}가 차단됐습니다 code: 2")
            elif tag.name == 'a':
                attrs = self.get_tag_info(tag)
                Button(parent, text=attrs["href"]).pack()

            elif tag.name == 'ul':
                listbox = Listbox(parent)
                num = 0
                for tag3 in tag.find_all():
                    listbox.insert(num, tag3.text)
                    num += 1
                listbox.pack()

if __name__ == "__main__":
    root = Tk()
    browser = SimpleBrowser(root)
    root.mainloop()
