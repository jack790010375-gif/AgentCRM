"""LangGraph 核心流程（第8步+第9步：人工确认）。"""

from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

from app.model import get_llm_with_tools
from app.tools import all_tools
from app.rag import search_knowledge_base

llm = get_llm_with_tools(all_tools + [search_knowledge_base])

# 危险操作需要人工确认
DANGEROUS_TOOLS = {"update_customer", "delete_customer"}


def call_model(state: MessagesState):
    """Agent 节点：调用大模型。"""
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


def should_continue(state: MessagesState):
    """条件边：模型要调用工具吗？"""
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "confirm"
    return END


def confirm_or_proceed(state: MessagesState):
    """检查是否需要人工确认。"""
    from langchain_core.messages import ToolMessage

    last_message = state["messages"][-1]
    tool_calls = last_message.tool_calls

    dangerous = [tc for tc in tool_calls if tc["name"] in DANGEROUS_TOOLS]

    if not dangerous:
        return Command(goto="tools")

    question = "以下操作需要确认：\n"
    for tc in dangerous:
        question += f"- {tc['name']}，参数：{tc['args']}\n"
    question += "回复 True 确认，False 取消"

    confirmed = interrupt({"question": question})

    if confirmed:
        return Command(goto="tools")
    else:
        # 用户取消：给每个 tool_call 补一个工具回复，告诉模型操作被取消了
        tool_messages = [
            ToolMessage(content="用户取消了操作，未执行", tool_call_id=tc["id"])
            for tc in tool_calls
        ]
        return Command(
            goto="agent",
            update={"messages": tool_messages},
        )



# 构建图
workflow = StateGraph(MessagesState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(all_tools + [search_knowledge_base]))
workflow.add_node("confirm", confirm_or_proceed)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue, {
    "confirm": "confirm",
    END: END,
})
workflow.add_edge("tools", "agent")

# checkpointer 让图能暂停/恢复
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
conn = sqlite3.connect("data/checkpoints.db", check_same_thread=False)
checkpointer = SqliteSaver(conn)
graph = workflow.compile(checkpointer=checkpointer)

