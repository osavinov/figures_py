import os
import pygame as pg

main_dir = os.path.split(os.path.abspath(__file__))[0]


# our game object class
class GameObject:
    def __init__(self, image, speed):
        self.speed = speed
        self.image = image
        self.pos = image.get_rect()

    def move(self):
        self.pos = self.pos.move(self.speed, 0)
        if self.pos.right > 600:
            self.pos.left = 0


# quick function to load an image
def load_image(name):
    path = os.path.join(main_dir, "data", name)
    return pg.image.load(path).convert()


# here's the full code
def main():
    pg.init()
    screen = pg.display.set_mode((640, 480))

    player_image = load_image("player.bmp")
    background_image = load_image("background.bmp")

    screen.blit(background_image, (0, 0))

    player = GameObject(player_image, 5)

    while True:
        screen.blit(background_image, player.pos, player.pos)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            elif event.type == pg.KEYDOWN:
                player.move()
        screen.blit(player.image, player.pos)
        pg.display.update()


if __name__ == "__main__":
    main()
