import asyncio
from backend.core.config import get_settings
from backend.core.models import GraphState
from backend.core.extractor import extract_entities

async def run_real_llm_test():
    # 1. 读取 .env 里的真实 API Key
    settings = get_settings()
    if not settings.DEEPSEEK_API_KEY or settings.DEEPSEEK_API_KEY == "your_key_here":
        print("❌ 请先在 .env 文件中填入真实的 DEEPSEEK_API_KEY")
        return

    # 2. 伪造一个“第一章”的初始状态
    initial_state = GraphState(
        known_characters=[
            {"name": "Hercule Poirot", "aliases": ["Poirot"], "description": "A Belgian detective."}
        ],
        known_relationships=[]
    )

    # 3. 喂给它一段“第二章”的新文本（包含别名和新关系）
    text_chunk = """
    The Belgian little man sat quietly. 'My dear Hastings,' Hercule Poirot said, 
    'the murderer is someone in this very room!' Captain Arthur Hastings looked shocked.
    """

    print("🚀 正在呼叫 DeepSeek... 请等待约 3-5 秒...")
    
    # 4. 真实调用！
    new_state = await extract_entities(text_chunk, initial_state, settings.DEEPSEEK_API_KEY)
    
    print("\n✅ 提取成功！最新的知识图谱状态如下：")
    print(new_state.model_dump_json(indent=2))

if __name__ == "__main__":
    asyncio.run(run_real_llm_test())