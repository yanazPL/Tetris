import pygame
import random


class Tile:
    """Represents one tile of brick"""
    def __init__(self, position, kind, is_brick_tile=False):
        """
        Attributes
        ----------
        position : tuple(int, int)
            Represents position of a tile
        kind :
            Represents kind of brick which  tile belongs/belonged to.
        is_brick_tile : bool
            True for tiles belonging to active brick.
            False for others.
        """
        self.is_brick_tile = is_brick_tile
        self.position = position
        self.kind = kind

    def __str__(self):
        return f"{self.position}: {self.kind}"

    def __eq__(self, other):
        if isinstance(other, Tile):
            return (
                self.is_brick_tile == other.is_brick_tile and
                self.position == other.position and
                self.kind == other.kind
            )
        return False


class Brick:
    """Represents active brick which player can control"""
    tile_vectors = {
        'O':
        {
            "up": ((0, 0), (1, 1), (0, 1), (1, 0)),
            "right": ((0, 0), (1, 1), (0, 1), (1, 0)),
            "down": ((0, 0), (1, 1), (0, 1), (1, 0)),
            "left": ((0, 0), (1, 1), (0, 1), (1, 0))
        },
        'I':
        {
            "up": ((-1, 1), (0, 1), (1, 1), (2, 1)),
            "right": ((1, -1), (1, 0), (1, 1), (1, 2)),
            "down": ((-1, 0), (0, 0), (1, 0), (2, 0)),
            "left": ((0, -1), (0, 0), (0, 1), (0, 2))
        }
    }
    spawn_pos = {
        'O': (0, 5),
        'I': (4, 0)
    }
    spawn_orientation = {
        'O': "down",
        'I': "down"
    }

    def __init__(self, state, position, kind, orientation):
        self.state = state
        self.kind = kind
        self.tiles = []
        self.move_or_rotate(position, orientation)

    def move(self, position):
        """Moves the brick"""
        self.move_or_rotate(position, self.orientation)

    def move_or_rotate(self, position, orientation):

        for tile in self.tiles:
            for vector in Brick.tile_vectors[self.kind][orientation]:
                if (
                    position[0] + vector[0] < 0 or
                    position[0] + vector[0] >= GameState.WORLD_WIDTH or
                    position[1] + vector[1] < 0 or
                    position[1] + vector[1] >= GameState.WORLD_HEIGHT or
                    self.state.tile_exists(
                        (position[0] + vector[0], position[1] + vector[1])
                    )
                ):
                    return

        self.orientation = orientation
        self.position = position

        while self.tiles:
            self.state.tiles.remove(self.tiles.pop())
        for vector in Brick.tile_vectors[self.kind][orientation]:
            tile = Tile(
                    (position[0] + vector[0], position[1] + vector[1]),
                    self.kind,
                    True
                )
            self.state.tiles.append(tile)
            self.tiles.append(tile)

    def rotate(self, direction):
        # orientation_order = ["up", "right", "down", "left"]
        if direction == "right":
            if self.orientation == "up":
                new_orientation = "right"
            elif self.orientation == "right":
                new_orientation = "down"
            elif self.orientation == "down":
                new_orientation = "left"
            elif self.orientation == "left":
                new_orientation = "up"
        elif direction == "left":
            if self.orientation == "left":
                new_orientation = "down"
            elif self.orientation == "down":
                new_orientation = "right"
            elif self.orientation == "right":
                new_orientation = "up"
            elif self.orientation == "up":
                new_orientation = "left"
        self.move_or_rotate(self.position, new_orientation)

    def touches_ground(self):
        """Checks whether brick is touching last row of world"""
        for tile in self.tiles:
            print(tile, end=" ")
            if tile.position[1] >= GameState.WORLD_HEIGHT - 1:
                return True
        return False

    def touches_tile(self):
        """Checks if brick touches any non-brick tile"""
        for state_tile in self.state.tiles:
            for brick_tile in self.tiles:
                if (
                    not state_tile.is_brick_tile and
                    brick_tile.position[0] == state_tile.position[0] and
                    brick_tile.position[1] == state_tile.position[1] - 1
                ):
                    return True
        return False

    def freeze(self):
        """Ends control of player over the bricks"""
        for brick_tile in self.tiles[:]:
            print(brick_tile, end=" ")
            idx = self.state.tiles.index(brick_tile)
            self.tiles.remove(brick_tile)
            self.state.tiles[idx].is_brick_tile = False


class GameState:
    WORLD_WIDTH = 10
    WORLD_HEIGHT = 40

    def __init__(self):
        self.tiles = []
        self.brick = Brick(self, (0, 0), 'O', "down")
        self.epoch = 1

    def tile_exists(self, position):
        for tile in self.tiles:
            if tile.position == position and not tile.is_brick_tile:
                return True
        return False

    def move_bricks_down(self):
        epoch_dividor = 20
        brick = self.brick

        if self.epoch >= epoch_dividor:
            brick.move(
                (brick.position[0], brick.position[1] + 1)
            )
            self.epoch = 0
        self.epoch += 1

    def hard_drop(self):
        brick = self.brick
        while not (brick.touches_ground() or brick.touches_tile()):
            brick.move(
                (brick.position[0], brick.position[1] + 1)
            )

    def respawn(self):
        print("before respawn: ", end=" ")
        for tile in self.brick.tiles:
            print(tile, sep=" ", end="")

        brick_kind = random.choice(
            list(Brick.tile_vectors.keys())
        )
        self.brick.kind = brick_kind
        self.brick.move_or_rotate(
            Brick.spawn_pos[brick_kind],
            Brick.spawn_orientation[brick_kind]
        )

    def update(self):
        """Non player controlled after-move actions are here"""
        if (self.brick.touches_ground() or
                self.brick.touches_tile()):
            self.brick.freeze()
            self.respawn()
        else:
            self.move_bricks_down()
            # check lines


class UserInterface():
    """Bridges user actions and game state. Uses pyGame"""
    FPS = 60
    CELL_SIZE = 20

    def __init__(self):

        pygame.init()

        # Game state
        self.game_state = GameState()

        # Window
        WINDOW_WIDTH = self.CELL_SIZE * self.game_state.WORLD_WIDTH
        WINDOW_HEIGHT = self.CELL_SIZE * self.game_state.WORLD_HEIGHT
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Tetris")
        # pygame.display.set_icon(pygame.image.load("icon.png"))
        # Loop properties
        self.clock = pygame.time.Clock()
        self.running = True

    def process_input(self):
        events = pygame.event.get()

        brick = self.game_state.brick

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                brick.move(
                    (brick.position[0] - 1, brick.position[1])
                )
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                brick.move(
                    (brick.position[0] + 1, brick.position[1])
                )
            if (event.type == pygame.KEYDOWN and
                    (event.key == pygame.K_x or event.key == pygame.K_UP)):
                brick.rotate("right")
                pygame.key.set_repeat(100)
            if (event.type == pygame.KEYDOWN and
                    (event.key == pygame.K_RCTRL or event.key == pygame.K_z)):
                brick.rotate("left")
                pygame.key.set_repeat(100)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.game_state.hard_drop()

    def update(self):
        self.game_state.update()

    def draw(self):
        """Draws tiles with approperiate colors"""
        color = {'0': (255, 255, 255), 'O': (255, 255, 0), 'I': (0, 128, 128)}
        self.window.fill((255, 255, 255))
        for tile in self.game_state.tiles:
            rect = pygame.Rect(
                tile.position[0] * self.CELL_SIZE,
                tile.position[1] * self.CELL_SIZE,
                self.CELL_SIZE,
                self.CELL_SIZE
            )
            pygame.draw.rect(self.window, color[tile.kind], rect)
        pygame.display.update()

    def run(self):
        """Runs the game loop"""
        while self.running:
            self.process_input()
            self.update()
            self.draw()
            self.clock.tick(UserInterface.FPS)


UserInterface().run()
