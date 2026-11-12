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
