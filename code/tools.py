from langchain_core.tools import tool
from public.public_variable import logger
from typing import Annotated, Optional
from langgraph.types import Command
from langchain_core.messages import ToolMessage
from langgraph.prebuilt import InjectedState
from langchain_core.tools import tool, InjectedToolCallId
from core.llm.models import AgentState
from utils.databases.service_factory import create_neo4j_service,create_qdrant_service,create_mysql_service

@tool("query_by_cypher")
async def query_by_cypher(state: Annotated[AgentState, InjectedState], cypher: str, page: int = 0, size: int = 10) -> str:
    """
    run the cypher query on the neo4j database and return the result.

    to avoid the result is too long, you can use the page and size to limit the result.
    the default page is 0, the default size is 10.
    """
    neo4j_service = create_neo4j_service()
    cypher = f"{cypher} SKIP {page} * {size} LIMIT {size}"
    logger.info(f"query_by_cypher cypher: {cypher}")
    try:
        res = await neo4j_service.run_query(cypher)
        logger.info(f"query_by_cypher result: {res}")
        return f"{res}"
    except Exception as e:
        logger.error(f"Failed to execute query: {str(e)}")
        logger.error(f"Query: {cypher}")
        return f"Failed to execute query: {str(e)}"

@tool("search_for_precise_node_name")
async def search_for_precise_node_name(state: Annotated[AgentState, InjectedState], node_name: str) -> str:
    """
    search for the precise node name in the neo4j database based on the rough/similar name and return the exact name.

    the input node_name is the rough/similar name of the node you want to search for.
    the return will be some possible exact names for the node, you can choose the most similar one.
    It is possible that the name returned is not related to your request.
    """
    
    logger.info(f"search_for_precise_node_name node_name: {node_name}")
    qdrant_service = create_qdrant_service()
    qdrant_store = qdrant_service.set_langchain_vecstore(
        collection_name="odlm",
        retrieval_mode="hybrid"
    )
    res = await qdrant_service.aretrieve_documents(
        qdrant_store,
        node_name,
        top_k=5
    )
    res = [f"name: {doc.metadata['name']}, is_instance_of: {doc.metadata['is_instance_of']}, labels: {doc.metadata['label']}" for doc in res]
    logger.info(f"search_for_precise_node_name result: {res}")
    
    return f"存在并可能的节点有：{res}"

@tool("find_binding_data_of_object")
async def find_binding_data_of_object(state: Annotated[AgentState, InjectedState], source_table_name: str, sql_query: str) -> str:
    """
    find the binding data of the object field from the source table inside relation database like mysql.

    this tool is used to lookup the real records of the Ontology Object. you need to lock down the source table name, 
    then generate the sql query to get the real records of the Ontology Object.

    Most of the time, use LIKE to match the value instead of exact match.
    """
    # mysql_service = create_mysql_service()
    mysql_service = create_mysql_service()
    sql_query = sql_query.replace(f"{source_table_name}_", "")
    logger.info(f"find_binding_data_of_object source_table_name: {source_table_name}, sql_query: {sql_query}")
    res = await mysql_service.afetch_all(sql_query)
    logger.info(f"find_binding_data_of_object result: {res}")
    return f"{res}"