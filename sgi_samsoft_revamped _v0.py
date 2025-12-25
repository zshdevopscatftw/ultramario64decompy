# ============================================================
# The SGI Samsoft REVAMPED Revival Project 0.2
# B3313-Style DEBUG MENU + MS-DOS BOOT + FULL IMPLEMENTATION
# Single file • pygame only • no assets
# ============================================================

import pygame
import math
import random
import time
from enum import Enum

# ---------------- VECTOR ----------------
class Vector3:
    def __init__(self, x=0, y=0, z=0):
        self.x, self.y, self.z = float(x), float(y), float(z)
    
    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar):
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)

# ---------------- STATES ----------------
class State(Enum):
    DEBUG_MENU = 1
    LOADING = 2
    GAME = 3
    EMPTY_MAP = 4
    CAMERA_TEST = 5
    AI_TEST = 6

# ---------------- PLAYER ----------------
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.width = 32
        self.height = 48
        self.on_ground = False
        self.facing_right = True
        self.state = "idle"
        self.anim_frame = 0
        self.anim_timer = 0
        self.coins = 0
        self.stars = 0
        self.health = 8
        self.max_health = 8
        self.lives = 4
        self.jump_held = False
        self.run_timer = 0
        
    def update(self, platforms, keys):
        # Horizontal movement
        accel = 0.5
        max_speed = 6
        friction = 0.85
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx -= accel
            self.facing_right = False
            self.run_timer += 1
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx += accel
            self.facing_right = True
            self.run_timer += 1
        else:
            self.vx *= friction
            self.run_timer = 0
            
        self.vx = max(-max_speed, min(max_speed, self.vx))
        
        # Jump
        if (keys[pygame.K_SPACE] or keys[pygame.K_z]) and self.on_ground and not self.jump_held:
            self.vy = -14
            self.on_ground = False
            self.jump_held = True
        
        if not (keys[pygame.K_SPACE] or keys[pygame.K_z]):
            self.jump_held = False
            
        # Variable jump height
        if not self.on_ground and self.vy < -4 and not (keys[pygame.K_SPACE] or keys[pygame.K_z]):
            self.vy = -4
            
        # Gravity
        self.vy += 0.6
        self.vy = min(self.vy, 12)
        
        # Move X
        self.x += self.vx
        self.resolve_collision_x(platforms)
        
        # Move Y
        self.y += self.vy
        self.on_ground = False
        self.resolve_collision_y(platforms)
        
        # Animation state
        if not self.on_ground:
            self.state = "jump"
        elif abs(self.vx) > 0.5:
            self.state = "run"
        else:
            self.state = "idle"
            
        # Animation frame
        self.anim_timer += 1
        if self.anim_timer > 6:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % 4
            
    def resolve_collision_x(self, platforms):
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        for plat in platforms:
            if rect.colliderect(plat):
                if self.vx > 0:
                    self.x = plat.left - self.width
                elif self.vx < 0:
                    self.x = plat.right
                self.vx = 0
                
    def resolve_collision_y(self, platforms):
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        for plat in platforms:
            if rect.colliderect(plat):
                if self.vy > 0:
                    self.y = plat.top - self.height
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0:
                    self.y = plat.bottom
                    self.vy = 0
                    
    def draw(self, screen, camera_x=0, camera_y=0):
        x = self.x - camera_x
        y = self.y - camera_y
        
        # Shadow
        pygame.draw.ellipse(screen, (0, 0, 0, 80), (x - 4, y + self.height - 8, self.width + 8, 12))
        
        # Body (blue overalls)
        body_rect = pygame.Rect(x + 4, y + 20, self.width - 8, self.height - 24)
        pygame.draw.rect(screen, (30, 60, 200), body_rect)
        
        # Shirt (red)
        pygame.draw.rect(screen, (220, 30, 30), (x + 6, y + 16, self.width - 12, 14))
        
        # Head (skin)
        head_x = x + self.width // 2
        pygame.draw.circle(screen, (255, 200, 160), (int(head_x), int(y + 10)), 14)
        
        # Hat (red)
        hat_points = [(head_x - 16, y + 8), (head_x + 16, y + 8), 
                      (head_x + 12, y - 8), (head_x - 12, y - 8)]
        pygame.draw.polygon(screen, (220, 30, 30), hat_points)
        pygame.draw.circle(screen, (255, 255, 255), (int(head_x), int(y - 2)), 6)
        
        # Eyes
        eye_offset = 3 if self.facing_right else -3
        pygame.draw.circle(screen, (0, 0, 0), (int(head_x + eye_offset - 4), int(y + 8)), 2)
        pygame.draw.circle(screen, (0, 0, 0), (int(head_x + eye_offset + 4), int(y + 8)), 2)
        
        # Mustache
        pygame.draw.ellipse(screen, (60, 30, 10), (head_x - 8, y + 10, 16, 6))
        
        # Feet animation
        foot_offset = math.sin(self.anim_frame * 1.5) * 4 if self.state == "run" else 0
        pygame.draw.ellipse(screen, (90, 50, 20), (x + 2, y + self.height - 10 + foot_offset, 12, 10))
        pygame.draw.ellipse(screen, (90, 50, 20), (x + self.width - 14, y + self.height - 10 - foot_offset, 12, 10))

# ---------------- COIN ----------------
class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.collected = False
        self.anim = 0
        
    def update(self):
        self.anim += 0.15
        
    def draw(self, screen, camera_x=0, camera_y=0):
        if self.collected:
            return
        x = self.x - camera_x
        y = self.y - camera_y + math.sin(self.anim) * 3
        
        # Coin with shine
        width = abs(math.sin(self.anim * 2)) * 16 + 4
        pygame.draw.ellipse(screen, (255, 200, 0), (x + 10 - width/2, y, width, 20))
        pygame.draw.ellipse(screen, (255, 255, 100), (x + 10 - width/4, y + 4, width/2, 8))

# ---------------- STAR ----------------
class Star:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.collected = False
        self.anim = 0
        self.sparkles = []
        
    def update(self):
        self.anim += 0.1
        if random.random() < 0.1:
            self.sparkles.append([self.x + random.randint(-20, 20), 
                                  self.y + random.randint(-20, 20), 10])
        self.sparkles = [[s[0], s[1], s[2] - 0.5] for s in self.sparkles if s[2] > 0]
        
    def draw(self, screen, camera_x=0, camera_y=0):
        if self.collected:
            return
        x = self.x - camera_x
        y = self.y - camera_y + math.sin(self.anim * 2) * 5
        
        # Sparkles
        for s in self.sparkles:
            alpha = int(s[2] * 25)
            pygame.draw.circle(screen, (255, 255, min(255, 100 + alpha)), 
                             (int(s[0] - camera_x), int(s[1] - camera_y)), int(s[2]/3))
        
        # Star shape
        points = []
        for i in range(5):
            angle = math.radians(i * 72 - 90 + math.sin(self.anim) * 10)
            points.append((x + math.cos(angle) * 24, y + math.sin(angle) * 24))
            angle2 = math.radians(i * 72 - 90 + 36 + math.sin(self.anim) * 10)
            points.append((x + math.cos(angle2) * 10, y + math.sin(angle2) * 10))
        
        pygame.draw.polygon(screen, (255, 220, 0), points)
        pygame.draw.polygon(screen, (255, 255, 150), points, 2)
        
        # Eyes
        pygame.draw.circle(screen, (0, 0, 0), (int(x - 6), int(y - 2)), 3)
        pygame.draw.circle(screen, (0, 0, 0), (int(x + 6), int(y - 2)), 3)

# ---------------- HUD ----------------
class HUD:
    def __init__(self):
        self.coin_anim = 0
        self.star_anim = 0
        self.show_debug = False
        
    def draw(self, screen, player, fps, show_debug_info=False):
        self.coin_anim += 0.1
        self.star_anim += 0.05
        
        # Health pie (SM64 style)
        self.draw_health_pie(screen, 60, 60, player.health, player.max_health)
        
        # Lives
        self.draw_lives(screen, 20, 110, player.lives)
        
        # Coins
        self.draw_coins(screen, 640, 30, player.coins)
        
        # Stars
        self.draw_stars(screen, 640, 70, player.stars)
        
        # Course name
        font = pygame.font.SysFont("arial", 20, bold=True)
        course = font.render("TEST STAGE 1-1", True, (255, 255, 255))
        shadow = font.render("TEST STAGE 1-1", True, (0, 0, 0))
        screen.blit(shadow, (screen.get_width()//2 - course.get_width()//2 + 2, 12))
        screen.blit(course, (screen.get_width()//2 - course.get_width()//2, 10))
        
        # Debug overlay
        if show_debug_info:
            self.draw_debug_overlay(screen, player, fps)
            
    def draw_health_pie(self, screen, x, y, health, max_health):
        # Background circle
        pygame.draw.circle(screen, (40, 40, 80), (x, y), 35)
        pygame.draw.circle(screen, (60, 60, 120), (x, y), 32)
        
        # Health wedges
        for i in range(max_health):
            angle_start = math.radians(-90 + i * (360 / max_health))
            angle_end = math.radians(-90 + (i + 1) * (360 / max_health) - 5)
            
            if i < health:
                color = (50, 200, 50) if health > 2 else (200, 200, 50) if health > 1 else (200, 50, 50)
            else:
                color = (80, 80, 80)
                
            # Draw wedge
            points = [(x, y)]
            for a in range(int(math.degrees(angle_start)), int(math.degrees(angle_end)) + 1, 5):
                rad = math.radians(a)
                points.append((x + math.cos(rad) * 28, y + math.sin(rad) * 28))
            if len(points) > 2:
                pygame.draw.polygon(screen, color, points)
                
        # Center icon (Mario head silhouette)
        pygame.draw.circle(screen, (255, 200, 160), (x, y), 12)
        pygame.draw.rect(screen, (220, 30, 30), (x - 10, y - 14, 20, 8))
        
    def draw_lives(self, screen, x, y, lives):
        font = pygame.font.SysFont("arial", 18, bold=True)
        
        # Mini Mario icon
        pygame.draw.circle(screen, (255, 200, 160), (x + 12, y + 10), 10)
        pygame.draw.rect(screen, (220, 30, 30), (x + 4, y - 2, 16, 6))
        
        # X and count
        text = font.render(f"x {lives}", True, (255, 255, 255))
        shadow = font.render(f"x {lives}", True, (0, 0, 0))
        screen.blit(shadow, (x + 28, y + 2))
        screen.blit(text, (x + 26, y))
        
    def draw_coins(self, screen, x, y, coins):
        font = pygame.font.SysFont("arial", 22, bold=True)
        
        # Animated coin icon
        width = abs(math.sin(self.coin_anim)) * 16 + 4
        pygame.draw.ellipse(screen, (255, 200, 0), (x - width/2, y - 2, width, 24))
        
        # Count
        text = font.render(f"x {coins:03d}", True, (255, 255, 255))
        shadow = font.render(f"x {coins:03d}", True, (0, 0, 0))
        screen.blit(shadow, (x + 18, y + 2))
        screen.blit(text, (x + 16, y))
        
    def draw_stars(self, screen, x, y, stars):
        font = pygame.font.SysFont("arial", 22, bold=True)
        
        # Star icon
        star_x, star_y = x, y + 10
        points = []
        for i in range(5):
            angle = math.radians(i * 72 - 90 + math.sin(self.star_anim) * 5)
            points.append((star_x + math.cos(angle) * 12, star_y + math.sin(angle) * 12))
            angle2 = math.radians(i * 72 - 90 + 36)
            points.append((star_x + math.cos(angle2) * 5, star_y + math.sin(angle2) * 5))
        pygame.draw.polygon(screen, (255, 220, 0), points)
        
        # Count
        text = font.render(f"x {stars}", True, (255, 255, 255))
        shadow = font.render(f"x {stars}", True, (0, 0, 0))
        screen.blit(shadow, (x + 18, y + 2))
        screen.blit(text, (x + 16, y))
        
    def draw_debug_overlay(self, screen, player, fps):
        font = pygame.font.SysFont("couriernew", 14)
        
        # Dark background panel
        panel = pygame.Surface((200, 180), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 180))
        screen.blit(panel, (10, 140))
        
        lines = [
            f"FPS: {fps:.1f}",
            f"POS: ({player.x:.1f}, {player.y:.1f})",
            f"VEL: ({player.vx:.2f}, {player.vy:.2f})",
            f"STATE: {player.state}",
            f"ON_GROUND: {player.on_ground}",
            f"HEALTH: {player.health}/{player.max_health}",
            f"COINS: {player.coins}",
            f"STARS: {player.stars}",
        ]
        
        y = 145
        for line in lines:
            text = font.render(line, True, (0, 255, 0))
            screen.blit(text, (15, y))
            y += 20

# ---------------- AI TEST SYSTEM ----------------
class AITestSystem:
    def __init__(self):
        self.messages = [
            "INITIALIZING PERSONALIZATION MATRIX...",
            "SCANNING PLAYER BEHAVIOR PATTERNS...",
            "LOADING NEURAL PATHWAY SIMULATORS...",
            "CALIBRATING EMOTIONAL RESPONSE UNITS...",
            "WARNING: ANOMALY DETECTED IN SECTOR 7G",
            "ADJUSTING DIFFICULTY PARAMETERS...",
            "PLAYER PROFILE: UNKNOWN",
            "RECOMMENDATION: OBSERVE AND ADAPT",
            "AI STATUS: WATCHING",
            "DO NOT LOOK BEHIND YOU",
            "JUST KIDDING :)",
            "SYSTEM NOMINAL"
        ]
        self.current_msg = 0
        self.timer = 0
        self.glitch_timer = 0
        self.display_text = ""
        self.char_index = 0
        self.log = []
        self.scan_line = 0
        
    def update(self):
        self.timer += 1
        self.glitch_timer += 1
        self.scan_line = (self.scan_line + 2) % 600
        
        # Typewriter effect
        if self.current_msg < len(self.messages):
            if self.timer % 3 == 0 and self.char_index < len(self.messages[self.current_msg]):
                self.display_text += self.messages[self.current_msg][self.char_index]
                self.char_index += 1
            elif self.char_index >= len(self.messages[self.current_msg]):
                if self.timer % 60 == 0:
                    self.log.append(self.display_text)
                    if len(self.log) > 8:
                        self.log.pop(0)
                    self.current_msg += 1
                    self.display_text = ""
                    self.char_index = 0
                    
    def draw(self, screen):
        # CRT-style background
        screen.fill((0, 10, 0))
        
        # Scan lines
        for y in range(0, 600, 4):
            alpha = 30 if y % 8 == 0 else 15
            pygame.draw.line(screen, (0, alpha, 0), (0, y), (800, y))
            
        # Moving scan bar
        pygame.draw.rect(screen, (0, 60, 0), (0, self.scan_line, 800, 3))
        
        font_title = pygame.font.SysFont("couriernew", 28, bold=True)
        font = pygame.font.SysFont("couriernew", 18)
        
        # Title with glitch
        title = "PERSONALIZATION AI v2.3.1"
        if self.glitch_timer % 120 < 5:
            title = "".join([c if random.random() > 0.3 else chr(random.randint(33, 126)) for c in title])
        
        title_surf = font_title.render(title, True, (0, 255, 0))
        screen.blit(title_surf, (40, 40))
        
        # Separator
        pygame.draw.line(screen, (0, 150, 0), (40, 80), (760, 80), 2)
        
        # Log history
        y = 100
        for log_line in self.log:
            color = (0, 180, 0) if "WARNING" not in log_line else (255, 150, 0)
            text = font.render(f"> {log_line}", True, color)
            screen.blit(text, (40, y))
            y += 26
            
        # Current typing line with cursor blink
        cursor = "_" if self.timer % 30 < 15 else " "
        current = font.render(f"> {self.display_text}{cursor}", True, (0, 255, 0))
        screen.blit(current, (40, y))
        
        # Status panel
        pygame.draw.rect(screen, (0, 40, 0), (550, 400, 220, 150))
        pygame.draw.rect(screen, (0, 100, 0), (550, 400, 220, 150), 2)
        
        status_lines = [
            "STATUS PANEL",
            "------------",
            f"CPU: {random.randint(45, 55)}%",
            f"MEM: {random.randint(2048, 3072)}MB",
            f"NET: ISOLATED",
            f"THREATS: 0"
        ]
        
        sy = 410
        for sl in status_lines:
            st = font.render(sl, True, (0, 200, 0))
            screen.blit(st, (560, sy))
            sy += 22
            
        # Footer
        hint = font.render("ESC: RETURN TO DEBUG MENU", True, (0, 120, 0))
        screen.blit(hint, (40, 560))

# ---------------- CAMERA TEST ----------------
class CameraTest:
    def __init__(self):
        self.cam_x = 400
        self.cam_y = 300
        self.cam_z = 100
        self.cam_angle = 0
        self.target_x = 400
        self.target_y = 300
        self.mode = 0
        self.modes = ["FREE", "ORBIT", "FOLLOW", "FIXED"]
        self.orbit_angle = 0
        
    def update(self, keys):
        speed = 5
        
        if self.mode == 0:  # Free cam
            if keys[pygame.K_LEFT]: self.cam_x -= speed
            if keys[pygame.K_RIGHT]: self.cam_x += speed
            if keys[pygame.K_UP]: self.cam_y -= speed
            if keys[pygame.K_DOWN]: self.cam_y += speed
            if keys[pygame.K_q]: self.cam_z -= speed
            if keys[pygame.K_e]: self.cam_z += speed
            
        elif self.mode == 1:  # Orbit
            self.orbit_angle += 0.02
            self.cam_x = self.target_x + math.cos(self.orbit_angle) * 200
            self.cam_y = self.target_y + math.sin(self.orbit_angle) * 100
            
        elif self.mode == 2:  # Follow (lerp to target)
            self.cam_x += (self.target_x - self.cam_x) * 0.05
            self.cam_y += (self.target_y - self.cam_y) * 0.05
            
    def draw(self, screen):
        screen.fill((20, 20, 40))
        
        # Grid floor
        for x in range(0, 800, 50):
            intensity = 100 - abs(x - self.cam_x) // 10
            intensity = max(30, min(100, intensity))
            pygame.draw.line(screen, (intensity, intensity, intensity + 20), (x, 200), (x, 500))
        for y in range(200, 500, 30):
            intensity = 100 - abs(y - 350) // 5
            intensity = max(30, min(100, intensity))
            pygame.draw.line(screen, (intensity, intensity, intensity + 20), (0, y), (800, y))
            
        # 3D reference objects
        objects = [
            (400, 350, (255, 0, 0)),
            (300, 320, (0, 255, 0)),
            (500, 380, (0, 0, 255)),
            (350, 400, (255, 255, 0)),
        ]
        
        for obj in objects:
            # Simple size based on "distance"
            dist = math.sqrt((obj[0] - self.cam_x)**2 + (obj[1] - self.cam_y)**2)
            size = max(10, 50 - dist // 20)
            
            # Draw cube-ish shape
            ox = obj[0] - (self.cam_x - 400) * 0.3
            oy = obj[1] - (self.cam_y - 300) * 0.3
            
            pygame.draw.rect(screen, obj[2], (ox - size//2, oy - size//2, size, size))
            # Fake 3D edge
            pygame.draw.polygon(screen, tuple(c//2 for c in obj[2]), [
                (ox + size//2, oy - size//2),
                (ox + size//2 + 10, oy - size//2 - 10),
                (ox + size//2 + 10, oy + size//2 - 10),
                (ox + size//2, oy + size//2)
            ])
            
        # Crosshair at center
        pygame.draw.line(screen, (255, 255, 255), (395, 300), (405, 300), 2)
        pygame.draw.line(screen, (255, 255, 255), (400, 295), (400, 305), 2)
        
        # Camera info HUD
        font = pygame.font.SysFont("couriernew", 20)
        
        # Panel background
        pygame.draw.rect(screen, (0, 0, 0, 180), (20, 20, 250, 160))
        pygame.draw.rect(screen, (100, 100, 150), (20, 20, 250, 160), 2)
        
        info = [
            f"CAMERA TEST v1.0",
            f"MODE: {self.modes[self.mode]}",
            f"POS: ({self.cam_x:.0f}, {self.cam_y:.0f}, {self.cam_z:.0f})",
            f"ZOOM: {self.cam_z}%",
            "",
            "TAB: CYCLE MODE"
        ]
        
        y = 30
        for line in info:
            color = (0, 255, 0) if "MODE:" in line else (255, 255, 255)
            text = font.render(line, True, color)
            screen.blit(text, (30, y))
            y += 24
            
        # Controls
        ctrl_font = pygame.font.SysFont("couriernew", 16)
        controls = ctrl_font.render("ARROWS: MOVE | Q/E: ZOOM | ESC: EXIT", True, (150, 150, 150))
        screen.blit(controls, (200, 570))

# ---------------- MAIN GAME ----------------
class SGISamsoftRevamped:
    def __init__(self):
        pygame.init()
        self.w, self.h = 800, 600
        self.screen = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption("SGI Samsoft REVAMPED Revival Project 0.2")
        self.clock = pygame.time.Clock()
        self.running = True
        self.fps = 60

        self.state = State.DEBUG_MENU

        self.font = pygame.font.SysFont("couriernew", 24)
        self.font_small = pygame.font.SysFont("couriernew", 18)

        self.menu_items = [
            "TEST STAGE",
            "PERSONALIZATION AI TEST",
            "EMPTY MAP",
            "CAMERA TEST",
            "RETURN"
        ]
        self.menu_index = 0

        # Loading sequence
        self.loading_lines = [
            "[BOOTING SGI SAMSOFT KERNEL........OK]",
            "[LOADING AI........................OK]",
            "[LOADING BIOS N64DD................OK]",
            "[INITIALIZING RENDERER.............OK]",
            "[MOUNTING VIRTUAL CARTRIDGE........OK]",
            "[READY]",
        ]
        self.loading_index = 0
        self.loading_timer = 0
        self.loading_target = None
        
        # Game objects
        self.player = None
        self.platforms = []
        self.coins = []
        self.stars = []
        self.hud = HUD()
        self.camera_x = 0
        self.camera_y = 0
        self.level_width = 2400
        self.level_height = 600
        self.show_debug = False
        
        # Subsystems
        self.ai_test = AITestSystem()
        self.camera_test = CameraTest()
        
        # Background elements
        self.clouds = [(random.randint(0, 2400), random.randint(50, 150), random.randint(40, 80)) for _ in range(15)]
        self.bg_hills = [(random.randint(0, 2400), random.randint(20, 60)) for _ in range(8)]

    def init_test_stage(self):
        self.player = Player(100, 400)
        self.player.coins = 0
        self.player.stars = 0
        
        # Ground
        self.platforms = [
            pygame.Rect(0, 520, 600, 80),
            pygame.Rect(700, 520, 400, 80),
            pygame.Rect(1200, 520, 600, 80),
            pygame.Rect(1900, 520, 500, 80),
        ]
        
        # Floating platforms
        self.platforms.extend([
            pygame.Rect(200, 420, 100, 20),
            pygame.Rect(400, 350, 120, 20),
            pygame.Rect(600, 280, 80, 20),
            pygame.Rect(800, 400, 100, 20),
            pygame.Rect(1000, 320, 150, 20),
            pygame.Rect(1250, 380, 100, 20),
            pygame.Rect(1400, 280, 80, 20),
            pygame.Rect(1600, 350, 120, 20),
            pygame.Rect(1800, 250, 100, 20),
            pygame.Rect(2000, 350, 150, 20),
            pygame.Rect(2200, 280, 80, 20),
        ])
        
        # ? Blocks (visual platforms)
        self.question_blocks = [
            pygame.Rect(300, 350, 40, 40),
            pygame.Rect(500, 280, 40, 40),
            pygame.Rect(900, 330, 40, 40),
            pygame.Rect(1300, 300, 40, 40),
            pygame.Rect(1700, 280, 40, 40),
        ]
        self.platforms.extend(self.question_blocks)
        
        # Coins
        self.coins = [
            Coin(220, 380), Coin(250, 380), Coin(280, 380),
            Coin(420, 310), Coin(460, 310), Coin(500, 310),
            Coin(620, 240), Coin(660, 240),
            Coin(830, 360), Coin(870, 360),
            Coin(1020, 280), Coin(1060, 280), Coin(1100, 280),
            Coin(1270, 340), Coin(1310, 340),
            Coin(1420, 240), Coin(1460, 240),
            Coin(1620, 310), Coin(1680, 310),
            Coin(1820, 210), Coin(1880, 210),
            Coin(2020, 310), Coin(2080, 310), Coin(2140, 310),
        ]
        
        # Star at the end
        self.stars = [Star(2250, 200)]

    def init_empty_map(self):
        self.player = Player(400, 400)
        self.platforms = [pygame.Rect(0, 520, self.w, 80)]
        self.coins = []
        self.stars = []
        self.question_blocks = []

    # ---------------- DEBUG MENU ----------------
    def draw_debug_menu(self):
        self.screen.fill((0, 0, 0))
        
        # Retro CRT effect lines
        for y in range(0, self.h, 4):
            pygame.draw.line(self.screen, (10, 10, 10), (0, y), (self.w, y))

        # Title with glow effect
        title_font = pygame.font.SysFont("couriernew", 28, bold=True)
        title = title_font.render("SGI SAMSOFT DEBUG MENU", True, (0, 255, 0))
        glow = title_font.render("SGI SAMSOFT DEBUG MENU", True, (0, 100, 0))
        self.screen.blit(glow, (42, 42))
        self.screen.blit(title, (40, 40))
        
        # Version
        ver = self.font_small.render("REVAMPED v0.2 // B3313 STYLE", True, (100, 100, 100))
        self.screen.blit(ver, (40, 75))

        # Separator
        pygame.draw.line(self.screen, (0, 150, 0), (40, 100), (400, 100), 2)

        y = 130
        for i, item in enumerate(self.menu_items):
            if i == self.menu_index:
                # Selection highlight
                pygame.draw.rect(self.screen, (0, 50, 0), (60, y - 5, 350, 36))
                prefix = ">"
                color = (0, 255, 0)
            else:
                prefix = " "
                color = (180, 180, 180)
                
            text = self.font.render(f"{prefix} {item}", True, color)
            self.screen.blit(text, (80, y))
            y += 42

        # Footer box
        pygame.draw.rect(self.screen, (30, 30, 30), (30, self.h - 80, self.w - 60, 60))
        pygame.draw.rect(self.screen, (0, 100, 0), (30, self.h - 80, self.w - 60, 60), 2)
        
        footer = self.font_small.render(
            "UP/DOWN: SELECT   ENTER: CONFIRM   ESC: QUIT",
            True,
            (0, 200, 0)
        )
        self.screen.blit(footer, (50, self.h - 60))
        
        footer2 = self.font_small.render(
            "TAB: TOGGLE DEBUG INFO IN GAME",
            True,
            (0, 150, 0)
        )
        self.screen.blit(footer2, (50, self.h - 38))

    # ---------------- LOADING (MS-DOS STYLE) ----------------
    def draw_loading(self):
        self.screen.fill((0, 0, 0))
        
        # Retro scanlines
        for y in range(0, self.h, 3):
            pygame.draw.line(self.screen, (0, 8, 0), (0, y), (self.w, y))

        # Header
        header = self.font.render("SGI SAMSOFT BOOT SEQUENCE", True, (0, 200, 0))
        self.screen.blit(header, (40, 40))
        pygame.draw.line(self.screen, (0, 100, 0), (40, 75), (500, 75))

        y = 100
        for i in range(min(self.loading_index, len(self.loading_lines))):
            line = self.loading_lines[i]
            color = (0, 255, 0) if "OK" in line or "READY" in line else (255, 200, 0)
            text = self.font.render(line, True, color)
            self.screen.blit(text, (40, y))
            y += 32

        # Blinking cursor on current line
        if self.loading_index < len(self.loading_lines):
            cursor = "_" if (self.loading_timer // 15) % 2 == 0 else " "
            partial = self.loading_lines[self.loading_index][:min(self.loading_timer // 2, len(self.loading_lines[self.loading_index]))]
            text = self.font.render(partial + cursor, True, (0, 255, 0))
            self.screen.blit(text, (40, y))

        # Progress bar
        progress = self.loading_index / len(self.loading_lines)
        pygame.draw.rect(self.screen, (30, 30, 30), (40, self.h - 60, self.w - 80, 20))
        pygame.draw.rect(self.screen, (0, 200, 0), (40, self.h - 60, int((self.w - 80) * progress), 20))
        pygame.draw.rect(self.screen, (0, 100, 0), (40, self.h - 60, self.w - 80, 20), 2)

        self.loading_timer += 1
        line_len = len(self.loading_lines[self.loading_index]) if self.loading_index < len(self.loading_lines) else 0
        
        if self.loading_timer > line_len * 2 + 30:
            self.loading_timer = 0
            self.loading_index += 1
            if self.loading_index > len(self.loading_lines):
                self.loading_index = 0
                if self.loading_target == "AI":
                    self.state = State.AI_TEST
                    self.ai_test = AITestSystem()
                elif self.loading_target == "EMPTY":
                    self.init_empty_map()
                    self.state = State.EMPTY_MAP
                elif self.loading_target == "CAMERA":
                    self.camera_test = CameraTest()
                    self.state = State.CAMERA_TEST
                else:
                    self.init_test_stage()
                    self.state = State.GAME

    # ---------------- GAME RENDER ----------------
    def draw_game(self, is_empty=False):
        # Sky gradient
        for y in range(self.h):
            ratio = y / self.h
            r = int(92 + (135 - 92) * ratio)
            g = int(148 + (206 - 148) * ratio)
            b = int(252 + (250 - 252) * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.w, y))
            
        # Clouds (parallax)
        for cx, cy, size in self.clouds:
            draw_x = (cx - self.camera_x * 0.3) % (self.level_width + 200) - 100
            pygame.draw.ellipse(self.screen, (255, 255, 255), (draw_x, cy, size, size * 0.6))
            pygame.draw.ellipse(self.screen, (255, 255, 255), (draw_x + size * 0.3, cy - size * 0.2, size * 0.7, size * 0.5))
            pygame.draw.ellipse(self.screen, (255, 255, 255), (draw_x - size * 0.2, cy + size * 0.1, size * 0.5, size * 0.4))
            
        # Background hills (parallax)
        for hx, hsize in self.bg_hills:
            draw_x = (hx - self.camera_x * 0.5) % (self.level_width + 300) - 150
            pygame.draw.ellipse(self.screen, (34, 139, 34), (draw_x, 400, hsize * 3, hsize * 2))
            
        # Platforms
        for plat in self.platforms:
            draw_rect = plat.move(-self.camera_x, -self.camera_y)
            
            # Check if it's a ? block
            if plat in self.question_blocks:
                # ? Block style
                pygame.draw.rect(self.screen, (200, 150, 50), draw_rect)
                pygame.draw.rect(self.screen, (150, 100, 30), draw_rect, 3)
                # Question mark
                q_font = pygame.font.SysFont("arial", 24, bold=True)
                q_text = q_font.render("?", True, (255, 255, 255))
                self.screen.blit(q_text, (draw_rect.centerx - 7, draw_rect.centery - 14))
            elif plat.height > 40:
                # Ground
                pygame.draw.rect(self.screen, (139, 90, 43), draw_rect)  # Brown dirt
                pygame.draw.rect(self.screen, (34, 139, 34), (draw_rect.x, draw_rect.y, draw_rect.width, 15))  # Green grass
            else:
                # Floating platform - brick style
                pygame.draw.rect(self.screen, (180, 100, 50), draw_rect)
                pygame.draw.rect(self.screen, (120, 60, 30), draw_rect, 2)
                # Brick lines
                for bx in range(draw_rect.x, draw_rect.x + draw_rect.width, 25):
                    pygame.draw.line(self.screen, (120, 60, 30), (bx, draw_rect.y), (bx, draw_rect.y + draw_rect.height))
                    
        # Coins
        for coin in self.coins:
            coin.update()
            coin.draw(self.screen, self.camera_x, self.camera_y)
            
            # Collection check
            if not coin.collected and self.player:
                if abs(coin.x - self.player.x) < 30 and abs(coin.y - self.player.y) < 40:
                    coin.collected = True
                    self.player.coins += 1
                    
        # Stars
        for star in self.stars:
            star.update()
            star.draw(self.screen, self.camera_x, self.camera_y)
            
            # Collection check
            if not star.collected and self.player:
                if abs(star.x - self.player.x) < 40 and abs(star.y - self.player.y) < 50:
                    star.collected = True
                    self.player.stars += 1
                    
        # Player
        if self.player:
            self.player.draw(self.screen, self.camera_x, self.camera_y)
            
        # HUD
        if self.player:
            self.hud.draw(self.screen, self.player, self.fps, self.show_debug)
            
        # Level name for empty map
        if is_empty:
            font = pygame.font.SysFont("arial", 20, bold=True)
            course = font.render("EMPTY MAP - DEBUG ZONE", True, (255, 255, 255))
            shadow = font.render("EMPTY MAP - DEBUG ZONE", True, (0, 0, 0))
            self.screen.blit(shadow, (self.w//2 - course.get_width()//2 + 2, 12))
            self.screen.blit(course, (self.w//2 - course.get_width()//2, 10))

    # ---------------- UPDATE ----------------
    def update_game(self):
        keys = pygame.key.get_pressed()
        
        if self.player:
            self.player.update(self.platforms, keys)
            
            # Camera follow
            target_x = self.player.x - self.w // 3
            target_y = self.player.y - self.h // 2
            
            self.camera_x += (target_x - self.camera_x) * 0.1
            self.camera_y += (target_y - self.camera_y) * 0.1
            
            # Clamp camera
            self.camera_x = max(0, min(self.camera_x, self.level_width - self.w))
            self.camera_y = max(0, min(self.camera_y, self.level_height - self.h))
            
            # Fall reset
            if self.player.y > 700:
                self.player.x = 100
                self.player.y = 400
                self.player.health -= 1
                self.camera_x = 0
                if self.player.health <= 0:
                    self.player.lives -= 1
                    self.player.health = self.player.max_health

    # ---------------- LOOP ----------------
    def run(self):
        while self.running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False

                if e.type == pygame.KEYDOWN:
                    if self.state == State.DEBUG_MENU:
                        if e.key == pygame.K_UP:
                            self.menu_index = (self.menu_index - 1) % len(self.menu_items)
                        if e.key == pygame.K_DOWN:
                            self.menu_index = (self.menu_index + 1) % len(self.menu_items)
                        if e.key == pygame.K_RETURN:
                            item = self.menu_items[self.menu_index]
                            if item == "RETURN":
                                self.running = False
                            else:
                                self.state = State.LOADING
                                self.loading_index = 0
                                self.loading_timer = 0
                                if item == "PERSONALIZATION AI TEST":
                                    self.loading_target = "AI"
                                elif item == "EMPTY MAP":
                                    self.loading_target = "EMPTY"
                                elif item == "CAMERA TEST":
                                    self.loading_target = "CAMERA"
                                else:
                                    self.loading_target = "GAME"
                        if e.key == pygame.K_ESCAPE:
                            self.running = False

                    elif self.state == State.LOADING:
                        if e.key == pygame.K_ESCAPE:
                            self.state = State.DEBUG_MENU
                            
                    elif self.state in (State.GAME, State.EMPTY_MAP):
                        if e.key == pygame.K_ESCAPE:
                            self.state = State.DEBUG_MENU
                        if e.key == pygame.K_TAB:
                            self.show_debug = not self.show_debug
                            
                    elif self.state == State.AI_TEST:
                        if e.key == pygame.K_ESCAPE:
                            self.state = State.DEBUG_MENU
                            
                    elif self.state == State.CAMERA_TEST:
                        if e.key == pygame.K_ESCAPE:
                            self.state = State.DEBUG_MENU
                        if e.key == pygame.K_TAB:
                            self.camera_test.mode = (self.camera_test.mode + 1) % len(self.camera_test.modes)

            # Update
            if self.state in (State.GAME, State.EMPTY_MAP):
                self.update_game()
            elif self.state == State.AI_TEST:
                self.ai_test.update()
            elif self.state == State.CAMERA_TEST:
                keys = pygame.key.get_pressed()
                self.camera_test.update(keys)

            # Draw
            if self.state == State.DEBUG_MENU:
                self.draw_debug_menu()
            elif self.state == State.LOADING:
                self.draw_loading()
            elif self.state == State.GAME:
                self.draw_game()
            elif self.state == State.EMPTY_MAP:
                self.draw_game(is_empty=True)
            elif self.state == State.AI_TEST:
                self.ai_test.draw(self.screen)
            elif self.state == State.CAMERA_TEST:
                self.camera_test.draw(self.screen)

            pygame.display.flip()
            self.fps = self.clock.get_fps()
            self.clock.tick(60)

        pygame.quit()

# ---------------- ENTRY ----------------
if __name__ == "__main__":
    SGISamsoftRevamped().run()
