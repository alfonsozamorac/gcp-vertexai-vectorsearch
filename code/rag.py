import argparse
from google.cloud import aiplatform

from vector_db_loader import VectorDBVertexAILoader
from rag_chat import RAGChatBot
from constants import REGION, BUCKET, GCS_BUCKET_URI, MODEL


class ChatBot():

    def __init__(self, project_id, index_id, index_endpoint_id) -> None:
        self.project_id = project_id
        self.index_id = index_id
        self.index_endpoint_id = index_endpoint_id

    def resolve_question(self, question):
        aiplatform.init(project=self.project_id, location=REGION,
                        staging_bucket=GCS_BUCKET_URI)
        print("Getting retriever")
        vector_loader = VectorDBVertexAILoader(
            self.project_id, REGION, BUCKET, self.index_id, self.index_endpoint_id)
        retriever = vector_loader.get_retriever()
        print("Loading RAG Chatbot")
        chatbot = RAGChatBot(retriever, MODEL)
        print("Question answering:")
        response = chatbot.invoke(question)
        return response
