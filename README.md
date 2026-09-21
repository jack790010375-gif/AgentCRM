# AgentCRM: 基于 LangGraph 的智能客户管理与服务 Agent

一个通过自然语言操作客户数据的智能 Agent 系统。用户直接输入"帮我添加客户张三"，Agent 会理解意图、提取参数、调用工具、操作数据库，并在危险操作前请求人工确认。

## 架构

```
用户自然语言
    ↓
Streamlit 界面 / FastAPI 接口
    ↓
LangGraph 流程控制
    ├── 大模型理解意图（DeepSeek）
    ├── 工具调用（增删改查客户）
    ├── RAG 知识库（退款/会员/FAQ）
    └── 人工确认（修改/删除前暂停）
    ↓
SQLite 数据库 + 对话状态持久化
```

## 技术栈

| 技术 | 用途 |
|------|------|
| LangGraph | Agent 工作流编排、人工确认、多轮对话 |
| LangChain Tools | 工具定义与绑定 |
| DeepSeek API | 大模型理解与决策 |
| Pydantic | 数据模型校验 |
| SQLite | 客户数据持久化 |
| ChromaDB + bge-small-zh | RAG 向量检索 |
| FastAPI | 后端接口 |
| Streamlit | 聊天界面 |
| LangSmith | 调用链监控 |
| pytest | 自动化测试 |

## 功能

- 自然语言客户管理：添加、查询、修改、删除、列出客户
- 危险操作人工确认：修改和删除前暂停，等待用户确认或取消
- 多轮对话记忆：基于 thread_id 区分会话，SQLite 持久化
- RAG 知识库：退款政策、会员规则、常见问题的检索增强回答
- 自动校验：ID格式、年龄范围、手机号、邮箱格式
- 完整测试：34 个单元测试 + 10 个 Agent 评测用例

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env`，填入你的 DeepSeek API Key 和 LangSmith API Key。

### 3. 运行单元测试

```bash
pytest tests/ -v
```

### 4. 启动聊天界面

```bash
streamlit run app/ui.py
```

### 5. 启动 API 服务

```bash
uvicorn app.api:app --reload
```

访问 http://localhost:8000/docs 查看 API 文档。

## 项目结构

```
AgentCRM/
├── app/
│   ├── customer.py      # Pydantic 数据模型与校验
│   ├── database.py      # SQLite 连接与建表
│   ├── repository.py    # 数据库增删改查
│   ├── service.py       # 业务逻辑层
│   ├── tools.py         # LangChain 工具定义
│   ├── model.py         # 大模型配置
│   ├── graph.py         # LangGraph 工作流
│   ├── rag.py           # RAG 知识库
│   ├── api.py           # FastAPI 接口
│   └── ui.py            # Streamlit 界面
├── knowledge_base/       # RAG 文档
├── tests/               # 测试
├── requirements.txt
├── Dockerfile
├── .env.example
├── .gitignore
└── README.md
```

## 示例对话

```
用户：帮我添加一个客户，编号1001，姓名张三，年龄25，电话13800138000
Agent：客户1001已创建。

用户：查一下1001的信息
Agent：1001号客户：张三，25岁，13800138000

用户：删除1001
Agent：⚠️ 确认删除客户1001？该操作无法撤销。
       [确认] [取消]

用户：超过七天能退款吗？
Agent：根据退款政策，签收后7天内可无理由退款...
```
