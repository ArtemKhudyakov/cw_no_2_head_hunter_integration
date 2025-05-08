from bs4 import BeautifulSoup


class Viewer:
    def __init__(self, text,):
        self.text = text

    @staticmethod
    def clean_html(text: str) -> str:
        return BeautifulSoup(text, 'html.parser').get_text()