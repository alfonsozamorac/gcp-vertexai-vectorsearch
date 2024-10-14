import os
from langchain_core.vectorstores import VectorStoreRetriever
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_google_vertexai import VertexAI


class RAGChatBot:

    def __init__(self, retriever: VectorStoreRetriever, model: str = "gemini-1.5-flash") -> None:
        self.retriever = retriever
        self.model = model
        self.company = os.getenv("COMPANY")
        self.support_mail = os.getenv("SUPPORT_MAIL")
        self.chain = self._initialize_chain()

    def _generate_template(self) -> str:
        return f"""
        You are an assistant specialized in answering questions about the company {self.company}.
        Use the following context snippets to respond to the question.
        Always respond in the same language as the question asked.
        If you don’t know the answer or you can't answer based on the context provided, you can say
        in the language of the question that you don´t know the answer and redirect to the
        Human Resources email {self.support_mail}.
        Do not assume or invent an answer.
        Avoid referencing the context itself in your response.
        Provide a direct answer in a simple, concise format. Do not repeat the question.
        ---------------------------------------
        Context:
        {{context}}
        ---------------------------------------
        Question:
        {{question}}
        """

    def _initialize_chain(self):
        prompt_template = PromptTemplate(
            template=self._generate_template(),
            input_variables=["context", "question"],
        )

        llm = VertexAI(model_name=self.model, temperature=0,
                       convert_system_message_to_human=True)
        return RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt_template}
        )

    def invoke(self, query: str) -> str:
        return self.chain({"query": query})["result"]
