# 文件功能說明指南

## 🚀 快速開始

**推薦使用**: `python bp_react_assistant.py`

這是 BP 分析助手的主程式，支援自然語言輸入，自動處理中文英雄名稱映射。

---

## 📋 文件分類

### 1️⃣ 主程式（入口點）

#### `bp_react_assistant.py` ⭐⭐⭐ **推薦使用**
- **功能**: BP 分析助手主程式（使用 LLM）
- **特點**: 
  - 支援自然語言輸入
  - 自動映射中文英雄名稱
  - 使用 ReAct Agent 智能解析
- **使用**: `python bp_react_assistant.py`

#### `bp_assistant.py` ⭐ 備用
- **功能**: BP 分析助手（正則解析版本）
- **特點**: 不依賴 LLM，但解析能力較弱
- **使用**: `python bp_assistant.py`

---

### 2️⃣ 核心模組 (`src/`)

#### Agent 模組 (`src/agent/`)

**`bp_react_agent.py`** ⭐⭐⭐
- **功能**: BP 專用 ReAct Agent
- **作用**: 
  - 使用 LLM 解析用戶自然語言輸入
  - 生成結構化的 JSON Action
  - 自動調用對應的工具函數
- **關鍵**: 在執行工具前自動映射英雄名稱

**`react_agent.py`**
- **功能**: 通用 ReAct Agent 範例
- **作用**: 演示 ReAct 模式的使用（與 BP 無關）

#### 工具模組 (`src/tools/`)

**`bp_predictor.py`** ⭐⭐⭐
- **功能**: BP 預測工具的主要接口
- **提供函數**:
  - `predict_winrate()` - 預測勝率
  - `recommend_pick()` - 推薦選擇英雄
  - `recommend_ban()` - 推薦禁用英雄
- **特點**: 自動整合英雄名稱映射功能

**`hero_name_mapper.py`** ⭐⭐⭐
- **功能**: 英雄名稱映射工具
- **提供函數**:
  - `load_hero_names()` - 載入映射表
  - `translate_hero_name()` - 翻譯單個名稱
  - `translate_hero_list()` - 批量翻譯
- **作用**: 將中文名稱（如「趙信」）映射為英文名稱（如「Xin Zhao」）

**`count_letters.py`**
- **功能**: 範例工具（計算字母數量）
- **作用**: 演示工具的使用方式

#### 其他模組

**`src/llm_client.py`** ⭐⭐
- **功能**: LLM 客戶端封裝
- **支援**: Ollama 和 OpenAI API
- **作用**: 提供統一的 LLM 調用接口

**`src/vision/vision_service.py`**
- **功能**: 圖像分類服務
- **備註**: 與 BP 分析無關

**`src/rag/rag_index.py`**
- **功能**: RAG 索引服務
- **備註**: 與 BP 分析無關

---

### 3️⃣ 核心算法

**`predict.py`** ⭐⭐⭐
- **功能**: BP 預測器的核心實現
- **包含**:
  - `BPpredictor` 類
  - 模型訓練邏輯
  - 特徵工程（counter、synergy 計算）
  - 勝率預測算法
- **技術**: 使用 XGBoost 進行預測

**`preprocessing.py`** ⭐
- **功能**: 數據預處理
- **作用**: 將原始比賽數據轉換為訓練格式

---

### 4️⃣ 數據文件

**`HeroNames.txt`** ⭐⭐⭐ **必需**
- **格式**: JSON
- **內容**: 英雄英文名稱到中文別名的映射
- **範例**: `{"Xin Zhao": ["趙信", "趙雲", "趙子龍"]}`
- **用途**: 用於將用戶輸入的中文名稱轉換為標準英文名稱

**`bp_predictor.model`** ⭐⭐⭐ **必需**
- **格式**: XGBoost 模型文件
- **用途**: 用於勝率預測
- **生成**: 通過 `predict.py` 訓練生成

**`games.csv`** ⭐⭐
- **內容**: 遊戲數據
- **用途**: 用於初始化 `BPpredictor` 模型

**`heroes.csv`** ⭐⭐
- **內容**: 英雄數據
- **用途**: 用於初始化 `BPpredictor` 模型

**`match_*.csv`** ⭐
- **內容**: 原始比賽數據
- **用途**: 用於數據預處理和訓練
- **備註**: 可移動到 `data/` 目錄

---

### 5️⃣ 文檔

**`README.md`** ⭐⭐
- **內容**: 項目總體說明
- **包含**: 快速開始、工作流程、使用範例

**`PROJECT_STRUCTURE.md`** ⭐
- **內容**: 項目結構詳細說明
- **包含**: 目錄結構、文件分類

**`FILES_GUIDE.md`** ⭐
- **內容**: 本文件，各文件功能說明

---

### 6️⃣ 其他

**`requirement.txt`** ⭐⭐
- **內容**: Python 依賴包列表
- **用途**: `pip install -r requirement.txt`

**`run_demo.py`**
- **功能**: 演示程式
- **備註**: 與 BP 分析無關，用於演示其他功能

---

## 🔄 典型使用流程

1. **用戶輸入**: `"藍隊選擇了妮可，紅隊選了趙信跟岩雀，請預測勝率"`

2. **`bp_react_assistant.py`** 接收輸入

3. **`bp_react_agent.py`** 使用 LLM 解析，生成 JSON Action

4. **`bp_predictor.py`** 接收 Action，調用 `predict_winrate()`

5. **`hero_name_mapper.py`** 將中文名稱映射為英文：
   - 「妮可」→「Neeko」
   - 「趙信」→「Xin Zhao」
   - 「岩雀」→「Taliyah」

6. **`predict.py`** 的 `BPpredictor` 類執行預測

7. **返回結果**: 勝率預測結果

---

## 📌 重要提示

1. **必需文件**: `HeroNames.txt`, `bp_predictor.model`, `games.csv`, `heroes.csv`
2. **推薦使用**: `bp_react_assistant.py`（功能更強大）
3. **映射功能**: 自動處理，無需手動轉換
4. **LLM 配置**: 需要配置 Ollama 或 OpenAI（見 `src/llm_client.py`）

---

## 🗂️ 文件整理建議

可以考慮：
- 將 `match_*.csv` 移動到 `data/` 目錄
- 如果只使用 `bp_react_assistant.py`，可以刪除 `bp_assistant.py`
- 將演示文件（如 `run_demo.py`）移動到 `examples/` 目錄
