import arcade
from files.views import MenuView

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 672
SCREEN_TITLE = "JumpQuest"


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    menu_view = MenuView()
    window.show_view(menu_view)

    arcade.run()


if __name__ == "__main__":
    main()