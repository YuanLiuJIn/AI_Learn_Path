"""
Search-R1 风格 RLVR 奖励函数（最小可运行版，对应你 05_reward_design.md 的 Rule/Outcome）。

真实 Search-R1 的奖励在仓库 `search_r1/reward.py`（`reward_for_search`）。
这里给出一个代表性实现，便于你理解"可验证奖励"如何打分：
  - outcome（结果）奖励：抽取模型最终答案，与 ground_truth 精确匹配 → +1 / 0
  - format（格式）奖励：模型是否使用了 <search> 工具调用 → 轻微鼓励（防"只输出不搜索"）

注意：抽取正则必须与模型输出格式一致，否则 reward 恒 0（见 README §5 坑表）。
"""
import re


def extract_answer(text: str):
    """从模型输出中抽取 <answer>...</answer> 之间的答案。"""
    m = re.search(r"<answer>(.*?)</answer>", text, re.DOTALL)
    return m.group(1).strip() if m else None


def normalize(s: str) -> str:
    """小写、去标点、去多余空白，用于宽松精确匹配。"""
    s = s.lower()
    s = re.sub(r"[^\w\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def reward_for_search(sample: dict, model_output: str) -> float:
    """
    sample: 训练样本，含 reward_model.ground_truth
    model_output: 模型一轮/整条轨迹的生成文本
    返回：标量奖励
    """
    gt = sample.get("reward_model", {}).get("ground_truth", "")
    pred = extract_answer(model_output)

    score = 0.0
    if pred is not None and normalize(pred) == normalize(str(gt)):
        score += 1.0  # outcome 奖励：答案正确

    # format 奖励：鼓励使用搜索工具（<search>...</search>）
    if re.search(r"<search>.*?</search>", model_output, re.DOTALL):
        score += 0.1

    return score


if __name__ == "__main__":
    sample = {"reward_model": {"ground_truth": "Barack Obama"}}
    out_ok = "Let me search. <search>us president 2009</search> ... <answer>Barack Obama</answer>"
    out_bad = "I think the answer is Barack Obama."
    print("correct+search :", reward_for_search(sample, out_ok))   # 1.1
    print("correct no tool:", reward_for_search(sample, out_bad))  # 1.0 (无格式奖励)
