import tkinter as tk
import os
import time
import pygame

pygame.mixer.init(
    frequency=44100,
    size=-16,
    channels=2,
    buffer=2048
)

class GameObject:
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)


class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 10
        self.direction = [1, -1]
        self.speed = 2
        self.colliding_items = set()

        item = canvas.create_oval(
            x - self.radius,
            y - self.radius,
            x + self.radius,
            y + self.radius,
            fill="#ffffff",
            outline=""
        )

        super().__init__(canvas, item)

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()

        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1

        if coords[1] <= 0:
            self.direction[1] *= -1

        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed

        self.move(x, y)

    def collide(self, game_objects):
        current_items = {game_object.item for game_object in game_objects}
        new_collisions = [
            game_object
            for game_object in game_objects
            if game_object.item not in self.colliding_items
        ]
        self.colliding_items = current_items

        if not new_collisions:
            return 0

        ball_coords = self.get_position()
        ball_x = (ball_coords[0] + ball_coords[2]) / 2

        if len(new_collisions) > 1:
            self.direction[1] *= -1

        else:
            game_object = new_collisions[0]
            object_coords = game_object.get_position()

            if ball_x > object_coords[2]:
                self.direction[0] = 1
            elif ball_x < object_coords[0]:
                self.direction[0] = -1
            else:
                self.direction[1] *= -1

        points = 0

        for game_object in new_collisions:
            if isinstance(game_object, Brick):
                if game_object.hit():
                    points += 10

        return points


class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 80
        self.height = 10
        self.ball = None

        item = canvas.create_rectangle(
            x - self.width / 2,
            y - self.height / 2,
            x + self.width / 2,
            y + self.height / 2,
            fill="yellow",
            outline=""
        )

        super().__init__(canvas, item)

    def set_ball(self, ball):
        self.ball = ball

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()

        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super().move(offset, 0)

            if self.ball is not None:
                self.ball.move(offset, 0)

