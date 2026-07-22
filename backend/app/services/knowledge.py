"""
知识检索服务
=============
基于 TF-IDF 向量搜索的知识库检索，为 AI 诊断提供专业防治知识。
无外部依赖，纯 Python 实现，适合小规模知识库（<100条）的高效检索。
"""

import math
import re
from collections import Counter

from backend.app.services.knowledge_base import KNOWLEDGE_BASE


class KnowledgeService:
    """单例知识检索服务。"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_ready"):
            return
        self._ready = True
        self._docs = KNOWLEDGE_BASE
        self._idf = self._build_idf()

    # ── TF-IDF 构建 ──────────────────────────────────────

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """中文粗粒度分词：拆单个汉字 + 保留连续数字/外文。"""
        tokens = []
        for ch in text:
            if ch.isalpha() or ch.isdigit():
                tokens.append(ch.lower())
            elif not ch.isspace():
                tokens.append(ch)
        # 补充 bi-gram 提升匹配精度
        bigrams = [a + b for a, b in zip(tokens, tokens[1:])]
        return tokens + bigrams

    def _build_idf(self) -> dict[str, float]:
        n = len(self._docs)
        df = Counter()
        for doc in self._docs:
            tokens = set(self._tokenize(self._doc_text(doc)))
            df.update(tokens)
        return {t: math.log((n + 1) / (f + 1)) + 1 for t, f in df.items()}

    @staticmethod
    def _doc_text(doc: dict) -> str:
        return f"{doc['crop']} {doc['name_cn']} {doc['symptoms']} {doc['chemical']} {doc['biological']} {doc['agricultural']}"

    # ── 查询 ────────────────────────────────────────────

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """根据查询文本检索最相关的病害知识条目。"""
        query_tokens = self._tokenize(query)
        q_tf = {t: c / max(len(query_tokens), 1) for t, c in Counter(query_tokens).items()}

        scores = []
        for doc in self._docs:
            doc_tokens = set(self._tokenize(self._doc_text(doc)))
            score = sum(q_tf.get(t, 0) * self._idf.get(t, 0) for t in doc_tokens & q_tf.keys())
            if score > 0:
                scores.append((score, doc))

        scores.sort(key=lambda x: x[0], reverse=True)
        return [d for _, d in scores[:top_k]]

    # ── 格式化 ──────────────────────────────────────────

    def format_context(self, detections: list[dict]) -> str:
        """将检测结果对应的知识格式化为 RAG 上下文。"""
        seen = set()
        lines = []

        for d in detections:
            name = d.get("class_name", "")
            if name in seen:
                continue
            seen.add(name)
            # 精确匹配知识库
            for doc in self._docs:
                if doc["name_en"] == name:
                    lines.append(self._doc_to_str(doc))
                    break

        if not lines:
            return ""

        return "\n\n---\n\n".join(lines)

    @staticmethod
    def _doc_to_str(doc: dict) -> str:
        return (
            f"【{doc['name_cn']}({doc['crop']}) · 严重程度: {doc['severity']}】\n"
            f"症状: {doc['symptoms']}\n"
            f"化学防治: {doc['chemical']}\n"
            f"生物防治: {doc['biological']}\n"
            f"农业措施: {doc['agricultural']}\n"
            f"传染性: {'强' if doc['contagious'] else '无'} — {doc['contagion_note']}"
        )
