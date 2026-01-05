"""英雄名稱映射工具：將中文名稱映射到英文名稱"""
import json
import os
from typing import Dict, Optional

# 載入映射表
_HERO_MAP: Optional[Dict[str, str]] = None
_REVERSE_MAP: Optional[Dict[str, str]] = None


def load_hero_names(file_path: str = "HeroNames.txt") -> Dict[str, str]:
    """載入英雄名稱映射表
    
    Args:
        file_path: 映射表文件路徑
        
    Returns:
        中文名稱到英文名稱的映射字典
    """
    global _HERO_MAP, _REVERSE_MAP
    
    if _HERO_MAP is not None:
        return _HERO_MAP
    
    # 嘗試多個可能的路徑
    possible_paths = [
        file_path,
        os.path.join(os.path.dirname(__file__), "..", "..", file_path),
        os.path.join(os.getcwd(), file_path),
    ]
    
    hero_file = None
    for path in possible_paths:
        if os.path.exists(path):
            hero_file = path
            break
    
    if hero_file is None:
        raise FileNotFoundError(f"找不到英雄名稱映射文件: {file_path}")
    
    try:
        with open(hero_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 建立反向映射：中文 -> 英文
        _HERO_MAP = {}
        _REVERSE_MAP = {}
        
        for english_name, chinese_names in data.items():
            # 英文名稱本身也可以映射到自己
            _HERO_MAP[english_name.lower()] = english_name
            _REVERSE_MAP[english_name] = english_name
            
            # 建立所有中文別名到英文名稱的映射
            if isinstance(chinese_names, list):
                for chinese_name in chinese_names:
                    _HERO_MAP[chinese_name] = english_name
                    _HERO_MAP[chinese_name.lower()] = english_name
        
        return _HERO_MAP
    except json.JSONDecodeError as e:
        raise ValueError(f"載入英雄名稱映射失敗: {e}")


def translate_hero_name(name: str) -> Optional[str]:
    """將中文或英文英雄名稱翻譯為標準英文名稱
    
    Args:
        name: 輸入的英雄名稱（中文或英文）
        
    Returns:
        標準英文名稱，如果找不到則返回 None
    """
    if _HERO_MAP is None:
        load_hero_names()
    
    # 先嘗試直接匹配
    if name in _HERO_MAP:
        return _HERO_MAP[name]
    
    # 嘗試小寫匹配
    name_lower = name.lower()
    if name_lower in _HERO_MAP:
        return _HERO_MAP[name_lower]
    
    # 嘗試部分匹配（處理大小寫和空格問題）
    for key, value in _HERO_MAP.items():
        if key.lower() == name_lower or key.lower().replace(" ", "") == name_lower.replace(" ", ""):
            return value
    
    return None


def translate_hero_list(names: list) -> list:
    """批量翻譯英雄名稱列表
    
    Args:
        names: 英雄名稱列表（可能包含中文或英文）
        
    Returns:
        翻譯後的英文名稱列表
    """
    translated = []
    for name in names:
        if not name or not name.strip():
            continue
        translated_name = translate_hero_name(name.strip())
        if translated_name:
            translated.append(translated_name)
        else:
            # 如果找不到映射，保留原名（可能是已經是英文名稱）
            translated.append(name.strip())
    return translated
