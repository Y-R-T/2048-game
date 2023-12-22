import random
import copy
import logging
import sqlite3
import bcrypt



# 连接到SQLite数据库
# 如果文件不存在，会自动在当前目录创建
conn = sqlite3.connect('game_users.db')

# 创建一个Cursor对象
cursor = conn.cursor()

# 创建表
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    score INTEGER DEFAULT 0
)
''')

# 数据库插入新用户，哈希密码
def add_user(username, password):
    """添加用户，存储哈希密码"""
    hashed_password = hash_password(password)
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()

# 数据库查询用户
def query_user(username):
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    return cursor.fetchone()

# 数据库更新用户分数
def update_score(username, score):
    cursor.execute("UPDATE users SET score=? WHERE username=?", (score, username))
    conn.commit()

def hash_password(password): # 生成密码哈希值
    """生成密码的哈希值"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(hashed_password, user_password): # 检测密码哈希值是否正确
    """检查输入的密码与存储的哈希值是否匹配"""
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password)

def login(): # 登录输入模块
    while True:
        user_name = input("请输入用户名:")
        user_password = input("输入密码:")
        if validate_user(user_name,user_password):
            return user_name
        print("用户名或密码错误，请重试！")

def validate_user(username, password): # 登录用户
    """验证用户登录"""
    user = query_user(username)
    if user and check_password(user[2], password):  # 直接使用 user[2]，它已经是 bytes 类型
        return True
    return False



def user_exists(user_name): # 调用数据库，检测用户是否存在
    # 连接到SQLite数据库
    conn = sqlite3.connect('game_users.db')
    cursor = conn.cursor()

    # 查询用户名
    cursor.execute("SELECT * FROM users WHERE username=?", (user_name,))
    user = cursor.fetchone()

    # 关闭Cursor和连接
    cursor.close()
    conn.close()

    # 如果找到用户，返回True，否则返回False
    return user is not None

def ask_if_register(): # 问用户是否注册，y注册，n不注册
    while True:
        a = input("登录请输入R，注册请输入Y，匿名进入输入N（匿名进入无个人存档）：")
        if a == "Y" or a == "y":
            user_name = register()
            return user_name
        if a == "N" or a == "n":
            user_name = "unnamed_user"
            return user_name
        if a == "R" or a == "r":
            if user_exists:
                user_name = login()    
                return user_name
        
        print("输入了不存在的选项，请重新输入！")
        
def register(): # 注册输入模块 + 注册模块，成功后自动登录
    user_name = input("请输入用户名:")
    if user_exists(user_name):
        print("该用户名已存在，请重新输入！")
        return register()
    else: 
        while True:   
            user_password = input("输入密码:")
            user_password_again = input("再次输入密码:")

            if user_password == user_password_again: # 两次密码相同则成功注册
                add_user(user_name, user_password) # add_user函数内转化为hash，调用时直接明文就行
                print("成功注册！即将以注册账户登录。")
                return user_name
            
            print("两次输入的密码不同，请重试！")

def initialize_board(): # 初始化
    board = [[0] * 4 for _ in range(4)]
    for _ in range(2):
        add_new_tile(board)
    return board

def add_new_tile(board): # 生成新方块
    empty_cells = [(i, j) for i in range(4) for j in range(4) if board[i][j] == 0]
    if empty_cells:
        i, j = random.choice(empty_cells)
        board[i][j] = random.choices([2, 4], weights=[0.8, 0.2])[0]

def print_board(board): # 打印
    for row in board:
        print(" ".join(str(cell).rjust(4) if cell != 0 else "   ." for cell in row)) # 这是三个空格加点
    print()

def slide(row): #去空格
    new_row = [cell for cell in row if cell != 0] + [0] * row.count(0)
    return new_row

def merge(row): #合并同种
    for i in range(3):
        if row[i] == row[i + 1] and row[i] != 0:
            row[i] *= 2
            row[i + 1] = 0
    return row

def move(board, direction): #输入反应
    
    if direction == "p":
        print(board)
        return board

    if direction in ["up", "down"]:
        board = [list(t) for t in zip(*board)]  # Transpose for up/down movement

    for i in range(4):
        row = board[i]
        if direction in ["right", "down"]:
            row = row[::-1]  # Reverse the row for right or down movement

        row = slide(row)
        row = merge(row)
        row = slide(row)

        if direction in ["right", "down"]:
            row = row[::-1]  # Reverse back after moving

        board[i] = row

    if direction in ["up", "down"]:
        board = [list(t) for t in zip(*board)]  # Transpose back

    
    

    return board

def is_game_over(board): #检测game over
    for i in range(4):
        for j in range(4):
            if board[i][j] == 0 or (j < 3 and board[i][j] == board[i][j + 1]) or (i < 3 and board[i][j] == board[i + 1][j]):
                return False
    return True

def jian(inp): #输入适配
    # v1.0.1: 适配mac键盘
    # v1.0.2: 加入wasd操作
    if inp == "\x1b[A" or inp == "w":
        inp = "up"
    elif inp == "\x1b[B" or inp == "s":
        inp = "down"
    elif inp == "\x1b[C" or inp == "d":
        inp = "right"
    elif inp == "\x1b[D" or inp == "a":
        inp = "left"
    return inp        
    
        

# 主循环
def main(player):
    logging.basicConfig(filename='game_log.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    board = initialize_board()
    if user_name != "unnamed_user":
        logging.info(f"玩家 {player} 的新游戏开始，初始图为 {board}")
    while not is_game_over(board):
        print_board(board)
        direction = input("请输入移动方向（left/right/up/down）：")
        direction = jian(direction)

        if direction in ["left", "right", "up", "down", "p"]:
            original_board = copy.deepcopy(board)  # 复制原始棋盘
            new_board = move(board, direction)

            if new_board != original_board:  # 检查棋盘是否发生了变化
                board = new_board
                add_new_tile(board)
                if user_name != "unnamed_user":
                    logging.debug(f"玩家 {player} 执行了动作 {direction}，当前地图为 {board}")
            else:
                print(f"命令 {direction} 无法使游戏状态改变，请输入 left, right, up 或 down 中可执行的操作。")
        else:
            print("无效的输入，请输入 left, right, up 或 down。")

    print("游戏结束！")
    print_board(board)

if __name__ == "__main__":
    user_name = ask_if_register()
    main(user_name)
