from random import randrange as rnd, choice
import tkinter as tk
import math
import time





class Ball:
    def __init__(self, x=40, y=450, vx=0, vy=0):
        """ Конструктор класса ball

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
        self.id = canv.create_oval(
                self.x - self.r,
                self.y - self.r,
                self.x + self.r,
                self.y + self.r,
                fill=self.color
        )
        self.live = 30

    def set_coords(self):
        canv.coords(
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
        # FIXME
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
        # FIXME
        return False


class Gun:
    def __init__(self):
        self.f2_power = 10
        self.f2_on = 0
        self.angle = 1
        self.id = canv.create_line(20,450,50,420,width=7) # FIXME: don't know how to set it...

    def fire_starter(self, event):
        """ Выбор силы выстрела? """
        self.f2_on = 1

    def firing(self, event):
        """Выстрел мячом.

        Происходит при отпускании кнопки мыши.
        Начальные значения компонент скорости мяча vx и vy зависят от положения мыши.
        """
        global bullet
        bullet += 1     # FIXME зачем это


        self.angle = math.atan((event.y - 450) / (event.x - 40))
        vx = self.f2_power * math.cos(self.angle)
        vy = - self.f2_power * math.sin(self.angle)
        balls.append(Ball(40, 450 , vx, vy))


        self.f2_on = 0
        self.f2_power = 10

    def targetting(self, event=0):
        """Прицеливание. Зависит от положения мыши."""
        if event:
            self.angle = math.atan((event.y - 450) / (event.x - 20))
        if self.f2_on:  # выстрел
            canv.itemconfig(self.id, fill='orange')
        else:
            canv.itemconfig(self.id, fill='black')
        canv.coords(self.id, 20, 450,
                    20 + max(self.f2_power, 20) * math.cos(self.angle),
                    450 + max(self.f2_power, 20) * math.sin(self.angle)
                    )

    def power_up(self):
        if self.f2_on:
            if self.f2_power < 100:
                self.f2_power += 1
            canv.itemconfig(self.id, fill='orange')
        else:
            canv.itemconfig(self.id, fill='black')


class Target:
    def __init__(self):
        self.points = 0
        self.live = 1
        color = self.color = 'red'

        x = self.x = rnd(600, 780)
        y = self.y = rnd(300, 550)
        r = self.r = rnd(2, 50)

        self.id = canv.create_oval(x-r, y-r, x+r, y+r, fill = color)

        self.id_points = canv.create_text(30,30,text = self.points,font = '28')     # очки?




    def hit(self, points=1):
        """Попадание шарика в цель."""
        canv.coords(self.id, -10, -10, -10, -10)
        self.points += points
        canv.itemconfig(self.id_points, text=self.points)



def new_game():
    #target.new_target()

    #target.live = 1
    while target.live or balls:
        for b in balls:
            b.move()
            if b.hittest(target) and target.live:
                target.live = 0
                target.hit()
                canv.bind('<Button-1>', '')
                canv.bind('<ButtonRelease-1>', '')
                canv.itemconfig(screen1, text='Вы уничтожили цель за ' + str(bullet) + ' выстрелов')
        canv.update()
        time.sleep(0.03)
        gun.targetting()
        gun.power_up()
    canv.itemconfig(screen1, text='')
    canv.delete(Gun)
    root.after(750, new_game)









root = tk.Tk()
fr = tk.Frame(root)
root.geometry('800x600')
canv = tk.Canvas(root, bg='white')
canv.pack(fill=tk.BOTH, expand=1)




bullet = 0
balls = []

target = Target()

screen1 = canv.create_text(400, 300, text='', font='28')

gun = Gun()


canv.bind('<Button-1>', gun.fire_starter)
canv.bind('<ButtonRelease-1>', gun.firing)
canv.bind('<Motion>', gun.targetting)


new_game()

root.mainloop()
