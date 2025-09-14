from typing import Any, Dict, List, Optional, TYPE_CHECKING

import numpy as np
from pymilvus import (
    MilvusClient,
    AsyncMilvusClient,
    DataType,
    RRFRanker,
    AnnSearchRequest,
    CollectionSchema
)
from public.public_variable import logger

try:
    # Optional: available via langchain-milvus
    from langchain_milvus import Milvus as MilvusVectorStore
except Exception:  # pragma: no cover - optional dependency path
    MilvusVectorStore = None  # type: ignore

if TYPE_CHECKING:  # typing-only import to avoid runtime dependency
    from langchain_core.embeddings import Embeddings


class MilvusService:
    """
    Milvus vector database service (sync + async), modeled after QdrantService.

    Key capabilities:
    - Client management for both sync and async clients
    - Collection lifecycle: create/drop/get/list
    - Indexing and loading (load/release)
    - Data operations: insert, delete, get, query, search, hybrid_search
    - Optional LangChain VectorStore integration (dense only by default)

    Reference tutorial for asyncio usage: https://milvus.io/docs/use-async-milvus-client-with-asyncio.md
    """

    def __init__(
        self,
        *,
        uri: str,
        token: Optional[str] = None,
        db_name: Optional[str] = None,
        dense_embedding: Optional["Embeddings"] = None,
        # Placeholder for future sparse/hybrid support via LangChain (not guaranteed in all versions)
        sparse_embedding: Optional["Embeddings"] = None,
    ) -> None:
        if uri is None:
            raise ValueError("Milvus 'uri' must be provided")

        self.uri = uri
        self.token = token
        self.db_name = db_name
        self.dense_embedding = dense_embedding
        self.sparse_embedding = sparse_embedding

        # Initialize sync and async clients
        self.client = MilvusClient(uri=self.uri, token=self.token, db_name=self.db_name)
        self.async_client = AsyncMilvusClient(uri=self.uri, token=self.token, db_name=self.db_name)

    def create_database(self, *, db_name: str) -> None:
        self.client.create_database(db_name)
        logger.info(f"Database '{db_name}' created")

    def drop_database(self, *, db_name: str) -> None:
        all_collections = self.client.list_collections()
        for collection in all_collections:
            self.client.drop_collection(collection)
        self.client.drop_database(db_name)
        logger.info(f"Database '{db_name}' dropped")
    
    def list_databases(self) -> List[str]:
        return self.client.list_databases()
    
    def view_database(self, *, db_name: str) -> None:
        return self.client.describe_database(db_name)
    
    def alter_database_properties(self, *, db_name: str, properties: Dict[str, Any]) -> None:
        self.client.alter_database_properties(db_name, properties)
        logger.info(f"Database '{db_name}' properties altered")
    
    def drop_database_properties(self, *, db_name: str, property_keys: List[str]) -> None:
        self.client.drop_database_properties(db_name, property_keys)
        logger.info(f"Database '{db_name}' properties dropped")
    
    def switch_db(self, *, db_name: str) -> None:
        self.client.use_database(db_name)
        self.async_client.use_database(db_name)
        logger.info(f"Switched to database '{db_name}'")
    
    # -----------------------------
    # Schema helpers
    # -----------------------------
    def create_schema(self, *, auto_id: bool = False, description: str = "") -> CollectionSchema:
        """
        Create a schema using the (sync) client API exposed on the async client as per docs.
        You can then call schema.add_field(...).
        """
        # Per docs, AsyncMilvusClient exposes create_schema() synchronously
        schema = self.async_client.create_schema(auto_id=auto_id, description=description)
        return schema

    def default_schema(
        self,
        *,
        dense_dim: int,
        with_sparse: bool = False,
        with_text: bool = True,
        text_max_length: int = 512,
        auto_id: bool = False,
        description: str = "",
        id_field: str = "id",
        dense_field: str = "dense_vector",
        sparse_field: str = "sparse_vector",
        text_field: str = "text",
    ) -> Any:
        """
        Build a typical schema: INT64 id (primary), dense vector, optional sparse vector, optional text.
        """
        schema = self.create_schema(auto_id=auto_id, description=description)
        schema.add_field(id_field, DataType.INT64, is_primary=True)
        schema.add_field(dense_field, DataType.FLOAT_VECTOR, dim=dense_dim)
        if with_sparse:
            schema.add_field(sparse_field, DataType.SPARSE_FLOAT_VECTOR)
        if with_text:
            schema.add_field(text_field, DataType.VARCHAR, max_length=text_max_length)
        return schema

    # -----------------------------
    # Collection lifecycle
    # -----------------------------
    def create_collection(self, *, collection_name: str, schema: Any) -> None:
        if self.client.has_collection(collection_name):
            logger.info(f"Collection '{collection_name}' already exists")
            return
        self.client.create_collection(collection_name=collection_name, schema=schema)
        logger.info(f"Collection '{collection_name}' created")

    async def acreate_collection(self, *, collection_name: str, schema: Any) -> None:
        if await self.async_client.has_collection(collection_name):
            logger.info(f"Collection '{collection_name}' already exists")
            return
        await self.async_client.create_collection(collection_name=collection_name, schema=schema)
        logger.info(f"Collection '{collection_name}' created")

    def drop_collection(self, *, collection_name: str) -> None:
        if self.client.has_collection(collection_name):
            self.client.drop_collection(collection_name)
            logger.info(f"Collection '{collection_name}' dropped")

    async def adrop_collection(self, *, collection_name: str) -> None:
        if await self.async_client.has_collection(collection_name):
            await self.async_client.drop_collection(collection_name)
            logger.info(f"Collection '{collection_name}' dropped")

    def get_collections(self) -> Any:
        return self.client.list_collections()

    async def aget_collections(self) -> Any:
        return await self.async_client.list_collections()

    def get_collection(self, *, collection_name: str) -> Any:
        return self.client.describe_collection(collection_name)

    async def aget_collection(self, *, collection_name: str) -> Any:
        return await self.async_client.describe_collection(collection_name)

    # -----------------------------
    # Indexing and loading
    # -----------------------------
    def create_index(self, *, collection_name: str, index_params: Optional[Any] = None) -> None:
        params = index_params or self._prepare_default_index_params()
        self.client.create_index(collection_name, params)

    async def acreate_index(self, *, collection_name: str, index_params: Optional[Any] = None) -> None:
        params = index_params or self._prepare_default_index_params()
        await self.async_client.create_index(collection_name, params)

    def _prepare_default_index_params(self) -> Any:
        """Create AUTOINDEX for common fields if present (dense/sparse/text)."""
        params = self.client.prepare_index_params()
        # These additions are safe; Milvus will ignore non-existent fields at creation time
        try:
            params.add_index(field_name="dense_vector", index_type="AUTOINDEX", metric_type="IP")
        except Exception:
            pass
        try:
            params.add_index(field_name="sparse_vector", index_type="AUTOINDEX", metric_type="IP")
        except Exception:
            pass
        try:
            params.add_index(field_name="text", index_type="AUTOINDEX")
        except Exception:
            pass
        return params

    def load_collection(self, *, collection_name: str) -> None:
        self.client.load_collection(collection_name)
        logger.info(f"Load state: {self.client.get_load_state(collection_name)}")

    async def aload_collection(self, *, collection_name: str) -> None:
        await self.async_client.load_collection(collection_name)
        logger.info(f"Load state: {self.client.get_load_state(collection_name)}")

    def release_collection(self, *, collection_name: str) -> None:
        self.client.release_collection(collection_name)

    async def arelease_collection(self, *, collection_name: str) -> None:
        await self.async_client.release_collection(collection_name)

    # -----------------------------
    # Data operations
    # -----------------------------
    def insert(self, *, collection_name: str, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self.client.insert(collection_name, data)

    async def ainsert(self, *, collection_name: str, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        return await self.async_client.insert(collection_name, data)

    def upsert(self, *, collection_name: str, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self.client.upsert(collection_name, data)

    async def aupsert(self, *, collection_name: str, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        return await self.async_client.upsert(collection_name, data)

    def delete(self, *, collection_name: str, ids: Optional[List[int]] = None, filter_expr: Optional[str] = None) -> Any:
        if ids is None and not filter_expr:
            raise ValueError("Provide 'ids' or 'filter_expr' for delete")
        return self.client.delete(collection_name=collection_name, ids=ids, filter=filter_expr)

    async def adelete(self, *, collection_name: str, ids: Optional[List[int]] = None, filter_expr: Optional[str] = None) -> Any:
        if ids is None and not filter_expr:
            raise ValueError("Provide 'ids' or 'filter_expr' for delete")
        return await self.async_client.delete(collection_name=collection_name, ids=ids, filter=filter_expr)

    def get(self, *, collection_name: str, ids: List[int], output_fields: Optional[List[str]] = None) -> Any:
        return self.client.get(collection_name=collection_name, ids=ids, output_fields=output_fields)

    async def aget(self, *, collection_name: str, ids: List[int], output_fields: Optional[List[str]] = None) -> Any:
        return await self.async_client.get(collection_name=collection_name, ids=ids, output_fields=output_fields)

    def query(self, *, collection_name: str, filter_expr: str, output_fields: Optional[List[str]] = None, limit: Optional[int] = None) -> Any:
        return self.client.query(collection_name=collection_name, filter=filter_expr, output_fields=output_fields, limit=limit)

    async def aquery(self, *, collection_name: str, filter_expr: str, output_fields: Optional[List[str]] = None, limit: Optional[int] = None) -> Any:
        return await self.async_client.query(collection_name=collection_name, filter=filter_expr, output_fields=output_fields, limit=limit)

    def search(
        self,
        *,
        collection_name: str,
        data: List[Any],
        anns_field: str,
        output_fields: Optional[List[str]] = None,
        limit: int = 10,
        search_params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        params = search_params or {"metric_type": "IP"}
        return self.client.search(
            collection_name=collection_name,
            data=data,
            anns_field=anns_field,
            output_fields=output_fields,
            limit=limit,
            param=params,
        )

    async def asearch(
        self,
        *,
        collection_name: str,
        data: List[Any],
        anns_field: str,
        output_fields: Optional[List[str]] = None,
        limit: int = 10,
        search_params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        params = search_params or {"metric_type": "IP"}
        return await self.async_client.search(
            collection_name=collection_name,
            data=data,
            anns_field=anns_field,
            output_fields=output_fields,
            limit=limit,
            search_params=params,
        )

    def hybrid_search(
        self,
        *,
        collection_name: str,
        dense_queries: Optional[List[np.ndarray]] = None,
        sparse_queries: Optional[List[Any]] = None,
        limit: int = 10,
        output_fields: Optional[List[str]] = None,
        metric_type: str = "IP",
    ) -> Any:
        reqs: List[AnnSearchRequest] = []
        if dense_queries:
            reqs.append(
                AnnSearchRequest(
                    data=dense_queries,
                    anns_field="dense_vector",
                    param={"metric_type": metric_type},
                    limit=limit,
                )
            )
        if sparse_queries:
            reqs.append(
                AnnSearchRequest(
                    data=sparse_queries,
                    anns_field="sparse_vector",
                    param={"metric_type": metric_type},
                    limit=limit,
                )
            )
        ranker = RRFRanker()
        return self.client.hybrid_search(collection_name=collection_name, reqs=reqs, ranker=ranker, output_fields=output_fields)

    async def ahybrid_search(
        self,
        *,
        collection_name: str,
        reqs: List[AnnSearchRequest],
        output_fields: Optional[List[str]] = None,
    ) -> Any:
        
        ranker = RRFRanker()
        return await self.async_client.hybrid_search(collection_name=collection_name, reqs=reqs, ranker=ranker, output_fields=output_fields)

    async def aupload_docs(self, *, collection_name: str, docs: List[Dict[str, Any]], vec_key: str) -> None:
        from utils.component.embedding.embedding_model import CustomDense
        res = await self.async_client.describe_collection(
            collection_name=collection_name
        )
        dense_vec_field_names = [field["name"] for field in res["fields"] if field["type"] == 101]
        sparse_vec_field_names = [field["name"] for field in res["fields"] if field["type"] == 104]
        if len(dense_vec_field_names) > 1:
            raise ValueError(f"Only one dense vector field is supported, but got {len(dense_vec_field_names)}")
        elif len(dense_vec_field_names) == 0:
            raise ValueError("No dense vector field found")
        if len(sparse_vec_field_names) > 1:
            raise ValueError(f"Only one or zero sparse vector field is supported, but got {len(sparse_vec_field_names)}")
        dense_vec_field_name = dense_vec_field_names[0]
        if len(sparse_vec_field_names) == 1:
            sparse_vec_field_name = sparse_vec_field_names[0]
        else:
            sparse_vec_field_name = None
        field_names = [field["name"] for field in res["fields"] if field["name"] not in [dense_vec_field_name, sparse_vec_field_name]]
        dense_embedding = CustomDense()
        upload_data = []
        for doc in docs:
            if not all(field_name in doc for field_name in field_names ):
                missing_fields = [f for f in field_names if f not in doc]
                raise ValueError(f"Document is missing required fields: {missing_fields}")
        embedding_values = await dense_embedding.aembed_documents([doc[vec_key] for doc in docs])
        for doc, embedding_value in zip(docs, embedding_values):
            doc[dense_vec_field_name] = embedding_value
            upload_data.append(
                doc
            )
        res = await self.aupsert(collection_name=collection_name, data=upload_data)
        return res
        

    # -----------------------------
    # Lifecycle
    # -----------------------------
    def close(self) -> None:
        try:
            self.client.close()
        except Exception:
            pass

    async def aclose(self) -> None:
        try:
            await self.async_client.close()
        except Exception:
            pass


