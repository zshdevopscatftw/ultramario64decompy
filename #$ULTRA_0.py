"""
Super Mario 64 DS - Pure Math Engine (FIXED)
Test Level with Warp Pipes & Checkerboard Floor
"""

import pygame
import math
import numpy as np
from collections import defaultdict
from enum import Enum

class Vector3:
    __slots__ = ['x', 'y', 'z']
    
    def __init__(self, x=0, y=0, z=0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
    
    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar):
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def cross(self, other):
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    
    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
    
    def normalize(self):
        l = self.length()
        if l > 0.0001:
            return Vector3(self.x / l, self.y / l, self.z / l)
        return Vector3(0, 0, 0)
    
    def copy(self):
        return Vector3(self.x, self.y, self.z)

class Matrix4:
    def __init__(self, values=None):
        if values is None:
            self.m = np.identity(4, dtype=np.float64)
        else:
            self.m = np.array(values, dtype=np.float64)
    
    def __matmul__(self, other):
        result = Matrix4()
        result.m = self.m @ other.m
        return result
    
    @staticmethod
    def perspective(fov, aspect, near, far):
        f = 1.0 / math.tan(math.radians(fov) * 0.5)
        nf = 1.0 / (near - far)
        return Matrix4([
            [f / aspect, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (far + near) * nf, 2 * far * near * nf],
            [0, 0, -1, 0]
        ])
    
    @staticmethod
    def look_at(eye, target, up):
        f = (target - eye).normalize()
        r = f.cross(up).normalize()
        u = r.cross(f)
        
        return Matrix4([
            [r.x, r.y, r.z, -r.dot(eye)],
            [u.x, u.y, u.z, -u.dot(eye)],
            [-f.x, -f.y, -f.z, f.dot(eye)],
            [0, 0, 0, 1]
        ])
    
    def transform_point(self, v):
        x = self.m[0,0]*v.x + self.m[0,1]*v.y + self.m[0,2]*v.z + self.m[0,3]
        y = self.m[1,0]*v.x + self.m[1,1]*v.y + self.m[1,2]*v.z + self.m[1,3]
        z = self.m[2,0]*v.x + self.m[2,1]*v.y + self.m[2,2]*v.z + self.m[2,3]
        w = self.m[3,0]*v.x + self.m[3,1]*v.y + self.m[3,2]*v.z + self.m[3,3]
        return x, y, z, w

class WarpPipe:
    def __init__(self, pos, destination, color=(0, 180, 0)):
        self.pos = pos
        self.destination = destination
        self.color = color
        self.radius = 2.0
        self.cooldown = 0
    
    def check_enter(self, player_pos):
        dx = player_pos.x - self.pos.x
        dz = player_pos.z - self.pos.z
        dist = math.sqrt(dx * dx + dz * dz)
        return dist < self.radius and abs(player_pos.y - self.pos.y) < 3 and self.cooldown <= 0

class Mesh:
    def __init__(self):
        self.vertices = []
        self.faces = []
        self.colors = []
    
    def add_quad(self, v0, v1, v2, v3, color):
        """Add a quad as 2 triangles"""
        base = len(self.vertices)
        self.vertices.extend([v0, v1, v2, v3])
        # Two triangles with correct winding
        self.faces.append((base, base+1, base+2))
        self.colors.append(color)
        self.faces.append((base, base+2, base+3))
        self.colors.append(color)
    
    def add_cube(self, center, size, color):
        hs = size * 0.5
        cx, cy, cz = center.x, center.y, center.z
        
        # 8 vertices
        v = [
            Vector3(cx-hs, cy-hs, cz-hs),  # 0: left bottom front
            Vector3(cx+hs, cy-hs, cz-hs),  # 1: right bottom front
            Vector3(cx+hs, cy+hs, cz-hs),  # 2: right top front
            Vector3(cx-hs, cy+hs, cz-hs),  # 3: left top front
            Vector3(cx-hs, cy-hs, cz+hs),  # 4: left bottom back
            Vector3(cx+hs, cy-hs, cz+hs),  # 5: right bottom back
            Vector3(cx+hs, cy+hs, cz+hs),  # 6: right top back
            Vector3(cx-hs, cy+hs, cz+hs),  # 7: left top back
        ]
        
        # Shading for different faces
        c = color
        top = (min(255, c[0]+20), min(255, c[1]+20), min(255, c[2]+20))
        bottom = (max(0, c[0]-40), max(0, c[1]-40), max(0, c[2]-40))
        left = (max(0, c[0]-20), max(0, c[1]-20), max(0, c[2]-20))
        right = (max(0, c[0]-10), max(0, c[1]-10), max(0, c[2]-10))
        
        # Front face (z-)
        self.add_quad(v[0], v[1], v[2], v[3], c)
        # Back face (z+)
        self.add_quad(v[5], v[4], v[7], v[6], c)
        # Top face (y+)
        self.add_quad(v[3], v[2], v[6], v[7], top)
        # Bottom face (y-)
        self.add_quad(v[4], v[5], v[1], v[0], bottom)
        # Right face (x+)
        self.add_quad(v[1], v[5], v[6], v[2], right)
        # Left face (x-)
        self.add_quad(v[4], v[0], v[3], v[7], left)
    
    def add_pipe(self, pos, height, radius, color, segments=12):
        """Add warp pipe cylinder"""
        dark = (max(0, color[0]-30), max(0, color[1]-30), max(0, color[2]-30))
        light = (min(255, color[0]+20), min(255, color[1]+20), min(255, color[2]+20))
        
        # Cylinder walls
        for i in range(segments):
            a1 = 2 * math.pi * i / segments
            a2 = 2 * math.pi * ((i + 1) % segments) / segments
            
            x1 = pos.x + math.cos(a1) * radius
            z1 = pos.z + math.sin(a1) * radius
            x2 = pos.x + math.cos(a2) * radius
            z2 = pos.z + math.sin(a2) * radius
            
            # Shade based on angle
            shade = 0.5 + 0.5 * math.cos(a1)
            col = (
                int(dark[0] + (light[0] - dark[0]) * shade),
                int(dark[1] + (light[1] - dark[1]) * shade),
                int(dark[2] + (light[2] - dark[2]) * shade)
            )
            
            v0 = Vector3(x1, pos.y, z1)
            v1 = Vector3(x2, pos.y, z2)
            v2 = Vector3(x2, pos.y + height, z2)
            v3 = Vector3(x1, pos.y + height, z1)
            
            self.add_quad(v0, v1, v2, v3, col)
        
        # Rim
        rim_h = 0.6
        rim_r = radius * 1.25
        rim_color = (max(0, color[0]-50), max(0, color[1]-50), max(0, color[2]-50))
        
        for i in range(segments):
            a1 = 2 * math.pi * i / segments
            a2 = 2 * math.pi * ((i + 1) % segments) / segments
            
            x1 = pos.x + math.cos(a1) * rim_r
            z1 = pos.z + math.sin(a1) * rim_r
            x2 = pos.x + math.cos(a2) * rim_r
            z2 = pos.z + math.sin(a2) * rim_r
            
            v0 = Vector3(x1, pos.y + height, z1)
            v1 = Vector3(x2, pos.y + height, z2)
            v2 = Vector3(x2, pos.y + height + rim_h, z2)
            v3 = Vector3(x1, pos.y + height + rim_h, z1)
            
            self.add_quad(v0, v1, v2, v3, rim_color)
        
        # Inner hole (black)
        for i in range(segments):
            a1 = 2 * math.pi * i / segments
            a2 = 2 * math.pi * ((i + 1) % segments) / segments
            
            inner_r = radius * 0.7
            x1 = pos.x + math.cos(a1) * radius
            z1 = pos.z + math.sin(a1) * radius
            x2 = pos.x + math.cos(a2) * radius
            z2 = pos.z + math.sin(a2) * radius
            x3 = pos.x + math.cos(a2) * inner_r
            z3 = pos.z + math.sin(a2) * inner_r
            x4 = pos.x + math.cos(a1) * inner_r
            z4 = pos.z + math.sin(a1) * inner_r
            
            top_y = pos.y + height + rim_h
            
            v0 = Vector3(x1, top_y, z1)
            v1 = Vector3(x2, top_y, z2)
            v2 = Vector3(x3, top_y, z3)
            v3 = Vector3(x4, top_y, z4)
            
            self.add_quad(v0, v1, v2, v3, (20, 20, 20))
    
    def add_checkerboard(self, center, size, tiles, c1, c2):
        """Checkerboard floor"""
        tile_size = size / tiles
        half = size / 2
        
        for tx in range(tiles):
            for tz in range(tiles):
                x = center.x - half + tx * tile_size
                z = center.z - half + tz * tile_size
                y = center.y
                
                color = c1 if (tx + tz) % 2 == 0 else c2
                
                v0 = Vector3(x, y, z)
                v1 = Vector3(x + tile_size, y, z)
                v2 = Vector3(x + tile_size, y, z + tile_size)
                v3 = Vector3(x, y, z + tile_size)
                
                self.add_quad(v0, v1, v2, v3, color)

class Renderer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.pixels = pygame.Surface((width, height))
        self.z_buffer = np.full((height, width), float('inf'), dtype=np.float32)
    
    def clear(self, color):
        self.pixels.fill(color)
        self.z_buffer.fill(float('inf'))
    
    def project_vertex(self, v, mvp):
        x, y, z, w = mvp.transform_point(v)
        
        if w < 0.001:
            return None
        
        # Perspective divide
        x /= w
        y /= w
        z /= w
        
        # NDC to screen
        sx = int((x + 1) * 0.5 * self.width)
        sy = int((1 - y) * 0.5 * self.height)
        
        return (sx, sy, z, w)
    
    def draw_triangle(self, p0, p1, p2, color):
        """Scanline triangle rasterizer"""
        # Bounds
        min_x = max(0, min(p0[0], p1[0], p2[0]))
        max_x = min(self.width - 1, max(p0[0], p1[0], p2[0]))
        min_y = max(0, min(p0[1], p1[1], p2[1]))
        max_y = min(self.height - 1, max(p0[1], p1[1], p2[1]))
        
        if min_x >= max_x or min_y >= max_y:
            return
        
        # Edge function setup
        def edge(ax, ay, bx, by, cx, cy):
            return (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)
        
        area = edge(p0[0], p0[1], p1[0], p1[1], p2[0], p2[1])
        if abs(area) < 1:
            return
        
        inv_area = 1.0 / area
        
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                w0 = edge(p1[0], p1[1], p2[0], p2[1], x, y)
                w1 = edge(p2[0], p2[1], p0[0], p0[1], x, y)
                w2 = edge(p0[0], p0[1], p1[0], p1[1], x, y)
                
                if (w0 >= 0 and w1 >= 0 and w2 >= 0) or (w0 <= 0 and w1 <= 0 and w2 <= 0):
                    w0 *= inv_area
                    w1 *= inv_area
                    w2 *= inv_area
                    
                    z = w0 * p0[2] + w1 * p1[2] + w2 * p2[2]
                    
                    if z < self.z_buffer[y, x] and z > -1:
                        self.z_buffer[y, x] = z
                        self.pixels.set_at((x, y), color)
    
    def render_mesh(self, mesh, mvp):
        # Sort faces by depth (painter's algorithm backup)
        face_depths = []
        for i, face in enumerate(mesh.faces):
            v0 = mesh.vertices[face[0]]
            v1 = mesh.vertices[face[1]]
            v2 = mesh.vertices[face[2]]
            
            # Average Z in world space
            avg_z = (v0.z + v1.z + v2.z) / 3
            face_depths.append((avg_z, i))
        
        # Sort back to front
        face_depths.sort(reverse=True)
        
        for _, i in face_depths:
            face = mesh.faces[i]
            v0 = mesh.vertices[face[0]]
            v1 = mesh.vertices[face[1]]
            v2 = mesh.vertices[face[2]]
            
            p0 = self.project_vertex(v0, mvp)
            p1 = self.project_vertex(v1, mvp)
            p2 = self.project_vertex(v2, mvp)
            
            if p0 is None or p1 is None or p2 is None:
                continue
            
            # Backface culling in screen space
            cross = (p1[0] - p0[0]) * (p2[1] - p0[1]) - (p1[1] - p0[1]) * (p2[0] - p0[0])
            if cross > 0:
                continue
            
            self.draw_triangle(p0, p1, p2, mesh.colors[i])

class PlayerState(Enum):
    IDLE = 0
    WALKING = 1
    JUMPING = 2
    FALLING = 3
    WARPING = 4

class SM64DSGame:
    def __init__(self):
        pygame.init()
        
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Super Mario 64 DS - Test Level")
        
        self.renderer = Renderer(self.width, self.height)
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Camera
        self.cam_dist = 30
        self.cam_angle = 0
        self.cam_height = 15
        
        # Player
        self.player_pos = Vector3(0, 5, 0)
        self.player_vel = Vector3(0, 0, 0)
        self.player_state = PlayerState.FALLING
        self.grounded = False
        
        # Physics
        self.gravity = 0.4
        self.jump_power = 9
        self.move_speed = 0.4
        
        # Level data
        self.platforms = []
        self.warp_pipes = []
        self.coins = []
        self.collected_coins = set()
        self.coin_count = 0
        self.stars = 0
        self.star_collected = False
        self.star_pos = Vector3(0, 15, 30)
        
        # Warp
        self.warp_timer = 0
        self.warp_dest = None
        
        # Build level
        self.world = Mesh()
        self.build_level()
        
        # Input
        self.keys = defaultdict(bool)
    
    def build_level(self):
        """Create test level"""
        # Main checkerboard floor
        self.world.add_checkerboard(
            Vector3(0, 0, 0), 80, 16,
            (230, 230, 230), (40, 40, 40)
        )
        self.platforms.append({'x': 0, 'y': 0, 'z': 0, 'hw': 40, 'hd': 40})
        
        # Raised platform 1
        self.world.add_cube(Vector3(-15, 2, -15), 10, (150, 150, 150))
        self.platforms.append({'x': -15, 'y': 7, 'z': -15, 'hw': 5, 'hd': 5})
        
        # Staircase
        for i in range(5):
            self.world.add_cube(Vector3(15 + i*4, i*2 + 1, 0), 4, (120, 100, 80))
            self.platforms.append({'x': 15 + i*4, 'y': (i+1)*2 + 2, 'z': 0, 'hw': 2, 'hd': 2})
        
        # Floating island with checkerboard
        self.world.add_checkerboard(
            Vector3(0, 12, 30), 16, 4,
            (180, 180, 255), (80, 80, 180)
        )
        self.platforms.append({'x': 0, 'y': 12, 'z': 30, 'hw': 8, 'hd': 8})
        
        # Warp pipes
        # Green: main area teleport
        self.world.add_pipe(Vector3(-25, 0, 10), 4, 3, (0, 180, 0))
        self.warp_pipes.append(WarpPipe(
            Vector3(-25, 4, 10), Vector3(25, 3, -15), (0, 180, 0)
        ))
        
        self.world.add_pipe(Vector3(25, 0, -15), 4, 3, (0, 180, 0))
        self.warp_pipes.append(WarpPipe(
            Vector3(25, 4, -15), Vector3(-25, 5, 10), (0, 180, 0)
        ))
        
        # Red: to floating island
        self.world.add_pipe(Vector3(10, 0, 20), 4, 3, (200, 50, 50))
        self.warp_pipes.append(WarpPipe(
            Vector3(10, 4, 20), Vector3(0, 14, 30), (200, 50, 50)
        ))
        
        # Blue: island back to start
        self.world.add_pipe(Vector3(-5, 12, 25), 3, 2.5, (50, 50, 200))
        self.warp_pipes.append(WarpPipe(
            Vector3(-5, 15, 25), Vector3(0, 3, 0), (50, 50, 200)
        ))
        
        # Coins in ring
        for i in range(8):
            a = i * math.pi * 2 / 8
            pos = Vector3(math.cos(a) * 12, 2, math.sin(a) * 12)
            self.coins.append(pos)
            self.world.add_cube(pos, 1.5, (255, 220, 0))
        
        # Platform coins
        self.coins.append(Vector3(-15, 9, -15))
        self.world.add_cube(Vector3(-15, 9, -15), 1.5, (255, 220, 0))
        
        # Star on island
        self.world.add_cube(self.star_pos, 2.5, (255, 255, 50))
        
        # Question blocks
        for pos in [Vector3(-8, 5, 5), Vector3(8, 5, 5), Vector3(0, 5, -10)]:
            self.world.add_cube(pos, 3, (255, 200, 50))
        
        # Boundary walls
        wall_col = (100, 80, 120)
        for i in range(-4, 5):
            self.world.add_cube(Vector3(i*10, 4, -42), 8, wall_col)
            self.world.add_cube(Vector3(i*10, 4, 42), 8, wall_col)
            self.world.add_cube(Vector3(-42, 4, i*10), 8, wall_col)
            self.world.add_cube(Vector3(42, 4, i*10), 8, wall_col)
    
    def handle_input(self):
        if self.player_state == PlayerState.WARPING:
            return
        
        mx, mz = 0, 0
        if self.keys[pygame.K_w]: mz = -1
        if self.keys[pygame.K_s]: mz = 1
        if self.keys[pygame.K_a]: mx = -1
        if self.keys[pygame.K_d]: mx = 1
        
        if mx and mz:
            mx *= 0.707
            mz *= 0.707
        
        cos_a = math.cos(self.cam_angle)
        sin_a = math.sin(self.cam_angle)
        
        speed = self.move_speed * (0.6 if not self.grounded else 1.0)
        self.player_vel.x = (mx * cos_a - mz * sin_a) * speed
        self.player_vel.z = (mx * sin_a + mz * cos_a) * speed
        
        if (mx or mz) and self.grounded:
            self.player_state = PlayerState.WALKING
        elif self.grounded:
            self.player_state = PlayerState.IDLE
        
        if self.keys[pygame.K_SPACE] and self.grounded:
            self.player_vel.y = self.jump_power
            self.grounded = False
            self.player_state = PlayerState.JUMPING
        
        if self.keys[pygame.K_LEFT]: self.cam_angle += 0.05
        if self.keys[pygame.K_RIGHT]: self.cam_angle -= 0.05
        if self.keys[pygame.K_UP]: self.cam_height = min(35, self.cam_height + 0.5)
        if self.keys[pygame.K_DOWN]: self.cam_height = max(5, self.cam_height - 0.5)
    
    def update(self):
        # Warp handling
        if self.player_state == PlayerState.WARPING:
            self.warp_timer -= 1
            if self.warp_timer <= 0:
                self.player_pos = self.warp_dest.copy()
                self.player_vel = Vector3(0, 0, 0)
                self.player_state = PlayerState.FALLING
                for pipe in self.warp_pipes:
                    if (pipe.pos - self.player_pos).length() < 6:
                        pipe.cooldown = 45
            return
        
        # Gravity
        self.player_vel.y -= self.gravity
        self.player_vel.y = max(-20, self.player_vel.y)
        
        new_pos = self.player_pos + self.player_vel
        
        # Collision
        self.grounded = False
        for p in self.platforms:
            if abs(new_pos.x - p['x']) < p['hw'] and abs(new_pos.z - p['z']) < p['hd']:
                if self.player_vel.y < 0 and new_pos.y <= p['y'] + 2 and self.player_pos.y >= p['y'] - 1:
                    new_pos.y = p['y'] + 2
                    self.player_vel.y = 0
                    self.grounded = True
                    if self.player_state in [PlayerState.JUMPING, PlayerState.FALLING]:
                        self.player_state = PlayerState.IDLE
                    break
        
        if not self.grounded and self.player_vel.y < 0:
            self.player_state = PlayerState.FALLING
        
        # Bounds
        new_pos.x = max(-38, min(38, new_pos.x))
        new_pos.z = max(-38, min(38, new_pos.z))
        
        if new_pos.y < -50:
            new_pos = Vector3(0, 10, 0)
            self.player_vel = Vector3(0, 0, 0)
        
        self.player_pos = new_pos
        
        # Pipe cooldowns
        for pipe in self.warp_pipes:
            if pipe.cooldown > 0:
                pipe.cooldown -= 1
        
        # Coins
        for i, c in enumerate(self.coins):
            if i not in self.collected_coins:
                if (self.player_pos - c).length() < 3:
                    self.collected_coins.add(i)
                    self.coin_count += 1
        
        # Star
        if not self.star_collected and (self.player_pos - self.star_pos).length() < 4:
            self.star_collected = True
            self.stars += 1
        
        # Pipes
        if self.grounded:
            for pipe in self.warp_pipes:
                if pipe.check_enter(self.player_pos):
                    self.player_state = PlayerState.WARPING
                    self.warp_timer = 25
                    self.warp_dest = pipe.destination
                    self.player_vel = Vector3(0, 0, 0)
                    break
    
    def render(self):
        # Camera
        cx = self.player_pos.x + math.sin(self.cam_angle) * self.cam_dist
        cz = self.player_pos.z + math.cos(self.cam_angle) * self.cam_dist
        cy = self.player_pos.y + self.cam_height
        
        cam = Vector3(cx, cy, cz)
        target = self.player_pos + Vector3(0, 3, 0)
        
        view = Matrix4.look_at(cam, target, Vector3(0, 1, 0))
        proj = Matrix4.perspective(55, self.width / self.height, 0.5, 500)
        mvp = proj @ view
        
        self.renderer.clear((120, 180, 255))
        self.renderer.render_mesh(self.world, mvp)
        
        # Player
        player_mesh = Mesh()
        player_mesh.add_cube(self.player_pos + Vector3(0, 1, 0), 2, (255, 50, 50))
        player_mesh.add_cube(self.player_pos + Vector3(0, 2.8, 0), 1.5, (255, 200, 150))
        player_mesh.add_cube(self.player_pos + Vector3(0, 3.8, 0), 1.2, (255, 0, 0))
        self.renderer.render_mesh(player_mesh, mvp)
        
        self.screen.blit(self.renderer.pixels, (0, 0))
        
        # HUD
        font = pygame.font.Font(None, 36)
        big = pygame.font.Font(None, 48)
        
        self.screen.blit(big.render(f"★ {self.stars}", True, (255, 255, 0)), (20, 15))
        self.screen.blit(font.render(f"Coins: {self.coin_count}", True, (255, 220, 0)), (20, 55))
        
        info = f"Pos: {self.player_pos.x:.1f}, {self.player_pos.y:.1f}, {self.player_pos.z:.1f}"
        self.screen.blit(font.render(info, True, (255, 255, 255)), (20, 90))
        self.screen.blit(font.render(f"State: {self.player_state.name}", True, (200, 200, 200)), (20, 120))
        
        controls = ["WASD: Move", "SPACE: Jump", "Arrows: Camera", "R: Reset", "ESC: Quit"]
        for i, c in enumerate(controls):
            self.screen.blit(font.render(c, True, (255, 255, 255)), (self.width - 180, 15 + i*25))
        
        self.screen.blit(big.render("TEST LEVEL", True, (255, 255, 255)), (self.width//2 - 80, 10))
        
        if self.player_state == PlayerState.WARPING:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            alpha = min(220, (25 - self.warp_timer) * 12)
            overlay.fill((0, 0, 0, alpha))
            self.screen.blit(overlay, (0, 0))
            txt = big.render("WARPING...", True, (0, 255, 0))
            self.screen.blit(txt, (self.width//2 - 80, self.height//2 - 20))
    
    def run(self):
        while self.running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False
                elif e.type == pygame.KEYDOWN:
                    self.keys[e.key] = True
                    if e.key == pygame.K_ESCAPE:
                        self.running = False
                    if e.key == pygame.K_r:
                        self.player_pos = Vector3(0, 5, 0)
                        self.player_vel = Vector3(0, 0, 0)
                elif e.type == pygame.KEYUP:
                    self.keys[e.key] = False
            
            self.handle_input()
            self.update()
            self.render()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()

def main():
    print("=" * 50)
    print("  SUPER MARIO 64 DS - TEST LEVEL")
    print("=" * 50)
    print("  B&W Checkerboard | Warp Pipes | Platforms")
    print()
    print("  WASD: Move | SPACE: Jump | Arrows: Camera")
    print("  R: Reset | ESC: Quit")
    print("=" * 50)
    
    game = SM64DSGame()
    game.run()

if __name__ == "__main__":
    main()
