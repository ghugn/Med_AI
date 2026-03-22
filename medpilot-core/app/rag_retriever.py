import chromadb
import requests
from typing import List, Dict

class DiseaseRAGRetriever:
    def __init__(self, db_path: str = "./chroma_db", model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        """
        Khởi tạo RAG Retriever
        
        Args:
            db_path: Đường dẫn Chroma DB
            model_name: Tên model Sentence-Transformers
        """
        self.model_name = model_name
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_collection(name="diseases")
        print("✅ RAG Retriever initialized")
    
    def _get_embedding(self, text: str) -> list:
        try:
            response = requests.post(
                "http://localhost:11434/api/embeddings",
                json={
                    "model": "all-minilm", # User can use any model
                    "prompt": text
                },
                timeout=2.0
            )
            if response.status_code == 200:
                data = response.json()
                if "embedding" in data:
                    return data["embedding"]
        except Exception as e:
            pass
        # Fallback to zeros if Ollama is currently down
        return [0.0] * 384

    
    def retrieve(self, query: str, top_k: int = 5, min_similarity: float = 0.3) -> List[Dict]:
        """
        Retrieve thông tin liên quan từ Vector DB
        
        Args:
            query: Câu hỏi của người dùng (tiếng Việt)
            top_k: Số kết quả trả về
            min_similarity: Ngưỡng độ tương đồng tối thiểu (0-1)
        
        Returns:
            List các kết quả với thông tin chi tiết
        """
        query_embedding = self._get_embedding(query)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        retrieved_data = []
        
        if results['documents'] and len(results['documents']) > 0:
            for idx, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )):
                # Chroma trả về distance, cần convert sang similarity
                similarity = 1 - distance  # Cosine distance -> similarity
                
                if similarity >= min_similarity:
                    retrieved_data.append({
                        "rank": idx + 1,
                        "disease": metadata.get('disease', 'Unknown'),
                        "file": metadata.get('file', 'Unknown'),
                        "content": doc,
                        "similarity": round(similarity, 3),
                        "source": f"{metadata.get('disease')}/{metadata.get('file')}.txt"
                    })
        
        return retrieved_data
    
    def retrieve_by_disease(self, disease_name: str) -> List[Dict]:
        """
        Retrieve tất cả thông tin của 1 bệnh cụ thể
        
        Args:
            disease_name: Tên bệnh (tiếng Việt)
        
        Returns:
            List các chunks của bệnh đó
        """
        results = self.collection.get(
            where={"disease": disease_name}
        )
        
        retrieved_data = []
        if results['documents']:
            for doc, metadata in zip(results['documents'], results['metadatas']):
                retrieved_data.append({
                    "disease": metadata.get('disease'),
                    "file": metadata.get('file'),
                    "content": doc,
                    "source": f"{metadata.get('disease')}/{metadata.get('file')}.txt"
                })
        
        return retrieved_data
    
    def list_all_diseases(self) -> List[str]:
        """
        Liệt kê tất cả bệnh trong DB
        
        Returns:
            List tên các bệnh
        """
        results = self.collection.get()
        diseases = set()
        
        for metadata in results['metadatas']:
            diseases.add(metadata.get('disease'))
        
        return sorted(list(diseases))
    
    def get_collection_info(self) -> Dict:
        """Lấy thông tin về collection"""
        results = self.collection.get()
        diseases = {}
        
        for metadata in results['metadatas']:
            disease = metadata.get('disease')
            if disease not in diseases:
                diseases[disease] = 0
            diseases[disease] += 1
        
        return {
            "total_chunks": len(results['ids']),
            "total_diseases": len(diseases),
            "diseases_detail": diseases
        }