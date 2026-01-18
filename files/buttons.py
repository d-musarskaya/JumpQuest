import arcade
import arcade.gui

class MainMenu(arcade.gui.UIAnchorLayout):
    def __init__(self):
        super().__init__()
        button_style = {
            "normal": arcade.gui.UIFlatButton.UIStyle(
                font_size=20, font_color=arcade.color.WHITE,
                bg=(80, 194, 137), border=(80, 194, 137), border_width=0
            ),
            "hover": arcade.gui.UIFlatButton.UIStyle(
                font_size=20, font_color=arcade.color.WHITE,
                bg=(70, 170, 120), border=(70, 170, 120), border_width=0
            ),
            "press": arcade.gui.UIFlatButton.UIStyle(
                font_size=20, font_color=arcade.color.WHITE,
                bg=(28, 22, 79), border=(28, 22, 79), border_width=0
            ),
        }

        self.v_box = arcade.gui.UIBoxLayout(space_between=10)
        self.start_button = arcade.gui.UIFlatButton(text="Начать играть", width=280, height=50, style=button_style)
        self.settings_button = arcade.gui.UIFlatButton(text="Настройки", width=280, height=50, style=button_style)
        self.v_box.add(self.start_button)
        self.v_box.add(self.settings_button)
        self.add(child=self.v_box, anchor_x="center_x", anchor_y="center_y")