import arcade
import arcade.gui

# Импортируем стиль для кнопки, если он нужен здесь,
# либо определите BACK_STYLE прямо в этом файле
BACK_STYLE = {
    "normal": arcade.gui.UIFlatButton.UIStyle(bg=(100, 100, 100, 150), font_size=18, font_color=arcade.color.WHITE),
    "hover": arcade.gui.UIFlatButton.UIStyle(bg=(120, 120, 120, 200), font_size=18, font_color=arcade.color.WHITE),
    "press": arcade.gui.UIFlatButton.UIStyle(bg=(150, 150, 150), font_size=18, font_color=arcade.color.BLACK),
}


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.tile_map = None
        self.scene = None
        self.manager = None

    def setup(self):
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Кнопка назад
        layout = arcade.gui.UIAnchorLayout()
        back_btn = arcade.gui.UIFlatButton(text="←", width=30, height=30, style=BACK_STYLE)

        @back_btn.event("on_click")
        def on_back(event):
            # Импорт внутри, чтобы избежать круговой зависимости
            from files.views.views import MenuView
            self.window.show_view(MenuView())

        layout.add(child=back_btn, anchor_x="left", anchor_y="top", align_x=20, align_y=-20)
        self.manager.add(layout)

        # Путь к карте
        map_path = "static/maps/map_1.tmx"
        layer_options = {"walls": {"use_spatial_hash": True}}

        try:
            self.tile_map = arcade.load_tilemap(map_path, scaling=1.0, layer_options=layer_options)
            self.scene = arcade.Scene.from_tilemap(self.tile_map)
            if self.tile_map.background_color:
                arcade.set_background_color(self.tile_map.background_color)
        except Exception as e:
            print(f"Ошибка загрузки карты: {e}")

    def on_show_view(self):
        self.setup()

    def on_draw(self):
        self.clear()
        if self.scene:
            self.scene.draw()
        self.manager.draw()  # Рисуем кнопку поверх карты

    def on_hide_view(self):
        if self.manager:
            self.manager.disable()