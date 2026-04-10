import os
import chromadb
from openai import OpenAI


class RAGService:
    def __init__(self):
        self.client = OpenAI()
        self.chroma = chromadb.Client()
        self.collection = self.chroma.create_collection(name="knowledge_base")
        self._load_knowledge()

    def _embed(self, text: str) -> list:
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding

    def _load_knowledge(self):
        chunks = [
            "Refunds are processed within 7 days of purchase. Customers must submit a refund request via email with their order ID.",
            "Our support team is available Monday to Friday, 9am to 6pm IST. You can reach us at support@company.com.",
            "Shipping is free for orders above 500 INR. Standard delivery takes 3-5 business days across India.",
            "You can track your order by logging into your account and visiting the Orders section.",
            "We accept payments via UPI, credit card, debit card, and net banking. Cash on delivery is available in select cities.",
        ]

        embeddings = [self._embed(chunk) for chunk in chunks]

        self.collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=[f"chunk_{i}" for i in range(len(chunks))]
        )

        print(f"📚 Loaded {len(chunks)} chunks into vector store")

    def retrieve(self, query: str, top_k: int = 2) -> list:
        query_embedding = self._embed(query)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        return results["documents"][0]
