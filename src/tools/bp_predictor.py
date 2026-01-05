"""BP（Ban/Pick）預測工具"""
import sys
import os
import pandas as pd

# 添加項目根目錄到路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from predict import BPpredictor
from .hero_name_mapper import translate_hero_list, load_hero_names

# 全局模型實例
_model: BPpredictor = None


def get_model():
    """獲取或初始化 BP 預測模型"""
    global _model
    if _model is None:
        try:
            games_df = pd.read_csv("games.csv")
            hero_df = pd.read_csv("heroes.csv")
            _model = BPpredictor(games_df, hero_df, modelName="bp_predictor.model")
        except Exception as e:
            raise RuntimeError(f"無法載入 BP 預測模型: {e}")
    return _model


def predict_winrate(team1_picks=None, team2_picks=None, 
                   team1_bans=None, team2_bans=None, team="blue"):
    """預測勝率
    
    Args:
        team1_picks: 藍隊選擇的英雄列表（可以是中文或英文名稱）
        team2_picks: 紅隊選擇的英雄列表（可以是中文或英文名稱）
        team1_bans: 藍隊禁用的英雄列表（可以是中文或英文名稱）
        team2_bans: 紅隊禁用的英雄列表（可以是中文或英文名稱）
        team: 要預測的隊伍（"blue" 或 "red"），預設為 "blue"
        
    Returns:
        勝率（0-1之間的浮點數）
    """
    # 確保映射表已載入
    try:
        load_hero_names()
    except Exception as e:
        return f"錯誤：無法載入英雄名稱映射表 - {e}"
    
    # 初始化模型
    try:
        model = get_model()
    except Exception as e:
        return f"錯誤：無法載入預測模型 - {e}"
    
    # 翻譯所有英雄名稱
    data = {
        "team1_picks": translate_hero_list(team1_picks or []),
        "team2_picks": translate_hero_list(team2_picks or []),
        "team1_bans": translate_hero_list(team1_bans or []),
        "team2_bans": translate_hero_list(team2_bans or [])
    }
    
    try:
        winrate = model.predict_winrate(data)
        
        # 根據 team 參數返回對應隊伍的勝率
        if team == "red":
            winrate = 1 - winrate
        
        return {
            "winrate": winrate,
            "team": team,
            "translated_data": data
        }
    except Exception as e:
        return f"錯誤：預測失敗 - {e}"


def recommend_pick(team1_picks=None, team2_picks=None,
                  team1_bans=None, team2_bans=None, 
                  team="blue", top_k=5):
    """推薦選擇的英雄
    
    Args:
        team1_picks: 藍隊選擇的英雄列表
        team2_picks: 紅隊選擇的英雄列表
        team1_bans: 藍隊禁用的英雄列表
        team2_bans: 紅隊禁用的英雄列表
        team: 要推薦的隊伍（"blue" 或 "red"）
        top_k: 返回前 k 個推薦
        
    Returns:
        推薦的英雄列表，每個元素為 (英雄名稱, 預測勝率)
    """
    try:
        load_hero_names()
        model = get_model()
    except Exception as e:
        return f"錯誤：{e}"
    
    data = {
        "team1_picks": translate_hero_list(team1_picks or []),
        "team2_picks": translate_hero_list(team2_picks or []),
        "team1_bans": translate_hero_list(team1_bans or []),
        "team2_bans": translate_hero_list(team2_bans or [])
    }
    
    try:
        recommendations = model.recommend_pick(data, team=team, top_k=top_k)
        return recommendations
    except Exception as e:
        return f"錯誤：推薦失敗 - {e}"


def recommend_ban(team1_picks=None, team2_picks=None,
                 team1_bans=None, team2_bans=None,
                 target_team="red", top_k=5):
    """推薦禁用的英雄
    
    Args:
        team1_picks: 藍隊選擇的英雄列表
        team2_picks: 紅隊選擇的英雄列表
        team1_bans: 藍隊禁用的英雄列表
        team2_bans: 紅隊禁用的英雄列表
        target_team: 要為哪個隊伍推薦 ban（"blue" 或 "red"）
        top_k: 返回前 k 個推薦
        
    Returns:
        推薦的英雄列表，每個元素為 (英雄名稱, 優先級)
    """
    try:
        load_hero_names()
        model = get_model()
    except Exception as e:
        return f"錯誤：{e}"
    
    data = {
        "team1_picks": translate_hero_list(team1_picks or []),
        "team2_picks": translate_hero_list(team2_picks or []),
        "team1_bans": translate_hero_list(team1_bans or []),
        "team2_bans": translate_hero_list(team2_bans or [])
    }
    
    try:
        recommendations = model.recommend_ban(data, target_team=target_team, top_k=top_k)
        return recommendations
    except Exception as e:
        return f"錯誤：推薦失敗 - {e}"
