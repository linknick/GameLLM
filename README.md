# BP（Ban/Pick）分析助手

這是一個基於機器學習的 League of Legends BP（Ban/Pick）分析系統，可以預測勝率、推薦選擇和禁用英雄。

## 📁 項目結構

### 🎯 主程式（入口點）

- **`bp_react_assistant.py`** ⭐ **推薦使用**
  - BP 分析助手的主程式（使用 LLM ReAct Agent）
  - 支援自然語言輸入，使用 LLM 理解用戶意圖
  - 自動處理中文英雄名稱映射
  - **使用方式**: `python bp_react_assistant.py`

- **`bp_assistant.py`** （備用）
  - BP 分析助手的備用版本（使用正則表達式解析）
  - 不依賴 LLM，但解析能力較弱
  - 可作為備用方案使用

### 🧠 核心模組 (`src/`)

#### Agent 模組 (`src/agent/`)

- **`bp_react_agent.py`**
  - BP 專用的 ReAct Agent
  - 使用 LLM 解析用戶輸入並生成 JSON Action
  - 自動將中文英雄名稱映射為英文名稱
  - 整合預測、推薦等功能

- **`react_agent.py`**
  - 通用的 ReAct Agent 範例
  - 用於其他任務（如計數字母等）

#### 工具模組 (`src/tools/`)

- **`bp_predictor.py`** ⭐ **核心工具**
  - BP 預測工具的主要接口
  - 提供 `predict_winrate()`, `recommend_pick()`, `recommend_ban()` 函數
  - 自動整合英雄名稱映射功能
  - 封裝 `predict.py` 中的 `BPpredictor` 類

- **`hero_name_mapper.py`** ⭐ **映射工具**
  - 英雄名稱映射工具
  - 載入 `HeroNames.txt` 映射表
  - 提供 `translate_hero_name()` 和 `translate_hero_list()` 函數
  - 支援中文到英文的映射（如：「趙信」→「Xin Zhao」）

- **`count_letters.py`**
  - 範例工具：計算字母數量
  - 用於演示 ReAct Agent 的使用

#### 其他模組

- **`src/llm_client.py`**
  - LLM 客戶端封裝
  - 支援 Ollama 和 OpenAI API
  - 提供統一的接口

- **`src/vision/vision_service.py`**
  - 圖像分類服務（與 BP 分析無關）

- **`src/rag/rag_index.py`**
  - RAG 索引服務（與 BP 分析無關）

### 📊 數據文件

- **`HeroNames.txt`** ⭐ **映射表**
  - 英雄名稱映射表（JSON 格式）
  - 包含所有英雄的英文名稱和中文別名
  - 格式：`{"英文名稱": ["中文別名1", "中文別名2", ...]}`

- **`bp_predictor.model`**
  - 訓練好的 XGBoost 模型文件
  - 用於勝率預測

- **`games.csv`**
  - 遊戲數據（用於訓練和初始化模型）

- **`heroes.csv`**
  - 英雄數據（用於初始化模型）

- **`match_data.csv`, `match_datashort.csv`, `matchData.csv`, `matchDataShort1.csv`**
  - 原始比賽數據（用於數據預處理）

### 🔧 核心算法

- **`predict.py`**
  - BP 預測器的核心實現
  - `BPpredictor` 類：包含模型訓練、特徵工程、勝率預測等功能
  - 使用 XGBoost 進行勝率預測
  - 計算英雄之間的 counter 和 synergy 關係

- **`preprocessing.py`**
  - 數據預處理腳本
  - 將原始比賽數據轉換為訓練格式

### 📝 其他文件

- **`run_demo.py`**
  - 演示程式（圖像分類 + ReAct 範例）
  - 與 BP 分析無關，用於演示其他功能

- **`requirement.txt`**
  - Python 依賴包列表

## 🚀 快速開始

### 1. 安裝依賴

```bash
pip install -r requirement.txt
```

### 2. 運行 BP 分析助手

```bash
python bp_react_assistant.py
```

### 3. 使用範例

```
請輸入您的問題: 藍隊選擇了妮可，紅隊選了趙信跟岩雀，請預測勝率
```

系統會自動：
1. 解析用戶輸入
2. 將中文名稱映射為英文（「妮可」→「Neeko」，「趙信」→「Xin Zhao」，「岩雀」→「Taliyah」）
3. 預測勝率並返回結果

## 🔄 工作流程

```
用戶輸入（自然語言）
    ↓
bp_react_assistant.py
    ↓
bp_react_agent.py (使用 LLM 解析)
    ↓
生成 JSON Action
    ↓
bp_predictor.py (執行工具)
    ↓
hero_name_mapper.py (映射中文名稱)
    ↓
predict.py (BPpredictor 類)
    ↓
返回結果
```

## 📌 重要說明

1. **英雄名稱映射**：系統會自動將中文名稱映射為英文名稱，確保正確識別
2. **LLM 配置**：需要配置 LLM（Ollama 或 OpenAI），詳見 `src/llm_client.py`
3. **模型文件**：確保 `bp_predictor.model` 存在，否則需要先訓練模型

## 🗂️ 文件清理建議

以下文件可以考慮移動到 `data/` 或 `archive/` 目錄：
- `match_data.csv`, `match_datashort.csv`, `matchData.csv`, `matchDataShort1.csv`（原始數據）
- `bp_assistant.py`（如果只使用 `bp_react_assistant.py`）

## 📝 版本歷史

- **v1.0**: 初始版本，支援基本的 BP 預測功能
- **v1.1**: 添加英雄名稱映射功能，修復中文名稱識別問題
