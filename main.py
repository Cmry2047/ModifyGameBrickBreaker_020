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