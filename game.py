import pygame as pg

from field import Field
from figuresfactory import FiguresFactory
from images import Background, Particle


class GameLevel:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((640, 480))
        pg.display.set_caption("CRINGEtris v.0.1")
        self.field_v_size = 20
        self.field_h_size = 15

        self.background_images = Background("bottle")
        self.particle: Particle = Particle("obstacle.bmp")

        self.screen.blit(next(self.background_images), (0, 0))

        self.field = Field(self.field_v_size, self.field_h_size)
        self.figures_factory = FiguresFactory(self.field.x_size)

    def update_field(self) -> bool:
        figure = self.figures_factory.get_figure()
        moves_counter = 0
        stop_moving = False
        while not stop_moving:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_LEFT:
                        self.field.try_to_move_horizontally(figure, -1)
                    elif event.key == pg.K_RIGHT:
                        self.field.try_to_move_horizontally(figure, 1)
                    elif event.key == pg.K_ESCAPE:
                        return False
            figure.current_pos[1] += 1
            stop_moving = self.field.overlay(figure)
            self.draw_field(self.field.current_frame)

            if not stop_moving:
                pg.time.wait(100)

            if stop_moving and moves_counter == 0 and self.field.is_almost_filled():
                return False
            moves_counter += 1
        return True

    def draw_field(self, render_field):
        cell_x_size: int = 20
        cell_y_size: int = 20
        #right_border_width: int = 5
        #os.system('cls')
        #print("=" * (len(render_field) + 2))
        #for line in render_field:
        #    print("|" + ("".join([str(x) for x in line])).replace("0", " ").replace("1", "#") + "|")
        #print("=" * (len(render_field) + 2))

        self.screen.blit(next(self.background_images), (0, 0))
        #pg.draw.line(self.screen, (255, 255, 255), (self.field_h_size * cell_x_size + right_border_width, 0),
        #             (self.field_h_size * cell_x_size + right_border_width, 480), 5)
        for row_num in range(self.field_v_size):
            for elem_num in range(self.field_h_size):
                if render_field[row_num][elem_num] == 1:
                    self.screen.blit(self.particle.image, (cell_y_size * elem_num, cell_x_size * row_num))
        pg.display.update()


def main():
    game = GameLevel()
    while game.update_field():
        pass


if __name__ == "__main__":
    main()
