from tkinter import *
from math import *
# import time
#
# length = 600
# root = Tk()
# canvas = Canvas(root, width=length, height=length)
# canvas.pack()
#
# # speed = float(input('Введите значение от 1 до 10 с примерной скоростью движения точки:'))
# # direction = int(input('Введите 1 (движение по часовой) или 0 (движение против часовой):'))
#
#
# # def running_point(speed, direction):
# #     angle = 0
# #     while angle <= 360:
# #         angle += 0.01 * speed
# #         canvas.create_oval(x0 + (diameter * 1.5 + (cos(angle) * diameter / 2)), \
# #                            y0 + diameter * 1.5 + (sin(angle) * diameter / 2), 10, 10, fill='black')
#
#
# radius = 100
# x0 = length / 2
# y0 = length / 2
# canvas.create_oval(x0+radius, y0+radius, x0-radius, y0-radius, fill='red')
#
# angle = 1
# def moving_point(angle):
#     if angle<720:
#         point = canvas.create_oval(x0+radius*cos(radians(angle))+5, y0+radius*sin(radians(angle))+5,\
#                        x0+radius*cos(radians(angle))-5, y0+radius*sin(radians(angle))-5, fill='black')
#
#         angle += 5
#         return root.after(1000, moving_point(angle))
#     else:
#         return 'stop machine'
#
#
#
#
# root.mainloop()
# moving_point(angle)
root = Tk()
speed = 6 - int(input('Введите число от 0 до 5, отвечающее за скорость движения точки: '))
radius = 100
length = 600
x0, y0 = length/2, length/2

class Painting(object):
    def __init__(self, root, speed):
        self.root = root
        self.speed = speed
        self.point = None
        self.angle = 0
        self.canvas = Canvas(self.root, width=length, height=length)
        self.canvas.pack()

        self.root.title(' '*80 + 'Блоха')
        self.create_circle()
        self.create_point()


    def create_circle(self):
        circle = self.canvas.create_oval(x0 - radius, y0 - radius, x0 + radius, y0 + radius, fill='red')
        return circle

    def create_point(self):
        x1, y1 = x0+radius*cos(radians(self.angle)), y0+radius*sin(radians(self.angle))

        if self.point is None:
            self.point = self.canvas.create_oval(x1+5, y1+5, x1-5, y1-5, fill='black')

        return self.point


    def add_point_movement(self):
        x1, y1 = x0+radius*cos(radians(self.angle)), y0+radius*sin(radians(self.angle))

        self.canvas.coords(self.point, x1+5, y1+5, x1-5, y1-5)
        self.angle += 2

        self.root.after(speed, self.add_point_movement)




paint = Painting(root, speed)
paint.add_point_movement()
root.mainloop()

