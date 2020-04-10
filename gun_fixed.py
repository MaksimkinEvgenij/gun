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
        print(self.id)
        self.x += self.vx
        self.y -= self.vy
        self.set_coords()
        self.moving = self.game.root.after(100, self.move)

    def remove(self):
        """ Убирает шар с игрового поля. """
        self.game.root.after_cancel(self.moving)
        self.x = 10
        self.y = 10
        self.set_coords()

    def hittest(self, obj):
        """Функция проверяет сталкивалкивается ли данный обьект с целью, описываемой в обьекте obj.

        Args:
            obj: Обьект, с которым проверяется столкновение.
        Returns:
            Возвращает True в случае столкновения мяча и цели. В противном случае возвращает False.
        """

        if ((self.x - obj.x) ** 2 + (self.y - obj.y) ** 2) ** (1 / 2) <= self.r + obj.r:
            return True

        return False


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

        # self.id_points = self.game.playground.create_text(30, 30, text=self.points, font='28')  # очки?

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

    def remove(self):
        """Убирает цель с игрового поля."""
        self.game.root.after_cancel(self.moving)
        self.x = 50
        self.y = 300
        self.set_coords()
        del self


def game():
    """ Игра. """

    for b in balls:
        b.move()
        if b.hittest(target) and target.live:
            target.hit()
            playground.create_text(400, 300,
                                   text='Вы уничтожили цель за ' + str(amount_of_shots) + ' выстрелов',
                                   font='28')
            return
    playground.update()
    time.sleep(0.03)
    gun.targetting()
    gun.power_up()
    root.after(10, game)


def binds():
    playground.bind('<Button-1>', gun.fire_starter)
    playground.bind('<ButtonRelease-1>', gun.firing)
    playground.bind('<Motion>', gun.targetting)


class GunGame:
    def __init__(self):
        self.set_variables()
        self.set_constants()

        self.build_playground()

        self.create_gun()

        self.create_targets(number_of_targets=40)

        self.binds()

        self.start_game()

        self.root.mainloop()

    def set_variables(self):
        """ Переменные для работы игры. """
        self.amount_of_shots = 0
        self.balls = {}
        self.balls_last_position = 0
        self.targets = {}
        self.amount_of_shots = 0
        self.score = 0

    def set_constants(self):
        """ Константы для работы игры. """
        self.window_width = 800
        self.window_height = 600

    def build_playground(self):
        """ Создание окна - игрового поля. """
        self.root = tk.Tk()
        self.root.geometry(f'{self.window_width}x{self.window_height}')

        self.playground = tk.Canvas(self.root, bg='white')
        self.playground.pack(fill=tk.BOTH, expand=1)
        self.text_amount_of_shots = self.playground.create_text(
            50, 20, text=f'Выстрелов {self.amount_of_shots}', font=20)

        self.text_score = self.playground.create_text(
            30, 50, text=f'Счет {self.score}', font=20)

    def update_score(self):
        self.score += 1
        self.playground.itemconfig(self.text_score, text=f'Счет {self.score}')

    def update_amount_of_shots(self):
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

    def create_targets(self, number_of_targets):
        """ Создание целей."""

        for i in range(number_of_targets):
            self.targets[i] = Target(self)
        # self.target = Target(self)

    def start_game(self):
        """ Игровой процесс. """
        for position_of_ball in self.balls:
            for position_of_target in self.targets:
                self.check_collision(self.balls[position_of_ball],
                                     self.targets[position_of_target]
                                     )

        self.root.after(10, self.start_game)

    def check_collision(self, ball, target):
        """ Проверка попадание шара в цель."""
        if ((ball.x - target.x) ** 2 + (ball.y - target.y) ** 2) ** (1 / 2) <= ball.r + target.r:
            print(5)

            ball.remove()
            target.remove()
            self.update_score()

            # self.playground.delete(ball.id)

            # self.playground.delete(target.id)
            # del self.balls[0]
            # del ball


gg = GunGame()

'''

root = tk.Tk()
root.geometry('800x600')


playground = tk.Canvas(root, bg='white')
playground.pack(fill=tk.BOTH, expand=1)



amount_of_shots = 0
balls = []



target = Target()
gun = Gun()

binds()

game()

root.mainloop()
'''
