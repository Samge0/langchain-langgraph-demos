"""02 · 结构化输出：Pydantic schema → 模型输出 → 强类型对象。

面试考点：
- with_structured_output(MyModel) 默认走 function-calling 协议（最稳）。
- description 写得好不好，直接决定抽取字段准确率 —— 它会进 schema 给模型看。
- 演示"从一段面试自评中抽取信息"这种真实业务形态。
"""
from pydantic import BaseModel, Field
from typing import Literal

from common.config import get_llm

llm = get_llm()


# ---------- 1. 扁平 schema ----------
class CandidateProfile(BaseModel):
    """从文本中抽取候选人画像。"""
    name: str = Field(description="候选人姓名")
    years_of_experience: int = Field(description="工作年限（整数年）")
    target_role: Literal["Agent开发", "算法工程", "后端开发", "其他"] = Field(
        description="求职目标岗位")
    skills: list[str] = Field(description="掌握的技术栈，3-8项")
    interview_ready: bool = Field(description="自评是否已准备好面试")


text = (
    "我叫samge，做了6年后端，最近一年在深耕大模型应用："
    "熟悉LangChain、LangGraph、RAG和MCP，自己用vLLM部署过Qwen并做过Agent项目。"
    "目标是拿到AI Agent开发岗的offer，感觉准备得差不多了。"
)

structured_llm = llm.with_structured_output(CandidateProfile)
profile: CandidateProfile = structured_llm.invoke(f"请抽取候选人画像：\n{text}")

print("== 抽取结果（强类型对象）==")
print(profile)
print("\n直接当 Python 对象用：", f"{profile.name} / {profile.years_of_experience}年 / 目标={profile.target_role}")
print()

# ---------- 2. 嵌套 schema ----------
class Project(BaseModel):
    name: str = Field(description="项目名称")
    highlights: list[str] = Field(description="2-3条技术亮点")


class CandidateFull(CandidateProfile):
    projects: list[Project] = Field(description="参与过的代表性项目")


full: CandidateFull = llm.with_structured_output(CandidateFull).invoke(
    f"请抽取候选人画像与项目经历：\n{text}"
)
print("== 嵌套抽取 ==")
for p in full.projects:
    print(f"项目[{p.name}]")
    for h in p.highlights:
        print("  -", h)
