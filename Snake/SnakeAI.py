import tkinter as tk
from random import randint
from PIL import Image, ImageTk


MOVE_INCREMENT = 20
MOVES_PER_SECOND = 1500
GAME_SPEED = 1500 // MOVES_PER_SECOND

class Snake(tk.Canvas):
    def __init__(self):
        super().__init__(
            width=600, height=620, background="black", highlightthickness=0
        )

        self.playing = True

        self.snake_positions = [(100, 100), (120, 100), (140, 100)]
        self.food_position = self.set_new_food_position()
        self.direction = "Right"

        self.score = 0

        self.load_assets()
        self.create_objects()

        self.bind_all("<Key>", self.on_key_press)

        self.pack()

        self.createAIPath()

        self.after(GAME_SPEED, self.perform_actions)
    
    def split(self, x):
        return ((x // 30) * 20, (x % 30) * 20 + 20)

    def combine(self, a):
        x, y = a
        return ((x // 20) * 30) + ((y - 20) // 20)

    def safe(self, v, i):
        if not self.graph[self.path[i - 1]][v]:
            return False

        return v not in self.visited
    
    def pathUtil(self, i):
        n = 30 * 29
        if i == n: 
            return self.graph[self.path[i - 1]][self.path[0]]

        for v in range(n):
            if self.safe(v, i):
                self.path[i] = v
                self.visited.add(v)
                if self.pathUtil(i + 1):
                    return True
                self.visited.remove(v)
                self.path[i] = -1

        return False

    def check(self, a):
        x, y = a
        return not (x <= 0 or x >= 580 or y <= 20 or y >= 600)

    def createAIPath(self):
        # self.createAIPathUtil()
        self.path = []
        for i in range(40, 580, 40):
            for j in range(40, 600, 20):
                self.path.append((i, j))
            for j in range(580, 20, -20):
                self.path.append((i + 20, j))
        for i in range(580, 40, -20):
            self.path.append((i, 20))

        self.path = [(i, j) for j, i in self.path]

        self.ind = (self.path.index((100, 100)) + 1) % len(self.path)

    def createAIPathUtil(self):
        n = 30 * 29
        self.graph = [[0] * n for _ in range(n)]

        for i in range(n):
            x, y = self.split(i)
            if self.check((x - 20, y)):
                self.graph[i][self.combine((x - 20, y))] = 1
            if self.check((x + 20, y)):
                self.graph[i][self.combine((x + 20, y))] = 1
            if self.check((x, y - 20)):
                self.graph[i][self.combine((x, y - 20))] = 1
            if self.check((x, y + 20)):
                self.graph[i][self.combine((x, y + 20))] = 1

        self.path = [-1] * n
        self.path[0] = self.combine((100, 100))
        self.visited = {self.path[0]}

        self.pathUtil(1)

        self.ind = 0
        self.path = [self.split(i) for i in self.path]

    def load_assets(self):
        try:
            self.snake_body_image = Image.open("Snake/snake.png")
            self.snake_body = ImageTk.PhotoImage(self.snake_body_image)

            self.food_image = Image.open("Snake/food.png")
            self.food = ImageTk.PhotoImage(self.food_image)
        except IOError as error:
            root.destroy()
            raise

    def create_objects(self):
        self.create_text(
            35, 12, text=f"Score: {self.score}", tag="score", fill="#fff", font=10
        )

        for x_position, y_position in self.snake_positions:
            self.create_image(
                x_position, y_position, image=self.snake_body, tag="snake"
            )

        self.create_image(*self.food_position, image=self.food, tag="food")
        self.create_rectangle(7, 27, 593, 613, outline="#525d69")

    def check_collisions(self):
        head_x_position, head_y_position = self.snake_positions[0]

        return (
            head_x_position in (0, 600)
            or head_y_position in (20, 620)
            or (head_x_position, head_y_position) in self.snake_positions[1:]
        )

    def check_food_collision(self):
        if self.snake_positions[0] == self.food_position:
            self.score += 1
            self.snake_positions.append(self.snake_positions[-1])

            self.create_image(
                *self.snake_positions[-1], image=self.snake_body, tag="snake"
            )
            self.food_position = self.set_new_food_position()
            self.coords(self.find_withtag("food"), *self.food_position)

            score = self.find_withtag("score")
            self.itemconfigure(score, text=f"Score: {self.score}", tag="score")

    def end_game(self):        
        msg = f"Game over! You scored {self.score}!"
        
        highscore = int(open('Snake/highscore.txt', 'r').read())
        if self.score > highscore:
            msg += "\nNew highscore!"
            open('Snake/highscore.txt', 'w').write(str(self.score))

        self.delete(tk.ALL)
        self.create_text(
            self.winfo_width() / 2,
            self.winfo_height() / 2,
            text=msg,
            fill="#fff",
            font=14
        )

        self.playing = False

    def move_snake(self):
        head_x_position, head_y_position = self.snake_positions[0]

        new_head_position = self.path[self.ind]
        self.ind = (self.ind + 1) % len(self.path)

        self.snake_positions = [new_head_position] + self.snake_positions[:-1]

        for segment, position in zip(self.find_withtag("snake"), self.snake_positions):
            self.coords(segment, position)

    def on_key_press(self, e):
        new_direction = e.keysym

        all_directions = ("Up", "Down", "Left", "Right")
        opposites = ({"Up", "Down"}, {"Left", "Right"})

        if (
            new_direction in all_directions
            and {new_direction, self.direction} not in opposites
        ):
            self.direction = new_direction

    def perform_actions(self):
        if self.playing and self.check_collisions():
            self.end_game()
            return

        self.check_food_collision()
        self.move_snake()

        self.after(GAME_SPEED, self.perform_actions)

    def set_new_food_position(self):
        while True:
            x_position = randint(1, 29) * MOVE_INCREMENT
            y_position = randint(3, 29) * MOVE_INCREMENT
            food_position = (x_position, y_position)

            if food_position not in self.snake_positions:
                return food_position

root = tk.Tk()
root.title("Snake")
root.resizable(False, False)
root.tk.call("tk", "scaling", 4.0)

board = Snake()

root.mainloop()
