import numpy as np
import random
import pygame as p
from sys import exit
from time import sleep
import threading

p.init()


class Sudoku:
    def __init__(self, window):
        self.size = 9
        self.speed = 0.15

    # return a list containing which numbers 1-9 can be placed in a position
    def possible_options(self, row, column):
        numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        random.shuffle(numbers)
        add_x = add_y = 0
        for i in range(9):
            if numbers.count(window.board[row][i]) > 0:
                numbers.remove(window.board[row][i])
        for i in range(9):
            if numbers.count(window.board[i][column]) > 0:
                numbers.remove(window.board[i][column])
        if 0 <= row < 3:
            add_x = 0
        if 3 <= row < 6:
            add_x = 3
        if 6 <= row < 9:
            add_x = 6

        if 0 <= column < 3:
            add_y = 0
        if 3 <= column < 6:
            add_y = 3
        if 6 <= column < 9:
            add_y = 6

        for r in range(add_x, add_x + 3):
            for c in range(add_y, add_y + 3):
                if window.board[r][c] and r != row and c != column and numbers.count(window.board[r][c]) > 0:
                    numbers.remove(window.board[r][c])

        return numbers

    def solution(self, row, column):
        if row == 8 and column == 9:
            return True

        if column == 9:
            row = row + 1
            column = 0

        if window.user_board_copy[row][column] == -1:
            return self.solution(row, column + 1)

        numbers = self.possible_options(row, column)
        while len(numbers) > 0:
            if window.thread.is_alive():
                sleep(self.speed)
            window.board[row][column] = numbers[len(numbers) - 1]
            window.user_board_copy[row][column] = -1
            if self.solution(row, column + 1):
                return True
            numbers.pop()
            window.board[row][column] = 0
            window.user_board_copy[row][column] = 0

        return False

    def remove_elements(self):
        remove = random.randint(30, 40)
        removed_list = []
        while remove:
            removed = random.randint(0, 80)
            while len(removed_list) and removed_list.count(removed) > 0:
                removed = random.randint(0, 80)
            row = removed // 9
            column = removed % 9
            window.board[row][column] = 0
            remove -= 1
            removed_list.append(removed)


class Cell:
    def __init__(self, window, x, y, width, height, border, color, text_color, background, coord):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.i = coord[0]
        self.j = coord[1]
        self.border = border
        self.text_color = text_color
        self.color = color  # grey
        self.background = background  # black
        self.rect = p.Rect(self.x, self.y, self.width, self.height)
        self.text_surf = 0
        self.text_rect = 0

    def draw_rectangle(self):
        self.rect = p.Rect(self.x, self.y, self.width, self.height)
        p.draw.rect(window.screen, self.background, self.rect)
        self.rect = p.Rect(self.x + self.border, self.y + self.border,
                           self.width - 2 * self.border, self.height - 2 * self.border)
        p.draw.rect(window.screen, self.color, self.rect)

    def draw_numbers(self):
        if window.board[self.i][self.j]:
            text = str(window.board[self.i][self.j])
            self.text_surf = window.font.render(
                text, True, self.text_color, self.color)
            self.text_rect = self.text_surf.get_rect(
                center=window.cells[self.i][self.j].rect.center)
            window.screen.blit(self.text_surf, self.text_rect)


class Button:
    def __init__(self, screen, text, x, y, width, height, color, background, border):
        self.screen = screen
        self.text = text
        self.font = p.font.Font(None, 30)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.background = background
        self.border = border

        self.pressed = False

        self.background_rect = p.Rect(self.x, self.y, self.width, self.height)

    def draw(self):
        self.text_surf = self.font.render(
            self.text, True, "black", self.background)

        self.border_rect = p.Rect(
            self.x - self.border, self.y - self.border, self.width + 2*self.border, self.height + 2*self.border)

        self.text_rect = self.text_surf.get_rect(
            center=self.background_rect.center)

        p.draw.rect(self.screen, "black", self.border_rect)
        p.draw.rect(self.screen, self.background, self.background_rect)
        self.screen.blit(self.text_surf, self.text_rect)


class Label():
    def __init__(self, window, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.rect = p.Rect(self.x, self.y, self.width, self.height)

    def draw(self):
        p.draw.rect(window.screen, self.color, self.rect)


class Window:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.screen = p.display.set_mode((self.width, self.height))
        p.display.set_caption("Sudoku")
        self.font = p.font.Font(None, 45)
        self.clock = p.time.Clock()

        self.cells = []
        self.buttons = []
        self.sudoku = Sudoku(self)

        self.board_width = 540
        self.board_height = 540
        self.pos = 100

        self.board_copy = np.full((9, 9), 0, object)
        self.user_board_copy = np.full((9, 9), 0, object)
        self.board = np.full((9, 9), 0, object)
        self.user_board = np.full((9, 9), 0, object)
        self.solution_board = np.full((9, 9), 0, object)

        self.key_placed = 0
        self.size = 9
        self.mouse_pressed = False
        self.keyboard_pressed = False

        self.border = 1

        self.checking = False

        self.top_label = Label(self, 0, 0, self.width,
                               self.height - self.board_height, "dark green")

        self.thread = threading.Thread(
            target=self.sudoku.solution, args=(0, 0, ))

    def initialize(self):
        self.board = np.full((9, 9), 0, object)
        self.user_board_copy = np.full((9, 9), 0, object)
        self.user_board = np.full((9, 9), 0, object)
        self.sudoku.solution(0, 0)
        self.solution_board = self.board.copy()
        self.sudoku.remove_elements()

        for i in range(9):
            row = []
            for j in range(9):
                row.append(Cell(self, j * (self.board_width / 9), i *
                           (self.board_height / 9) + self.pos, self.board_width / 9, self.board_height / 9, self.border, "white", "black", "black", (i, j)))
                if self.board[i][j]:
                    self.user_board[i][j] = -1
                else:
                    self.user_board[i][j] = 0

            self.board_copy = self.board.copy()
            self.user_board_copy = self.user_board.copy()

            self.cells.append(row)


        #self.sudoku.solution(0, 0)

        self.buttons.append(Button(window.screen, "Clear",
                            8, 10, 125, 80, "grey", "black", 3))

        self.buttons.append(Button(window.screen, "Check",
                            141, 10, 125, 80, "grey", "black", 3))

        self.buttons.append(Button(window.screen, "Solve",
                            274, 10, 125, 80, "grey", "black", 3))

        self.buttons.append(Button(window.screen, "New Board",
                            407, 10, 125, 80, "grey", "black", 3))

    def check_key(self, event):
        if event == p.K_1:
            self.key_placed = 1
        elif event == p.K_2:
            self.key_placed = 2
        elif event == p.K_3:
            self.key_placed = 3
        elif event == p.K_4:
            self.key_placed = 4
        elif event == p.K_5:
            self.key_placed = 5
        elif event == p.K_6:
            self.key_placed = 6
        elif event == p.K_7:
            self.key_placed = 7
        elif event == p.K_8:
            self.key_placed = 8
        elif event == p.K_9:
            self.key_placed = 9
        else:
            self.key_placed = 0

    def check_input(self):
        mouse_pos = p.mouse.get_pos()
        for row in range(self.size):
            for column in range(self.size):
                if self.cells[row][column].rect.collidepoint(mouse_pos):
                    self.cells[row][column].color = "grey"
                    if self.keyboard_pressed and self.user_board[row][column] != -1:
                        self.checking = False
                        self.board[row][column] = self.key_placed
                        self.cells[row][column].text_color = "dark green"
                else:
                    self.cells[row][column].color = "white"

        for button in self.buttons:
            if button.background_rect.collidepoint(mouse_pos):
                if self.mouse_pressed:
                    self.checking = False
                    button.pressed = True
                else:
                    button.background = "green"
                    button.pressed = False
            else:
                button.background = "grey"
                button.pressed = False

        if self.buttons[0].pressed:
            self.clear()

        elif self.buttons[1].pressed:
            self.check()

        elif self.buttons[2].pressed:

            self.board = self.solution_board.copy()

            for row in range(self.size):
                for column in range(self.size):
                    self.cells[row][column].text_color = "black"
                    
            
            '''if not self.thread.is_alive():
                self.thread = threading.Thread(
                    target=self.sudoku.solution, args=(0, 0, ))
                self.thread.start()
            else:
                self.board = self.board_copy.copy()
                self.sudoku.speed = 0
                sleep(0.2)
                self.sudoku.speed = 0.15 '''
        elif self.buttons[3].pressed:
            self.initialize()

    def draw_lines(self):
        rect = p.Rect(0, self.pos, 4, self.board_height)
        p.draw.rect(self.screen, "black", rect)

        rect = p.Rect(180, self.pos, 4, self.board_height)
        p.draw.rect(self.screen, "black", rect)

        rect = p.Rect(360, self.pos, 4, self.board_height)
        p.draw.rect(self.screen, "black", rect)

        rect = p.Rect(537, self.pos, 4, self.board_height)
        p.draw.rect(self.screen, "black", rect)

        rect = p.Rect(0, self.pos, self.board_width, 4)
        p.draw.rect(self.screen, "black", rect)

        rect = p.Rect(0, 180 + self.pos, self.board_width, 4)
        p.draw.rect(self.screen, "black", rect)

        rect = p.Rect(0, 360 + self.pos, self.board_width, 4)
        p.draw.rect(self.screen, "black", rect)

        rect = p.Rect(0, 537 + self.pos, self.board_width, 4)
        p.draw.rect(self.screen, "black", rect)

    def clear(self):
        self.board = self.board_copy.copy()

    def check(self):
        self.checking = True
        for row in range(9):
            for column in range(9):
                if self.user_board_copy[row][column] != -1 and self.board[row][column] != 0:
                    if self.board[row][column] != self.solution_board[row][column]:
                        self.cells[row][column].text_color = "red"
                    else:
                        self.cells[row][column].text_color = "green"
                else:
                    self.cells[row][column].text_color = "black"

    def draw(self):
        for i in range(9):
            for j in range(9):
                if self.user_board[i][j] == -1:
                    self.cells[i][j].text_color = "black"
                self.cells[i][j].draw_rectangle()
                self.cells[i][j].draw_numbers()
        self.draw_lines()
        self.top_label.draw()
        for i in range(4):
            self.buttons[i].draw()

    def run(self):
        while True:
            for event in p.event.get():
                if event.type == p.QUIT:
                    p.quit()
                    exit()
                if event.type == p.MOUSEBUTTONDOWN:
                    self.mouse_pressed = True
                if event.type == p.KEYDOWN:
                    self.keyboard_pressed = True
                    self.check_key(event.key)

            self.screen.fill("white")

            self.check_input()

            self.draw()

            self.keyboard_pressed = False
            self.mouse_pressed = False

            p.display.update()


window = Window(540, 640)
window.initialize()
window.run()
