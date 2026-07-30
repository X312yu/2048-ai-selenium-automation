# 2048 AI 自動化控制與測試系統 (Expectimax AI & Selenium Automation)

> **中文：** 一款針對 2048 網頁原版開發的 AI 自動化控制與決策系統，結合 Python、Selenium、Expectimax 搜尋演算法與 JS 動態 HUD 視覺化監控介面。
> 
> **English:** An automated 2048 game AI agent built with Python, Selenium, and Expectimax search algorithm for the original 2048 web game, featuring an interactive HUD display.

---

## 💡 專案亮點 (Key Features)

- **Expectimax 決策搜尋 (Expectimax Decision Search)**：針對 2048 隨機生成方塊（90% 出 2, 10% 出 4）的機率特性，建構動態期望值搜尋模型，穩定突破 2048 / 4096 高分。
- **動態搜尋深度 (Dynamic Search Depth)**：根據盤面剩餘空格自動調配搜尋深度（Depth 4~7），靈活平衡計算效能與後期預測深度。
- **多維度 Heuristic 評分 (Multi-dimensional Heuristics)**：整合角落固定 (Corner)、單調性 (Monotonicity)、平滑度 (Smoothness)、邊緣平滑 (Edge Smoothness)、空格數 (Empty Cells)、合併潛力 (Merge Potential) 與蛇形餵食鏈 (Snake Feeding Chain)。
- **自動化控制與 DOM/State 解析 (Automation & State Parsing)**：使用 Selenium 進行網頁操控，並直接解析 `localStorage` 中的 `gameState`，繞過傳統 OCR/圖片辨識延遲，精準過濾動畫過渡狀態。
- **即時視覺化 HUD (Real-time Interactive HUD)**：透過 JavaScript 動態注入 DOM 元素至遊戲頁面，即時顯示當前 AI 狀態 (AI STATUS)、最佳方向 (AI MOVE) 與效能指標。
- **展演與穩定機制 (Showcase Mode & Auto Retry)**：支援自動偵測 Game Over / You Win 彈窗並自動重試/繼續，實現無人值守循環展示。

---

## 🏗 系統架構 (System Architecture)

```text
2048 AI Project
│
├── Selenium Automation
│   ├── Chrome Driver Controller (via webdriver-manager)
│   ├── Virtual Key Sender (Arrow Keys / Shortcut Listeners via 'keyboard')
│   └── Game Reset & Auto Retry Handler
│
├── Data Extraction (State Parsing)
│   └── LocalStorage Fetcher (Directly reading 'gameState' JSON object)
│
├── Expectimax Engine
│   ├── Dynamic Search Depth Evaluator
│   ├── Chance Node Probability Calculation (90% tile-2, 10% tile-4)
│   └── Transposition Table / Evaluation Cache
│
├── Heuristic Evaluation Matrix
│   ├── Corner Lock & Snake Feeding Chain
│   ├── Smoothness & Edge Smoothness
│   ├── Monotonicity & Empty Cells
│   └── Tile Merge Potential
│
├── Interactive HUD (Injected via JS)
│   ├── AI MOVE (Best Direction Overlay)
│   └── AI STATUS (State & Heuristic Score Overlay)
│
└── Showcase Mode
    ├── Game Over / You Win Pop-up Detection
    ├── Keep Playing Trigger
    └── Auto Retry Loop
```
## 🛠 環境需求與套件設定 (Environment & Dependencies)
### 1. 軟體環境 (Requirements)
Python: 3.10.x (Recommended)

Browser: Google Chrome (Latest Version)

Target Site: 2048 Variations (Original) (支援 localStorage 狀態提取)

### 2. Python 套件依存 (Python Packages)
專案核心僅使用以下主要第三方套件，架構極簡且便於快速部署：

selenium : 自動化網頁控制與 DOM 操作

webdriver-manager : 自動匹配與下載對應版本的 ChromeDriver

numpy : 處理 4x4 盤面矩陣運算與旋轉

keyboard : 監聽全域快捷鍵（1/2/3/R/ESC）控制 AI 狀態

## 套件安裝指令 (Installation Command):
pip install selenium webdriver-manager numpy keyboard


## 🚀 快速開始 (Quick Start)
## 執行步驟 (Execution)
##  1.複製專案 (Clone Repository):


git clone [https://github.com/X312yu/2048-ai-selenium-automation.git](https://github.com/X312yu/2048-ai-selenium-automation.git)
cd 2048-ai-selenium-automation

##  2.啟動 AI 自動化程式 (Run Main Script):

Windows 環境因 keyboard 套件監聽快捷鍵，建議以管理員權限 (Administrator) 執行命令提示字元或 VS Code：


python main.py

##  3.Chrome 啟動說明:

程式會自動透過 webdriver-manager 載入 Driver 並啟動 Chrome。

內建控制參數：--disable-infobars (隱藏自動測試提示)、--mute-audio (靜音)、--disable-notifications (關閉通知)。

瀏覽器必須允許 JavaScript 執行，以確保動態 HUD (Heads-Up Display) 能正確注入呈現。

## 📜 授權條款 (License)
This project is licensed under the MIT License - see the LICENSE file for details.



