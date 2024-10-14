from google.cloud import aiplatform

from confluence_export import ConfluenceExport
from vector_db_loader import VectorDBVertexAILoader
from constants import REGION, BUCKET


class IndexUpdater:

    def __init__(self, project_id, index_id, index_endpoint_id):
        self.project_id = project_id
        self.index_id = index_id
        self.index_endpoint_id = index_endpoint_id

    def update_index(self, page_ids, complete_overwrite) -> None:
        print("Exporting Confluence pages...")
        confluence_export = ConfluenceExport()
        confluence_pages = confluence_export.export_pages(page_ids)
        for parent_id in page_ids:
            child_page_ids = confluence_export.get_childs_pages(parent_id)
            confluence_pages.extend(
                confluence_export.export_pages(child_page_ids))

        print("Loading documents in VectorDB GCP")
        aiplatform.init(
            project=self.project_id,
            location=REGION,
        )
        vector_loader = VectorDBVertexAILoader(
            self.project_id, REGION, BUCKET, self.index_id, self.index_endpoint_id)

        vector_loader.load_document(confluence_pages, complete_overwrite)
        print("Documents succesfully loaded!")
