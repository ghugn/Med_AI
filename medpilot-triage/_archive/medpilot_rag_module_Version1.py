"""
MedPilot RAG Module
Converts Excel data to RAG system
Ready to integrate with backend
"""

import pandas as pd
import os
from pathlib import Path
import logging
from typing import Dict, List, Optional
import pickle
import hashlib
from datetime import datetime
import json

# Vector DB
import chromadb
from chromadb.config import Settings

# Embeddings
from sentence_transformers import SentenceTransformer

# For requests
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MedPilotRAGModule:
    """
    Complete RAG module for MedPilot backend
    
    Features:
    - Load data from Excel files
    - Create vector embeddings
    - Store in Chroma DB
    - Query with RAG
    - Cache management
    """
    
    def __init__(self,
                 excel_folder: str,
                 db_path: str = "./medpilot_db",
                 cache_path: str = "./medpilot_cache",
                 chat_api_url: str = "http://localhost:8001/v1/chat/completions",
                 model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                 top_k: int = 3):
        """
        Initialize MedPilot RAG
        
        Args:
            excel_folder: Folder containing Excel files
            db_path: Vector DB storage path
            cache_path: Cache storage path
            chat_api_url: Chat API endpoint (Ollama)
            model_name: Embedding model
            top_k: Top K chunks to retrieve
        """
        self.excel_folder = Path(excel_folder)
        self.db_path = db_path
        self.cache_path = Path(cache_path)
        self.chat_api_url = chat_api_url
        self.top_k = top_k
        
        # Create directories
        self.cache_path.mkdir(exist_ok=True)
        
        # Initialize embedding model
        logger.info(f"Loading embedding model: {model_name}")
        self.embedding_model = SentenceTransformer(model_name)
        
        # Initialize Chroma
        logger.info(f"Initializing Chroma DB: {db_path}")
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        self.collection = self.chroma_client.get_or_create_collection(
            name="medical_diseases",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Cache files
        self.cache_metadata_file = self.cache_path / "metadata.json"
        self.cache_data_file = self.cache_path / "diseases_data.pkl"
        
        print(f"✅ MedPilot RAG Module initialized")
        print(f"   📁 Excel folder: {excel_folder}")
        print(f"   💾 DB path: {db_path}")
        print(f"   🔗 Chat API: {chat_api_url}")
    
    # ============ EXCEL LOADING ============
    def load_excel_files(self) -> Dict[str, Dict[str, str]]:
        """
        Load all Excel files from folder
        
        Expected format:
        ├─ 病名.xlsx (disease name)
        │  ├─ Định nghĩa (definition)
        │  ├─ Triệu chứng (symptoms)
        │  ├─ Chẩn đoán (diagnosis)
        │  └─ Điều trị (treatment)
        └─ ...
        
        Returns:
            {disease_name: {field: content}}
        """
        logger.info(f"Loading Excel files from: {self.excel_folder}")
        
        diseases = {}
        excel_files = list(self.excel_folder.glob("*.xlsx")) + \
                      list(self.excel_folder.glob("*.xls"))
        
        if not excel_files:
            logger.warning(f"No Excel files found in {self.excel_folder}")
            return diseases
        
        logger.info(f"Found {len(excel_files)} Excel files")
        
        for idx, excel_file in enumerate(excel_files, 1):
            disease_name = excel_file.stem  # Filename without extension
            logger.info(f"[{idx}/{len(excel_files)}] Reading {disease_name}...")
            
            try:
                # Read Excel file
                df = pd.read_excel(excel_file, sheet_name=0)
                
                # Convert to dict
                disease_data = {}
                
                for col in df.columns:
                    # Skip empty columns
                    if df[col].isna().all():
                        continue
                    
                    # Combine column content
                    content = ""
                    for idx_row, value in enumerate(df[col]):
                        if pd.notna(value):
                            content += f"\n{value}"
                    
                    if content.strip():
                        disease_data[col] = content.strip()
                
                if disease_data:
                    diseases[disease_name] = disease_data
                    logger.info(f"   ✅ {disease_name}: {len(disease_data)} fields")
                else:
                    logger.warning(f"   ⚠️  {disease_name}: No data found")
            
            except Exception as e:
                logger.error(f"   ❌ Error reading {disease_name}: {str(e)}")
                continue
        
        logger.info(f"✅ Loaded {len(diseases)} diseases")
        return diseases
    
    # ============ CACHE MANAGEMENT ============
    def get_excel_hash(self) -> str:
        """Calculate hash of all Excel files"""
        hash_obj = hashlib.md5()
        
        for excel_file in sorted(self.excel_folder.glob("*.xlsx")) + \
                          sorted(self.excel_folder.glob("*.xls")):
            try:
                with open(excel_file, 'rb') as f:
                    hash_obj.update(f.read())
            except:
                pass
        
        return hash_obj.hexdigest()
    
    def is_cache_valid(self) -> bool:
        """Check if cache is still valid"""
        if not self.cache_metadata_file.exists():
            logger.info("Cache not found")
            return False
        
        try:
            with open(self.cache_metadata_file, 'r') as f:
                metadata = json.load(f)
            
            current_hash = self.get_excel_hash()
            
            if metadata.get('excel_hash') == current_hash:
                logger.info("✅ Cache valid (hash match)")
                return True
            else:
                logger.info("❌ Cache invalid (hash mismatch)")
                return False
        except Exception as e:
            logger.warning(f"Cache validation error: {e}")
            return False
    
    def save_cache(self, diseases: Dict):
        """Save diseases to cache"""
        logger.info("💾 Saving cache...")
        
        # Save data
        with open(self.cache_data_file, 'wb') as f:
            pickle.dump(diseases, f)
        
        # Save metadata
        metadata = {
            'excel_hash': self.get_excel_hash(),
            'saved_at': datetime.now().isoformat(),
            'total_diseases': len(diseases),
            'cache_file': str(self.cache_data_file)
        }
        
        with open(self.cache_metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"✅ Cache saved ({len(diseases)} diseases)")
    
    def load_cache(self) -> Dict:
        """Load diseases from cache"""
        logger.info("📂 Loading from cache...")
        
        with open(self.cache_data_file, 'rb') as f:
            diseases = pickle.load(f)
        
        logger.info(f"✅ Loaded {len(diseases)} diseases from cache")
        return diseases
    
    # ============ DATA LOADING (Smart) ============
    def load_diseases(self, force_reload: bool = False) -> Dict:
        """
        Load diseases (from cache or Excel)
        
        Args:
            force_reload: Force reload from Excel (ignore cache)
        
        Returns:
            {disease_name: {field: content}}
        """
        # Check cache validity
        if not force_reload and self.is_cache_valid():
            return self.load_cache()
        
        # Load from Excel
        diseases = self.load_excel_files()
        
        # Save cache
        self.save_cache(diseases)
        
        return diseases
    
    # ============ INDEXING ============
    def index_diseases(self, diseases: Dict, force_reindex: bool = False):
        """
        Index diseases to vector DB
        
        Args:
            diseases: Disease data dict
            force_reindex: Force reindex (clear DB first)
        """
        logger.info(f"Indexing {len(diseases)} diseases to Chroma...")
        
        if force_reindex:
            logger.warning("🔄 Force reindex - clearing collection...")
            self.chroma_client.delete_collection(name="medical_diseases")
            self.collection = self.chroma_client.get_or_create_collection(
                name="medical_diseases",
                metadata={"hnsw:space": "cosine"}
            )
        
        total_chunks = 0
        
        for disease_idx, (disease_name, fields) in enumerate(diseases.items(), 1):
            logger.info(f"[{disease_idx}/{len(diseases)}] Indexing {disease_name}...")
            
            for field_name, content in fields.items():
                # Split content into chunks
                chunks = self._chunk_text(content)
                
                for chunk_idx, chunk in enumerate(chunks):
                    # Create unique ID
                    chunk_id = f"{disease_name}_{field_name}_{chunk_idx}"
                    
                    # Embed chunk
                    embedding = self.embedding_model.encode(chunk)
                    
                    # Metadata
                    metadata = {
                        "disease": disease_name,
                        "field": field_name,
                        "chunk_idx": chunk_idx,
                        "indexed_at": datetime.now().isoformat()
                    }
                    
                    # Add to collection
                    self.collection.add(
                        ids=[chunk_id],
                        embeddings=[embedding.tolist()],
                        documents=[chunk],
                        metadatas=[metadata]
                    )
                    
                    total_chunks += 1
        
        logger.info(f"✅ Indexed {total_chunks} chunks")
        return total_chunks
    
    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
        """Split text into chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to split at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                if last_period > chunk_size * 0.7:
                    end = start + last_period + 1
            
            chunks.append(text[start:end].strip())
            start = end - overlap
        
        return [c for c in chunks if len(c.strip()) > 50]
    
    # ============ RETRIEVAL ============
    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[Dict]:
        """
        Retrieve relevant chunks
        
        Args:
            query: Search query
            top_k: Number of chunks to return
        
        Returns:
            List of {disease, field, content, score}
        """
        if top_k is None:
            top_k = self.top_k
        
        # Embed query
        query_embedding = self.embedding_model.encode(query)
        
        # Search in Chroma
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k
        )
        
        # Format results
        retrieved = []
        for idx in range(len(results['ids'][0])):
            retrieved.append({
                'id': results['ids'][0][idx],
                'disease': results['metadatas'][0][idx]['disease'],
                'field': results['metadatas'][0][idx]['field'],
                'content': results['documents'][0][idx],
                'distance': results['distances'][0][idx]
            })
        
        return retrieved
    
    # ============ RAG QUERY ============
    def build_messages(self, query: str, context: str) -> List[Dict]:
        """Build messages for chat API"""
        system_prompt = """Bạn là một trợ lý y tế chuyên nghiệp, thông thái và tử tế.

Hãy trả lời câu hỏi của người dùng dựa trên thông tin tham khảo được cung cấp.

Yêu cầu:
1. Trả lời chi tiết, chính xác, dễ hiểu
2. Nêu rõ nguồn thông tin
3. Nếu thông tin không đủ, hãy nói rõ ràng
4. Sử dụng tiếng Việt chuẩn"""
        
        user_prompt = f"""=== THÔNG TIN THAM KHẢO ===
{context}

=== CÂU HỎI ===
{query}

=== TRẢ LỜI ==="""
        
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    
    def query(self, query: str) -> Dict:
        """
        Full RAG query
        
        Args:
            query: User question
        
        Returns:
            {query, answer, sources, latency}
        """
        import time
        
        logger.info(f"\n{'='*70}")
        logger.info(f"Query: {query}")
        logger.info(f"{'='*70}")
        
        start_time = time.time()
        
        # Step 1: Retrieve
        logger.info("🔍 Retrieving context...")
        retrieved = self.retrieve(query)
        
        context = "\n\n".join([
            f"[{r['disease']} - {r['field']}]\n{r['content']}"
            for r in retrieved
        ])
        
        sources = list(set([r['disease'] for r in retrieved]))
        
        # Step 2: Build prompt
        logger.info("📝 Building prompt...")
        messages = self.build_messages(query, context)
        
        # Step 3: Query chat API
        logger.info("🤖 Querying LLM...")
        
        try:
            response = requests.post(
                self.chat_api_url,
                json={"messages": messages, "max_tokens": 1000},
                timeout=180
            )
            
            if response.status_code != 200:
                logger.error(f"Error: {response.status_code}")
                return {
                    "query": query,
                    "answer": f"❌ Error: {response.status_code}",
                    "sources": sources,
                    "latency": f"{time.time() - start_time:.2f}s"
                }
            
            answer = response.json()["choices"][0]["message"]["content"]
            
            latency = time.time() - start_time
            logger.info(f"✅ Answer received ({latency:.2f}s)")
            
            return {
                "query": query,
                "answer": answer,
                "sources": sources,
                "latency": f"{latency:.2f}s"
            }
        
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return {
                "query": query,
                "answer": f"❌ Error: {str(e)}",
                "sources": sources,
                "latency": f"{time.time() - start_time:.2f}s"
            }
    
    # ============ STATS ============
    def get_stats(self) -> Dict:
        """Get system statistics"""
        count = self.collection.count()
        
        return {
            "total_chunks": count,
            "db_path": self.db_path,
            "cache_valid": self.is_cache_valid(),
        }


# ============ USAGE ============
if __name__ == "__main__":
    # Initialize
    rag = MedPilotRAGModule(
        excel_folder="./diseases_excel",
        db_path="./medpilot_db",
        chat_api_url="http://localhost:8001/v1/chat/completions"
    )
    
    # Load diseases (from cache or Excel)
    diseases = rag.load_diseases()
    
    # Index
    rag.index_diseases(diseases)
    
    # Query
    queries = [
        "Bệnh gai den là gì?",
        "Triệu chứng gai den?",
        "Cách điều trị gai den?",
    ]
    
    for q in queries:
        result = rag.query(q)
        print(f"\n❓ Q: {result['query']}")
        print(f"📚 Sources: {', '.join(result['sources'])}")
        print(f"⏱️  Latency: {result['latency']}")
        print(f"💬 A: {result['answer'][:200]}...")