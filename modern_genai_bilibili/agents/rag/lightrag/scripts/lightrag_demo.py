# demo_lightrag_trace.py
import os
import asyncio
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed
from lightrag.kg.shared_storage import initialize_pipeline_status

assert load_dotenv(find_dotenv(), override=True)

WORKING_DIR = "./lightrag_demo_store"


async def build_rag():
    rag = LightRAG(
        working_dir=WORKING_DIR,
        embedding_func=openai_embed,
        llm_model_func=gpt_4o_mini_complete,
    )
    # 重要：必须初始化 storages（官方也强调 initialize_storages 会自动初始化 pipeline_status）
    await rag.initialize_storages()
    await initialize_pipeline_status()
    return rag


async def main():
    rag = await build_rag()

    # ========== 1) INDEX ==========
    docs = [
        "Alice likes graph RAG. LightRAG builds a knowledge graph from chunks.",
        "Bob works at ExampleCorp in Beijing. ExampleCorp acquired FooBar in 2022.",
    ]
    for d in docs:
        await rag.ainsert(d)

    # 打印落盘文件（方便你验证 index 的中间产物）
    print("\n[WORKING_DIR files]")
    for p in sorted(Path(WORKING_DIR).glob("*")):
        print(" -", p.name)

    # ========== 2) QUERY ==========
    q = "Explain the relationship between Alice and LightRAG in detail."
    ans = await rag.aquery(q, param=QueryParam(mode="hybrid"))
    print("\n[ANSWER]\n", ans)

    await rag.finalize_storages()


if __name__ == "__main__":
    asyncio.run(main())
