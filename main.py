from field import Field
from figure import Figure
from figuresfactory import FiguresFactory
from time import sleep
from os import system


def render(render_field):
    system('cls')
    print("=" * (len(render_field) + 2))
    for l in render_field:
        print("|" + ("".join([str(x) for x in l])).replace("0", " ").replace("1", "#") + "|")
    print("=" * (len(render_field) + 2))


def update_field(field: Field, figure: Figure) -> bool:
    moves_counter = 0
    stop_moving = False
    while not stop_moving:
        figure.current_pos[1] += 1
        stop_moving = field.overlay(figure)
        render(field.current_frame)

        if not stop_moving:
            sleep(0.01)

        if stop_moving and moves_counter == 0 and field.is_almost_filled():
            return False
        moves_counter += 1
    return True


def main():
    field = Field(15, 15)
    figures_factory = FiguresFactory(field.x_size)
    can_continue = True
    while can_continue:
        figure = figures_factory.get_figure()
        can_continue = update_field(field, figure)


if __name__ == '__main__':
    main()
