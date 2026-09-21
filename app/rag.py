"""RAG 知识库（第11步）：把 Markdown 文档向量化，提供检索工具。"""

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.tools import tool

# 1. 加载 knowledge_base 下所有 Markdown 文件
loader = DirectoryLoader(
    "knowledge_base",
    glob="**/*.md",
    loader_cls=TextLoader,
    loader_kwargs={"encoding": "utf-8"},
)

documents = loader.load()

# 2. 把长文档切成 500 字一段
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(documents)

# 3. 用本地 embedding 模型把文本转成向量，存入 ChromaDB
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-zh-v1.5")
vectorstore = Chroma.from_documents(
    chunks, embeddings, persist_directory="data/vector_store"
)

# 4. 检索器：每次取最相关的 3 段
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})


@tool
def search_knowledge_base(query: str) -> str:
    """搜索客户服务知识库，查询退款政策、会员规则、售后流程、常见问题等。

    Args:
        query: 用户的问题
    """
    results = retriever.invoke(query)
    if not results:
        return "知识库中没有找到相关信息，建议联系人工客服。"
    answers = []
    for doc in results:
        source = doc.metadata.get("source", "未知文件")
        # 只取文件名，不要完整路径
        filename = source.replace("\\", "/").split("/")[-1]
        answers.append(f"【来源：{filename}】\n{doc.page_content}")
    return "\n\n".join(answers)
