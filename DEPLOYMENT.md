# GitHub 部署指南

## 📋 部署步驟

### 1. 初始化 Git 倉庫

```bash
# 初始化 git 倉庫
git init

# 添加所有文件
git add .

# 創建初始提交
git commit -m "Initial commit: BP Analysis Assistant"
```

### 2. 在 GitHub 上創建新倉庫

1. 登入 GitHub
2. 點擊右上角的 "+" → "New repository"
3. 填寫倉庫信息：
   - Repository name: `bp-analysis-assistant` (或你喜歡的名稱)
   - Description: `League of Legends BP (Ban/Pick) Analysis Assistant`
   - 選擇 Public 或 Private
   - **不要**勾選 "Initialize this repository with a README"（因為我們已經有 README.md）
4. 點擊 "Create repository"

### 3. 連接本地倉庫到 GitHub

```bash
# 添加遠程倉庫（替換 YOUR_USERNAME 和 REPO_NAME）
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# 或者使用 SSH（推薦）
git remote add origin git@github.com:YOUR_USERNAME/REPO_NAME.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

### 4. 處理大文件（可選）

如果 `bp_predictor.model` 或數據文件很大，建議使用 Git LFS：

```bash
# 安裝 Git LFS
git lfs install

# 追蹤大文件
git lfs track "*.model"
git lfs track "*.csv"

# 添加 .gitattributes
git add .gitattributes
git commit -m "Add Git LFS tracking"
```

## 📝 重要文件說明

### 必須上傳的文件
- ✅ 所有 Python 源代碼（`.py` 文件）
- ✅ `HeroNames.txt`（映射表）
- ✅ `README.md` 和其他文檔
- ✅ `requirement.txt`
- ✅ `.gitignore`

### 不應該上傳的文件（已在 .gitignore 中）
- ❌ `__pycache__/` 目錄
- ❌ `*.model` 文件（模型文件，太大）
- ❌ `*.csv` 數據文件（太大，除了 games.csv 和 heroes.csv）
- ❌ `venv/` 虛擬環境
- ❌ `.env` 環境變量文件

### 建議處理方式

1. **模型文件** (`bp_predictor.model`):
   - 如果小於 100MB：可以直接上傳
   - 如果大於 100MB：使用 Git LFS 或提供下載鏈接

2. **數據文件**:
   - `games.csv` 和 `heroes.csv`：已設置為上傳
   - 其他 `match_*.csv`：已設置為不上傳（太大）

## 🔧 後續維護

### 更新代碼

```bash
# 添加更改
git add .

# 提交更改
git commit -m "描述你的更改"

# 推送到 GitHub
git push
```

### 創建 Release

1. 在 GitHub 倉庫頁面，點擊 "Releases"
2. 點擊 "Create a new release"
3. 填寫版本號（如 `v1.0.0`）和描述
4. 發布

## 📌 注意事項

1. **敏感信息**：確保不要上傳包含 API keys 的 `.env` 文件
2. **大文件**：GitHub 有文件大小限制（100MB），大文件需要使用 Git LFS
3. **License**：考慮添加 LICENSE 文件
4. **Contributing**：可以添加 CONTRIBUTING.md 文件

## 🎯 快速命令總結

```bash
# 完整部署流程
git init
git add .
git commit -m "Initial commit: BP Analysis Assistant"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
git push -u origin main
```

## 📚 相關文檔

- [GitHub 官方文檔](https://docs.github.com/)
- [Git LFS 文檔](https://git-lfs.github.com/)
