import arcade
import arcade.gui
from files.buttons import MainMenu


BACK_STYLE = {
    "normal": arcade.gui.UIFlatButton.UIStyle(
        bg=(100, 100, 100, 150),
        font_size=18,
        font_color=arcade.color.WHITE,
        border_width=0
    ),
    "hover": arcade.gui.UIFlatButton.UIStyle(
        bg=(120, 120, 120, 200),
        font_size=18,
        font_color=arcade.color.WHITE,
        border_width=0
    ),
    "press": arcade.gui.UIFlatButton.UIStyle(
        bg=(150, 150, 150),
        font_size=18,
        font_color=arcade.color.BLACK,
        border_width=0
    ),
}


class MenuView(arcade.View):
    def on_show_view(self):
        self.back = arcade.load_texture("static/img/cave.png")
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        self.menu_element = MainMenu()
        self.manager.add(self.menu_element)

        @self.menu_element.start_button.event("on_click")
        def on_start(event):
            self.window.show_view(GameView())

        @self.menu_element.settings_button.event("on_click")
        def on_settings(event):
            self.window.show_view(SettingsView())

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(self.back, arcade.rect.XYWH(
            self.window.width // 2, self.window.height // 2, self.window.width, self.window.height))
        self.manager.draw()

    def on_hide_view(self):
        self.manager.disable()


class SettingsView(arcade.View):
    def on_show_view(self):
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        layout = arcade.gui.UIAnchorLayout()
        back_btn = arcade.gui.UIFlatButton(text="←", width=30, height=30, style=BACK_STYLE)

        @back_btn.event("on_click")
        def on_back(event):
            self.window.show_view(MenuView())

        layout.add(child=back_btn, anchor_x="left", anchor_y="top", align_x=20, align_y=-20)
        self.manager.add(layout)

    def on_draw(self):
        self.clear()
        arcade.set_background_color((9, 10, 41))
        self.manager.draw()

    def on_hide_view(self):
        self.manager.disable()


class GameView(arcade.View):
    def on_show_view(self):
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        layout = arcade.gui.UIAnchorLayout()
        back_btn = arcade.gui.UIFlatButton(text="←", width=30, height=30, style=BACK_STYLE)

        @back_btn.event("on_click")
        def on_back(event):
            self.window.show_view(MenuView())

        layout.add(child=back_btn, anchor_x="left", anchor_y="top", align_x=20, align_y=-20)
        self.manager.add(layout)

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.BLACK)
        self.manager.draw()

    def on_hide_view(self):
        self.manager.disable()