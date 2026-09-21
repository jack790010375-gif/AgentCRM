"""FastAPI 后端接口（第12步）。"""

from fastapi import FastAPI
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

from app.graph import graph
from app.service import CustomerService, CustomerNotFoundError

app = FastAPI(title="AgentCRM API")
svc = CustomerService()


class ChatRequest(BaseModel):
    message: str
    thread_id: str = "default"


class ChatResponse(BaseModel):
    answer: str
    thread_id: str


@app.get("/health")
def health():
    """健康检查。"""
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """和 Agent 聊天。"""
    config = {"configurable": {"thread_id": req.thread_id}}
    result = graph.invoke(
        {"messages": [HumanMessage(content=req.message)]},
        config=config,
    )
    answer = result["messages"][-1].content
    return ChatResponse(answer=answer, thread_id=req.thread_id)


@app.get("/customers/{customer_id}")
def get_customer(customer_id: str):
    """直接查询客户信息。"""
    try:
        customer = svc.get_customer(customer_id)
        return customer.model_dump()
    except CustomerNotFoundError as e:
        return {"error": str(e)}
