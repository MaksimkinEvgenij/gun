from random import randrange as rnd, choice
import tkinter as tk
import math
import time


class Ball:
    def __init__(self, game, x=40, y=450, vx=0, vy=0):
        """ Конструктор класса Ball

        Args:
        x - начальное положение мяча по горизонтали
        y - начальное положение мяча по вертикали
        """
        self.game = game
        self.x = x
        self.y = y
        self.r = 10
        self.vx = vx
        self.vy = vy
        self.color = choice(['blue', 'green', 'red', 'brown'])
        self.id = self.game.playground.create_oval(
            self.x - self.r,
            self.y - self.r,
            self.x + self.r,
            self.y + self.r,
            fill=self.color
        )
        self.move()

    def set_coords(self):
        """ Установка положения шара на игровом поле. """
        self.game.playground.coords(
            self.id,
            self.x - self.r,
            self.y - self.r,
            self.x + self.r,
            self.y + self.r
        )

    def move(self):
        """Переместить мяч по прошествии единицы времени.

        Метод описывает перемещение мяча за один кадр перерисовки. То есть, обновляет значения
        self.x и self.y с учетом скоростей self.vx и self.vy, силы гравитации, действующей на мяч,
        и стен по краям окна (размер окна 800х600).
        """
        # (self.id)
        self.x += self.vx
        self.y -= self.vy
        self.set_coords()
        self.moving = self.game.root.after(100, self.move)


class Gun:
    def __init__(self, game):
        self.game = game
        self.fire_power = 10
        self.firing_on = 0
        self.set_gun_position()

    def set_gun_position(self):
        """ Установка стартовой позиции пушки."""
        self.angle = 1
        self.start_pos_x = 20
        self.start_pos_y = 450
        self.end_pos_x = 50
        self.end_pos_y = 420
        self.id = self.game.playground.create_line(self.start_pos_x, self.start_pos_y, self.end_pos_x, self.end_pos_y,
                                                   width=7)

    def fire_starter(self, event):
        """ 'Зарядка' выстрела, для дальнейшего выбора силы выстрела.

        Происходит при нажатие до отпускания мыши.
        """
        self.firing_on = 1
        self.power_up()

    def firing(self, event):
        """Выстрел шаром.

        Происходит при отпускании кнопки мыши.
        Начальные значения компонент скорости мяча vx и vy зависят от положения мыши.
        """

        self.angle = math.atan((event.y - self.start_pos_y) / (event.x - self.start_pos_x))
        vx = self.fire_power * math.cos(self.angle)
        vy = - self.fire_power * math.sin(self.angle)
        self.game.create_ball(self.end_pos_x, self.end_pos_y, vx, vy)

        self.firing_on = 0
        self.fire_power = 10

        self.game.root.after_cancel(self.changing_power)

        self.redraw_gun()

        self.game.update_amount_of_shots()

    def targetting(self, event=0):
        """Прицеливание. Зависит от положения мыши."""
        if event:
            if event.x - self.start_pos_x != 0:
                self.angle = math.atan((event.y - self.start_pos_y) / (event.x - self.start_pos_x))

        if self.firing_on:  # выстрел
            self.game.playground.itemconfig(self.id, fill='orange')
        else:
            self.game.playground.itemconfig(self.id, fill='black')

        self.redraw_gun()

    def redraw_gun(self):
        """ Перерисовка пушки. """
        self.end_pos_x = self.start_pos_x + max(self.fire_power, 20) * math.cos(self.angle)
        self.end_pos_y = self.start_pos_y + max(self.fire_power, 20) * math.sin(self.angle)

        self.game.playground.coords(self.id,
                                    self.start_pos_x, self.start_pos_y,
                                    self.end_pos_x, self.end_pos_y)

    def power_up(self):
        """ Изменяет силу выстрела. """

        if self.firing_on:
            if self.fire_power < 100:
                self.fire_power += 1
            self.game.playground.itemconfig(self.id, fill='orange')
        else:
            self.game.playground.itemconfig(self.id, fill='black')

        self.redraw_gun()

        self.changing_power = self.game.root.after(10, self.power_up)


class Target:
    def __init__(self, game):
        self.game = game

        color = self.color = 'red'

        r = self.r = rnd(2, 50)
        x = self.x = rnd(game.window_width - r - 580, game.window_width - r)
        y = self.y = rnd(r, game.window_height - r)
        self.vy = rnd(-30, 30)

        self.id = self.game.playground.create_oval(x - r, y - r, x + r, y + r, fill=color)

        self.make_a_move()

    def hit(self, points=1):
        """Попадание шарика в цель."""
        self.game.playground.coords(self.id, -10, -10, -10, -10)
        self.points += points
        self.game.playground.itemconfig(self.id_points, text=self.points)
        self.live = 0

    def make_a_move(self):
        """ Задание движения целям. """

        self.y += self.vy
        self.set_coords()

        if self.y - self.r <= 0 or self.y + self.r >= self.game.window_height:
            self.vy *= -1

        self.moving = self.game.root.after(100, self.make_a_move)

    def set_coords(self):
        """ Установка положения цели на игровом поле. """
        self.game.playground.coords(self.id,
                                    self.x - self.r, self.y - self.r,
                                    self.x + self.r, self.y + self.r)


class GunGame:
    def __init__(self):
        self.set_variables()
        self.set_constants()

        self.build_playground()
        self.create_gun()
        self.create_targets(number_of_targets=self.number_of_targets)

        self.binds()

        self.checking_collisions()

        self.root.mainloop()

    def set_variables(self):
        """ Переменные для работы игры. """
        self.balls = {}
        self.balls_last_position = 0
        self.targets = {}
        self.amount_of_shots = 0
        self.score = 0

    def set_constants(self):
        """ Константы для работы игры. """
        self.window_width = 800
        self.window_height = 600
        self.number_of_targets = 40

    def build_playground(self):
        """ Создание окна - игрового поля. """
        self.root = tk.Tk()
        self.root.geometry(f'{self.window_width}x{self.window_height}')

        self.reload_button = tk.Button(self.root, text='reload', command=self.reload_game)
        self.reload_button.pack()

        self.playground = tk.Canvas(self.root, bg='white')
        self.playground.pack(fill=tk.BOTH, expand=1)
        self.text_amount_of_shots = self.playground.create_text(
            50, 20, text=f'Выстрелов {self.amount_of_shots}', font=20)

        self.text_score = self.playground.create_text(
            30, 50, text=f'Счет {self.score}', font=20)

    def reload_game(self):
        """ Перезапуск игры по нажатию соответствующей кнопки. """

        targets = {i: self.targets[i] for i in self.targets}
        balls = {i: self.balls[i] for i in self.balls}

        for i in targets:
            self.del_target(i)

        for i in balls:
            self.del_ball(i)

        self.set_variables()
        self.update_score(0)
        self.update_amount_of_shots(0)

        self.create_targets(number_of_targets=self.number_of_targets)

    def update_score(self, score=None):
        """ Обновить счет подбитых мишеней. """
        if score is not None:
            self.score = score
        else:
            self.score += 1
        self.playground.itemconfig(self.text_score, text=f'Счет {self.score}')

    def update_amount_of_shots(self, amount_of_shots=None):
        """ Обновить счет выстрелов. """
        if amount_of_shots is not None:
            self.amount_of_shots = amount_of_shots
        else:
            self.amount_of_shots += 1
        self.playground.itemconfig(self.text_amount_of_shots, text=f'Выстрелов {self.amount_of_shots}')

    def binds(self):
        """ Бинды. """
        self.playground.bind('<Button-1>', self.gun.fire_starter)
        self.playground.bind('<ButtonRelease-1>', self.gun.firing)
        self.playground.bind('<Motion>', self.gun.targetting)

    def create_gun(self):
        """ Создание пушки. """
        self.gun = Gun(self)

    def create_ball(self, start_x, srart_y, vx, vy):
        """ Создание шара. """
        self.balls[self.balls_last_position] = Ball(self, start_x, srart_y, vx, vy, )
        self.balls_last_position += 1

    def create_targets(self, number_of_targets):
        """ Создание целей."""
        for i in range(number_of_targets):
            self.targets[i] = Target(self)

    def checking_collisions(self):
        """ Игровой процесс. """

        balls = {i: self.balls[i] for i in self.balls}
        targets = {i: self.targets[i] for i in self.targets}

        for position_of_ball in balls:
            for position_of_target in targets:
                self.check_collision(position_of_ball,
                                     position_of_target
                                     )

        self.root.after(10, self.checking_collisions)

    def check_collision(self, position_of_ball, position_of_target):
        """ Проверка попадание шара в цель."""
        if position_of_ball not in self.balls or position_of_target not in self.targets:
            return
        ball = self.balls[position_of_ball]
        target = self.targets[position_of_target]

        if ((ball.x - target.x) ** 2 + (ball.y - target.y) ** 2) ** (1 / 2) <= ball.r + target.r:
            self.update_score()
            self.del_ball(position_of_ball)
            self.del_target(position_of_target)

    def del_ball(self, position_of_ball):
        """Удалить шар по ключу в словаре шаров. """
        self.playground.delete(self.balls[position_of_ball].id)
        del self.balls[position_of_ball]

    def del_target(self, position_of_target):
        """ Удалить мишень по ключу в словаре мишеней. """
        self.playground.delete(self.targets[position_of_target].id)
        del self.targets[position_of_target]


if __name__ == '__main__':
    game = GunGame()
