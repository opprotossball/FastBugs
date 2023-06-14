import math
import os

import numpy as np
import pygame
from Backend.board import valid_tile
from info import resources

from Backend.Bug import decode_bug


def join_path(path):
    return os.path.join(os.path.dirname(__file__), path)


class GameScene:
    def __init__(self):
        self.backgroundColor = 80, 80, 80
        self.tileColor = 153, 153, 153
        self.resourcesColor = 29, 122, 29
        self.hatcheryColor = 150, 45, 45
        self.highlightedColor = 81, 210, 252
        self.selectedColor = 255, 225, 64
        self.attacked_color = 150, 45, 45

        self.TILE_RADIUS = 58
        self.TILE_MARGIN = 4
        self.X_BOARD_CENTER = 759
        self.Y_BOARD_CENTER = 450

        self.side_colors = [(255, 255, 255), (0, 0, 0)]

        self.phase_titles = [
            "White's combat phase",
            "White's move phase",
            "White's hatch phase",
            "Black's combat phase",
            "Black's move phase",
            "Black's hatch phase"
        ]
        self.bug_names = [
            "Grasshopper",
            "Ant",
            "Spider",
            "Beetle"
        ]

        self.font40 = pygame.font.Font(join_path("Assets/Fonts/ANTQUAB.TTF"), 40)
        self.font35 = pygame.font.Font(join_path("Assets/Fonts/ANTQUAB.TTF"), 35)
        self.font30 = pygame.font.Font(join_path("Assets/Fonts/ANTQUAB.TTF"), 30)

        self.tiltAngle = math.pi / 2

        self.cos30 = math.cos(math.pi / 6)
        self.sin30 = math.sin(math.pi / 6)
        self.cos60 = math.cos(math.pi / 3)
        self.sin60 = math.sin(math.pi / 3)
        self.tileButtons = []
        self.highlightedTiles = []

        self.main_surface = None
        self.window_scale = None

        beetle_white = pygame.transform.flip(pygame.image.load(join_path("Assets/Bugs/BeetleWhite.png")), True,
                                                 False)
        beetle_black = pygame.image.load(join_path("Assets/Bugs/BeetleBlack.png"))
        spider_white = pygame.transform.flip(pygame.image.load(join_path("Assets/Bugs/SpiderWhite.png")), True,
                                                 False)
        spider_black = pygame.image.load(join_path("Assets/Bugs/SpiderBlack.png"))
        ant_white = pygame.transform.flip(pygame.image.load(join_path("Assets/Bugs/AntWhite.png")), True, False)
        ant_black = pygame.image.load(join_path("Assets/Bugs/AntBlack.png"))
        grasshooper_white = pygame.transform.flip(pygame.image.load(join_path("Assets/Bugs/GrasshooperWhite.png")),
                                                      True, False)
        grasshooper_black = pygame.image.load(join_path("Assets/Bugs/GrasshooperBlack.png"))

        self.bug_images = [
            [grasshooper_white, ant_white, spider_white, beetle_white],
            [grasshooper_black, ant_black, spider_black, beetle_black]
        ]

    def show(self, game_state, surface, window_scale):
        active_side = game_state.active_side()
        color = self.side_colors[active_side]
        self.main_surface = surface
        self.window_scale = window_scale
        surface.fill(self.backgroundColor)
        self.show_phase_title(self.phase_titles[game_state.phase], color)
        self.show_number_of_bugs_available(game_state.players_bugs[active_side], color)
        self.show_number_of_resources(game_state.active_player_resources, color)
        self.draw_board(game_state)

    def draw_hex(self, x_center, y_center, radius, color):
        vertices = []
        for i in range(6):
            x = x_center + radius * math.cos(self.tiltAngle + math.pi * 2 * i / 6)
            y = y_center + radius * math.sin(self.tiltAngle + math.pi * 2 * i / 6)
            vertices.append([int(x), int(y)])
        return pygame.draw.polygon(self.main_surface, color, vertices)

    def transform_to_real_coordinates(self, x, y):
        x -= 4
        y -= 4
        x = int(self.X_BOARD_CENTER + (self.TILE_RADIUS + self.TILE_MARGIN) * self.cos30 * (-2*x - y))
        y = int(self.Y_BOARD_CENTER + (self.TILE_RADIUS + self.TILE_MARGIN) * -y * (self.sin30 + 1))
        return x, y

    def draw_bug(self, bug_code):
        bug = decode_bug(bug_code)
        x, y = self.transform_to_real_coordinates(bug.get_x(), bug.get_y())
        image = self.bug_images[bug.get_side()][bug.get_type()]
        self.main_surface.blit(image, (int(x - image.get_width() / 2), int(y - image.get_height() / 2)))

    def show_phase_title(self, phase_title, color):
        title = self.font40.render(phase_title, True, color)
        self.main_surface.blit(title, (int(1310 - title.get_width() / 2), int(75 - title.get_height() / 2)))

    def show_number_of_bugs_available(self, bugs_available, color):
        x = 170
        y = 310
        for count in bugs_available:
            text = self.font40.render(f"x{count}", True, color)
            self.main_surface.blit(text, (x, y))
            y += 144

    def show_number_of_resources(self, number_of_resources, color):
        x = 85
        y = 80
        text = self.font40.render("{}".format(number_of_resources), True, color)
        self.draw_hex(x, y, 55, self.resourcesColor)
        self.main_surface.blit(text, (int(x - text.get_width() / 2), int(y - text.get_height() / 2)))

    def show_tip(self, message, color):
        self.write_multiline_text_30(message, color, 1314, 700)

    def write_multiline_text_30(self, message, color, x, y, space_height_ratio=1.3, align=False, title=False):
        if message is None:
            return
        lines = message.split("\n")
        if title:
            text = self.font35.render(lines[0], True, color)
            self.main_surface.blit(text, (int(x - text.get_width() / 2), int(y - text.get_height() / 2)))
            y += int(text.get_height() * space_height_ratio)
            del lines[0]
        if align:
            text = self.font30.render(lines[0], True, color)
            x = int(x - text.get_width() / 2)
            self.main_surface.blit(text, (x, int(y - text.get_height() / 2)))
            y += int(text.get_height() * space_height_ratio)
            for line in lines[1:]:
                text = self.font30.render(line, True, color)
                self.main_surface.blit(text, (x, int(y - text.get_height() / 2)))
                y += int(text.get_height() * space_height_ratio)
        else:
            for line in lines:
                text = self.font30.render(line, True, color)
                self.main_surface.blit(text, (int(x - text.get_width() / 2), int(y - text.get_height() / 2)))
                y += int(text.get_height() * space_height_ratio)

    def draw_board(self, board_state):
        for (x, y), bug_code in np.ndenumerate(board_state.board):
            if not valid_tile(x, y):
                continue
            color = self.tileColor
            if (x, y) in resources:
                color = self.resourcesColor
            x, y = self.transform_to_real_coordinates(x, y)
            self.draw_hex(x, y, self.TILE_RADIUS, color)
            if bug_code != 0:
                self.draw_bug(bug_code)
