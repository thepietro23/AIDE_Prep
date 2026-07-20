import uuid
import requests
from bs4 import BeautifulSoup
from app.models.document import Document
from app.loaders.base_loader import Baseloader

class WebsiteLoader(Baseloader):
    def __init__(self, url):
        self.url = url

    def load(self):
        response = requests.get(self.url, timeout=10)

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        title = soup.title.text.strip() if soup.title else "No Title"

        for tag in soup(["script", "style", "header", "footer", "nav", "aside"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)

        document = Document(
            id=str(uuid.uuid4()),
            title=title,
            content=text,
            source="https://forensiccybertech.com/",
            location=self.url,
            metadata={"source": "web", "url": self.url}
        )

        return [document]