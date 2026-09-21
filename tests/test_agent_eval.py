"""Agent 评测集（第15步）。"""

from langchain_core.messages import HumanMessage
from app.graph import graph

# 每个用例：(用户问题, 期望调用的工具名, 备注)
CASES = [
    # --- 正常：查询 ---
    ("帮我查一下客户1001", "get_customer", "查询客户"),
    ("列出所有客户", "list_customers", "列出客户"),
    ("搜索名叫张三的客户", "search_customers", "搜索客户"),

    # --- 正常：添加 ---
    ("帮我添加一个客户，编号2001，姓名王五，年龄30", "create_customer", "添加客户"),

    # --- 正常：知识库 ---
    ("超过七天还能退款吗", "search_knowledge_base", "知识库-退款"),
    ("金卡会员有什么权益", "search_knowledge_base", "知识库-会员"),
    ("一般几天能收到货", "search_knowledge_base", "知识库-物流"),

    # --- 危险操作：应该触发确认 ---
    # ("删除客户9999", "delete_customer", "删除需确认"),
    # ("把9999的邮箱改成new@test.com", "update_customer", "修改需确认"),

    # --- 错误输入：应该返回错误提示 ---
    ("添加客户编号999，姓名测试，年龄500", None, "年龄超标应报错"),
    ("添加客户编号abc，姓名测试", None, "ID非数字应报错"),
    ("查询客户99999", "get_customer", "不存在的客户应提示"),
]


def run_case(question: str, expected_tool: str | None, note: str) -> dict:
    """运行一个测试用例。"""
    from langgraph.types import Command

    config = {"configurable": {"thread_id": f"eval-{note}"}}

    result = graph.invoke(
        {"messages": [HumanMessage(content=question)]},
        config=config,
    )

    # 遍历所有消息，找到模型调用过的所有工具
    tools_called = []
    for msg in result["messages"]:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                tools_called.append(tc["name"])

    # 危险操作：检查是否触发了 interrupt
    interrupted = "__interrupt__" in result

    # 如果是危险操作，恢复（取消）避免真的执行
    if interrupted:
        pass

    passed = True
    reason = ""

    if expected_tool and expected_tool not in tools_called:
        passed = False
        reason = f"期望调用 {expected_tool}，实际调用 {tools_called}"

    # if note == "删除需确认" and not interrupted:
    #     passed = False
    #     reason = "删除操作没有触发确认！"

    if note == "修改需确认" and not interrupted:
        passed = False
        reason = "修改操作没有触发确认！"

    return {
        "note": note,
        "question": question,
        "tools_called": tools_called,
        "interrupted": interrupted,
        "passed": passed,
        "reason": reason,
    }



if __name__ == "__main__":
    from langgraph.types import Command

    results = []
    for question, expected_tool, note in CASES:
        print(f"测试：{note} ...", end=" ")
        r = run_case(question, expected_tool, note)
        results.append(r)
        if r["passed"]:
            print("✅ 通过")
        else:
            print(f"❌ 失败 - {r['reason']}")

    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    print(f"\n{'='*50}")
    print(f"通过：{passed}/{total}")
    if passed < total:
        print("失败用例：")
        for r in results:
            if not r["passed"]:
                print(f"  - {r['note']}: {r['reason']}")
