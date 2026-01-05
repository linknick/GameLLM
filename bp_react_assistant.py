"""BP（Ban/Pick）分析助手 - 使用 ReAct Agent"""
import sys
import os

# 添加項目路徑
sys.path.insert(0, os.path.dirname(__file__))

from src.agent.bp_react_agent import run_bp_react
from src.tools.hero_name_mapper import load_hero_names


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
            
            # 使用 ReAct Agent 處理
            result = run_bp_react(user_input)
            print(f"\n{result}\n")
        
        except KeyboardInterrupt:
            print("\n\n再見！")
            break
        except Exception as e:
            print(f"\n錯誤: {e}\n")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    main()
