import asyncio
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

# ==========================================
# 1. Mock Storage Classes (简化版存储模拟)
# ==========================================

@dataclass
class MockGraphStorage:
    nodes: Dict[str, Dict] = field(default_factory=dict)
    edges: Dict[Tuple[str, str], Dict] = field(default_factory=dict)

    async def has_node(self, node_id: str) -> bool:
        return node_id in self.nodes

    async def get_node(self, node_id: str) -> Optional[Dict]:
        return self.nodes.get(node_id)

    async def upsert_node(self, node_id: str, node_data: Dict) -> None:
        print(f"  [DB] Upsert Node: {node_id} | Data: {node_data}")
        self.nodes[node_id] = node_data

    async def has_edge(self, src: str, tgt: str) -> bool:
        return (src, tgt) in self.edges or (tgt, src) in self.edges

    async def get_edge(self, src: str, tgt: str) -> Optional[Dict]:
        if (src, tgt) in self.edges:
            return self.edges[(src, tgt)]
        if (tgt, src) in self.edges:
            return self.edges[(tgt, src)]
        return None

    async def upsert_edge(self, src: str, tgt: str, edge_data: Dict) -> None:
        # 统一存储顺序，模拟无向图
        key = tuple(sorted((src, tgt)))
        print(f"  [DB] Upsert Edge: {key} | Data: {edge_data}")
        self.edges[key] = edge_data


# ==========================================
# 2. 核心合并逻辑 (简化版复现)
# ==========================================

GRAPH_FIELD_SEP = "<SEP>"

def merge_source_ids(existing: List[str], new_ids: List[str]) -> List[str]:
    # 简单的去重合并
    return list(set(existing + new_ids))

async def _merge_nodes_then_upsert(
    entity_name: str,
    nodes_data: List[Dict],
    graph_storage: MockGraphStorage
):
    print(f"\n--- Processing Entity: {entity_name} ---")
    
    # 1. 获取现有数据
    already_node = await graph_storage.get_node(entity_name)
    existing_desc = []
    existing_source_ids = []
    
    if already_node:
        print(f"  Found existing node: {already_node}")
        existing_desc = already_node["description"].split(GRAPH_FIELD_SEP)
        existing_source_ids = already_node["source_id"].split(GRAPH_FIELD_SEP)
    
    # 2. 准备新数据
    new_source_ids = [n["source_id"] for n in nodes_data]
    new_descs = [n["description"] for n in nodes_data]
    
    # 3. 合并逻辑
    # 3.1 Source IDs
    merged_source_ids = merge_source_ids(existing_source_ids, new_source_ids)
    
    # 3.2 Description (去重 + 简单的拼接模拟 summarize)
    merged_descs = list(set(existing_desc + new_descs))
    # 过滤空字符串
    merged_descs = [d for d in merged_descs if d]
    
    # 3.3 Entity Type (简单投票，取出现最多的)
    types = [n["entity_type"] for n in nodes_data]
    if already_node:
        types.append(already_node["entity_type"])
    most_common_type = Counter(types).most_common(1)[0][0]

    # 4. 构建最终数据
    final_data = {
        "entity_name": entity_name,
        "entity_type": most_common_type,
        "description": GRAPH_FIELD_SEP.join(merged_descs),
        "source_id": GRAPH_FIELD_SEP.join(merged_source_ids)
    }
    
    # 5. 写入数据库
    await graph_storage.upsert_node(entity_name, final_data)
    return final_data


async def _merge_edges_then_upsert(
    src_id: str,
    tgt_id: str,
    edges_data: List[Dict],
    graph_storage: MockGraphStorage
):
    print(f"\n--- Processing Edge: {src_id} <-> {tgt_id} ---")
    
    # 1. 确保节点存在 (简化版：如果节点不存在，这里仅打印警告，真实逻辑会尝试创建)
    if not await graph_storage.has_node(src_id) or not await graph_storage.has_node(tgt_id):
        print(f"  [WARN] One of the nodes ({src_id}, {tgt_id}) does not exist!")
        # 在真实代码中，这里会补救性创建节点
    
    # 2. 获取现有边
    already_edge = await graph_storage.get_edge(src_id, tgt_id)
    existing_weight = 0
    existing_keywords = []
    
    if already_edge:
        print(f"  Found existing edge: {already_edge}")
        existing_weight = already_edge["weight"]
        existing_keywords = already_edge["keywords"].split(",")
        
    # 3. 合并逻辑
    # 3.1 Weight 累加
    new_weight = sum(e["weight"] for e in edges_data)
    total_weight = existing_weight + new_weight
    
    # 3.2 Keywords 合并
    new_keywords = []
    for e in edges_data:
        new_keywords.extend(e["keywords"].split(","))
    
    merged_keywords = list(set(existing_keywords + new_keywords))
    merged_keywords = [k for k in merged_keywords if k]

    # 3.3 Description 合并 (模拟真实逻辑：收集 -> 去重 -> 拼接/摘要)
    existing_descs = []
    if already_edge and "description" in already_edge:
        existing_descs = already_edge["description"].split(GRAPH_FIELD_SEP)
    
    new_descs = [e["description"] for e in edges_data]
    
    # 去重合并
    merged_descs = list(set(existing_descs + new_descs))
    merged_descs = [d for d in merged_descs if d]
    
    # 4. 构建最终数据
    final_data = {
        "source": src_id,
        "target": tgt_id,
        "weight": total_weight,
        "keywords": ",".join(merged_keywords),
        "description": GRAPH_FIELD_SEP.join(merged_descs) # 修正：合并描述而不是只取第一个
    }
    
    # 5. 写入数据库
    await graph_storage.upsert_edge(src_id, tgt_id, final_data)


async def merge_nodes_and_edges(chunk_results, graph_storage):
    print("=== STARTING MERGE PROCESS ===")
    
    # 0. 预处理：收集所有节点和边
    all_nodes = defaultdict(list)
    all_edges = defaultdict(list)
    
    for maybe_nodes, maybe_edges in chunk_results:
        for name, nodes in maybe_nodes.items():
            all_nodes[name].extend(nodes)
        
        for key, edges in maybe_edges.items():
            sorted_key = tuple(sorted(key))
            all_edges[sorted_key].extend(edges)
            
    # PHASE 1: Process Nodes
    print("\n>>> PHASE 1: MERGING NODES")
    for entity_name, nodes_list in all_nodes.items():
        await _merge_nodes_then_upsert(entity_name, nodes_list, graph_storage)
        
    # PHASE 2: Process Edges
    print("\n>>> PHASE 2: MERGING EDGES")
    for (src, tgt), edges_list in all_edges.items():
        await _merge_edges_then_upsert(src, tgt, edges_list, graph_storage)

# ==========================================
# 3. 运行示例
# ==========================================

async def main():
    storage = MockGraphStorage()
    
    # 模拟第一次提取结果 (Chunk 1)
    # 包含: Alice (Engineer), Bob (Manager), Alice->Bob (Colleague)
    chunk1_results = (
        {
            "Alice": [{"entity_name": "Alice", "entity_type": "Person", "description": "An engineer", "source_id": "chunk_1"}],
            "Bob": [{"entity_name": "Bob", "entity_type": "Person", "description": "A manager", "source_id": "chunk_1"}]
        },
        {
            ("Alice", "Bob"): [{"weight": 1, "keywords": "colleague,work", "description": "Alice works with Bob"}]
        }
    )
    
    # 模拟第二次提取结果 (Chunk 2) - 模拟重复和增量信息
    # 包含: Alice (Lives in NY), Alice->Bob (Friends)
    chunk2_results = (
        {
            "Alice": [{"entity_name": "Alice", "entity_type": "Person", "description": "Lives in NY", "source_id": "chunk_2"}]
        },
        {
            ("Alice", "Bob"): [{"weight": 2, "keywords": "friend", "description": "Alice is friends with Bob"}]
        }
    )
    
    # 1. 运行第一次合并
    print("\n--- [Run 1] Processing Chunk 1 ---")
    await merge_nodes_and_edges([chunk1_results], storage)
    
    # 2. 运行第二次合并 (模拟增量更新)
    print("\n--- [Run 2] Processing Chunk 2 (Incremental) ---")
    await merge_nodes_and_edges([chunk2_results], storage)
    
    # 3. 查看最终结果
    print("\n=== FINAL GRAPH STATE ===")
    print("Nodes:", storage.nodes)
    print("Edges:", storage.edges)

if __name__ == "__main__":
    asyncio.run(main())
