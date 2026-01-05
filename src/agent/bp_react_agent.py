"""BP（Ban/Pick）分析助手的 ReAct Agent"""
import re
import json
import os
import sys
from typing import List, Dict, Optional

# 添加項目路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from ..llm_client import LLMClient
from ..tools.hero_name_mapper import load_hero_names, translate_hero_name, translate_hero_list
from ..tools.bp_predictor import predict_winrate, recommend_pick, recommend_ban

llm = LLMClient()

# 載入映射表以提供給 LLM
_HERO_MAP_STR = None

def get_hero_mapping_info():
    """獲取英雄映射信息，用於提示 LLM"""
    global _HERO_MAP_STR
    if _HERO_MAP_STR is None:
        try:
            load_hero_names()
            # 讀取映射文件並格式化
            with open("HeroNames.txt", 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 構建映射字符串
            mapping_examples = []
            for eng_name, chinese_names in list(data.items())[:10]:  # 只顯示前10個作為示例
                if isinstance(chinese_names, list) and chinese_names:
                    mapping_examples.append(f'  "{chinese_names[0]}": "{eng_name}"')
            
            _HERO_MAP_STR = "\n".join(mapping_examples)
        except Exception as e:
            _HERO_MAP_STR = f"載入映射表失敗: {e}"
    return _HERO_MAP_STR

def get_system_prompt():
    """獲取系統提示詞（動態載入映射信息）"""
    mapping_info = get_hero_mapping_info()
    return f"""你是一個 BP（Ban/Pick）分析助手。當用戶詢問 BP 相關問題時，你需要：

1. 解析用戶輸入，提取隊伍和英雄信息
2. **重要**：將所有中文英雄名稱轉換為標準英文名稱（使用提供的映射表）
3. 輸出 JSON 格式的 Action

可用的工具：
- predict_winrate(team1_picks, team2_picks, team1_bans, team2_bans, team): 預測勝率
- recommend_pick(team1_picks, team2_picks, team1_bans, team2_bans, team, top_k): 推薦選擇
- recommend_ban(team1_picks, team2_picks, team1_bans, team2_bans, target_team, top_k): 推薦禁用

**英雄名稱映射規則（必須嚴格遵守）：**
- 必須使用標準英文名稱，例如："Xin Zhao"（不是 "Zhao Xin"）、"Taliyah"（不是 "Yan"）、"Neeko"（不是 "Niko"）
- 常見映射示例：
{mapping_info}
- 完整映射表已載入，請確保使用正確的英文名稱

輸出格式：
```json
{{
  "action": "predict_winrate" | "recommend_pick" | "recommend_ban",
  "args": {{
    "team1_picks": ["英文名稱1", "英文名稱2"],
    "team2_picks": ["英文名稱1", "英文名稱2"],
    "team1_bans": [],
    "team2_bans": [],
    "team": "blue" | "red",
    "top_k": 1
  }}
}}
```

請確保：
1. 所有英雄名稱都是標準英文名稱（參考映射表）
2. team1_picks 和 team2_picks 是字符串數組
3. 如果沒有指定，bans 為空數組
4. team 參數：預測勝率時指定要查詢的隊伍，推薦時指定要為哪個隊伍推薦

用繁體中文回應。"""


def parse_json_action(text: str) -> Optional[Dict]:
    """從 LLM 輸出中解析 JSON Action"""
    # 嘗試提取 JSON 塊
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        # 嘗試直接找 JSON 對象
        json_match = re.search(r'\{.*"action".*\}', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
        else:
            return None
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None


def run_bp_react(user_input: str) -> str:
    """運行 BP ReAct 循環"""
    messages = [
        {"role": "system", "content": get_system_prompt()},
        {"role": "user", "content": user_input}
    ]
    
    # Step 1: 讓 LLM 解析輸入並生成 Action
    print("\n[Agent 思考]")
    step1 = llm.generate(messages)
    print(step1)
    
    # 解析 Action
    action_data = parse_json_action(step1)
    
    if not action_data:
        return "無法解析 Action，請檢查輸出格式。"
    
    action = action_data.get("action")
    args = action_data.get("args", {})
    
    print(f"\n[執行 Action: {action}]")
    print(f"[參數: {json.dumps(args, ensure_ascii=False, indent=2)}]")
    
    # 執行對應的工具
    obs = None
    try:
        # 先翻譯所有英雄名稱
        team1_picks = translate_hero_list(args.get("team1_picks", []))
        team2_picks = translate_hero_list(args.get("team2_picks", []))
        team1_bans = translate_hero_list(args.get("team1_bans", []))
        team2_bans = translate_hero_list(args.get("team2_bans", []))
        
        print(f"\n[翻譯後的陣容]")
        print(f"藍隊選擇: {team1_picks}")
        print(f"紅隊選擇: {team2_picks}")
        print(f"藍隊禁用: {team1_bans}")
        print(f"紅隊禁用: {team2_bans}")
        
        if action == "predict_winrate":
            result = predict_winrate(
                team1_picks=team1_picks,
                team2_picks=team2_picks,
                team1_bans=team1_bans,
                team2_bans=team2_bans,
                team=args.get("team", "blue")
            )
            if isinstance(result, dict) and "winrate" in result:
                team_name = "藍隊" if result["team"] == "blue" else "紅隊"
                obs = f"{team_name}的預測勝率: {result['winrate']:.2%}"
            else:
                obs = str(result)
        
        elif action == "recommend_pick":
            result = recommend_pick(
                team1_picks=team1_picks,
                team2_picks=team2_picks,
                team1_bans=team1_bans,
                team2_bans=team2_bans,
                team=args.get("team", "blue"),
                top_k=args.get("top_k", 5)
            )
            if isinstance(result, list):
                obs = "推薦選擇:\n" + "\n".join([f"{i+1}. {hero}: {score:.4f}" for i, (hero, score) in enumerate(result)])
            else:
                obs = str(result)
        
        elif action == "recommend_ban":
            result = recommend_ban(
                team1_picks=team1_picks,
                team2_picks=team2_picks,
                team1_bans=team1_bans,
                team2_bans=team2_bans,
                target_team=args.get("team", "red"),
                top_k=args.get("top_k", 5)
            )
            if isinstance(result, list):
                obs = "推薦禁用:\n" + "\n".join([f"{i+1}. {hero}: {priority:.4f}" for i, (hero, priority) in enumerate(result)])
            else:
                obs = str(result)
        
        else:
            obs = f"未知的動作: {action}"
    
    except Exception as e:
        obs = f"執行錯誤: {e}"
        import traceback
        traceback.print_exc()
    
    # Step 2: 將觀察結果返回給 LLM，讓它生成最終回答
    messages.append({"role": "assistant", "content": step1})
    messages.append({"role": "user", "content": f"Observation: {obs}\n\n請用繁體中文總結結果並給出建議。"})
    
    print(f"\n[助手回應]")
    final = llm.generate(messages)
    print(final)
    
    return final


if __name__ == '__main__':
    # 測試
    test_input = "藍隊選擇了妮可，紅隊選了趙信跟岩雀，請預測勝率"
    result = run_bp_react(test_input)
    print(f"\n最終結果:\n{result}")
