from random import randrange as rnd, choice
import tkinter as tk
import math
import time


class Ball:
    def __init__(self, x=40, y=450, vx=0, vy=0):
        """ Конструктор класса Ball

        Args:
        x - начальное положение мяча по горизонтали
        y - начальное положение мяча по вертикали
        """
        self.x = x
        self.y = y
        self.r = 10
        self.vx = vx
        self.vy = vy
        self.color = choice(['blue', 'green', 'red', 'brown'])
        self.id = playground.create_oval(
            self.x - self.r,
            self.y - self.r,
            self.x + self.r,
            self.y + self.r,
            fill=self.color
        )

    def set_coords(self):
        playground.coords(
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

        self.x += self.vx
        self.y -= self.vy

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
    def __init__(self):
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
        self.id = playground.create_line(self.start_pos_x, self.start_pos_y, self.end_pos_x, self.end_pos_y, width=7)

    def fire_starter(self, event):
        """ 'Зарядка' выстрела, для дальнейшего выбора силы выстрела.

        Происходит при нажатие до отпускания мыши.
        """
        self.firing_on = 1

    def firing(self, event):
        """Выстрел мячом.

        Происходит при отпускании кнопки мыши.
        Начальные значения компонент скорости мяча vx и vy зависят от положения мыши.
        """
        global amount_of_shots
        amount_of_shots += 1

        self.angle = math.atan((event.y - self.start_pos_y) / (event.x - self.start_pos_x))
        vx = self.fire_power * math.cos(self.angle)
        vy = - self.fire_power * math.sin(self.angle)
        balls.append(Ball(self.end_pos_x, self.end_pos_y, vx, vy))

        self.firing_on = 0
        self.fire_power = 10

    def targetting(self, event=0):
        """Прицеливание. Зависит от положения мыши."""
        if event:
            if event.x - self.start_pos_x != 0:
                self.angle = math.atan((event.y - self.start_pos_y) / (event.x - self.start_pos_x))

        if self.firing_on:  # выстрел
            playground.itemconfig(self.id, fill='orange')
        else:
            playground.itemconfig(self.id, fill='black')

        self.end_pos_x = self.start_pos_x + max(self.fire_power, 20) * math.cos(self.angle)
        self.end_pos_y = self.start_pos_y + max(self.fire_power, 20) * math.sin(self.angle)

        playground.coords(self.id,
                          self.start_pos_x, self.start_pos_y,
                          self.end_pos_x, self.end_pos_y)

    def power_up(self):
        """ Изменяет силу выстрела. """
        if self.firing_on:
            if self.fire_power < 100:
                self.fire_power += 1
            playground.itemconfig(self.id, fill='orange')
        else:
            playground.itemconfig(self.id, fill='black')


class Target:
    def __init__(self):
        self.points = 0
        self.live = 1
        color = self.color = 'red'

        x = self.x = rnd(600, 780)
        y = self.y = rnd(300, 550)
        r = self.r = rnd(2, 50)

        self.id = playground.create_oval(x - r, y - r, x + r, y + r, fill=color)

        self.id_points = playground.create_text(30, 30, text=self.points, font='28')  # очки?

    def hit(self, points=1):
        """Попадание шарика в цель."""
        playground.coords(self.id, -10, -10, -10, -10)
        self.points += points
        playground.itemconfig(self.id_points, text=self.points)
        self.live = 0


def game():
    """ Игра. """

    for b in balls:
        b.move()
        if b.hittest(target) and target.live:
            target.hit()
            playground.itemconfig(message_screen,
                                  text='Вы уничтожили цель за ' + str(amount_of_shots) + ' выстрелов')
            return
    playground.update()
    time.sleep(0.03)
    gun.targetting()
    gun.power_up()
    root.after(10, game)



root = tk.Tk()

root.geometry('800x600')
playground = tk.Canvas(root, bg='white')
playground.pack(fill=tk.BOTH, expand=1)

message_screen = playground.create_text(400, 300, text='', font='28')


amount_of_shots = 0
balls = []



target = Target()

gun = Gun()

playground.bind('<Button-1>', gun.fire_starter)
playground.bind('<ButtonRelease-1>', gun.firing)
playground.bind('<Motion>', gun.targetting)

game()

root.mainloop()
