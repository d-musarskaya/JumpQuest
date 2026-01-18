import arcade
import random

# Константы
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 670
SCREEN_TITLE = "JumpQuest"

TILE_SIZE = 32
PLAYER_SIZE = 96
GHOST_SIZE = 32
TORCH_SIZE = 32

PLAYER_SPEED = 2
GHOST_SPEED = 1

PLAYER_MAX_HP = 100
GHOST_MAX_HP = 100
GHOST_DAMAGE = 10
TORCH_DAMAGE = 50
TORCH_DURATION = 3.0
TORCH_COOLDOWN = 2.0

# Состояния игры
MENU = 0
PLAYING = 1
GAME_OVER = 2
GAME_WON = 3


class Player(arcade.Sprite):
    def __init__(self, character_num, scale=3.0):
        self.character_num = character_num
        char_path = f"static/img/characters/char{character_num}/pose_01.png"
        super().__init__(char_path, scale=scale)

        self.max_hp = PLAYER_MAX_HP
        self.current_hp = PLAYER_MAX_HP
        self.direction = "right"
        self.on_ladder = False

        # Анимация
        self.walk_textures = []
        self.ladder_textures = []

        # Загрузка текстур для ходьбы влево (1-3) и вправо (4-6)
        for i in range(1, 4):
            texture = arcade.load_texture(f"static/img/characters/char{character_num}/pose_0{i}.png")
            self.walk_textures.append(texture)

        for i in range(4, 7):
            texture = arcade.load_texture(f"static/img/characters/char{character_num}/pose_0{i}.png")
            self.walk_textures.append(texture)

        # Загрузка текстур для лестницы (7-9)
        for i in range(7, 10):
            texture = arcade.load_texture(f"static/img/characters/char{character_num}/pose_0{i}.png")
            self.ladder_textures.append(texture)

        self.current_walk_frame = 0
        self.walk_frame_delay = 0
        self.walk_frame_speed = 5  # Чем меньше, тем быстрее

        # Факел
        self.torch_active = False
        self.torch_cooldown = False
        self.torch_timer = 0
        self.torch_cooldown_timer = 0

        self.torch_textures = []
        for i in range(1, 7):
            texture = arcade.load_texture(f"static/img/torch/torch_pose_0{i}.png")
            self.torch_textures.append(texture)

        self.current_torch_frame = 0
        self.torch_frame_delay = 0
        self.torch_frame_speed = 3

        self.torch_sprite = None

    def update_animation(self, delta_time):
        # Обновление анимации ходьбы
        self.walk_frame_delay += 1
        if self.walk_frame_delay >= self.walk_frame_speed:
            self.walk_frame_delay = 0
            if self.change_x != 0 and not self.on_ladder:
                self.current_walk_frame = (self.current_walk_frame + 1) % 3
                if self.change_x > 0:  # Вправо
                    self.texture = self.walk_textures[3 + self.current_walk_frame]
                    self.direction = "right"
                else:  # Влево
                    self.texture = self.walk_textures[self.current_walk_frame]
                    self.direction = "left"
            elif self.on_ladder and self.change_y != 0:
                self.current_walk_frame = (self.current_walk_frame + 1) % 3
                self.texture = self.ladder_textures[self.current_walk_frame]

        # Обновление анимации факела
        if self.torch_active:
            self.torch_frame_delay += 1
            if self.torch_frame_delay >= self.torch_frame_speed:
                self.torch_frame_delay = 0
                self.current_torch_frame = (self.current_torch_frame + 1) % 6
                self.torch_sprite.texture = self.torch_textures[self.current_torch_frame]

            # Обновление позиции факела
            if self.direction == "right":
                self.torch_sprite.center_x = self.center_x + 20
                self.torch_sprite.center_y = self.center_y
            else:
                self.torch_sprite.center_x = self.center_x - 20
                self.torch_sprite.center_y = self.center_y

            if self.torch_sprite is not None:
                if self.direction == "right":
                    self.torch_sprite.center_x = self.center_x + 20
                    self.torch_sprite.center_y = self.center_y
                else:
                    self.torch_sprite.center_x = self.center_x - 20
                    self.torch_sprite.center_y = self.center_y

            # Таймер активности факела
            self.torch_timer -= delta_time
            if self.torch_timer <= 0:
                self.torch_active = False
                self.torch_sprite.texture = self.torch_textures[0]
                self.torch_cooldown = True
                self.torch_cooldown_timer = TORCH_COOLDOWN

        elif self.torch_cooldown:
            self.torch_cooldown_timer -= delta_time
            if self.torch_cooldown_timer <= 0:
                self.torch_cooldown = False

    def activate_torch(self):
        if not self.torch_active and not self.torch_cooldown:
            self.torch_active = True
            self.torch_timer = TORCH_DURATION
            self.current_torch_frame = 0

            # Создаем спрайт факела при активации
            if self.torch_sprite is None:
                self.torch_sprite = arcade.Sprite(f"static/img/torch/torch_pose_01.png", scale=1.0)
            else:
                self.torch_sprite.texture = arcade.load_texture(f"static/img/torch/torch_pose_01.png")

            if self.direction == "right":
                self.torch_sprite.center_x = self.center_x + 20
                self.torch_sprite.center_y = self.center_y
            else:
                self.torch_sprite.center_x = self.center_x - 20
                self.torch_sprite.center_y = self.center_y



class Ghost(arcade.Sprite):
    def __init__(self, x, y, scale=1.0):
        texture = arcade.load_texture("static/img/characters/ghost/hood_pose_01.png")
        super().__init__(texture, scale=scale)

        self.center_x = x
        self.center_y = y
        self.max_hp = GHOST_MAX_HP
        self.current_hp = GHOST_MAX_HP
        self.direction = random.choice(["left", "right"])
        self.speed = GHOST_SPEED

        self.last_move_time = 0
        self.stuck_timer = 0
        self.last_x_position = x
        self.initial_y = y

        # Текстуры для анимации
        self.left_textures = []
        self.right_textures = []

        for i in range(1, 4):
            texture = arcade.load_texture(f"static/img/characters/ghost/hood_pose_0{i}.png")
            self.left_textures.append(texture)

        for i in range(4, 7):
            texture = arcade.load_texture(f"static/img/characters/ghost/hood_pose_0{i}.png")
            self.right_textures.append(texture)

        self.current_frame = 0
        self.frame_delay = 0
        self.frame_speed = 8

        if self.direction == "left":
            self.change_x = -self.speed
            self.texture = self.left_textures[0]
        else:
            self.change_x = self.speed
            self.texture = self.right_textures[0]

    def update_animation(self):
        self.frame_delay += 1
        if self.frame_delay >= self.frame_speed:
            self.frame_delay = 0
            self.current_frame = (self.current_frame + 1) % 3

            if self.direction == "left":
                self.texture = self.left_textures[self.current_frame]
            else:
                self.texture = self.right_textures[self.current_frame]

    def take_damage(self, damage):
        self.current_hp -= damage
        return self.current_hp <= 0


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        self.game_state = MENU
        self.current_level = 1
        self.max_levels = 3

        # Списки спрайтов
        self.scene = None
        self.player = None
        self.ghosts = None
        self.physics_engine = None

        # Слои карты
        self.background_layer = None
        self.walls_layer = None
        self.decor_layer = None
        self.stairs_layer = None
        self.tile_map = None


        # Таймеры
        self.total_time = 0.0

        # UI
        self.health_bar_width = 200
        self.health_bar_height = 20

    def setup_level(self, level_num):
        """Настройка уровня"""
        # Загрузка карты
        map_path = f"static/maps/map_{level_num}.tmx"
        self.tile_map = arcade.load_tilemap(map_path)

        # Инициализация сцены
        self.scene = arcade.Scene()

        # Получение слоев
        self.background_layer = self.tile_map.sprite_lists.get("background", [])
        self.walls_layer = self.tile_map.sprite_lists.get("walls", [])
        self.decor_layer = self.tile_map.sprite_lists.get("decor", [])
        self.stairs_layer = self.tile_map.sprite_lists.get("stairs", [])

        # Добавление слоев в сцену
        if self.background_layer:
            self.scene.add_sprite_list("background", sprite_list=self.background_layer)
        if self.walls_layer:
            self.scene.add_sprite_list("walls", sprite_list=self.walls_layer)
        if self.decor_layer:
            self.scene.add_sprite_list("decor", sprite_list=self.decor_layer)
        if self.stairs_layer:
            self.scene.add_sprite_list("stairs", sprite_list=self.stairs_layer)

        # Создание игрока
        self.player = Player(level_num)

        # Начальная позиция игрока
        start_x = TILE_SIZE * 2 + TILE_SIZE // 2  # Центр клетки (2, 18)
        start_y = TILE_SIZE * 18 + TILE_SIZE // 2
        self.player.center_x = start_x
        self.player.center_y = start_y

        self.scene.add_sprite("player", self.player)

        # Создание привидений
        self.ghosts = arcade.SpriteList()
        self.scene.add_sprite_list("ghosts")

        # Генерация привидений (5 на каждом уровне пола)
        if self.walls_layer:
            # Определяем уровни (в клетках) где должны появляться привидения
            spawn_levels = [2, 6, 10, 14, 18]

            for level_y in spawn_levels:
                y_pos = level_y * TILE_SIZE

                # 5 привидений на каждом уровне
                for _ in range(5):
                    # Рандомная позиция X, кроме первой и последней клетки
                    min_x = TILE_SIZE * 2
                    max_x = (self.tile_map.width - 2) * TILE_SIZE
                    x_pos = random.randint(min_x, max_x)

                    ghost = Ghost(x_pos, y_pos, scale=0.1)
                    self.ghosts.append(ghost)
                    self.scene.add_sprite("ghosts", ghost)

        # Физический движок
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player,
            self.walls_layer
        )


        self.game_state = PLAYING

    def setup(self):
        """Настройка игры"""
        self.game_state = MENU

    def on_draw(self):
        """Отрисовка игры"""
        self.clear()

        if self.game_state == MENU:
            self.draw_menu()
        elif self.game_state == PLAYING:
            self.draw_game()
            self.draw_ui()
        elif self.game_state == GAME_WON:
            self.draw_game_won()
        elif self.game_state == GAME_OVER:
            self.draw_game_over()

    def draw_menu(self):
        """Отрисовка меню"""
        button_width = 240
        button_height = 60

        # Фон
        arcade.draw_lrbt_rectangle_filled(left=0, right=self.width, top=self.height, bottom=0, color=arcade.color.WHITE)

        # Заголовок
        arcade.draw_text(
            "JumpQuest",
            self.width / 2,
            450,
            arcade.color.BLACK,
            font_size=50,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )

        # Кнопки
        arcade.draw_lrbt_rectangle_filled(
            left=(self.width - button_width) // 2,
            right=(self.width + button_width) // 2,
            top=320 + button_height,
            bottom=320,
            color=(0, 194, 168)
        )
        arcade.draw_lrbt_rectangle_filled(
            left=(self.width - button_width) // 2,
            right=(self.width + button_width) // 2,
            top=230 + button_height,
            bottom=230,
            color=(0, 194, 168)
        )

        # Текст кнопок
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

    def draw_game(self):
        """Отрисовка игрового процесса"""
        self.scene.draw()  # Это отрисует все спрайты, включая игрока

        # Отрисовка факела отдельно (если он активен)
        if self.player.torch_active and self.player.torch_sprite is not None:
            self.player.torch_sprite.draw()


    def draw_ui(self):
        """Отрисовка интерфейса"""
        # Координаты для полоски здоровья
        left = self.width // 2 - self.health_bar_width // 2
        right = self.width // 2 + self.health_bar_width // 2
        bottom = self.height - 20 - self.health_bar_height // 2
        top = self.height - 20 + self.health_bar_height // 2

        # Рамка здоровья
        arcade.draw_lrbt_rectangle_filled(
            left=left,
            right=right,
            bottom=bottom,
            top=top,
            color=arcade.color.BLACK
        )

        # Заполненная часть здоровья
        health_percentage = self.player.current_hp / self.player.max_hp
        if health_percentage > 0:
            fill_right = left + self.health_bar_width * health_percentage
            arcade.draw_lrbt_rectangle_filled(
                left=left + 2,
                right=fill_right - 2,
                bottom=bottom + 2,
                top=top - 2,
                color=arcade.color.RED
            )

        # Отображение уровня
        arcade.draw_text(
            f"Уровень: {self.current_level}",
            10,
            self.height - 40,
            arcade.color.BLACK,
            font_size=16
        )

        # Отображение состояния факела
        torch_text = "Факел: "
        if self.player.torch_active:
            torch_text += "АКТИВЕН"
            color = arcade.color.YELLOW
        elif self.player.torch_cooldown:
            torch_text += "ПЕРЕЗАРЯДКА"
            color = arcade.color.RED
        else:
            torch_text += "ГОТОВ"
            color = arcade.color.GREEN

        arcade.draw_text(
            torch_text,
            self.width - 200,
            self.height - 40,
            color,
            font_size=16
        )

    def draw_game_won(self):
        """Отрисовка экрана победы"""
        arcade.draw_rectangle_filled(
            self.width // 2,
            self.height // 2,
            self.width,
            self.height,
            arcade.color.BLACK
        )

        arcade.draw_text(
            "Игра пройдена!",
            self.width // 2,
            self.height // 2,
            arcade.color.GOLD,
            font_size=50,
            anchor_x="center",
            anchor_y="center"
        )

        arcade.draw_text(
            "Нажмите ESC для выхода в меню",
            self.width // 2,
            self.height // 2 - 60,
            arcade.color.WHITE,
            font_size=20,
            anchor_x="center",
            anchor_y="center"
        )

    def draw_game_over(self):
        """Отрисовка экрана поражения"""
        arcade.draw_rectangle_filled(
            self.width // 2,
            self.height // 2,
            self.width,
            self.height,
            arcade.color.BLACK
        )

        arcade.draw_text(
            "Игра окончена",
            self.width // 2,
            self.height // 2,
            arcade.color.RED,
            font_size=50,
            anchor_x="center",
            anchor_y="center"
        )

        arcade.draw_text(
            "Нажмите ESC для выхода в меню",
            self.width // 2,
            self.height // 2 - 60,
            arcade.color.WHITE,
            font_size=20,
            anchor_x="center",
            anchor_y="center"
        )

    def on_update(self, delta_time):
        """Обновление игры"""
        if self.game_state != PLAYING:
            return

        self.total_time += delta_time

        # Обновление физики
        self.physics_engine.update()

        # Обновление анимации игрока
        self.player.update_animation(delta_time)

        # Проверка нахождения на лестнице
        self.player.on_ladder = False
        if self.stairs_layer:
            ladder_collisions = arcade.check_for_collision_with_list(self.player, self.stairs_layer)
            if ladder_collisions:
                self.player.on_ladder = True

        # Обновление привидений
        for ghost in self.ghosts:
            # Движение и проверка стен
            ghost.center_x += ghost.change_x

            # Проверка столкновения со стенами
            wall_hit = arcade.check_for_collision_with_list(ghost, self.walls_layer)
            if wall_hit:
                # Разворот
                ghost.change_x *= -1
                ghost.direction = "left" if ghost.change_x < 0 else "right"

            # Обновление анимации
            ghost.update_animation()

            # Проверка столкновения с игроком
            if arcade.check_for_collision(ghost, self.player):
                self.player.current_hp -= GHOST_DAMAGE
                if self.player.current_hp <= 0:
                    self.game_state = GAME_OVER

            # Проверка столкновения с факелом
            if self.player.torch_active:
                if arcade.check_for_collision(ghost, self.player.torch_sprite):
                    if ghost.take_damage(TORCH_DAMAGE):
                        ghost.remove_from_sprite_lists()

        # Обновление камеры

        # Проверка переходов между уровнями
        self.check_level_transitions()

        # Проверка смерти игрока
        if self.player.current_hp <= 0:
            self.game_state = GAME_OVER


    def check_level_transitions(self):
        """Проверка переходов между уровнями"""
        # Проверяем позицию игрока в клетках
        player_tile_x = int(self.player.center_x // TILE_SIZE)
        player_tile_y = int(self.player.center_y // TILE_SIZE)

        if self.current_level == 1:
            if player_tile_x == 9 and player_tile_y == 2:
                self.current_level = 2
                self.setup_level(self.current_level)
        elif self.current_level == 2:
            if player_tile_x == 29 and player_tile_y == 2:
                self.current_level = 3
                self.setup_level(self.current_level)
        elif self.current_level == 3:
            if player_tile_x == 2 and player_tile_y == 2:
                self.game_state = GAME_WON

    def on_key_press(self, key, modifiers):
        """Обработка нажатия клавиш"""
        if self.game_state != PLAYING:
            if key == arcade.key.ESCAPE:
                self.setup()
            return

        if key == arcade.key.A or key == arcade.key.LEFT:
            self.player.change_x = -PLAYER_SPEED
        elif key == arcade.key.D or key == arcade.key.RIGHT:
            self.player.change_x = PLAYER_SPEED
        elif (key == arcade.key.W or key == arcade.key.UP) and self.player.on_ladder:
            self.player.change_y = PLAYER_SPEED
        elif (key == arcade.key.S or key == arcade.key.DOWN) and self.player.on_ladder:
            self.player.change_y = -PLAYER_SPEED

    def on_key_release(self, key, modifiers):
        """Обработка отпускания клавиш"""
        if self.game_state != PLAYING:
            return

        if key in (arcade.key.A, arcade.key.D, arcade.key.LEFT, arcade.key.RIGHT):
            self.player.change_x = 0
        elif key in (arcade.key.W, arcade.key.S, arcade.key.UP, arcade.key.DOWN):
            self.player.change_y = 0

    def on_mouse_press(self, x, y, button, modifiers):
        """Обработка нажатия мыши"""
        if self.game_state == MENU:
            button_width = 240
            button_height = 60

            # Проверка нажатия на кнопку "Начать играть"
            button_x1 = (self.width - button_width) // 2
            button_x2 = (self.width + button_width) // 2
            button_y1 = 320
            button_y2 = 320 + button_height

            if button_x1 <= x <= button_x2 and button_y1 <= y <= button_y2:
                self.current_level = 1
                self.setup_level(self.current_level)

        elif self.game_state == PLAYING:
            if button == arcade.MOUSE_BUTTON_RIGHT:
                # Проверка переходов (уже обрабатывается в update)
                pass
            elif button == arcade.MOUSE_BUTTON_LEFT:
                # Активация факела
                self.player.activate_torch()

    def on_mouse_motion(self, x, y, dx, dy):
        """Обработка движения мыши"""
        pass


def main():
    """Главная функция"""
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
