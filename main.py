import arcade

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 601
SCREEN_TITLE = "JumpQuest"


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.WHITE)

    def on_draw(self):
        self.clear()


def setup_game(width=900, height=600, title="JumpQuest"):
    game = MyGame(width, height, title)
    return game


def main():
    setup_game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()