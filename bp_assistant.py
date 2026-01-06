"""BP（Ban/Pick）分析助手主程式（備用版本）

注意：此文件使用正則表達式解析輸入，功能較弱。
推薦使用 bp_react_assistant.py（使用 LLM 解析，更智能）
"""
import sys
import os
import re
import json

# 添加項目路徑
sys.path.insert(0, os.path.dirname(__file__))

from src.tools.hero_name_mapper import load_hero_names, translate_hero_name, translate_hero_list
from src.tools.bp_predictor import predict_winrate, recommend_pick, recommend_ban


def parse_user_input(user_input: str):
    """解析用戶輸入，提取隊伍和英雄信息"""
    # 初始化結果
    result = {
        "team1_picks": [],
        "team2_picks": [],
        "team1_bans": [],
        "team2_bans": [],
        "action": None,
        "team": "blue"
    }
    
    user_input = user_input.strip()
    # 檢測動作類型
    if "預測" in user_input or "勝率" in user_input:
        result["action"] = "predict_winrate"
    elif "選" in user_input and ("推薦" in user_input or "應該" in user_input):
        result["action"] = "recommend_pick"
    elif "ban" in user_input.lower() or "禁" in user_input or "禁用" in user_input:
        result["action"] = "recommend_ban"
    else:
        result["action"] = "predict_winrate"  # 預設動作
    
    # 檢測隊伍
    if "紅隊" in user_input or "紅方" in user_input:
        result["team"] = "red"
    elif "藍隊" in user_input or "藍方" in user_input:
        result["team"] = "blue"
    
    # 提取英雄名稱（使用正則表達式）
    # 匹配模式：隊伍名稱 + 動詞 + 英雄名稱列表
    patterns = [
        r"藍隊[選選了]*[:：]?([^，,。.]+)",
        r"紅隊[選選了]*[:：]?([^，,。.]+)",
        r"藍方[選選了]*[:：]?([^，,。.]+)",
        r"紅方[選選了]*[:：]?([^，,。.]+)",
    ]
    
    # 提取藍隊選擇
    for pattern in [r"藍隊[選選了]*[:：]?([^，,。.紅]+)", r"藍方[選選了]*[:：]?([^，,。.紅]+)"]:
        matches = re.findall(pattern, user_input)
        for match in matches:
            heroes = re.split(r'[，,、和跟]', match.strip())
            result["team1_picks"].extend([h.strip() for h in heroes if h.strip()])
    
    # 提取紅隊選擇
    for pattern in [r"紅隊[選選了]*[:：]?([^，,。.藍]+)", r"紅方[選選了]*[:：]?([^，,。.藍]+)"]:
        matches = re.findall(pattern, user_input)
        for match in matches:
            heroes = re.split(r'[，,、和跟]', match.strip())
            result["team2_picks"].extend([h.strip() for h in heroes if h.strip()])
    
    # 如果沒有明確的隊伍標記，嘗試從上下文推斷
    if not result["team1_picks"] and not result["team2_picks"]:
        # 嘗試提取所有可能的英雄名稱
        # 這裡可以改進，使用更智能的解析
        pass
    
    return result


def format_result(result):
    """格式化結果輸出"""
    if isinstance(result, dict):
        if "winrate" in result:
            winrate = result["winrate"]
            team = result["team"]
            team_name = "藍隊" if team == "blue" else "紅隊"
            return f"{team_name}的預測勝率: {winrate:.2%}\n\n翻譯後的陣容:\n{json.dumps(result.get('translated_data', {}), ensure_ascii=False, indent=2)}"
        elif "translated_data" in result:
            return json.dumps(result, ensure_ascii=False, indent=2)
    elif isinstance(result, list):
        # 推薦列表
        output = "推薦結果:\n"
        for i, (hero, score) in enumerate(result, 1):
            output += f"{i}. {hero}: {score:.4f}\n"
        return output
    elif isinstance(result, str):
        return result
    else:
        return str(result)


def main():
    """主程式"""
    print("=" * 60)
    print("BP（Ban/Pick）分析助手")
    print("=" * 60)
    print("\n您可以輸入自然語言來詢問 BP 相關問題，例如：")
    print("- '當前陣容是藍隊選了 Neeko, Trundle，紅隊選了 Xin Zhao, Taliyah，請預測勝率'")
    print("- '藍隊應該選誰？'")
    print("- '推薦紅隊應該 ban 誰'")
    print("- '輸入 quit 或 exit 退出'\n")
    
    # 載入映射表
    try:
        load_hero_names()
        print("✓ 英雄名稱映射表載入成功\n")
    except Exception as e:
        print(f"✗ 載入英雄名稱映射失敗: {e}\n")
        return
    
    while True:
        try:
            user_input = input("請輸入您的問題: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                print("再見！")
                break
            
            if not user_input:
                continue
            
            # 解析用戶輸入
            parsed = parse_user_input(user_input)
            
            # 執行對應的動作
            if parsed["action"] == "predict_winrate":
                result = predict_winrate(
                    team1_picks=parsed["team1_picks"],
                    team2_picks=parsed["team2_picks"],
                    team1_bans=parsed["team1_bans"],
                    team2_bans=parsed["team2_bans"],
                    team=parsed["team"]
                )
                print("\n" + format_result(result) + "\n")
            
            elif parsed["action"] == "recommend_pick":
                result = recommend_pick(
                    team1_picks=parsed["team1_picks"],
                    team2_picks=parsed["team2_picks"],
                    team1_bans=parsed["team1_bans"],
                    team2_bans=parsed["team2_bans"],
                    team=parsed["team"]
                )
                print("\n" + format_result(result) + "\n")
            
            elif parsed["action"] == "recommend_ban":
                result = recommend_ban(
                    team1_picks=parsed["team1_picks"],
                    team2_picks=parsed["team2_picks"],
                    team1_bans=parsed["team1_bans"],
                    team2_bans=parsed["team2_bans"],
                    target_team=parsed["team"]
                )
                print("\n" + format_result(result) + "\n")
        
        except KeyboardInterrupt:
            print("\n\n再見！")
            break
        except Exception as e:
            print(f"\n錯誤: {e}\n")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    main()
