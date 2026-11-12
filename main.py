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


class Brick(GameObject):
    COLORS = {
        1: "white",
        2: "#3498db",
        3: "#222222"
    }

    def __init__(self, canvas, x, y, hits, destroy_sound=None):
        self.width = 70
        self.height = 20
        self.hits = hits
        self.destroy_sound = destroy_sound
        self.destroyed = False

        item = canvas.create_rectangle(
            x - self.width / 2,
            y - self.height / 2,
            x + self.width / 2,
            y + self.height / 2,
            fill=Brick.COLORS[hits],
            outline="#111111",
            width=2,
            tags="brick"
        )

        super().__init__(canvas, item)

    def hit(self):
        if self.destroyed:
            return False

        self.hits -= 1

        if self.hits <= 0:
            self.destroyed = True

            if self.destroy_sound is not None:
                self.destroy_sound.play()

            self.delete()
        else:
            self.canvas.itemconfig(
                self.item,
                fill=Brick.COLORS[self.hits]
            )

        return True


class Game(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.lives = 3
        self.score = 0
        self.width = 610
        self.height = 400
        self.running = False

        self.folder = os.path.dirname(os.path.abspath(__file__))

        self.music_file = os.path.join(
            self.folder,
            "Backsound_compatible.wav"
        )

        self.brick_sound_file = os.path.join(
            self.folder,
            "brickhancur.wav"
        )

        self.life_lost_sound_file = os.path.join(
            self.folder,
            "nyawa_berkurang.wav"
        )

        self.lose_sound_file = os.path.join(
            self.folder,
            "kalah.wav"
        )

        self.brick_sound = self.load_sound(
            self.brick_sound_file,
            "brick_hancur.wav"
        )

        self.life_lost_sound = self.load_sound(
            self.life_lost_sound_file,
            "nyawa_berkurang.wav"
        )

        self.lose_sound = self.load_sound(
            self.lose_sound_file,
            "kalah.wav"
        )

        if self.brick_sound is not None:
            self.brick_sound.set_volume(1.0)

        if self.life_lost_sound is not None:
            self.life_lost_sound.set_volume(1.0)

        if self.lose_sound is not None:
            self.lose_sound.set_volume(1.0)

        self.canvas = tk.Canvas(
            self,
            bg= "#739bd0",
            width=self.width,
            height=self.height,
            highlightthickness=0
        )

        self.canvas.pack()
        self.pack()

        self.items = {}
        self.ball = None
        self.hud = None
        self.score_hud = None
        self.text = None
        self.keys = set()

        self.paddle = Paddle(
            self.canvas,
            self.width / 2,
            326
        )

        self.items[self.paddle.item] = self.paddle

        for x in range(45, self.width - 20, 75):
            self.add_brick(x, 55, 2)
            self.add_brick(x, 80, 1)
            self.add_brick(x, 105, 1)

        self.update_score_text()
        self.setup_game()

        self.canvas.bind(
            "<KeyPress-Left>",
            lambda event: self.keys.add("Left")
        )

        self.canvas.bind(
            "<KeyRelease-Left>",
            lambda event: self.keys.discard("Left")
        )

        self.canvas.bind(
            "<KeyPress-Right>",
            lambda event: self.keys.add("Right")
        )

        self.canvas.bind(
            "<KeyRelease-Right>",
            lambda event: self.keys.discard("Right")
        )

        self.canvas.focus_set()
        self.paddle_loop()
        self.play_music()

        self.master.protocol(
            "WM_DELETE_WINDOW",
            self.close_game
        )

    def load_sound(self, sound_file, sound_name):
        if not os.path.exists(sound_file):
            print("File %s tidak ditemukan." % sound_name)
            return None

        try:
            return pygame.mixer.Sound(sound_file)
        except pygame.error as error:
            print(
                "Gagal membuka %s: %s"
                % (sound_name, error)
            )
            return None

    def play_music(self):
        if not os.path.exists(self.music_file):
            print("File musik.wav tidak ditemukan.")
            return

        try:
            pygame.mixer.music.load(self.music_file)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        except pygame.error as error:
            print("Gagal membuka musik.wav:", error)

    def play_life_lost_sound(self):
        if self.life_lost_sound is not None:
            self.life_lost_sound.play()

    def play_lose_sound(self):
        if self.lose_sound is not None:
            self.lose_sound.play()

    def stop_music(self):
        pygame.mixer.music.stop()

    def close_game(self):
        self.running = False
        pygame.mixer.music.stop()
        pygame.mixer.stop()
        pygame.mixer.quit()
        self.master.destroy()

    def paddle_loop(self):
        if not self.master.winfo_exists():
            return

        if "Left" in self.keys:
            self.paddle.move(-4)

        if "Right" in self.keys:
            self.paddle.move(4)

        self.after(16, self.paddle_loop)

    def setup_game(self):
        self.running = False
        self.add_ball()
        self.update_lives_text()

        if self.text is not None:
            self.canvas.delete(self.text)

        self.text = self.draw_text(
            300,
            200,
            "Tekan SPACE untuk memulai"
        )

        self.canvas.bind(
            "<space>",
            lambda event: self.start_game()
        )

        self.canvas.focus_set()

    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()

        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) / 2

        self.ball = Ball(
            self.canvas,
            x,
            310
        )

        self.paddle.set_ball(self.ball)

    def add_brick(self, x, y, hits):
        brick = Brick(
            self.canvas,
            x,
            y,
            hits,
            self.brick_sound
        )

        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size=25):
        font = ("Montserrat Bold", size)

        return self.canvas.create_text(
            x,
            y,
            text=text,
            font=font,
            fill="white"
        )

    def update_lives_text(self):
        text = "Nyawa: %s" % self.lives

        if self.hud is None:
            self.hud = self.draw_text(
                50,
                20,
                text,
                15
            )
        else:
            self.canvas.itemconfig(
                self.hud,
                text=text
            )

    def update_score_text(self):
        text = "Total Score: %s" % self.score

        if self.score_hud is None:
            self.score_hud = self.draw_text(
                540,
                20,
                text,
                12
            )
        else:
            self.canvas.itemconfig(
                self.score_hud,
                text=text
            )

    def start_game(self):
        if self.running:
            return

        self.running = True
        self.canvas.unbind("<space>")

        if self.text is not None:
            self.canvas.delete(self.text)
            self.text = None

        self.paddle.ball = None
        self.game_loop()

    def game_loop(self):
        if not self.running:
            return

        self.check_collisions()

        num_bricks = len(
            self.canvas.find_withtag("brick")
        )

        if num_bricks == 0:
            self.running = False
            self.stop_music()

            self.draw_text(
                300,
                200,
                "Kamu Menang!"
            )

        elif self.ball.get_position()[3] >= self.height:
            self.running = False
            self.lives -= 1
            self.update_lives_text()

            if self.lives <= 0:
                self.stop_music()
                self.play_lose_sound()

                self.draw_text(
                    300,
                    200,
                    "Nice Try bang!"
                )
            else:
                self.play_life_lost_sound()
                self.after(1000, self.setup_game)

        else:
            self.ball.update()
            self.after(16, self.game_loop)

    def check_collisions(self):
        ball_coords = self.ball.get_position()

        overlapping_items = self.canvas.find_overlapping(
            *ball_coords
        )

        objects = [
            self.items[item]
            for item in overlapping_items
            if item in self.items
        ]

        points = self.ball.collide(objects)

        if points > 0:
            self.score += points
            self.update_score_text()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Brick Breaker")
    root.resizable(False, False)

    game = Game(root)
    root.mainloop()
    