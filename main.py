import json
import time
import math
import random
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import keyboard

# ======== 2048 棋盤大小 ========
SIZE = 4

# ======== 基本移動邏輯（模擬 2048 合併規則） ========
def can_move(board):
    # 判斷是否存在任何合法移動
    for d in range(4):
        if not np.array_equal(board, move_sim(board, d)):
            return True
    return False

def move_sim(board, direction):
    # 旋轉來簡化上下左右的實作
    b = np.rot90(board, -direction)
    moved = np.zeros_like(b)

    # 每列進行壓縮 + 合併
    for i in range(SIZE):
        row = b[i][b[i] != 0]
        new_row, skip = [], False
        for j in range(len(row)):
            if skip:
                skip = False
                continue
            if j + 1 < len(row) and row[j] == row[j + 1]:
                new_row.append(row[j] * 2)
                skip = True
            else:
                new_row.append(row[j])
        moved[i, :len(new_row)] = new_row

    # 旋回原方向
    return np.rot90(moved, direction)

# ======== 啟發式函式（決定盤面好壞） ========
last_corner = None
corner_streak = 0

def heuristic(board):
    # 2048 AI 判斷盤面的多重評分組合
    global last_corner, corner_streak

    empty = np.sum(board == 0)          # 空格越多越安全
    max_tile = np.max(board)            # 最大數字越大越好

    # ---- 平滑度（避免相鄰差距大 → 盤面混亂）----
    smoothness = 0
    for r in range(SIZE):
        for c in range(SIZE - 1):
            if board[r, c] and board[r, c + 1]:
                smoothness -= abs(math.log2(board[r, c]) - math.log2(board[r, c + 1]))
    for r in range(SIZE - 1):
        for c in range(SIZE):
            if board[r, c] and board[r + 1, c]:
                smoothness -= abs(math.log2(board[r, c]) - math.log2(board[r + 1, c]))

    # ---- 外圈平滑度（環狀蛇形越順越好）----
    edge_indices = (
        [(0, c) for c in range(SIZE)] +
        [(r, SIZE - 1) for r in range(SIZE)] +
        [(SIZE - 1, c) for c in range(SIZE - 1, -1, -1)] +
        [(r, 0) for r in range(SIZE - 1, -1, -1)]
    )
    edge_values = [board[r, c] for (r, c) in edge_indices if board[r, c] != 0]
    edge_smooth = 0
    if len(edge_values) > 1:
        for i in range(len(edge_values) - 1):
            edge_smooth -= abs(math.log2(edge_values[i]) - math.log2(edge_values[i + 1]))

    # ---- 單調性（每排/欄是否遞增或遞減）----
    mono = 0
    for r in range(SIZE):
        row = board[r, :]
        if np.all(np.diff(row) <= 0) or np.all(np.diff(row) >= 0):
            mono += np.sum(row)
    for c in range(SIZE):
        col = board[:, c]
        if np.all(np.diff(col) <= 0) or np.all(np.diff(col) >= 0):
            mono += np.sum(col)

    # ---- 最大 tile 固定角落（穩定性核心）----
    corners = [(0,0),(0,3),(3,0),(3,3)]
    corner_bonus = 0
    for (r,c) in corners:
        if board[r,c] == max_tile:
            if (r,c) == last_corner:
                corner_streak += 1
            else:
                corner_streak = 1
                last_corner = (r,c)
            corner_bonus = max_tile * (0.5 + 0.05 * min(corner_streak, 8))
            break

    # ---- 主列合併潛力（右側垂直餵食）----
    merge_potential = 0
    main_col = board[:, 3]
    for i in range(SIZE - 1):
        if main_col[i] == main_col[i + 1] and main_col[i] != 0:
            merge_potential += main_col[i] * 2

    # ---- 分散懲罰（相同數字離太遠 → 不利餵食鏈）----
    feed_penalty = 0
    values = np.unique(board[board > 0])
    for v in values:
        coords = list(zip(*np.where(board == v)))
        if len(coords) >= 2:
            for i in range(len(coords) - 1):
                r1, c1 = coords[i]
                r2, c2 = coords[i + 1]
                feed_penalty += abs(r1 - r2) + abs(c1 - c2)

    # ---- 餵食鏈（32→64→128 等倍數鏈）----
    feeding_bonus = 0
    for r in range(SIZE):
        for c in range(SIZE - 1):
            if board[r, c] != 0 and board[r, c + 1] == board[r, c] * 2:
                feeding_bonus += board[r, c]
    for c in range(SIZE):
        for r in range(SIZE - 1):
            if board[r, c] != 0 and board[r + 1, c] == board[r, c] * 2:
                feeding_bonus += board[r, c]

    # ---- 最終評分 ----
    total_score = (
        empty * 200 +
        math.log(max_tile, 2) * 100 +
        smoothness * 0.45 +
        edge_smooth * 0.85 +
        mono +
        corner_bonus +
        merge_potential * 0.5 +
        feeding_bonus * 0.3 -
        feed_penalty * 10
    )

    return total_score


# ======== Expectimax 搜尋 ========
cache = {}

def expectimax(board, depth, is_player):
    # 大量計算時使用 cache 加速
    if len(cache) > 50000:
        cache.clear()

    key = (board.tobytes(), depth, is_player)
    if key in cache:
        return cache[key]

    # 遞迴結束 → 回傳盤面評分
    if depth == 0 or not can_move(board):
        val = heuristic(board)
        cache[key] = val
        return val

    # 玩家節點：選最好的方向
    if is_player:
        best = -float("inf")
        for d in range(4):
            nb = move_sim(board, d)
            if not np.array_equal(nb, board):
                best = max(best, expectimax(nb, depth - 1, False))
        cache[key] = best
        return best

    # 電腦節點：隨機生成 2/4
    empties = list(zip(*np.where(board == 0)))
    if not empties:
        val = heuristic(board)
        cache[key] = val
        return val

    if len(empties) > 4:
        empties = random.sample(empties, 4)

    val = 0
    for r, c in empties:
        for tile, p in [(2, 0.9), (4, 0.1)]:
            nb = board.copy()
            nb[r, c] = tile
            val += p * expectimax(nb, depth - 1, True) / len(empties)

    cache[key] = val
    return val


# ======== 找最佳方向 ========
def find_best_move(board):
    empty = np.sum(board == 0)
    max_tile = np.max(board)

    # 動態調整搜尋深度
    if empty >= 6:
        depth = 3
    elif empty >= 4:
        depth = 4
    else:
        depth = 5
    if max_tile >= 512 and empty >= 3:
        depth = min(depth + 1, 7)

    scores = []
    for d in range(4):
        nb = move_sim(board, d)
        if not np.array_equal(nb, board):
            scores.append((expectimax(nb, depth - 1, False), d))

    if not scores:
        return -1

    scores.sort(reverse=True, key=lambda x: x[0])
    return scores[0][1]


# ======== JS 顯示元件 ========
def inject_move_label(driver):
    # 在網頁左上角顯示 AI 移動方向
    js = """
    if (!document.getElementById("ai-move-label")) {
        let div = document.createElement("div");
        div.id = "ai-move-label";
        div.style.position = "fixed";
        div.style.top = "10px";
        div.style.left = "10px";
        div.style.padding = "6px 12px";
        div.style.background = "rgba(0,0,0,0.55)";
        div.style.color = "white";
        div.style.fontSize = "16px";
        div.style.zIndex = "9999";
        div.style.borderRadius = "6px";
        document.body.appendChild(div);
    }
    """
    driver.execute_script(js)

def update_move_label(driver, txt):
    js = f"""
    let div = document.getElementById("ai-move-label");
    if (div) div.textContent = "{txt}";
    """
    driver.execute_script(js)

def inject_status_label(driver):
    # 右上角顯示 AI 狀態
    js = """
    if (!document.getElementById("ai-status-label")) {
        let div = document.createElement("div");
        div.id = "ai-status-label";
        div.style.position = "fixed";
        div.style.top = "10px";
        div.style.right = "10px";
        div.style.padding = "6px 12px";
        div.style.background = "rgba(0,0,0,0.55)";
        div.style.color = "yellow";
        div.style.fontSize = "16px";
        div.style.zIndex = "9999";
        div.style.borderRadius = "6px";
        document.body.appendChild(div);
    }
    """
    driver.execute_script(js)

def update_status_label(driver, txt):
    # 更新右上角狀態文字
    js = f"""
    let div = document.getElementById("ai-status-label");
    if (div) div.textContent = "{txt}";
    """
    driver.execute_script(js)


# ======== Browser Control ========
def setup_driver():
    # 初始化瀏覽器
    options = Options()
    options.add_argument("--disable-infobars")
    options.add_argument("--mute-audio")
    options.add_argument("--disable-notifications")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://2048-variations.net/en/original")
    time.sleep(1)

    inject_move_label(driver)
    inject_status_label(driver)
    update_status_label(driver, "AI IDLE")
    return driver

def get_board(driver):
    # 從 localStorage 讀取真實盤面
    js = """
    let s = localStorage.getItem("gameState");
    if (!s) return null;
    let data = JSON.parse(s);
    if (!data || !data.grid || !data.grid.cells) return null;
    return data.grid.cells.map(row => row.map(cell => cell ? cell.value : 0));
    """
    state = driver.execute_script(js)
    return np.array(state) if state else np.zeros((4, 4), dtype=int)

def click_keep_going(driver):
    # 遇到 You Win → 自動按 Keep Going
    try:
        btn = driver.find_element(By.CLASS_NAME, "keep-playing-button")
        btn.click()
        return True
    except:
        return False

def is_game_over(driver):
    # 偵測是否跳出 Game Over
    try:
        over = driver.find_element(By.CLASS_NAME, "game-over")
        return over.is_displayed()
    except:
        return False

def restart_game(driver):
    # 重啟遊戲
    try:
        btn = driver.find_element(By.CLASS_NAME, "restart-button")
        btn.click()
        time.sleep(1)
    except:
        driver.execute_script("localStorage.clear(); location.reload();")
        time.sleep(2)


# ======== 主流程 ========
def main():
    driver = setup_driver()
    body = driver.find_element(By.TAG_NAME, "body")

    ai_enabled = False        # 一般 AI 模式
    showcase_mode = False     # 展示模式（全自動）
    step = 0

    print("Controls: 1=Start 2=Stop 3=Showcase R=Restart ESC=Exit")

    while True:

        # ESC → 結束整個程式
        if keyboard.is_pressed("esc"):
            ai_enabled = False
            showcase_mode = False
            update_status_label(driver, "AI STOPPED")
            break

        # 1 → 啟動一般 AI 模式
        if keyboard.is_pressed("1"):
            ai_enabled = True
            showcase_mode = False
            update_status_label(driver, "AI RUNNING")
            time.sleep(0.3)

        # 2 → 停止所有 AI
        if keyboard.is_pressed("2"):
            ai_enabled = False
            showcase_mode = False
            update_status_label(driver, "AI STOPPED")
            time.sleep(0.3)

        # 3 → 展示模式 ON/OFF
        if keyboard.is_pressed("3"):
            showcase_mode = not showcase_mode
            ai_enabled = showcase_mode  # 展示模式需要 AI 自動走
            update_status_label(driver, "SHOWCASE MODE" if showcase_mode else "AI STOPPED")
            time.sleep(0.4)

        # R → 強制重開遊戲
        if keyboard.is_pressed("r"):
            ai_enabled = False
            showcase_mode = False
            update_status_label(driver, "RESTARTING...")
            restart_game(driver)
            update_status_label(driver, "AI IDLE")
            time.sleep(1)

        # ========== 展示模式：自動處理 You Win / Game Over ==========
        if showcase_mode:

            # 自動按 Keep Going
            if click_keep_going(driver):
                print("[SHOWCASE] Auto Keep Going")

            # Game Over → 自動重開
            if is_game_over(driver):
                print("[SHOWCASE] Game Over → auto restart in 3 sec")
                update_status_label(driver, "RESTART IN 3...")
                time.sleep(3)
                restart_game(driver)
                update_status_label(driver, "SHOWCASE MODE")
                ai_enabled = True
                continue

        # ========== AI 搜尋 + 自動操作 ==========
        if ai_enabled:

            board = get_board(driver)
            if board is None or np.all(board == 0):
                update_status_label(driver, "WAITING BOARD...")
                time.sleep(0.5)
                continue

            step += 1
            move = find_best_move(board)

            if move == -1:
                ai_enabled = False
                update_status_label(driver, "NO MOVE")
                continue

            # 顯示移動方向
            move_names = ["UP", "RIGHT", "DOWN", "LEFT"]
            update_move_label(driver, f"AI MOVE: {move_names[move]}")

            # 實際送出方向鍵
            keys = [Keys.ARROW_UP, Keys.ARROW_RIGHT, Keys.ARROW_DOWN, Keys.ARROW_LEFT]
            body.send_keys(keys[move])

            time.sleep(0.22)

        time.sleep(0.05)


if __name__ == "__main__":
    main()
