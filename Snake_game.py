import pygame
import random
import sqlite3
import sys

# Инициализация pygame
pygame.init()

# Цвета
white = (255, 255, 255)
yellow = (255, 255, 102)
black = (0, 0, 0)
red = (213, 50, 80)
green = (0, 255, 0)
blue = (50, 153, 213)

# Размеры экрана
width = 600
height = 400

# Создание окна
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Змейка')

# Часы для управления FPS
clock = pygame.time.Clock()

# Размер блока змейки и скорость
block_size = 10
snake_speed = 15

# Шрифт для отображения счёта
font_style = pygame.font.SysFont("bahnschrift", 25)
score_font = pygame.font.SysFont("comicsansms", 35)

# База данных для рекордов
def init_db():
    conn = sqlite3.connect('snake_records.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_name TEXT NOT NULL,
        score INTEGER NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

def add_score(player_name, score):
    conn = sqlite3.connect('snake_records.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO scores (player_name, score) VALUES (?, ?)', (player_name, score))
    conn.commit()
    conn.close()

def get_top_scores():
    conn = sqlite3.connect('snake_records.db')
    cursor = conn.cursor()
    cursor.execute('SELECT player_name, score FROM scores ORDER BY score DESC LIMIT 5')
    top_scores = cursor.fetchall()
    conn.close()
    return top_scores

# Функция для отображения счёта
def display_score(score):
    value = score_font.render("Ваш счёт: " + str(score), True, yellow)
    screen.blit(value, [0, 0])

# Функция для отрисовки змейки
def draw_snake(block_size, snake_list):
    for block in snake_list:
        pygame.draw.rect(screen, green, [block[0], block[1], block_size, block_size])

# Функция для отображения сообщения на экране
def display_message(msg, color):
    mesg = font_style.render(msg, True, color)
    screen.blit(mesg, [width / 6, height / 3])

# Функция для ввода имени
def input_name():
    font = pygame.font.SysFont("comicsansms", 35)
    input_text = ""
    active = True

    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Enter
                    active = False
                elif event.key == pygame.K_BACKSPACE:  # Backspace
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode  # Добавляем символ

        screen.fill(white)
        text_surface = font.render("Введите ваше имя: " + input_text, True, black)
        screen.blit(text_surface, [width / 4, height / 2])
        pygame.display.update()

    return input_text

# Функция для отрисовки кнопок
def draw_button(screen, text, x, y, width, height, inactive_color, active_color):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    # Проверка, находится ли курсор над кнопкой
    if x < mouse[0] < x + width and y < mouse[1] < y + height:
        pygame.draw.rect(screen, active_color, (x, y, width, height))
        if click[0] == 1:
            return True
    else:
        pygame.draw.rect(screen, inactive_color, (x, y, width, height))

    # Отрисовка текста на кнопке
    font = pygame.font.SysFont("comicsansms", 30)
    text_surface = font.render(text, True, black)
    text_rect = text_surface.get_rect(center=(x + width / 2, y + height / 2))
    screen.blit(text_surface, text_rect)
    return False

# Основной игровой цикл
def game_loop(player_name):
    game_over = False
    game_close = False

    # Начальная позиция змейки
    x = width / 2
    y = height / 2
    x_change = 0
    y_change = 0
    snake_list = []
    length_of_snake = 1

    # Еда
    food_x = round(random.randrange(0, width - block_size) / 10.0) * 10.0
    food_y = round(random.randrange(0, height - block_size) / 10.0) * 10.0

    while not game_over:
        while game_close:
            screen.fill(blue)
            display_message("Вы проиграли!", red)
            display_score(length_of_snake - 1)

            # Кнопка "Играть снова"
            if draw_button(screen, "Играть снова", width / 2 - 150, height / 2, 300, 50, green, blue):
                game_close = False  # Сброс состояния game_close
                break  # Выход из цикла while game_close

            # Кнопка "В главное меню"
            if draw_button(screen, "В главное меню", width / 2 - 150, height / 2 + 70, 300, 50, red, blue):
                game_over = True  # Завершение игры
                game_close = False  # Сброс состояния game_close
                pygame.event.clear()  # Очистка очереди событий
                return  # Возврат в главное меню

            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                    game_close = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x_change = -block_size
                    y_change = 0
                elif event.key == pygame.K_RIGHT:
                    x_change = block_size
                    y_change = 0
                elif event.key == pygame.K_UP:
                    y_change = -block_size
                    x_change = 0
                elif event.key == pygame.K_DOWN:
                    y_change = block_size
                    x_change = 0

        # Проверка выхода за границы экрана
        if x >= width or x < 0 or y >= height or y < 0:
            game_close = True

        x += x_change
        y += y_change
        screen.fill(black)

        # Отрисовка еды
        pygame.draw.rect(screen, red, [food_x, food_y, block_size, block_size])

        # Добавление головы змейки
        snake_head = []
        snake_head.append(x)
        snake_head.append(y)
        snake_list.append(snake_head)

        if len(snake_list) > length_of_snake:
            del snake_list[0]

        # Проверка на столкновение с собой
        for block in snake_list[:-1]:
            if block == snake_head:
                game_close = True

        draw_snake(block_size, snake_list)
        display_score(length_of_snake - 1)
        pygame.display.update()

        # Если змейка съела еду
        if x == food_x and y == food_y:
            food_x = round(random.randrange(0, width - block_size) / 10.0) * 10.0
            food_y = round(random.randrange(0, height - block_size) / 10.0) * 10.0
            length_of_snake += 1

        clock.tick(snake_speed)

    # После завершения игры
    if game_close:
        add_score(player_name, length_of_snake - 1)  # Запись результата

# Главное меню
def main_menu(player_name):
    init_db()  # Инициализация базы данных

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill(white)

        title_font = pygame.font.SysFont("comicsansms", 50)
        title_surface = title_font.render("Змейка", True, black)
        title_rect = title_surface.get_rect(center=(width / 2, height / 4))
        screen.blit(title_surface, title_rect)

        # Кнопка "Играть"
        if draw_button(screen, "Играть", width / 2 - 100, height / 2 - 50, 200, 50, green, blue):
            game_loop(player_name)  # Запуск игры
            pygame.event.clear()  # Очистка очереди событий

        # Кнопка "Рекорды"
        if draw_button(screen, "Рекорды", width / 2 - 100, height / 2 + 20, 200, 50, green, blue):
            show_records()
            pygame.event.clear()

        # Кнопка "Выход"
        if draw_button(screen, "Выход", width / 2 - 100, height / 2 + 90, 200, 50, red, blue):
            pygame.quit()
            sys.exit()

        pygame.display.update()
        clock.tick(15)

# Отображение рекордов
def show_records():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    main_menu(player_name)  # Переход в главное меню
                    return  # Завершение функции show_records

        screen.fill(white)
        title_font = pygame.font.SysFont("comicsansms", 50)
        title_surface = title_font.render("Рекорды", True, black)
        title_rect = title_surface.get_rect(center=(width / 2, height / 4))
        screen.blit(title_surface, title_rect)

        # Получение топ-5 рекордов
        top_scores = get_top_scores()
        font = pygame.font.SysFont("comicsansms", 30)
        y_offset = height / 2 - 50
        for i, (player_name, score) in enumerate(top_scores, 1):
            score_text = f"{i}. {player_name}: {score}"
            score_surface = font.render(score_text, True, black)
            score_rect = score_surface.get_rect(center=(width / 2, y_offset))
            screen.blit(score_surface, score_rect)
            y_offset += 40

        # Кнопка "Назад"
        if draw_button(screen, "Назад", width / 2 - 100, height - 100, 200, 50, green, blue):
            return  # Завершение функции show_records

        pygame.display.update()
        clock.tick(15)

# Запуск игры
if __name__ == "__main__":
    init_db()  # Инициализация базы данных
    player_name = input_name()  # Запрос имени
    main_menu(player_name)  # Переход в главное меню