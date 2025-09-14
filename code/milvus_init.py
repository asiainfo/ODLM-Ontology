from core.databases.milvus.milvus import MilvusService

milvus_service = MilvusService(uri="http://localhost:19530")

milvus_service.create_database(db_name="ontology")

milvus_service.switch_db(db_name="ontology")

from pymilvus import DataType, Function, FunctionType

m_schema = milvus_service.create_schema(auto_id=False, description="ontology instance schema")

m_schema.add_field(
    field_name="instance_id",
    datatype=DataType.VARCHAR,
    is_primary=True,
    auto_id=False,
    max_length=512
)
m_schema.add_field(
    field_name="sparse_vector",
    datatype=DataType.SPARSE_FLOAT_VECTOR
)
m_schema.add_field(
    field_name="dense_vector",
    datatype=DataType.FLOAT_VECTOR,
    dim=1024
)
m_schema.add_field(
    field_name="instance_name",
    datatype=DataType.VARCHAR,
    max_length=512
)
m_schema.add_field(
    field_name="instance_text",
    datatype=DataType.VARCHAR,
    max_length=65535,
    enable_analyzer=True
)
m_schema.add_field(
    field_name="instance_comment",
    datatype=DataType.VARCHAR,
    max_length=2048
)
m_schema.add_field(
    field_name="is_instance_of",
    datatype=DataType.VARCHAR,
    max_length=512
)
bm25_function = Function(
    name="text_bm25_emb", # Function name
    input_field_names=["instance_text"], # Name of the VARCHAR field containing raw text data
    output_field_names=["sparse_vector"], # Name of the SPARSE_FLOAT_VECTOR field reserved to store generated embeddings
    function_type=FunctionType.BM25, # Set to `BM25`
)

m_schema.add_function(bm25_function)

await milvus_service.acreate_collection(
    collection_name="ontology_instances",
    schema=m_schema
)

index_params = milvus_service.async_client.prepare_index_params()
index_params.add_index(
    field_name="sparse_vector",

    index_type="SPARSE_INVERTED_INDEX",
    metric_type="BM25",
    params={
        "inverted_index_algo": "DAAT_MAXSCORE",
        "bm25_k1": 1.2,
        "bm25_b": 0.75
    }
)
index_params.add_index(
    field_name="dense_vector",

    index_type="HNSW",
    index_name="dense_vector_index",
    metric_type="COSINE",
    params={
        "M": 64, # Maximum number of neighbors each node can connect to in the graph
        "efConstruction": 100 # Number of candidate neighbors considered for connection during index construction
    } # Index building params
)

await milvus_service.acreate_index(collection_name="ontology_instances", index_params=index_params)

await milvus_service.aload_collection(collection_name="ontology_instances")

print("已完成milvus初始化")