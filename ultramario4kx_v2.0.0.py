#!/usr/bin/env python3
"""
SUPER MARIO 64 DS - XD EDITION
Ultra Mario 4KX v2.0.0
(C) 2025 SAMSOFT

Complete SM64/SM64DS recreation with all levels.
"""

import pygame
import math
import random
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional

# =============================================================================
# CONSTANTS
# =============================================================================

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.5
JUMP_FORCE = 12
PLAYER_SPEED = 5
CAMERA_SMOOTHING = 0.1

# Colors
SKY_BLUE = (135, 206, 235)
GRASS_GREEN = (34, 139, 34)
CASTLE_GRAY = (180, 180, 180)
CASTLE_ROOF_RED = (180, 50, 50)
WATER_BLUE = (64, 164, 223)
LAVA_ORANGE = (255, 100, 0)
SAND_YELLOW = (238, 214, 175)
SNOW_WHITE = (250, 250, 255)
WOOD_BROWN = (139, 90, 43)

# =============================================================================
# GAME STATES
# =============================================================================

class GameState(Enum):
    MAIN_MENU = auto()
    DEAR_MARIO = auto()
    FILE_SELECT = auto()
    CASTLE_GROUNDS = auto()
    CASTLE_INTERIOR = auto()
    PLAYING_LEVEL = auto()
    PAUSED = auto()
    STAR_GET = auto()
    WARNING = auto()

# =============================================================================
# LEVEL DEFINITIONS - ALL SM64/SM64DS COURSES
# =============================================================================

class LevelID(Enum):
    # Main Courses (SM64 Original 15)
    BOB_OMB_BATTLEFIELD = 1
    WHOMPS_FORTRESS = 2
    JOLLY_ROGER_BAY = 3
    COOL_COOL_MOUNTAIN = 4
    BIG_BOOS_HAUNT = 5
    HAZY_MAZE_CAVE = 6
    LETHAL_LAVA_LAND = 7
    SHIFTING_SAND_LAND = 8
    DIRE_DIRE_DOCKS = 9
    SNOWMANS_LAND = 10
    WET_DRY_WORLD = 11
    TALL_TALL_MOUNTAIN = 12
    TINY_HUGE_ISLAND = 13
    TICK_TOCK_CLOCK = 14
    RAINBOW_RIDE = 15
    
    # Bowser Levels
    BOWSER_DARK_WORLD = 16
    BOWSER_FIRE_SEA = 17
    BOWSER_SKY = 18
    
    # Castle Areas
    CASTLE_GROUNDS = 19
    CASTLE_INTERIOR = 20
    CASTLE_COURTYARD = 21
    
    # SM64DS Exclusive
    SUNSHINE_ISLES = 22
    GOOMBOSS_BATTLE = 23
    BIG_BOOS_BALCONY = 24
    CHIEF_CHILLY = 25
    
    # Secret Levels
    PRINCESS_SECRET_SLIDE = 26
    SECRET_AQUARIUM = 27
    WING_MARIO_OVER_RAINBOW = 28
    CAVERN_OF_METAL_CAP = 29
    VANISH_CAP_UNDER_MOAT = 30
    WING_CAP_TOWER = 31

@dataclass
class LevelData:
    """Complete level definition."""
    id: LevelID
    name: str
    stars: int
    required_stars: int
    sky_color: Tuple[int, int, int]
    ground_color: Tuple[int, int, int]
    has_water: bool = False
    has_lava: bool = False
    has_snow: bool = False
    music_id: int = 0
    star_names: List[str] = field(default_factory=list)

# All level definitions
LEVELS: Dict[LevelID, LevelData] = {
    LevelID.BOB_OMB_BATTLEFIELD: LevelData(
        LevelID.BOB_OMB_BATTLEFIELD,
        "Bob-omb Battlefield", 7, 0,
        SKY_BLUE, GRASS_GREEN,
        star_names=["Big Bob-omb on the Summit", "Footrace with Koopa the Quick",
                   "Shoot to the Island in the Sky", "Find the 8 Red Coins",
                   "Mario Wings to the Sky", "Behind Chain Chomp's Gate", "100 Coins"]
    ),
    LevelID.WHOMPS_FORTRESS: LevelData(
        LevelID.WHOMPS_FORTRESS,
        "Whomp's Fortress", 7, 1,
        SKY_BLUE, (160, 140, 120),
        star_names=["Chip Off Whomp's Block", "To the Top of the Fortress",
                   "Shoot into the Wild Blue", "Red Coins on the Floating Isle",
                   "Fall onto the Caged Island", "Blast Away the Wall", "100 Coins"]
    ),
    LevelID.JOLLY_ROGER_BAY: LevelData(
        LevelID.JOLLY_ROGER_BAY,
        "Jolly Roger Bay", 7, 3,
        SKY_BLUE, SAND_YELLOW, has_water=True,
        star_names=["Plunder in the Sunken Ship", "Can the Eel Come Out to Play?",
                   "Treasure of the Ocean Cave", "Red Coins on the Ship Afloat",
                   "Blast to the Stone Pillar", "Through the Jet Stream", "100 Coins"]
    ),
    LevelID.COOL_COOL_MOUNTAIN: LevelData(
        LevelID.COOL_COOL_MOUNTAIN,
        "Cool, Cool Mountain", 7, 3,
        (200, 220, 255), SNOW_WHITE, has_snow=True,
        star_names=["Slip Slidin' Away", "Li'l Penguin Lost",
                   "Big Penguin Race", "Frosty Slide for 8 Red Coins",
                   "Snowman's Lost His Head", "Wall Kicks Will Work", "100 Coins"]
    ),
    LevelID.BIG_BOOS_HAUNT: LevelData(
        LevelID.BIG_BOOS_HAUNT,
        "Big Boo's Haunt", 7, 12,
        (40, 30, 60), (60, 50, 40),
        star_names=["Go on a Ghost Hunt", "Ride Big Boo's Merry-Go-Round",
                   "Secret of the Haunted Books", "Seek the 8 Red Coins",
                   "Big Boo's Balcony", "Eye to Eye in the Secret Room", "100 Coins"]
    ),
    LevelID.HAZY_MAZE_CAVE: LevelData(
        LevelID.HAZY_MAZE_CAVE,
        "Hazy Maze Cave", 7, 8,
        (80, 70, 90), (100, 90, 80), has_water=True,
        star_names=["Swimming Beast in the Cavern", "Elevate for 8 Red Coins",
                   "Metal-Head Mario Can Move!", "Navigating the Toxic Maze",
                   "A-Maze-Ing Emergency Exit", "Watch for Rolling Rocks", "100 Coins"]
    ),
    LevelID.LETHAL_LAVA_LAND: LevelData(
        LevelID.LETHAL_LAVA_LAND,
        "Lethal Lava Land", 7, 8,
        (60, 20, 20), (80, 40, 20), has_lava=True,
        star_names=["Boil the Big Bully", "Bully the Bullies",
                   "8-Coin Puzzle with 15 Pieces", "Red-Hot Log Rolling",
                   "Hot-Foot-It into the Volcano", "Elevator Tour in the Volcano", "100 Coins"]
    ),
    LevelID.SHIFTING_SAND_LAND: LevelData(
        LevelID.SHIFTING_SAND_LAND,
        "Shifting Sand Land", 7, 8,
        (255, 200, 150), SAND_YELLOW,
        star_names=["In the Talons of the Big Bird", "Shining Atop the Pyramid",
                   "Inside the Ancient Pyramid", "Stand Tall on the Four Pillars",
                   "Free Flying for 8 Red Coins", "Pyramid Puzzle", "100 Coins"]
    ),
    LevelID.DIRE_DIRE_DOCKS: LevelData(
        LevelID.DIRE_DIRE_DOCKS,
        "Dire, Dire Docks", 7, 30,
        (20, 40, 80), (40, 60, 100), has_water=True,
        star_names=["Board Bowser's Sub", "Chests in the Current",
                   "Pole-Jumping for Red Coins", "Through the Jet Stream",
                   "The Manta Ray's Reward", "Collect the Caps...", "100 Coins"]
    ),
    LevelID.SNOWMANS_LAND: LevelData(
        LevelID.SNOWMANS_LAND,
        "Snowman's Land", 7, 50,
        (180, 200, 255), SNOW_WHITE, has_snow=True,
        star_names=["Snowman's Big Head", "Chill with the Bully",
                   "In the Deep Freeze", "Whirl from the Freezing Pond",
                   "Shell Shreddin' for Red Coins", "Into the Igloo", "100 Coins"]
    ),
    LevelID.WET_DRY_WORLD: LevelData(
        LevelID.WET_DRY_WORLD,
        "Wet-Dry World", 7, 50,
        SKY_BLUE, (140, 140, 160), has_water=True,
        star_names=["Shocking Arrow Lifts!", "Top o' the Town",
                   "Secrets in the Shallows & Sky", "Express Elevator--Hurry Up!",
                   "Go to Town for Red Coins", "Quick Race Through Downtown!", "100 Coins"]
    ),
    LevelID.TALL_TALL_MOUNTAIN: LevelData(
        LevelID.TALL_TALL_MOUNTAIN,
        "Tall, Tall Mountain", 7, 50,
        SKY_BLUE, (120, 100, 80),
        star_names=["Scale the Mountain", "Mystery of the Monkey Cage",
                   "Scary 'Shrooms, Red Coins", "Mysterious Mountainside",
                   "Breathtaking View from Bridge", "Blast to the Lonely Mushroom", "100 Coins"]
    ),
    LevelID.TINY_HUGE_ISLAND: LevelData(
        LevelID.TINY_HUGE_ISLAND,
        "Tiny-Huge Island", 7, 50,
        SKY_BLUE, GRASS_GREEN, has_water=True,
        star_names=["Pluck the Piranha Flower", "The Tip Top of the Huge Island",
                   "Rematch with Koopa the Quick", "Five Itty Bitty Secrets",
                   "Wiggler's Red Coins", "Make Wiggler Squirm", "100 Coins"]
    ),
    LevelID.TICK_TOCK_CLOCK: LevelData(
        LevelID.TICK_TOCK_CLOCK,
        "Tick Tock Clock", 7, 50,
        (60, 50, 70), (80, 70, 60),
        star_names=["Roll into the Cage", "The Pit and the Pendulums",
                   "Get a Hand", "Stomp on the Thwomp",
                   "Timed Jumps on Moving Bars", "Stop Time for Red Coins", "100 Coins"]
    ),
    LevelID.RAINBOW_RIDE: LevelData(
        LevelID.RAINBOW_RIDE,
        "Rainbow Ride", 7, 50,
        (100, 150, 255), (255, 200, 255),
        star_names=["Cruiser Crossing the Rainbow", "The Big House in the Sky",
                   "Coins Amassed in a Maze", "Swingin' in the Breeze",
                   "Tricky Triangles!", "Somewhere Over the Rainbow", "100 Coins"]
    ),
    LevelID.BOWSER_DARK_WORLD: LevelData(
        LevelID.BOWSER_DARK_WORLD, "Bowser in the Dark World", 1, 8, (20, 10, 30), (40, 30, 50)
    ),
    LevelID.BOWSER_FIRE_SEA: LevelData(
        LevelID.BOWSER_FIRE_SEA, "Bowser in the Fire Sea", 1, 30, (60, 20, 10), (80, 30, 20), has_lava=True
    ),
    LevelID.BOWSER_SKY: LevelData(
        LevelID.BOWSER_SKY, "Bowser in the Sky", 1, 70, (30, 20, 60), (50, 40, 80)
    ),
    LevelID.CASTLE_GROUNDS: LevelData(
        LevelID.CASTLE_GROUNDS, "Castle Grounds", 0, 0, SKY_BLUE, GRASS_GREEN, has_water=True
    ),
    LevelID.CASTLE_INTERIOR: LevelData(
        LevelID.CASTLE_INTERIOR, "Inside the Castle", 0, 0, (180, 160, 140), (160, 140, 120)
    ),
    LevelID.CASTLE_COURTYARD: LevelData(
        LevelID.CASTLE_COURTYARD, "Castle Courtyard", 0, 0, (60, 40, 80), GRASS_GREEN
    ),
    LevelID.SUNSHINE_ISLES: LevelData(
        LevelID.SUNSHINE_ISLES, "Sunshine Isles", 2, 0, SKY_BLUE, SAND_YELLOW, has_water=True
    ),
    LevelID.GOOMBOSS_BATTLE: LevelData(
        LevelID.GOOMBOSS_BATTLE, "Goomboss Battle", 1, 8, (40, 60, 40), (60, 80, 40)
    ),
    LevelID.BIG_BOOS_BALCONY: LevelData(
        LevelID.BIG_BOOS_BALCONY, "Big Boo's Balcony", 1, 12, (30, 20, 50), (50, 40, 60)
    ),
    LevelID.CHIEF_CHILLY: LevelData(
        LevelID.CHIEF_CHILLY, "Chief Chilly Challenge", 1, 50, (200, 220, 255), SNOW_WHITE, has_snow=True
    ),
    LevelID.PRINCESS_SECRET_SLIDE: LevelData(
        LevelID.PRINCESS_SECRET_SLIDE, "The Princess's Secret Slide", 2, 1, (255, 200, 220), (200, 150, 170)
    ),
    LevelID.SECRET_AQUARIUM: LevelData(
        LevelID.SECRET_AQUARIUM, "The Secret Aquarium", 1, 3, (40, 80, 120), (60, 100, 140), has_water=True
    ),
    LevelID.WING_MARIO_OVER_RAINBOW: LevelData(
        LevelID.WING_MARIO_OVER_RAINBOW, "Wing Mario Over the Rainbow", 1, 10, (150, 180, 255), (200, 220, 255)
    ),
    LevelID.CAVERN_OF_METAL_CAP: LevelData(
        LevelID.CAVERN_OF_METAL_CAP, "Cavern of the Metal Cap", 1, 8, (60, 80, 60), (80, 100, 80), has_water=True
    ),
    LevelID.VANISH_CAP_UNDER_MOAT: LevelData(
        LevelID.VANISH_CAP_UNDER_MOAT, "Vanish Cap Under the Moat", 1, 8, (40, 60, 100), (60, 80, 120), has_water=True
    ),
    LevelID.WING_CAP_TOWER: LevelData(
        LevelID.WING_CAP_TOWER, "Tower of the Wing Cap", 1, 10, (255, 200, 200), (200, 150, 150)
    ),
}

# =============================================================================
# 3D MATH
# =============================================================================

@dataclass
class Vector3:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def __add__(self, o): return Vector3(self.x + o.x, self.y + o.y, self.z + o.z)
    def __sub__(self, o): return Vector3(self.x - o.x, self.y - o.y, self.z - o.z)
    def __mul__(self, s): return Vector3(self.x * s, self.y * s, self.z * s)
    def length(self): return math.sqrt(self.x**2 + self.y**2 + self.z**2)

# =============================================================================
# PLAYER CHARACTER
# =============================================================================

class Character(Enum):
    YOSHI = 0
    MARIO = 1
    LUIGI = 2
    WARIO = 3

@dataclass
class Player:
    pos: Vector3 = field(default_factory=lambda: Vector3(0, 0, 0))
    vel: Vector3 = field(default_factory=lambda: Vector3(0, 0, 0))
    character: Character = Character.MARIO
    health: int = 8
    coins: int = 0
    stars: int = 0
    lives: int = 4
    grounded: bool = False
    facing_angle: float = 0.0
    is_jumping: bool = False
    
    def get_color(self) -> Tuple[int, int, int]:
        colors = {
            Character.YOSHI: (80, 200, 80),
            Character.MARIO: (255, 50, 50),
            Character.LUIGI: (50, 200, 50),
            Character.WARIO: (255, 255, 50),
        }
        return colors.get(self.character, (255, 50, 50))

# =============================================================================
# GAME OBJECTS
# =============================================================================

@dataclass
class Platform:
    x: float; y: float; z: float
    width: float; height: float; depth: float
    color: Tuple[int, int, int]

@dataclass
class Coin:
    x: float; y: float; z: float
    collected: bool = False
    is_red: bool = False

@dataclass  
class Star:
    x: float; y: float; z: float
    star_id: int
    collected: bool = False

@dataclass
class Warp:
    x: float; y: float; z: float
    radius: float
    target_level: LevelID
    required_stars: int = 0

# =============================================================================
# LEVEL GEOMETRY GENERATOR
# =============================================================================

class LevelGeometry:
    @staticmethod
    def generate_castle_grounds():
        platforms = [
            Platform(-500, 0, -500, 1000, 20, 1000, GRASS_GREEN),
            Platform(-100, 0, -300, 200, 100, 150, CASTLE_GRAY),
            Platform(-90, 100, -290, 40, 80, 40, CASTLE_GRAY),
            Platform(50, 100, -290, 40, 80, 40, CASTLE_GRAY),
            Platform(-100, 100, -300, 200, 20, 150, CASTLE_ROOF_RED),
            Platform(-40, 0, -150, 80, 10, 100, WOOD_BROWN),
            Platform(-400, 0, 200, 150, 50, 150, (50, 150, 50)),
            Platform(300, 0, 100, 120, 40, 120, (50, 150, 50)),
        ]
        coins = [Coin(-50, 30, 0), Coin(0, 30, 0), Coin(50, 30, 0)]
        warps = [Warp(0, 50, -200, 30, LevelID.CASTLE_INTERIOR, 0)]
        return platforms, coins, warps

    @staticmethod
    def generate_bob_omb_battlefield():
        platforms = [
            Platform(-400, 0, -400, 800, 20, 800, GRASS_GREEN),
            Platform(100, 0, 100, 200, 100, 200, (139, 119, 101)),
            Platform(120, 100, 120, 160, 80, 160, (139, 119, 101)),
            Platform(140, 180, 140, 120, 60, 120, (139, 119, 101)),
            Platform(160, 240, 160, 80, 30, 80, (160, 140, 120)),
            Platform(-100, 30, 50, 100, 10, 30, WOOD_BROWN),
            Platform(-200, 150, -100, 80, 20, 80, GRASS_GREEN),
            Platform(-250, 0, 200, 100, 15, 100, GRASS_GREEN),
        ]
        coins = [Coin(x * 40 - 160, 30, z * 40 - 160) 
                 for x in range(8) for z in range(8) if random.random() > 0.7]
        stars = [Star(180, 290, 180, 1), Star(-200, 180, -100, 3)]
        return platforms, coins, stars

    @staticmethod
    def generate_generic_level(level_data: LevelData):
        platforms = [Platform(-300, 0, -300, 600, 20, 600, level_data.ground_color)]
        if level_data.has_water:
            platforms.append(Platform(-250, -50, -250, 500, 10, 500, WATER_BLUE))
        if level_data.has_lava:
            platforms.append(Platform(-200, -30, -200, 400, 5, 400, LAVA_ORANGE))
        if level_data.has_snow:
            for i in range(5):
                platforms.append(Platform(random.randint(-200, 200), 0, 
                                         random.randint(-200, 200), 60, 30, 60, SNOW_WHITE))
        for _ in range(8):
            platforms.append(Platform(random.randint(-250, 250), 0, random.randint(-250, 250),
                                      50, random.randint(30, 100), 50, level_data.ground_color))
        coins = [Coin(random.randint(-200, 200), 30, random.randint(-200, 200)) for _ in range(20)]
        stars = [Star(random.randint(-150, 150), random.randint(50, 150), 
                      random.randint(-150, 150), i+1) for i in range(min(level_data.stars, 3))]
        return platforms, coins, stars

# =============================================================================
# DEAR MARIO LETTER
# =============================================================================

DEAR_MARIO_LETTER = """
Dear Mario:

Please come to the castle.
I've baked a cake for you.

Yours truly--

Princess Toadstool

                 Peach
"""

# =============================================================================
# MAIN GAME CLASS
# =============================================================================

class SM64DSGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("SUPER MARIO 64 DS - XD EDITION")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.state = GameState.MAIN_MENU
        self.player = Player()
        self.camera_pos = Vector3(0, 100, 200)
        
        self.current_level: Optional[LevelID] = None
        self.platforms: List[Platform] = []
        self.coins: List[Coin] = []
        self.stars: List[Star] = []
        self.warps: List[Warp] = []
        
        self.collected_stars: Dict[LevelID, List[int]] = {level: [] for level in LevelID}
        self.total_stars = 0
        
        self.title_wave = 0.0
        self.letter_scroll = 0.0
        self.letter_done = False
        self.glitch_timer = 0
        self.glitch_color = (255, 0, 0)
        self.glitch_offset = (0, 0)
        
        self.font_title = pygame.font.SysFont('arial', 42, bold=True)
        self.font_large = pygame.font.SysFont('arial', 32, bold=True)
        self.font_medium = pygame.font.SysFont('arial', 24, bold=True)
        self.font_small = pygame.font.SysFont('arial', 16)
        self.font_letter = pygame.font.SysFont('georgia', 22)
        
        self.start_rect = pygame.Rect(0, 0, 0, 0)
        self.exit_rect = pygame.Rect(0, 0, 0, 0)
        
        print("[SM64DS-XD] SAMSOFT Engine Initialized!")
        print(f"[SM64DS-XD] {len(LEVELS)} levels loaded")
    
    def load_level(self, level_id: LevelID):
        self.current_level = level_id
        level_data = LEVELS[level_id]
        
        self.player.pos = Vector3(0, 50, 0)
        self.player.vel = Vector3()
        self.player.grounded = False
        
        if level_id == LevelID.CASTLE_GROUNDS:
            self.platforms, self.coins, self.warps = LevelGeometry.generate_castle_grounds()
            self.stars = []
        elif level_id == LevelID.BOB_OMB_BATTLEFIELD:
            self.platforms, self.coins, self.stars = LevelGeometry.generate_bob_omb_battlefield()
            self.warps = []
        else:
            self.platforms, self.coins, self.stars = LevelGeometry.generate_generic_level(level_data)
            self.warps = []
        
        if level_id in (LevelID.CASTLE_GROUNDS, LevelID.CASTLE_INTERIOR, LevelID.CASTLE_COURTYARD):
            self.state = GameState.CASTLE_GROUNDS
        else:
            self.state = GameState.PLAYING_LEVEL
        
        print(f"[SM64DS-XD] Loaded: {level_data.name}")
    
    def update_player(self, dt: float):
        keys = pygame.key.get_pressed()
        
        move_x, move_z = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]: move_z = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: move_z = 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: move_x = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: move_x = 1
        
        if move_x != 0 and move_z != 0:
            move_x *= 0.707
            move_z *= 0.707
        
        self.player.vel.x = move_x * PLAYER_SPEED
        self.player.vel.z = move_z * PLAYER_SPEED
        
        if move_x != 0 or move_z != 0:
            self.player.facing_angle = math.atan2(move_x, -move_z)
        
        if not self.player.grounded:
            self.player.vel.y -= GRAVITY
        
        self.player.pos.x += self.player.vel.x
        self.player.pos.y += self.player.vel.y
        self.player.pos.z += self.player.vel.z
        
        self.player.grounded = False
        for plat in self.platforms:
            if self.check_platform_collision(plat):
                if self.player.vel.y <= 0:
                    self.player.pos.y = plat.y + plat.height
                    self.player.vel.y = 0
                    self.player.grounded = True
                    self.player.is_jumping = False
        
        for coin in self.coins:
            if not coin.collected:
                dx = self.player.pos.x - coin.x
                dy = self.player.pos.y - coin.y
                dz = self.player.pos.z - coin.z
                if dx*dx + dy*dy + dz*dz < 900:
                    coin.collected = True
                    self.player.coins += 5 if coin.is_red else 1
        
        for star in self.stars:
            if not star.collected and star.star_id not in self.collected_stars.get(self.current_level, []):
                dx = self.player.pos.x - star.x
                dy = self.player.pos.y - star.y
                dz = self.player.pos.z - star.z
                if dx*dx + dy*dy + dz*dz < 1600:
                    star.collected = True
                    self.collected_stars[self.current_level].append(star.star_id)
                    self.total_stars += 1
                    self.player.stars = self.total_stars
                    self.state = GameState.STAR_GET
        
        for warp in self.warps:
            dx = self.player.pos.x - warp.x
            dy = self.player.pos.y - warp.y
            dz = self.player.pos.z - warp.z
            if dx*dx + dy*dy + dz*dz < warp.radius * warp.radius:
                if self.total_stars >= warp.required_stars:
                    self.load_level(warp.target_level)
                    return
        
        if self.player.pos.y < -500:
            self.player.lives -= 1
            self.player.pos = Vector3(0, 50, 0)
            self.player.vel = Vector3()
    
    def check_platform_collision(self, plat: Platform) -> bool:
        px, py, pz = self.player.pos.x, self.player.pos.y, self.player.pos.z
        in_x = plat.x <= px <= plat.x + plat.width
        in_z = plat.z <= pz <= plat.z + plat.depth
        on_top = plat.y <= py <= plat.y + plat.height + 20
        return in_x and in_z and on_top
    
    def update_camera(self):
        target = Vector3(self.player.pos.x, self.player.pos.y + 80, self.player.pos.z + 150)
        self.camera_pos.x += (target.x - self.camera_pos.x) * CAMERA_SMOOTHING
        self.camera_pos.y += (target.y - self.camera_pos.y) * CAMERA_SMOOTHING
        self.camera_pos.z += (target.z - self.camera_pos.z) * CAMERA_SMOOTHING
    
    def project_point(self, x: float, y: float, z: float) -> Optional[Tuple[int, int]]:
        rx = x - self.camera_pos.x
        ry = y - self.camera_pos.y
        rz = z - self.camera_pos.z
        if rz >= -10: return None
        scale = 400 / (-rz)
        sx = int(SCREEN_WIDTH / 2 + rx * scale)
        sy = int(SCREEN_HEIGHT / 2 - ry * scale)
        return (sx, sy)
    
    def render_platform(self, plat: Platform):
        corners = [
            (plat.x, plat.y + plat.height, plat.z),
            (plat.x + plat.width, plat.y + plat.height, plat.z),
            (plat.x + plat.width, plat.y + plat.height, plat.z + plat.depth),
            (plat.x, plat.y + plat.height, plat.z + plat.depth),
        ]
        projected = [self.project_point(*c) for c in corners]
        if all(p is not None for p in projected):
            pygame.draw.polygon(self.screen, plat.color, projected)
            pygame.draw.polygon(self.screen, (0, 0, 0), projected, 2)
    
    def render_player(self):
        pos = self.project_point(self.player.pos.x, self.player.pos.y + 20, self.player.pos.z)
        if pos:
            pygame.draw.circle(self.screen, self.player.get_color(), pos, 20)
            pygame.draw.circle(self.screen, (0, 0, 0), pos, 20, 2)
            head_pos = (pos[0], pos[1] - 25)
            pygame.draw.circle(self.screen, (255, 200, 150), head_pos, 12)
            pygame.draw.circle(self.screen, (0, 0, 0), head_pos, 12, 2)
    
    def render_coin(self, coin: Coin):
        if coin.collected: return
        pos = self.project_point(coin.x, coin.y, coin.z)
        if pos:
            color = (255, 50, 50) if coin.is_red else (255, 215, 0)
            pygame.draw.circle(self.screen, color, pos, 10)
            pygame.draw.circle(self.screen, (200, 170, 0), pos, 10, 2)
    
    def render_star(self, star: Star):
        if star.collected: return
        pos = self.project_point(star.x, star.y, star.z)
        if pos:
            points = []
            for i in range(10):
                angle = i * math.pi / 5 - math.pi / 2
                r = 20 if i % 2 == 0 else 10
                points.append((pos[0] + int(r * math.cos(angle)), pos[1] + int(r * math.sin(angle))))
            pygame.draw.polygon(self.screen, (255, 255, 0), points)
            pygame.draw.polygon(self.screen, (200, 180, 0), points, 2)
    
    def render_level(self):
        level_data = LEVELS.get(self.current_level)
        if not level_data: return
        
        self.screen.fill(level_data.sky_color)
        sorted_platforms = sorted(self.platforms, key=lambda p: -(p.z - self.camera_pos.z))
        for plat in sorted_platforms: self.render_platform(plat)
        for coin in self.coins: self.render_coin(coin)
        for star in self.stars: self.render_star(star)
        self.render_player()
        self.render_hud(level_data)
    
    def render_hud(self, level_data: LevelData):
        star_text = self.font_medium.render(f"★ {self.total_stars}", True, (255, 255, 0))
        self.screen.blit(star_text, (20, 20))
        coin_text = self.font_medium.render(f"● {self.player.coins}", True, (255, 215, 0))
        self.screen.blit(coin_text, (20, 50))
        lives_text = self.font_medium.render(f"× {self.player.lives}", True, (255, 255, 255))
        self.screen.blit(lives_text, (20, 80))
        name_text = self.font_small.render(level_data.name, True, (255, 255, 255))
        self.screen.blit(name_text, (SCREEN_WIDTH - name_text.get_width() - 20, 20))
        hint = self.font_small.render("WASD: Move | SPACE: Jump | 1-9: Levels | ESC: Menu", True, (200, 200, 200))
        self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 30))
    
    def render_main_menu(self):
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            pygame.draw.line(self.screen, (int(100 + 35 * ratio), int(150 + 56 * ratio), int(220 + 30 * ratio)), 
                           (0, y), (SCREEN_WIDTH, y))
        
        self.title_wave += 0.1
        t1_surf = self.font_title.render("SUPER MARIO 64 DS", True, (255, 255, 255))
        t1_shadow = self.font_title.render("SUPER MARIO 64 DS", True, (0, 0, 0))
        t1_x = SCREEN_WIDTH // 2 - t1_surf.get_width() // 2
        t1_y = 60 + math.sin(self.title_wave) * 3
        self.screen.blit(t1_shadow, (t1_x + 3, t1_y + 3))
        self.screen.blit(t1_surf, (t1_x, t1_y))
        
        t2_surf = self.font_large.render("XD EDITION", True, (255, 220, 0))
        self.screen.blit(t2_surf, (SCREEN_WIDTH // 2 - t2_surf.get_width() // 2, 115))
        
        center_y = SCREEN_HEIGHT // 2 - 60
        presents = self.font_large.render("SAMSOFT PRESENTS", True, (255, 255, 255))
        self.screen.blit(presents, (SCREEN_WIDTH // 2 - presents.get_width() // 2, center_y))
        port = self.font_medium.render("(C) 2025 SM64 PY PORT", True, (255, 220, 0))
        self.screen.blit(port, (SCREEN_WIDTH // 2 - port.get_width() // 2, center_y + 40))
        
        btn_y = SCREEN_HEIGHT - 180
        self.start_rect = pygame.Rect(SCREEN_WIDTH // 2 - 110, btn_y, 220, 50)
        self.exit_rect = pygame.Rect(SCREEN_WIDTH // 2 - 110, btn_y + 60, 220, 50)
        mouse_pos = pygame.mouse.get_pos()
        
        for rect, text in [(self.start_rect, "START"), (self.exit_rect, "EXIT")]:
            hover = rect.collidepoint(mouse_pos)
            color = (255, 220, 50) if hover else (255, 200, 0)
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            pygame.draw.rect(self.screen, (180, 140, 0), rect, 3, border_radius=8)
            txt = self.font_medium.render(text, True, (180, 0, 0))
            self.screen.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))
        
        footer = self.font_small.render("(C) 2025 SAMSOFT", True, (255, 255, 255))
        self.screen.blit(footer, (SCREEN_WIDTH // 2 - footer.get_width() // 2, SCREEN_HEIGHT - 25))
    
    def render_dear_mario(self):
        self.screen.fill((245, 235, 220))
        pygame.draw.rect(self.screen, (180, 160, 140), (50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100), 5)
        
        if not self.letter_done:
            self.letter_scroll = min(self.letter_scroll + 2, len(DEAR_MARIO_LETTER))
        
        visible_text = DEAR_MARIO_LETTER[:int(self.letter_scroll)]
        y_offset = 100
        for line in visible_text.split('\n'):
            text_surf = self.font_letter.render(line, True, (60, 40, 20))
            self.screen.blit(text_surf, (100, y_offset))
            y_offset += 35
        
        if self.letter_scroll >= len(DEAR_MARIO_LETTER):
            self.letter_done = True
            hint = self.font_small.render("Press SPACE or ENTER to continue...", True, (100, 80, 60))
            self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 80))
    
    def render_star_get(self):
        self.screen.fill((0, 0, 0))
        center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
        points = []
        for i in range(10):
            angle = i * math.pi / 5 - math.pi / 2
            r = 80 if i % 2 == 0 else 40
            points.append((center[0] + int(r * math.cos(angle)), center[1] + int(r * math.sin(angle))))
        pygame.draw.polygon(self.screen, (255, 255, 0), points)
        
        text = self.font_title.render("GOT A STAR!", True, (255, 255, 255))
        self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 + 60))
        count = self.font_large.render(f"Total Stars: {self.total_stars}", True, (255, 220, 0))
        self.screen.blit(count, (SCREEN_WIDTH // 2 - count.get_width() // 2, SCREEN_HEIGHT // 2 + 110))
        hint = self.font_small.render("Press any key to continue...", True, (180, 180, 180))
        self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 50))
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state in (GameState.PLAYING_LEVEL, GameState.CASTLE_GROUNDS, 
                                     GameState.WARNING, GameState.DEAR_MARIO):
                        self.state = GameState.MAIN_MENU
                    elif self.state == GameState.MAIN_MENU:
                        self.running = False
                elif event.key == pygame.K_SPACE:
                    if self.state == GameState.DEAR_MARIO and self.letter_done:
                        self.load_level(LevelID.CASTLE_GROUNDS)
                    elif self.state in (GameState.PLAYING_LEVEL, GameState.CASTLE_GROUNDS):
                        if self.player.grounded:
                            self.player.vel.y = JUMP_FORCE
                            self.player.grounded = False
                            self.player.is_jumping = True
                elif event.key == pygame.K_RETURN:
                    if self.state == GameState.DEAR_MARIO and self.letter_done:
                        self.load_level(LevelID.CASTLE_GROUNDS)
                    elif self.state == GameState.STAR_GET:
                        self.state = GameState.PLAYING_LEVEL
                elif self.state == GameState.STAR_GET:
                    self.state = GameState.PLAYING_LEVEL
                elif self.state in (GameState.CASTLE_GROUNDS, GameState.PLAYING_LEVEL):
                    level_keys = {
                        pygame.K_1: LevelID.BOB_OMB_BATTLEFIELD,
                        pygame.K_2: LevelID.WHOMPS_FORTRESS,
                        pygame.K_3: LevelID.JOLLY_ROGER_BAY,
                        pygame.K_4: LevelID.COOL_COOL_MOUNTAIN,
                        pygame.K_5: LevelID.BIG_BOOS_HAUNT,
                        pygame.K_6: LevelID.HAZY_MAZE_CAVE,
                        pygame.K_7: LevelID.LETHAL_LAVA_LAND,
                        pygame.K_8: LevelID.SHIFTING_SAND_LAND,
                        pygame.K_9: LevelID.DIRE_DIRE_DOCKS,
                        pygame.K_0: LevelID.CASTLE_GROUNDS,
                    }
                    if event.key in level_keys:
                        self.load_level(level_keys[event.key])
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if self.state == GameState.MAIN_MENU:
                    if self.start_rect.collidepoint(mouse_pos):
                        self.letter_scroll = 0
                        self.letter_done = False
                        self.state = GameState.DEAR_MARIO
                    elif self.exit_rect.collidepoint(mouse_pos):
                        self.running = False
    
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            
            if self.state in (GameState.PLAYING_LEVEL, GameState.CASTLE_GROUNDS):
                self.update_player(dt)
                self.update_camera()
            
            if self.state == GameState.MAIN_MENU:
                self.render_main_menu()
            elif self.state == GameState.DEAR_MARIO:
                self.render_dear_mario()
            elif self.state in (GameState.PLAYING_LEVEL, GameState.CASTLE_GROUNDS):
                self.render_level()
            elif self.state == GameState.STAR_GET:
                self.render_star_get()
            
            pygame.display.flip()
        
        pygame.quit()

# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  SUPER MARIO 64 DS - XD EDITION")
    print("  Ultra Mario 4KX v2.0.0")
    print("  (C) 2025 SAMSOFT")
    print("=" * 60)
    print(f"\n  LEVELS: {len(LEVELS)} total")
    print("    - 15 Main Courses")
    print("    - 3 Bowser Stages")
    print("    - 6 Secret Levels")
    print("    - 4 SM64DS Exclusive")
    print("    - 3 Castle Areas")
    print("\n  CONTROLS:")
    print("    WASD/Arrows - Move")
    print("    SPACE - Jump")
    print("    1-9 - Quick Level Select")
    print("    0 - Castle Grounds")
    print("    ESC - Menu/Quit\n")
    
    game = SM64DSGame()
    game.run()
