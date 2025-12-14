import arcade

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
SCREEN_TITLE = "JumpQuest"


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.WHITE)

    def on_draw(self):
        button_width = 240
        button_height = 60
        self.clear()

        arcade.draw_lbwh_rectangle_filled((self.width - button_width) // 2, 320, button_width,
                                          button_height, (0, 194, 168))
        arcade.draw_lbwh_rectangle_filled((self.width - button_width) // 2, 230, button_width,
                                          button_height, (0, 194, 168))

        arcade.draw_text(
            "Начать играть",
            self.width / 2,
            320 + button_height / 2,
            arcade.color.WHITE,
            font_size=20,
            anchor_x="center",
            anchor_y="center",
        )
        arcade.draw_text(
            "Настройки",
            self.width / 2,
            230 + button_height / 2,
            arcade.color.WHITE,
            font_size=20,
            anchor_x="center",
            anchor_y="center",
        )


def setup_game(width=900, height=600, title="JumpQuest"):
    game = MyGame(width, height, title)
    return game


def main():
    setup_game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
