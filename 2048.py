import random
import copy
import logging
    
def initialize_board():
    board = [[0] * 4 for _ in range(4)]
    for _ in range(2):
        add_new_tile(board)
    return board

def add_new_tile(board):
    empty_cells = [(i, j) for i in range(4) for j in range(4) if board[i][j] == 0]
    if empty_cells:
        i, j = random.choice(empty_cells)
        board[i][j] = random.choices([2, 4], weights=[0.8, 0.2])[0]

def print_board(board):
    for row in board:
        print(" ".join(str(cell).rjust(4) if cell != 0 else "   ." for cell in row)) # 这是三个空格加点
    print()

def slide(row):
    new_row = [cell for cell in row if cell != 0] + [0] * row.count(0)
    return new_row

def merge(row):
    for i in range(3):
        if row[i] == row[i + 1] and row[i] != 0:
            row[i] *= 2
            row[i + 1] = 0
    return row

def move(board, direction):
    
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


def is_game_over(board):
    for i in range(4):
        for j in range(4):
            if board[i][j] == 0 or (j < 3 and board[i][j] == board[i][j + 1]) or (i < 3 and board[i][j] == board[i + 1][j]):
                return False
    return True

def jian(inp):
    # v1.0.1: 加入wasd操控
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
def main(player="unnamed_user"):
    logging.basicConfig(filename='game_log.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    board = initialize_board()
    logging.info("游戏开始")
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
                logging.debug(f"玩家 {player} 执行了动作 {move}")
            else:
                print(f"命令 {direction} 无法使游戏状态改变，请输入 left, right, up 或 down 中可执行的操作。")
        else:
            print("无效的输入，请输入 left, right, up 或 down。")

    print("游戏结束！")
    print_board(board)

if __name__ == "__main__":
    a = input("Do you want to be a registered user. Press Y/n:")
    if a == "Y":
        user_name = input("Enter your name:")
    main(user_name)

    # 以后加入用户数据库
