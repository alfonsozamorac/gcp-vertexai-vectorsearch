import os
from typing import Any, List
from atlassian import Confluence
from bs4 import BeautifulSoup
from langchain_core.documents import Document
from secrets_engine import SecretsEngine


class ConfluenceExport:

    def __init__(self) -> None:
        api_token = SecretsEngine(
            '/secrets/confluence-secret-auth').get_secret()
        confluence_url = os.getenv("CONFLUENCE_URL")
        self.client = Confluence(
            url=confluence_url,
            token=api_token
        )

    def get_childs_pages(self, parent_page_id: str) -> List[str]:
        return self.client.get_child_id_list(parent_page_id)

    def export_pages(self, page_list: List[str]) -> List[Document]:
        page_data_list = []
        for page_id in page_list:
            try:
                page = self.client.get_page_by_id(page_id, expand='body.view')
                page_title = page['title']
                page_content = page['body']['view']['value']
                soup = BeautifulSoup(page_content, 'html.parser')
                plain_text = soup.get_text().replace('\xa0', ' ').strip()
                metadata = {"page_title": page_title, "page_id": page_id}
                doc = Document(page_content=plain_text, metadata=metadata)
                page_data_list.append(doc)
            except Exception as e:
                print(f"Error when exporting page with id {page_id}: {str(e)}")
        return page_data_list
