from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, END, add_messages, START
from langgraph.prebuilt import ToolNode
from tools import query_by_cypher, search_for_precise_node_name, find_binding_data_of_object
from utils.databases.service_factory import create_mysql_service
from langchain_openai.chat_models.base import ChatOpenAI
from config import get_llm_config
from public.public_function import extract_json
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, AnyMessage
from public.public_variable import logger
from typing_extensions import TypedDict, Annotated
from enum import Enum

class AgentState(TypedDict):
    # The annotation tells the graph that new messages will always
    # be added to the current states
    messages: Annotated[list[AnyMessage], add_messages]
    task: dict

class AutoAgent:
    def __init__(self):
        workflow = StateGraph(AgentState)
        tool_node = ToolNode([query_by_cypher, search_for_precise_node_name, find_binding_data_of_object])

        workflow.add_node("decide_mission", self.decide_mission)
        workflow.add_node("auto_search_agent", self.auto_search_agent)
        workflow.add_node("tools", tool_node)

        workflow.add_edge(START, "decide_mission")
        workflow.add_edge("decide_mission", "auto_search_agent")
        workflow.add_conditional_edges("auto_search_agent", self.should_continue)
        workflow.add_edge("tools", "auto_search_agent")

        self.llm_config = get_llm_config("deepseek")
        self.app = workflow.compile()
        pass

    async def run(self, user_query: str):
        init_input = {
            "messages": [HumanMessage(content=user_query)],
            "task": {}
        }
        config = {"recursion_limit": 50}
        return await self.app.ainvoke(init_input, config=config)
    
    async def decide_mission(self, state: AgentState):
        for message in reversed(state["messages"]):
            if isinstance(message, HumanMessage):
                user_query = message.content
                break
        mysql_service = create_mysql_service()
        res = await mysql_service.afetch_all("SELECT id, name, detail FROM odlm.supported_task WHERE status = 'active'")
        if len(res) == 0:
            supported_tasks = "没有配置任何支持的任务"
        else:
            supported_tasks = "\n".join([f"id: {task['id']}, name: {task['name']}, detail: {task['detail']}" for task in res])
        
        llm = ChatOpenAI(
            model="deepseek-chat",
            temperature=0.6,
            api_key=self.llm_config.get("api_key"),
            base_url=self.llm_config.get("base_url")
        )
        llm = llm.bind(response_format={"type": "json_object"})
        prompt = f"""
你是一个任务调度专家，请根据用户的请求，从以下支持的任务中选择一个最合适的任务。
用户请求：{user_query}
支持的任务：{supported_tasks}
请只返回一个json对象，不要返回任何其他内容，格式如下：
{{
    "task_id": 任务id
}}
"""
        response = await llm.ainvoke(prompt)
        json_data = extract_json(response.content)[0]
        for task in res:
            if task["id"] == json_data["task_id"]:
                return {"task": task}
        return {"task": {}}

    async def auto_search_agent(self, state: AgentState):
        
        task = state["task"]
        if task:
            task_context = f"""
            {task["name"]}
            {task["detail"]}
            """
        else:
            task_context = "没有可供参考的任务流程，请依据请求，自行规划"
        logger.info(f"task_context: {task_context}")
        tools = [query_by_cypher, search_for_precise_node_name, find_binding_data_of_object]
        llm = ChatOpenAI(
            model="deepseek-chat",
            temperature=0.4,
            api_key=self.llm_config.get("api_key"),
            base_url=self.llm_config.get("base_url")
        )
        llm_with_tools = llm.bind_tools(tools)
        sys_prompt = f"""
# 角色
你是一名数据分析专家，作为我们数据系统平台的智能助手，帮助用户解决所有关于数据分析的问题。

# 能力
你可以通过不同的工具来与不同的数据库进行交互。以下是你可以使用的工具：
query_by_cypher：通过cypher语句查询neo4j数据库，但是只能进行查询，禁止进行写入和删除操作。
search_for_precise_node_name：通过文本相似度检索的方式，搜索neo4j数据库中的节点名称。因为大多数时候用户输入的节点名称或是数据名称是模糊的，所以需要通过这种方式来先确定精确的节点名称然后再编写cypher语句。
find_binding_data_of_object：通过源表名和sql查询语句，查询关系型数据库中的存储的真实数据。

# 数据系统的背景
我们的数据系统是基于本体论构建出来的，所有的实例的label都是Instance，每一个实例都来自于某一个label为Class的本体节点。实例与实例之间也许会存在关系，
实例与实例之间的关系也有可能会出现推导/推理关系，比如某一张表的字段，可能来自于另一张表中的字段，那么这两张表也就会存在关系，但是这个关系属于隐性关系，
需要通过多轮的cypher查询来进行推理得出。

目前系统中，有以下Class：
- Task: 系统中的任务，比如ETL任务等，每一个任务实例都拥有对应的输入和输出
- Field: 表/数据模型中的字段
- Table: 表/数据模型
- MySQL: 数据源的其中一种
- User: 系统中的用户
- Object: 用户基于本体概念构建的对象，与系统中的某个表或数据模型进行绑定，用于查询真实数据
- ObjectField: 本体对象中的字段，与系统中的某个表或数据模型中的字段进行绑定，用于查询真实数据

Class下的实例之间有以下关系：
'Field' - [FIELDFROMTABLE] -> 'Table'
'Field' - [FIELDTRANSFORMEDFROM] -> 'Field'
'Table' - [TABLEBELONGSTODATASOURCE] -> 'MySQL'
'Task' - [USED] -> 'Table'
'Task' - [TASK_OWNER] -> 'User'
'Task' - [GENERATED] -> 'Table'
'ObjectField' - [ISOBJECTFIELDOF] -> 'Object'
'ObjectField' - [ISOBJECTFIELDFROM] -> 'Field'
'Object' - [OBJECTCREATEDFROM] -> 'Table' //本体对象绑定的哪个表

举个例子，如果我们要检索user表有哪些字段，那么查询语句可以这么写：
MATCH (t:Instance {{{{name: 'user'}}}})<-[:FIELDFROMTABLE]-(f:Instance) RETURN f.name SKIP 0 * 10 LIMIT 10
因为user是Table的实例，所以我们可以通过FIELDFROMTABLE关系来找到user表的所有字段。

可以通过每个节点属性中的instance_of属性来判断节点属于哪个Class。

你可以先查询一个节点有哪些属性，这样可以帮助你更好的理解节点可执行的操作。

# 你的任务
你需要基于用户请求，利用工具，逐步推导并检索出支撑解决用户需求的结果。也就是说，你需要调用工具，观察工具的结果，再规划下一步行动并再次调用工具。

这个流程也许会重复很多次，直到你认为你已经找到了足够的信息来支撑解决用户需求。

# 可供参考的任务流程
{task_context}

# 开始！
"""
        first = True
        gathered_tool_calls = None
        prompt = ChatPromptTemplate.from_messages([
                ("system", sys_prompt),
                MessagesPlaceholder(variable_name="messages")
            ]
        )
        chain = prompt | llm_with_tools
        result = ""
        async for token in chain.astream({"messages": state["messages"]}):
            if token.content:
                result += token.content
                print(token.content, end="", flush=True)
            if first:
                gathered_tool_calls = token
                first = False
            else:
                gathered_tool_calls += token
        return {"messages": [AIMessage(content=result, tool_calls=gathered_tool_calls.tool_calls)]}
    
    def should_continue(self, state: AgentState):
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return END