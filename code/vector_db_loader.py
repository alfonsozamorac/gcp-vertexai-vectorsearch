from typing import List
from google.cloud import aiplatform
from langchain_core.documents.base import Document
from langchain_google_vertexai.vectorstores.vectorstores import VectorSearchVectorStore
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from constants import EMBEDDING_MODEL


class VectorDBVertexAILoader:

    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200

    def __init__(self, project_id: str, region: str, gcs_bucket_name: str, index_id: str, index_endpoint_id: str) -> None:
        self.project_id = project_id
        self.region = region
        self.gcs_bucket_name = gcs_bucket_name
        self.index_id = index_id
        self.index_endpoint_id = index_endpoint_id

        self.index = aiplatform.MatchingEngineIndex(self.index_id)
        self.index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
            self.index_endpoint_id)

        self.vectorstore = VectorSearchVectorStore.from_components(
            project_id=self.project_id,
            region=self.region,
            gcs_bucket_name=self.gcs_bucket_name,
            index_id=self.index.name,
            endpoint_id=self.index_endpoint.name,
            embedding=VertexAIEmbeddings(model_name=EMBEDDING_MODEL),
            stream_update=True
        )

    def load_document(self, docs: List[Document], is_complete_overwrite: bool) -> None:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.CHUNK_SIZE,
            chunk_overlap=self.CHUNK_OVERLAP
        )
        chunks = text_splitter.split_documents(docs)
        if not chunks:
            raise Exception(
                "No documents found for the provided document IDs.")

        self.vectorstore.add_documents(
            documents=chunks, is_complete_overwrite=is_complete_overwrite)

    def get_retriever(self):
        return self.vectorstore.as_retriever()
