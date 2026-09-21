"""Streamlit 聊天界面（第13步）。"""

import streamlit as st
from langchain_core.messages import HumanMessage
from langgraph.types import Command

from app.graph import graph

st.set_page_config(page_title="AgentCRM", page_icon="🤖")
st.title("AgentCRM 智能客户管理")

# 每个浏览器标签页一个 thread_id
if "thread_id" not in st.session_state:
    st.session_state.thread_id = "user-" + str(id(st))

thread_id = st.session_state.thread_id
config = {"configurable": {"thread_id": thread_id}}

# 初始化
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_interrupt" not in st.session_state:
    st.session_state.pending_interrupt = None

# 显示历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 如果有等待确认的操作，显示确认按钮
if st.session_state.pending_interrupt:
    st.warning(st.session_state.pending_interrupt)
    col1, col2 = st.columns(2)
    if col1.button("✅ 确认执行"):
        result = graph.invoke(Command(resume=True), config=config)
        answer = result["messages"][-1].content
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.session_state.pending_interrupt = None
        st.rerun()
    if col2.button("❌ 取消"):
        result = graph.invoke(Command(resume=False), config=config)
        answer = result["messages"][-1].content
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.session_state.pending_interrupt = None
        st.rerun()

# 输入框
if prompt := st.chat_input("输入你的需求，比如：帮我查客户1001"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    result = graph.invoke(
        {"messages": [HumanMessage(content=prompt)]},
        config=config,
    )

    if "__interrupt__" in result:
        question = result["__interrupt__"][0].value.get("question", "确认执行？")
        st.session_state.pending_interrupt = question
        st.rerun()
    else:
        answer = result["messages"][-1].content
        st.session_state.messages.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)
