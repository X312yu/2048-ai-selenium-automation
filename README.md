# 2048 AI 自動化控制與測試系統 (Expectimax AI & Selenium Automation)

中文： 一款針對 2048 網頁原版開發的 AI 自動化控制與決策系統，結合 Python、Selenium、Expectimax 搜尋演算法與 JS 動態 HUD 視覺化監控介面。

English: An automated 2048 game AI agent built with Python, Selenium, and Expectimax search algorithm for the original 2048 web game, featuring an interactive HUD display.

## 💡 專案亮點 (Key Features)

Expectimax 決策搜尋 (Expectimax Decision Search)：針對 2048 隨機生成方塊（90% 出 2, 10% 出 4）的機率特性，建構動態期望值搜尋模型，穩定突破 2048 / 4096 高分。

動態搜尋深度 (Dynamic Search Depth)：根據盤面剩餘空格自動調配搜尋深度（Depth 4~7），靈活平衡計算效能與後期預測深度。

多維度 Heuristic 評分 (Multi-dimensional Heuristics)：整合角落固定 (Corner Lock)、單調性 (Monotonicity)、平滑度 (Smoothness)、邊緣平滑 (Edge Smoothness)、空格數 (Empty Cells)、合併潛力 (Merge Potential) 與蛇形餵食鏈 (Snake Feeding Chain)。

自動化控制與 DOM/State 解析 (Automation & State Parsing)：使用 Selenium 進行網頁操控，並直接解析 localStorage 中的 gameState，繞過傳統 OCR/圖片辨識延遲，精準過濾動畫過渡狀態。

即時視覺化 HUD (Real-time Interactive HUD)：透過 JavaScript 動態注入 DOM 元素至遊戲頁面，即時顯示當前 AI 狀態 (AI STATUS)、最佳方向 (AI MOVE) 與效能指標。

展演與穩定機制 (Showcase Mode & Auto Retry)：支援自動偵測 Game Over / You Win 彈窗並自動重試/繼續，實現無人值守循環展示。

##　🏗 系統架構 (System Architecture)
```
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

##　📈 研發里程碑與技術演進 (Technical Evolution)

## 📌 階段一：自動化與資料奠基期 (Stages 1 - 4)

第一階段：研究專題方向

技術定位：結合 AI 決策、自動化測試、網頁控制與演算法，最終選定以 Python 結合 Selenium 控制 2048 網頁，實現能自動讀取、分析並決策的 AI 輔助系統。

第二階段：完成 Selenium 自動控制

關鍵突破：建立瀏覽器自動化基底，控制 Chrome 瀏覽器自動開啟 2048、模擬鍵盤方向鍵、以及偵測結束後自動重新開始。

遇到瓶頸：Selenium 送出按鍵速度過快，網頁動畫尚未播放完畢即送出下一步，導致讀取到尚未更新的過渡棋盤狀態。

解決方案：引入 Explicit Wait（顯式等待機制），並加入 DOM 渲染與移動完成確認，確保網頁狀態與自動化操作同步。

第三階段：取得棋盤資料（DOM 解析）

實作方法：透過解析網頁 DOM 樹（如 .tile-4 與 .tile-position-2-3 等 class 屬性），嘗試重建 4×4 棋盤矩陣。

遇到瓶頸：動畫播放期間會同時存在複數個暫存 Tile（如 tile-new、tile-merged、tile-moving），導致同一位置讀取到多個數值，產生嚴重誤判。

解決方案：撰寫專屬的 Board Parser，精確過濾動畫中的暫存元素，重新建構真實的盤面狀態。

第四階段：LocalStorage 資料存取進化

技術躍升：為了徹底解決 DOM 解析受網頁動畫干擾的痛點，改為直接透過 Selenium 執行 JavaScript 讀取網頁後台的 localStorage.gameState JSON 物件。

效能效益：免除了繁複的畫面解析與 OCR 延遲，保證決策大腦能以 100% 精準度讀取即時數據，大幅縮短每步擷取時間。

## 📌 階段二：決策演算法迭代與瓶頸探索期 (Stages 5 - 9)

第五階段：Rule-Based AI 規則嘗試

設計邏輯：採用靜態優先順序規則（如 Left → Down → Right → Up），並搭配「最大方塊鎖定角落、盡量避免向上、保持盤面整齊」之直覺策略。

實測成果：平均可合成 512 至 1024 方塊，偶爾可觸及 2048 臨界點。

遇到瓶頸：後期極易卡死。主因是靜態規則不具備「未來局勢預測」能力，面對高隨機盤面時容錯率極低。

第六階段：CNN 卷積神經網路探索

嘗試路徑：將 4×4 棋盤轉換為矩陣，輸入 CNN 模型預測四個方向（Left/Right/Up/Down）的動作分類。

遇到瓶頸：面臨高難度訓練挑戰——高質量 Label 取得極其不易，且 2048 後期高度隨機，模型推論效果不夠穩定，未能作為最終方案。

第七階段：DQN 強化學習研究

設計機制：引入強化學習（Reinforcement Learning），讓 AI 在自行建構的模擬環境中透過 State → Action → Reward → Update Network 進行自我迭代。

遇到瓶頸：面臨獎勵函數（Reward Function）設計困難、收斂速度極慢、訓練不穩定且極易陷入局部最優解（Local Optima）等經典挑戰。

第八階段：DDQN（Double DQN）改良與 Sim-to-Real 落差

改進方案：為了解決 DQN 的 Q-value 高估（Overestimation）與訓練波動問題，引入 DDQN 將動作選擇（Action Selection）與動作評估（Action Evaluation）解耦。

訓練成果：AI 能穩定達到 512 與 1024。然而，累積百萬級數據並嘗試知識蒸餾（Knowledge Distillation）後，仍難以穩定突破 2048/4096，模型容易卡在 1024。

核心痛點：Sim-to-Real 實戰落差。離線訓練使用的模擬 Reward 機制（如合併、角落、空格與存活獎勵）與 Selenium 控制的真實網頁流程及隨機生成機制存在落差，導致離線表現優異、部署至實戰卻顯著下滑。

第九階段：Minimax 博弈搜尋演算法研究

轉折：決定重回傳統演算法。首先嘗試 Minimax 演算法，將局勢定義為「玩家最大化收益（Max 節點），對手最小化收益（Min 節點）」。

遇到瓶頸：2048 沒有「主動惡意」的對手。玩家移動後，是由系統以 90% 出現 2、10% 出現 4 的機率隨機生成方塊。強行使用 Minimax 會導致 AI 預測過於保守悲觀，進而做出不合情理的退縮決策。

## 📌 階段三：Expectimax 與 Heuristics 終局方案 (Stages 10 - 12)

第十階段：Expectimax 機率期望搜尋

技術突破：針對 2048 的隨機特性，將 Minimax 中的「對手 Min 節點」改為 Chance Node（機率節點）。

數學模型：依據真實生成機率（90% 為 +2，10% 為 +4）加權計算盤面期望值：


$$E = \sum P(i) \times H(i)$$


這讓 AI 具備了科學預測未來隨機局面的核心能力。

第十一階段：Heuristic 多維啟發式評估優化

評估矩陣：為了精確評量模擬盤面的好壞，設計了高度調校的評估機制 $H(i)$：

Corner Rule（角落鎖定）：強制將最高數值方塊固定在角落。

Monotonicity（單調性）：確保數字由邊角向內呈遞減排列。

Snake / Feeding Chain（蛇形餵食鏈）：利於高值方塊在邊界順暢合併。

Smoothness（平滑度）：相鄰方塊數值差距最小化，避免方塊孤立。

Empty Cells（空格最大化）：保留充足空格以降低卡死風險。

策略動態化：加入 Dynamic Weight（動態權重） 與 Dynamic Search Depth（動態搜尋深度），前期局面單純時降低深度以提高速率，後期盤面複雜時加深搜尋以精準佈局。

第十二階段：搜尋效能最佳化

優化工程：為了解決 Expectimax 指數級計算爆炸的問題，引入 Cache / Memoization（重複狀態快取） 避免重複運算。

剪枝策略：主動篩選並過濾非法移動（無效 Move），限制隨機節點的展開數量，成功在「思考品質」與「網頁控制即時性」之間取得最佳平衡。

## 📌 階段四：產品級落地與高可觀測性展示 (Stages 13 - 17)

第十三階段：遊戲流程控制（You Win / Game Over 處理）

痛點解決：AI 自動化最大的死穴在於中斷。本階段加入自動偵測 Game Over 停止發送方向鍵；以及偵測 You Win! 彈窗並自動觸擊 Keep Playing 的機制，讓 AI 突破 2048 限制，挑戰更高極限。

第十四階段：網頁注入式 HUD 即時監控

視覺創舉：利用 Selenium 透過 JavaScript 動態將自訂 HTML/CSS 植入 Chrome 當前網頁中。

實時指標：在遊戲畫面旁即時更新顯示 AI MOVE（最佳移動方向預測）與 AI STATUS（包含當前得分、搜尋深度、Heuristic 評估分數與狀態），顯著提升了專案展示的可觀察性與專業美感。

第十五階段：Showcase Mode（展示模式）

展示優化：為成果展量身打造「無人值守循環測試功能」。當 AI 遭遇 Game Over 結束遊玩時，系統會自動偵測並點擊 Restart 重新開局，不需任何人工介入，非常適合現場長時間不間斷展示。

第十六階段：系統韌性與 Exception Auto-Retry

穩定化設計：為應對網頁卡頓、Selenium 連線異常或 DOM 讀取超時等物理不確定因素，設計了 Exception Recovery（異常恢復） 機制。一旦捕獲異常，系統會自動重新連線、恢復狀態並接管遊戲，達到工業級自動化的強健性（Resilience）。

第十七階段：最終 2048 AI 自動化展示系統

專案總結：成功整合成一套集 「Expectimax 機率搜尋 + 多維 Heuristics 動態權重評分 + 100% 精準 LocalStorage 解析 + 視覺化 HUD 即時監控 + 異常自我恢復」 於一身的展示級高階 AI 自動化系統！

## 📊 實測成果與效能指標 (Benchmarks & Performance)

經多次實驗測試，本系統在 Expectimax 與優化 Heuristic 架構下的運算及表現數據如下：

評估項目

測試表現數據

平均最高方塊 (Highest Tile)

1024 ～ 4096 (最高曾穩定合成 4096 方塊)

平均生存步數 (Survival Steps)

1200 ～ 2000 步

角落維持率 (Corner Retention)

83.5% ± 5%

平均單步決策時間 (Average Decision Time)

約 0.054 秒

搜尋深度 3 耗時 (Depth 3 Speed)

0.0087 秒

搜尋深度 4 耗時 (Depth 4 Speed)

0.0542 秒

搜尋深度 5 耗時 (Depth 5 Speed)

0.1238 秒

搜尋深度 6 耗時 (Depth 6 Speed)

0.5138 秒

## 🛠 環境需求與套件設定 (Environment & Dependencies)

1. 軟體環境 (Requirements)

Python: 3.10.x (Recommended)

Browser: Google Chrome (Latest Version)

Target Site: 2048 Variations (Original) (支援 localStorage 狀態提取)

2. Python 套件依存 (Python Packages)

專案核心僅使用以下主要第三方套件，架構極簡且便於快速部署：

selenium : 自動化網頁控制與 DOM 操作

webdriver-manager : 自動匹配與下載對應版本的 ChromeDriver

numpy : 處理 4x4 盤面矩陣運算與旋轉

keyboard : 監聽全域快捷鍵（1/2/3/R/ESC）控制 AI 狀態

套件安裝指令 (Installation Command):

pip install selenium webdriver-manager numpy keyboard


## 🚀 快速開始 (Quick Start)

執行步驟 (Execution)

複製專案 (Clone Repository):

git clone https://github.com/X312yu/2048-ai-selenium-automation.git
cd 2048-ai-selenium-automation


啟動 AI 自動化程式 (Run Main Script):

## ⚠️ Windows 運行提示：因專案使用了 keyboard 套件監聽全域快捷鍵，在 Windows 環境下建議以 系統管理員權限 (Administrator) 執行命令提示字元 (CMD)、PowerShell 或 VS Code，以防快捷鍵監聽失效。

python main.py


Chrome 啟動說明:

程式會自動透過 webdriver-manager 載入 Driver 並啟動 Chrome。

內建控制參數包括：--disable-infobars (隱藏自動測試提示)、--mute-audio (靜音)、--disable-notifications (關閉通知)。

瀏覽器必須允許 JavaScript 執行，以確保動態 HUD (Heads-Up Display) 能正確注入呈現。

## 📜 授權條款 (License)

This project is licensed under the MIT License - see the LICENSE file for details.
