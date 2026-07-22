"""
聊天服务模块
=============
接入通义千问 Qwen3-Omni-Flash 多模态模型，实现基于检测结果的智能诊断对话。
通过 DashScope API 的 SSE 流式接口逐 token 推送回复。
"""

import json
import logging
import os

import httpx

logger = logging.getLogger("agrivision.chat")

DASHSCOPE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
API_KEY = os.getenv("DASHSCOPE_API_KEY", "")

if not API_KEY:
    logger.warning("DASHSCOPE_API_KEY 未设置，AI 诊断功能将不可用")

SYSTEM_PROMPT = (
    "你是农业植保专家，服务于智慧农业病害检测平台 AgriVision。"
    "用户会提供一张已用 YOLOv8 标注检测框的作物叶片图片，以及对应的检测结果列表（病害名称、置信度）。"
    "请结合图片中的实际症状（霉斑颜色与面积、坏死范围、叶片整体状态等）给出诊断分析和防治建议。"
    "回答要求："
    "1. 先描述图片中观察到的主要症状特征"
    "2. 结合检测结果给出病害诊断"
    "3. 提供具体的防治方案，包括化学防治（农药名称与用量）、生物防治、农业措施"
    "4. 如有必要，补充预警建议（是否会传染、需要隔离的作物等）"
    "格式要求：不要使用 ### 和 --- 等 markdown 标题分隔符号。可以使用数字编号、换行分段、emoji 图标来组织内容。始终使用中文回答。"
)


def _build_system_prompt(detections: list[dict]) -> str:
    """构建带 RAG 知识库上下文的 system prompt。"""
    try:
        from backend.app.services.knowledge import KnowledgeService
        ctx = KnowledgeService().format_context(detections)
        if ctx:
            return (
                SYSTEM_PROMPT
                + "\n\n以下是检测到的病害的专业防治知识库，请基于这些权威信息并结合图片给出诊断建议，"
                "不要凭空编造农药名称和用量：\n\n"
                + ctx
            )
    except Exception:
        logger.exception("Failed to load knowledge context")
    return SYSTEM_PROMPT


def _build_detection_text(detections: list[dict]) -> str:
    """将检测列表格式化为文本摘要。"""
    if not detections:
        return "（未检测到病害目标）"
    lines = ["检测到以下病害："]
    for d in detections:
        name = d.get("class_name", "未知")
        conf = d.get("confidence", 0)
        lines.append(f"- {name}  置信度 {(conf * 100):.0f}%")
    return "\n".join(lines)


class ChatService:
    """单例聊天服务，封装千问 API 流式调用。"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def handle(self, websocket):
        detection_context: list[dict] = []
        annotated_image_b64: str | None = None
        messages: list[dict] = []

        while True:
            raw = await websocket.receive_text()
            msg = json.loads(raw)
            action = msg.get("action", "")

            if action == "attach":
                detection_context = msg.get("detections", [])
                annotated_image_b64 = msg.get("image_base64", "")
                messages = []
                await websocket.send_json({"type": "attached", "count": len(detection_context)})

            elif action == "ask":
                question = msg.get("question", "").strip()
                if not question:
                    continue

                user_content = []

                if annotated_image_b64:
                    user_content.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{annotated_image_b64}"},
                    })

                user_content.append({
                    "type": "text",
                    "text": f"{_build_detection_text(detection_context)}\n\n用户问题：{question}",
                })

                messages.append({"role": "user", "content": user_content})

                system_msg = _build_system_prompt(detection_context)

                payload = {
                    "model": "qwen3-omni-flash",
                    "stream": True,
                    "messages": [
                        {"role": "system", "content": system_msg},
                    ] + messages,
                }

                await websocket.send_json({"type": "stream_start"})
                full = ""

                try:
                    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=10.0)) as client:
                        async with client.stream(
                            "POST",
                            DASHSCOPE_URL,
                            json=payload,
                            headers={
                                "Authorization": f"Bearer {API_KEY}",
                                "Content-Type": "application/json",
                            },
                        ) as resp:
                            if resp.status_code != 200:
                                body = await resp.aread()
                                logger.error("DashScope API error %d: %s", resp.status_code, body)
                                await websocket.send_json({
                                    "type": "error",
                                    "message": f"模型服务异常 (HTTP {resp.status_code})",
                                })
                                continue

                            async for line in resp.aiter_lines():
                                if not line or not line.startswith("data: "):
                                    continue
                                data_str = line[6:].strip()
                                if data_str == "[DONE]":
                                    break
                                try:
                                    chunk = json.loads(data_str)
                                except json.JSONDecodeError:
                                    continue
                                choices = chunk.get("choices", [])
                                if not choices:
                                    continue
                                delta = choices[0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    full += content
                                    await websocket.send_json({"type": "token", "text": content})

                except httpx.RequestError as e:
                    logger.exception("DashScope request failed")
                    await websocket.send_json({"type": "error", "message": "模型请求失败，请稍后重试"})
                    continue

                messages.append({"role": "assistant", "content": full})
                await websocket.send_json({"type": "done"})
