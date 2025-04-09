"""
Vector database integration for knowledge storage and retrieval.
"""

import logging
import os
from typing import Dict, List, Optional, Any
import numpy as np

import chromadb
from chromadb.config import Settings

from config import VECTOR_DB_PATH

logger = logging.getLogger(__name__)

class VectorStore:
    """
    Vector database for storing and retrieving embeddings.
    """
    def __init__(self, collection_name: str = "default"):
        self.collection_name = collection_name
        self.client = chromadb.PersistentClient(
            path=str(VECTOR_DB_PATH),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
            logger.info(f"Using existing collection: {collection_name}")
        except ValueError:
            self.collection = self.client.create_collection(name=collection_name)
            logger.info(f"Created new collection: {collection_name}")
    
    def add(self, texts: List[str], metadata: Optional[List[Dict[str, Any]]] = None, 
            ids: Optional[List[str]] = None, embeddings: Optional[List[List[float]]] = None) -> List[str]:
        """
        Add documents to the vector store.
        
        Args:
            texts: List of text documents to add
            metadata: Optional list of metadata dictionaries for each document
            ids: Optional list of IDs for each document
            embeddings: Optional list of pre-computed embeddings
            
        Returns:
            List of document IDs
        """
        if not texts:
            return []
        
        # Generate IDs if not provided
        if ids is None:
            import uuid
            ids = [str(uuid.uuid4()) for _ in texts]
        
        # Use empty metadata if not provided
        if metadata is None:
            metadata = [{} for _ in texts]
        
        # Add documents to collection
        self.collection.add(
            documents=texts,
            metadatas=metadata,
            ids=ids,
            embeddings=embeddings
        )
        
        logger.info(f"Added {len(texts)} documents to collection {self.collection_name}")
        return ids
    
    def query(self, query_text: str, n_results: int = 5, 
              where: Optional[Dict[str, Any]] = None, 
              where_document: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Query the vector store for similar documents.
        
        Args:
            query_text: The query text
            n_results: Number of results to return
            where: Optional filter on metadata
            where_document: Optional filter on document content
            
        Returns:
            Dictionary with query results
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where,
            where_document=where_document
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results["ids"][0])):
            formatted_results.append({
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i] if "distances" in results else None
            })
        
        logger.info(f"Query '{query_text}' returned {len(formatted_results)} results")
        return {
            "query": query_text,
            "results": formatted_results,
            "count": len(formatted_results)
        }
    
    def get(self, ids: List[str]) -> Dict[str, Any]:
        """
        Get documents by ID.
        
        Args:
            ids: List of document IDs
            
        Returns:
            Dictionary with documents
        """
        results = self.collection.get(ids=ids)
        
        # Format results
        formatted_results = []
        for i in range(len(results["ids"])):
            formatted_results.append({
                "id": results["ids"][i],
                "text": results["documents"][i],
                "metadata": results["metadatas"][i],
                "embedding": results["embeddings"][i] if "embeddings" in results else None
            })
        
        logger.info(f"Retrieved {len(formatted_results)} documents by ID")
        return {
            "results": formatted_results,
            "count": len(formatted_results)
        }
    
    def delete(self, ids: Optional[List[str]] = None, 
               where: Optional[Dict[str, Any]] = None, 
               where_document: Optional[Dict[str, Any]] = None) -> int:
        """
        Delete documents from the vector store.
        
        Args:
            ids: Optional list of document IDs to delete
            where: Optional filter on metadata
            where_document: Optional filter on document content
            
        Returns:
            Number of documents deleted
        """
        # Get count before deletion
        count_before = self.collection.count()
        
        # Delete documents
        self.collection.delete(
            ids=ids,
            where=where,
            where_document=where_document
        )
        
        # Get count after deletion
        count_after = self.collection.count()
        deleted_count = count_before - count_after
        
        logger.info(f"Deleted {deleted_count} documents from collection {self.collection_name}")
        return deleted_count
    
    def count(self) -> int:
        """
        Get the number of documents in the collection.
        
        Returns:
            Number of documents
        """
        return self.collection.count()
    
    def list_collections(self) -> List[str]:
        """
        List all collections in the vector store.
        
        Returns:
            List of collection names
        """
        collections = self.client.list_collections()
        return [collection.name for collection in collections]
