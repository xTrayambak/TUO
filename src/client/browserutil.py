import webbrowser


class BrowserUtil:
    def __init__(self):
        self.urls = []

    def open(self, url: str = "https://fsf.org"):
        self.urls.append(url)
        webbrowser.open(url, 1)
