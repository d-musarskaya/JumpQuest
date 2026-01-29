import arcade
import random
import math
import sqlite3

# Константы
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 670
SCREEN_TITLE = "JumpQuest"

TILE_SIZE = 32
PLAYER_SIZE = 96
GHOST_SIZE = 32
LADDER_SPEED = 1

PLAYER_SPEED = 1
GHOST_SPEED = 1

PLAYER_MAX_HP = 200
GHOST_MAX_HP = 50

# Состояния игры
MENU = 0
PLAYING = 1
GAME_OVER = 2
GAME_WON = 3
SETTINGS = 4


class Player(arcade.Sprite):
    """Управляемый персонаж"""

    def __init__(self, x, y, character_num=1, scale=0.1):
        self.character_num = character_num
        char_path = f"static/img/characters/char{character_num}/pose_01.png"
        super().__init__(char_path, scale=scale)

        self.center_x = x
        self.center_y = y
        self.max_hp = PLAYER_MAX_HP
        self.current_hp = PLAYER_MAX_HP
        self.direction = "right"
        self.on_ladder = False
        self.climbing = False
        self.last_attack_time = 0
        self.attack_cooldown = 1.0  # 1 секунда перезарядки

        # Флаги для удержания клавиш
        self.move_up_pressed = False
        self.move_down_pressed = False
        self.move_left_pressed = False
        self.move_right_pressed = False

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
        self.walk_frame_speed = 5

    def update_animation(self, delta_time):
        self.walk_frame_delay += 1
        if self.walk_frame_delay >= self.walk_frame_speed:
            self.walk_frame_delay = 0
            if self.change_x != 0 and not self.climbing:
                self.current_walk_frame = (self.current_walk_frame + 1) % 3
                if self.change_x > 0:
                    self.texture = self.walk_textures[3 + self.current_walk_frame]
                    self.direction = "right"
                else:
                    self.texture = self.walk_textures[self.current_walk_frame]
                    self.direction = "left"
            elif self.climbing and (self.change_y != 0 or self.move_up_pressed or self.move_down_pressed):
                self.current_walk_frame = (self.current_walk_frame + 1) % 3
                self.texture = self.ladder_textures[self.current_walk_frame]
            elif self.climbing:
                self.texture = self.ladder_textures[1]

    def update_movement(self):
        """Обновление движения на основе нажатых клавиш"""
        # Горизонтальное движение
        self.change_x = 0
        if self.move_left_pressed and not self.move_right_pressed:
            self.change_x = -PLAYER_SPEED
        elif self.move_right_pressed and not self.move_left_pressed:
            self.change_x = PLAYER_SPEED

        # Вертикальное движение на лестнице
        if self.on_ladder:
            self.change_y = 0
            if self.move_up_pressed and not self.move_down_pressed:
                self.change_y = LADDER_SPEED
            elif self.move_down_pressed and not self.move_up_pressed:
                self.change_y = -LADDER_SPEED

    def can_attack(self, current_time):
        """Проверка возможности атаки (перезарядка)"""
        return current_time - self.last_attack_time >= self.attack_cooldown

    def attack(self, ghost, current_time):
        """Атака привидения"""
        if self.can_attack(current_time):
            ghost.current_hp -= 50
            self.last_attack_time = current_time
            return True
        return False


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
        self.damage_timer = 0
        self.damage_cooldown = 1.0  # 1 секунда между уроном игроку

        self.last_move_time = 0
        self.stuck_timer = 0
        self.last_x_position = x
        self.initial_y = y

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

    def is_in_attack_range(self, player, radius=96):
        """Проверка, находится ли игрок в радиусе атаки"""
        distance = math.sqrt((self.center_x - player.center_x) ** 2 + (self.center_y - player.center_y) ** 2)
        return distance <= radius

    def damage_player(self, player, current_time):
        """Нанесение урона игроку"""
        if current_time - self.damage_timer >= self.damage_cooldown:
            player.current_hp -= 10
            self.damage_timer = current_time
            return True
        return False


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        self.world_camera = arcade.camera.Camera2D()
        self.camera_zoom = 1.0

        # Громкость (0.0 — тишина, 1.0 — максимум)
        self.music_volume = 0.5
        self.sfx_volume = 0.7

        self.jump_sound = arcade.load_sound("static/sounds/jump_sound.mp3")
        self.throw_sound = arcade.load_sound("static/sounds/throw_sound.mp3")
        self.walk_sound = arcade.load_sound("static/sounds/walking_sound.mp3")
        self.music_sound = arcade.load_sound("static/sounds/music_sound.mp3")

        self.music_player = None

        self.game_state = MENU
        self.current_level = 1
        self.max_levels = 3

        self.scene = None
        self.player = None
        self.ghosts = None
        self.physics_engine = None

        self.background_layer = None
        self.walls_layer = None
        self.decor_layer = None
        self.stairs_layer = None
        self.tile_map = None

        self.total_time = 0.0
        self.health_bar_width = 200
        self.health_bar_height = 20

        # Для обработки кликов мыши
        self.mouse_x = 0
        self.mouse_y = 0

        self.high_score = 0

    def setup_level(self, level_num):
        map_path = f"static/maps/map_{level_num}.tmx"
        self.tile_map = arcade.load_tilemap(map_path)

        self.scene = arcade.Scene()

        self.background_layer = self.tile_map.sprite_lists.get("background", [])
        self.walls_layer = self.tile_map.sprite_lists.get("walls", [])
        self.decor_layer = self.tile_map.sprite_lists.get("decor", [])
        self.stairs_layer = self.tile_map.sprite_lists.get("stairs", [])

        if self.background_layer:
            self.scene.add_sprite_list("background", sprite_list=self.background_layer)
        if self.walls_layer:
            self.scene.add_sprite_list("walls", sprite_list=self.walls_layer)
        if self.decor_layer:
            self.scene.add_sprite_list("decor", sprite_list=self.decor_layer)
        if self.stairs_layer:
            self.scene.add_sprite_list("stairs", sprite_list=self.stairs_layer)

        # Выбор персонажа в зависимости от уровня
        character_num = 1
        if level_num == 2:
            character_num = 2
        elif level_num == 3:
            character_num = 3

        start_x = TILE_SIZE * 1 + TILE_SIZE // 2
        start_y = TILE_SIZE * 17 + TILE_SIZE // 2
        self.player = Player(start_x, start_y, character_num=character_num, scale=0.1)
        self.player.current_hp = 200 if level_num == 1 else self.player.current_hp

        self.torch_sprite = arcade.Sprite()
        self.torch_textures = []
        for i in range(1, 7):
            # Загружаем все 6 поз
            tex = arcade.load_texture(f"static/img/torch/torch_pose_0{i}.png")
            self.torch_textures.append(tex)

        # Устанавливаем начальные значения (динамические свойства)
        self.torch_sprite.texture = self.torch_textures[0]
        self.torch_sprite.scale = 0.05
        self.torch_sprite.current_frame = 0
        self.torch_sprite.frame_timer = 0

        self.scene.add_sprite("Torch", self.torch_sprite)

        if level_num == 1:
            initial_hp = 200
        else:
            initial_hp = self.player.current_hp

        self.player = Player(start_x, start_y, character_num=character_num, scale=0.1)
        self.player.current_hp = initial_hp
        self.player.max_hp = 200

        self.scene.add_sprite("player", self.player)

        self.ghosts = arcade.SpriteList()
        self.scene.add_sprite_list("ghosts")

        if self.walls_layer:
            spawn_levels = [2, 6, 10, 14, 18]

            for level_y in spawn_levels:
                y_pos = level_y * TILE_SIZE
                for _ in range(5):
                    min_x = TILE_SIZE * 2
                    max_x = (self.tile_map.width - 2) * TILE_SIZE
                    x_pos = random.randint(min_x, max_x)

                    ghost = Ghost(x_pos, y_pos, scale=0.1)
                    self.ghosts.append(ghost)
                    self.scene.add_sprite("ghosts", ghost)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player,
            self.walls_layer,
            gravity_constant=0.5
        )

        self.flying_torches = arcade.SpriteList()
        self.scene.add_sprite_list("flying_torches", sprite_list=self.flying_torches)

        self.is_holding_torch = False
        self.game_state = PLAYING

        # Создаем камеру 2D
        self.world_camera = arcade.camera.Camera2D()

        self.camera_zoom = 1.0

    def setup(self):
        self.game_state = MENU

    def on_draw(self):
        self.clear()

        if self.game_state == MENU:
            self.draw_menu()
        elif self.game_state == SETTINGS:
            self.draw_settings()
        elif self.game_state == PLAYING:
            self.world_camera.use()
            self.draw_game()
            self.draw_ui()
        elif self.game_state == GAME_WON:
            self.draw_game_won()
        elif self.game_state == GAME_OVER:
            self.draw_game_over()

    def draw_menu(self):
        button_width = 240
        button_height = 60

        arcade.draw_lrbt_rectangle_filled(left=0, right=self.width, top=self.height, bottom=0, color=arcade.color.WHITE)

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

    def draw_volume_bar(self, start_x, y_bottom, volume):
        bar_width = 30
        bar_height = 20
        padding = 5
        for i in range(10):
            color = (0, 122, 204) if i < volume * 10 else (60, 60, 60)
            arcade.draw_lrbt_rectangle_filled(
                left=start_x + i * (bar_width + padding),
                right=start_x + i * (bar_width + padding) + bar_width,
                bottom=y_bottom,
                top=y_bottom + bar_height,
                color=color
            )

    def draw_settings(self):
        arcade.draw_lrbt_rectangle_filled(0, self.width, 0, self.height, (30, 35, 40))
        arcade.draw_text("НАСТРОЙКИ", self.width / 2, 550, arcade.color.WHITE, 30, anchor_x="center")

        music_x = self.width / 2 - 170
        music_y = 390
        arcade.draw_text("Музыка", music_x, music_y + 30, arcade.color.WHITE, 16)

        # Кружок "-" слева
        arcade.draw_circle_outline(music_x - 30, music_y + 10, 15, arcade.color.WHITE, 2)
        arcade.draw_text("-", music_x - 30, music_y + 10, arcade.color.WHITE, 20, anchor_x="center", anchor_y="center")

        # Сама шкала
        self.draw_volume_bar(music_x, music_y, self.music_volume)

        # Кружок "+" справа
        arcade.draw_circle_outline(music_x + 380, music_y + 10, 15, arcade.color.WHITE, 2)
        arcade.draw_text("+", music_x + 380, music_y + 10, arcade.color.WHITE, 20, anchor_x="center", anchor_y="center")

        sfx_y = 290
        arcade.draw_text("Эффекты", music_x, sfx_y + 30, arcade.color.WHITE, 16)

        # Кружок "-"
        arcade.draw_circle_outline(music_x - 30, sfx_y + 10, 15, arcade.color.WHITE, 2)
        arcade.draw_text("-", music_x - 30, sfx_y + 10, arcade.color.WHITE, 20, anchor_x="center", anchor_y="center")

        self.draw_volume_bar(music_x, sfx_y, self.sfx_volume)

        # Кружок "+"
        arcade.draw_circle_outline(music_x + 380, sfx_y + 10, 15, arcade.color.WHITE, 2)
        arcade.draw_text("+", music_x + 380, sfx_y + 10, arcade.color.WHITE, 20, anchor_x="center", anchor_y="center")

        arcade.draw_text("ESC - Назад", self.width / 2, 100, arcade.color.GOLD, 16, anchor_x="center")


    def draw_game(self):
        self.scene.draw()

    def draw_ui(self):
        # Полоска здоровья
        health_bar_x = self.width // 2
        health_bar_y = self.height - 30

        # Вычисляем координаты для черного фона
        left = health_bar_x - self.health_bar_width // 2
        right = health_bar_x + self.health_bar_width // 2
        bottom = health_bar_y - self.health_bar_height // 2
        top = health_bar_y + self.health_bar_height // 2

        # Черный фон
        arcade.draw_lrbt_rectangle_filled(
            left=left,
            right=right,
            bottom=bottom,
            top=top,
            color=arcade.color.BLACK
        )

        # Красная полоска здоровья
        health_percentage = max(0, self.player.current_hp) / self.player.max_hp
        if health_percentage > 0:
            fill_width = max(0, (self.health_bar_width - 4) * health_percentage)
            fill_left = left + 2
            fill_right = fill_left + fill_width

            arcade.draw_lrbt_rectangle_filled(
                left=fill_left,
                right=fill_right,
                bottom=bottom + 2,
                top=top - 2,
                color=arcade.color.RED
            )

        arcade.draw_text(
            f"Уровень: {self.current_level}",
            10,
            self.height - 40,
            arcade.color.BLACK,
            font_size=16
        )

        arcade.draw_text(
            f"HP: {max(0, int(self.player.current_hp))}/{self.player.max_hp}",
            health_bar_x,
            self.height - 15,
            arcade.color.WHITE,
            font_size=14,
            anchor_x="center"
        )

    def draw_game_won(self):
        arcade.draw_lrbt_rectangle_filled(0, self.width, 0, self.height, arcade.color.BLACK)

        arcade.draw_text("МОЛОДЕЦ! ТЫ ВЫИГРАЛ!",
                         self.width // 2,
                         self.height // 2 + 100,
                         arcade.color.GOLD,
                         40,
                         anchor_x="center",
                         anchor_y="center")

        current_hp = int(max(0, self.player.current_hp))
        arcade.draw_text(f"ОСТАЛОСЬ HP: {current_hp}/600",
                         self.width // 2,
                         self.height // 2,
                         arcade.color.GREEN,
                         30,
                         anchor_x="center",
                         anchor_y="center")

        arcade.draw_text(f"РЕКОРД (ЛУЧШИЙ): {self.high_score}/600",
                         self.width // 2,
                         self.height // 2 - 60,
                         arcade.color.CYAN,
                         24,
                         anchor_x="center",
                         anchor_y="center")

        arcade.draw_text("Нажмите ESC для выхода в меню",
                         self.width // 2,
                         self.height // 2 - 140,
                         arcade.color.WHITE,
                         16,
                         anchor_x="center",
                                anchor_y="center")

    def draw_game_over(self):
        arcade.draw_lrbt_rectangle_filled(
            left=0,
            right=self.width,
            bottom=0,
            top=self.height,
            color=arcade.color.BLACK
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
        if self.game_state != PLAYING:
            return

        self.total_time += delta_time

        # Проверка здоровья игрока
        if self.player.current_hp <= 0:
            self.game_state = GAME_OVER
            return

        # Обновляем движение на основе нажатых клавиш
        self.player.update_movement()

        # Проверка нахождения на лестнице
        self.player.on_ladder = False
        if self.stairs_layer:
            ladder_collisions = arcade.check_for_collision_with_list(self.player, self.stairs_layer)
            if ladder_collisions:
                self.player.on_ladder = True

        # Если на лестнице, используем другую логику движения
        if self.player.on_ladder:
            self.player.climbing = True

            # Сохраняем текущую позицию X для горизонтального движения
            old_x = self.player.center_x
            old_y = self.player.center_y

            # Применяем горизонтальное движение
            self.player.center_x += self.player.change_x

            # Применяем вертикальное движение для лестницы
            self.player.center_y += self.player.change_y

            # Проверяем столкновения со стенами при движении по горизонтали
            wall_hit_x = arcade.check_for_collision_with_list(self.player, self.walls_layer)
            if wall_hit_x:
                # Отменяем горизонтальное движение при столкновении со стеной
                self.player.center_x = old_x

            # Проверяем, остались ли мы на лестнице после движения
            if not self.player.on_ladder:
                # Если спустились с лестницы, делаем небольшую корректировку
                self.player.center_y = old_y - 5

            # Отключаем гравитацию на лестнице
            self.physics_engine.gravity_constant = 0
            self.player.change_y = 0  # Отключаем гравитационное падение
        else:
            self.player.climbing = False
            self.physics_engine.gravity_constant = 0.5

            # Обычное обновление физики
            self.physics_engine.update()

        # Обновление анимации игрока
        self.player.update_animation(delta_time)

        # Смещение по умолчанию (в пикселях от центра героя)
        offset_x = -1
        offset_y = -5  # Путь будет чуть ниже плеча, ну, по вкусу подкрутишь

        if self.player.on_ladder:
            # На лестнице всегда чуть в стороне
            offset_x = 12 if self.player.change_y < 0 else -12
        elif self.player.change_x > 0:
            # Идем вправо
            offset_x = -12
        elif self.player.change_x < 0:
            # Идем влево
            offset_x = 12
        else:
            # ПЕРСОНАЖ СТОИТ: смотрим на его направление (direction)
            # Если direction == "right", факел пусть будет слева (-12), и наоборот
            if self.player.direction == "right":
                offset_x = -12
            else:
                offset_x = 12

        is_moving = self.player.move_left_pressed or self.player.move_right_pressed

        if is_moving or self.is_holding_torch:
            if self.camera_zoom < 1.5:
                self.camera_zoom += 0.02
        else:
            if self.camera_zoom > 1.0:
                self.camera_zoom -= 0.02

        self.torch_sprite.frame_timer += 1
        if self.torch_sprite.frame_timer >= 6:
            self.torch_sprite.frame_timer = 0
            self.torch_sprite.current_frame = (self.torch_sprite.current_frame + 1) % 6
            self.torch_sprite.texture = self.torch_textures[self.torch_sprite.current_frame]

        if self.is_holding_torch:
            self.torch_sprite.scale = 0.08
            self.torch_sprite.center_x = (self.player.center_x + offset_x + self.mouse_x) / 2
            self.torch_sprite.center_y = (self.player.center_y + offset_y + self.mouse_y) / 2
        else:
            self.torch_sprite.scale = 0.05
            self.torch_sprite.center_x = self.player.center_x + offset_x
            self.torch_sprite.center_y = self.player.center_y + offset_y


        self.world_camera.zoom = self.camera_zoom

        if is_moving or self.is_holding_torch:
            self.world_camera.position = (self.player.center_x, self.player.center_y)
        else:
            target_center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            cur_x, cur_y = self.world_camera.position
            new_x = arcade.math.lerp(cur_x, target_center[0], 0.05)
            new_y = arcade.math.lerp(cur_y, target_center[1], 0.05)
            self.world_camera.position = (new_x, new_y)

        self.flying_torches.update()

        self.flying_torches.update()

        for flying_torch in self.flying_torches:
            hit_list = arcade.check_for_collision_with_list(flying_torch, self.ghosts)
            if hit_list:
                for ghost in hit_list:
                    ghost.current_hp -= 50
                    flying_torch.remove_from_sprite_lists()
                    break

            if flying_torch.center_x < -100 or flying_torch.center_x > SCREEN_WIDTH + 100:
                flying_torch.remove_from_sprite_lists()



        # Обновление привидений и проверка столкновений с игроком
        dead_ghosts = []
        for ghost in self.ghosts:
            ghost.center_x += ghost.change_x
            wall_hit = arcade.check_for_collision_with_list(ghost, self.walls_layer)
            if wall_hit:
                ghost.change_x *= -1
                ghost.direction = "left" if ghost.change_x < 0 else "right"

            # Проверка столкновения с игроком
            if arcade.check_for_collision(ghost, self.player):
                ghost.damage_player(self.player, self.total_time)

            # Проверка здоровья привидения
            if ghost.current_hp <= 0:
                dead_ghosts.append(ghost)

            ghost.update_animation()

        # Удаление мертвых привидений
        for ghost in dead_ghosts:
            ghost.remove_from_sprite_lists()

        # Проверка переходов между уровнями
        self.check_level_transitions()

    def check_level_transitions(self):
        player_tile_x = int(self.player.center_x // TILE_SIZE)
        player_tile_y = int(self.player.center_y // TILE_SIZE)

        if self.current_level == 1:
            if player_tile_x == 9 and player_tile_y == 1:
                self.current_level = 2
                self.setup_level(self.current_level)
        elif self.current_level == 2:
            if player_tile_x == 28 and player_tile_y == 1:
                self.current_level = 3
                self.setup_level(self.current_level)
        elif self.current_level == 3:
            if player_tile_x == 2 and player_tile_y == 1:
                # --- ДОБАВЛЯЕМ СОХРАНЕНИЕ ---
                final_hp = int(self.player.current_hp)
                db = sqlite3.connect("JumpQuest.db")
                res = db.execute("SELECT score FROM record").fetchone()
                old_record = res[0] if res else 0

                if final_hp > old_record:
                    db.execute(f"UPDATE record SET score = {final_hp}")
                    db.commit()
                    self.high_score = final_hp
                else:
                    self.high_score = old_record
                db.close()
                self.game_state = GAME_WON

    def on_key_press(self, key, modifiers):
        if self.game_state != PLAYING:
            if key == arcade.key.ESCAPE:
                self.setup()
            return

        # Устанавливаем флаги нажатия клавиш
        if key == arcade.key.A or key == arcade.key.LEFT:
            self.player.move_left_pressed = True
        elif key == arcade.key.D or key == arcade.key.RIGHT:
            self.player.move_right_pressed = True
        elif key == arcade.key.W or key == arcade.key.UP:
            self.player.move_up_pressed = True
        elif key == arcade.key.S or key == arcade.key.DOWN:
            self.player.move_down_pressed = True

    def on_key_release(self, key, modifiers):
        if self.game_state != PLAYING:
            return

        # Сбрасываем флаги нажатия клавиш
        if key == arcade.key.A or key == arcade.key.LEFT:
            self.player.move_left_pressed = False
        elif key == arcade.key.D or key == arcade.key.RIGHT:
            self.player.move_right_pressed = False
        elif key == arcade.key.W or key == arcade.key.UP:
            self.player.move_up_pressed = False
        elif key == arcade.key.S or key == arcade.key.DOWN:
            self.player.move_down_pressed = False

    def on_mouse_press(self, x, y, button, modifiers):
        if self.game_state == MENU:
            button_width = 240
            button_height = 60
            button_x1 = (self.width - button_width) // 2
            button_x2 = (self.width + button_width) // 2

            # Координаты кнопки "Начать играть"
            button_y1 = 320
            button_y2 = 320 + button_height

            # Координаты кнопки "Настройки"
            settings_y1 = 230
            settings_y2 = 230 + button_height

            if button_x1 <= x <= button_x2 and button_y1 <= y <= button_y2:
                self.current_level = 1
                self.setup_level(self.current_level)

                # ЗАПУСК МУЗЫКИ
                if not self.music_player:
                    self.music_player = arcade.play_sound(self.music_sound, self.music_volume, loop=True)

                self.game_state = PLAYING

            # 2. Проверка нажатия "Настройки"
            elif button_x1 <= x <= button_x2 and settings_y1 <= y <= settings_y2:
                self.game_state = SETTINGS

        elif self.game_state == PLAYING:
            # Обновляем координаты мыши для прицеливания факелом
            self.mouse_x = x
            self.mouse_y = y

            if button == arcade.MOUSE_BUTTON_LEFT:
                self.is_holding_torch = True

                start_x = self.player.center_x
                start_y = self.player.center_y
                dest_x = x + self.world_camera.position[0] - self.width / 2
                dest_y = y + self.world_camera.position[1] - self.height / 2

                # Звук броска/захвата
                arcade.play_sound(self.throw_sound, self.sfx_volume)


        elif self.game_state == SETTINGS:

            music_x = self.width / 2 - 170
            # Кнопка МИНУС
            if arcade.math.get_distance(x, y, music_x - 30, 390 + 10) < 15:

                self.music_volume = max(0.0, self.music_volume - 0.1)

                if self.music_player:
                    self.music_player.volume = self.music_volume
            # Кнопка ПЛЮС
            if arcade.math.get_distance(x, y, music_x + 380, 390 + 10) < 15:

                self.music_volume = min(1.0, self.music_volume + 0.1)

                if self.music_player:
                    self.music_player.volume = self.music_volume

            if arcade.math.get_distance(x, y, music_x - 30, 290 + 10) < 15:
                self.sfx_volume = max(0.0, self.sfx_volume - 0.1)


            if arcade.math.get_distance(x, y, music_x + 380, 290 + 10) < 15:
                self.sfx_volume = min(1.0, self.sfx_volume + 0.1)

            if 50 <= y <= 150 and self.width / 2 - 100 <= x <= self.width / 2 + 100:
                self.game_state = MENU

    def on_mouse_release(self, x, y, button, modifiers):
        # Если мы отпускаем кнопку мыши и до этого держали факел
        if self.game_state == PLAYING and button == arcade.MOUSE_BUTTON_LEFT:
            if self.is_holding_torch:
                # полет
                new_torch = FlyingTorch(
                    self.torch_sprite.center_x,
                    self.torch_sprite.center_y,
                    x, y,
                    scale=0.05
                )
                self.flying_torches.append(new_torch)

                # больше не держим факел
                self.is_holding_torch = False

    def on_mouse_motion(self, x, y, dx, dy):
        # Сохраняем позицию мыши
        self.mouse_x = x
        self.mouse_y = y

    def handle_mouse_attack(self, mouse_x, mouse_y):
        """Обработка атаки мышью"""
        for ghost in self.ghosts:
            # Проверяем, находится ли привидение в радиусе атаки
            if ghost.is_in_attack_range(self.player):
                # Проверяем, кликнули ли по привидению
                ghost_left = ghost.center_x - ghost.width / 2
                ghost_right = ghost.center_x + ghost.width / 2
                ghost_bottom = ghost.center_y - ghost.height / 2
                ghost_top = ghost.center_y + ghost.height / 2

                if (ghost_left <= mouse_x <= ghost_right and
                        ghost_bottom <= mouse_y <= ghost_top):
                    # Атакуем привидение
                    self.player.attack(ghost, self.total_time)
                    break


class FlyingTorch(arcade.Sprite):
    def __init__(self, x, y, target_x, target_y, scale=0.05):
        # та же картинка, что и у обычного факела
        super().__init__("static/img/torch/torch_pose_01.png", scale=scale)
        self.center_x = x
        self.center_y = y

        dest_x = target_x - x
        dest_y = target_y - y
        angle = math.atan2(dest_y, dest_x)

        speed = 12
        self.change_x = math.cos(angle) * speed
        self.change_y = math.sin(angle) * speed
        self.angle = math.degrees(angle) - 90

    def update(self, delta_time: float = 1/60):
        self.center_x += self.change_x
        self.center_y += self.change_y


def main():
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()