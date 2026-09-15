import os
import asyncio
import shutil
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed
from lightrag.kg.shared_storage import initialize_pipeline_status

assert load_dotenv(find_dotenv(), override=True)

WORKING_DIR = "./lightrag_complex_demo_store"


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
    # 为了演示效果，每次运行前清理工作目录，确保是从零构建索引
    if os.path.exists(WORKING_DIR):
        shutil.rmtree(WORKING_DIR)
        print(f"Cleaned up directory: {WORKING_DIR}")

    rag = await build_rag()

    # ========== 1) INDEX (构建多跳推理场景) ==========
    # 场景：展示 KG 如何连接分散在不同文档中的实体关系
    # 逻辑链：Dr. Artemis -> Zenith Expedition -> Aethelgard -> Star Core -> Theta-Waves -> Global Tech
    # Naive RAG (仅向量) 很难将 "Dr. Artemis" 和 "Global Tech" 联系起来，因为它们从未出现在同一个 chunks 中，且语义距离较远
    docs = [
        "Dr. Artemis Fowl led the Zenith Expedition in 2024.",
        "The Zenith Expedition discovered the ruins of the Lost City of Aethelgard.",
        "In the main temple of Aethelgard, researchers found a mysterious energy source known as the 'Star Core'.",
        "The Star Core emits a unique radiation signature scientifically classified as 'Theta-Waves'.",
        "Theta-Waves were recently detected coming from the basement of the Global Tech headquarters.",
        # 添加一些干扰项，模拟真实环境
        "Global Tech released a new smartphone model yesterday.",
        "Dr. Artemis Fowl published a paper on quantum physics.",
        "Energy sources in 2024 are diversifying."
    ]

    print(f"\n[INDEXING] Inserting {len(docs)} documents into Knowledge Graph...")
    for d in docs:
        await rag.ainsert(d)

    # 打印落盘文件（验证 index 是否生成）
    print("\n[WORKING_DIR files]")
    if os.path.exists(WORKING_DIR):
        for p in sorted(Path(WORKING_DIR).glob("*")):
            print(" -", p.name)

    # ========== 2) QUERY ==========
    # 这是一个跨越多跳关系的问题
    q = "What is the connection between Dr. Artemis Fowl and the recent detection at Global Tech headquarters?"
    print(f"\n[QUESTION]: {q}")

    # --- 对比演示 ---
    
    # 1. Naive Mode: 仅基于向量检索。
    # 预期：可能找到首尾的文档，但很难串联出中间的 "Zenith -> Aethelgard -> Star Core -> Theta-Waves" 完整路径
    print("\n--- Naive RAG (Vector Only) ---")
    ans_naive = await rag.aquery(q, param=QueryParam(mode="naive"))
    print(ans_naive)

    # 2. Hybrid Mode: 结合 KG 路径游走 (Local + Global)
    # 预期：KG 能通过实体间的边（relations）找到完整路径，但不会直接检索原始文本块 (Chunks)
    print("\n--- Hybrid RAG (KG Only: Local + Global) ---")
    ans_hybrid = await rag.aquery(q, param=QueryParam(mode="hybrid"))
    print(ans_hybrid)

    # 3. Mix Mode: Hybrid + Naive (KG + Vector)
    # 预期：既有 KG 的推理能力，又有 Naive 的原始文本补充，通常是最全面的模式
    print("\n--- Mix RAG (KG + Vector) ---")
    ans_mix = await rag.aquery(q, param=QueryParam(mode="mix"))
    print(ans_mix)

    await rag.finalize_storages()


if __name__ == "__main__":
    asyncio.run(main())
