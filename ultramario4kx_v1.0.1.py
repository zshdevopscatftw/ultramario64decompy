#!/usr/bin/env python3
"""
SUPER MARIO 64 DS - XD EDITION
Ultra Mario 4KX v1.0.1
(C) 2025 SAMSOFT

Python port with menu system.
"""

import pygame
import math
import random
from enum import Enum
from typing import List, Tuple


# =============================================================================
# GAME STATES
# =============================================================================

class MenuState(Enum):
    MAIN_MENU = 1
    WARNING = 2
    GAME = 3


# =============================================================================
# MAIN GAME CLASS
# =============================================================================

class SM64DSGame:
    """Super Mario 64 DS - XD Edition main game class."""
    
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("SUPER MARIO 64 DS - XD EDITION")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Menu state
        self.current_state = MenuState.MAIN_MENU
        self.title_wave = 0.0
        
        # Warning screen glitch
        self.glitch_timer = 0
        self.glitch_offset_x = 0
        self.glitch_offset_y = 0
        self.glitch_color = (255, 0, 0)
        
        # Button hover states
        self.hover_start = False
        self.hover_options = False
        self.hover_exit = False
        
        # Pre-render some elements
        self.clouds = self._generate_clouds()
        self.hills = self._generate_hills()
        
        # Fonts
        self.font_title = pygame.font.SysFont('arial', 42, bold=True)
        self.font_button = pygame.font.SysFont('arial', 28, bold=True)
        self.font_warning = pygame.font.SysFont('courier', 20, bold=True)
        self.font_small = pygame.font.SysFont('arial', 14)
        
        # Button rects (will be set in render)
        self.start_rect = pygame.Rect(0, 0, 0, 0)
        self.options_rect = pygame.Rect(0, 0, 0, 0)
        self.exit_rect = pygame.Rect(0, 0, 0, 0)
        
        print("[SM64DS-XD] SAMSOFT Initialized!")
    
    def _generate_clouds(self) -> List[Tuple[int, int, int]]:
        """Generate cloud positions and sizes."""
        return [
            (120, 80, 70), (180, 60, 50), (80, 100, 55),
            (620, 120, 80), (560, 90, 55), (700, 140, 45),
            (350, 70, 40), (400, 95, 35)
        ]
    
    def _generate_hills(self) -> List[Tuple[int, int, int, Tuple[int, int, int]]]:
        """Generate rolling hills data."""
        hills = []
        colors = [(34, 139, 34), (50, 160, 50), (30, 120, 30), (45, 150, 45)]
        positions = [
            (100, 380, 180), (300, 360, 200), (550, 375, 170),
            (750, 365, 190), (-50, 390, 150), (200, 395, 120)
        ]
        for i, (x, y, r) in enumerate(positions):
            hills.append((x, y, r, colors[i % len(colors)]))
        return hills
    
    def _draw_cloud(self, x: int, y: int, size: int):
        """Draw a fluffy cloud."""
        pygame.draw.circle(self.screen, (255, 255, 255), (x, y), size)
        pygame.draw.circle(self.screen, (255, 255, 255), (x - size//2, y + size//4), int(size * 0.7))
        pygame.draw.circle(self.screen, (255, 255, 255), (x + size//2, y + size//4), int(size * 0.7))
        pygame.draw.circle(self.screen, (255, 255, 255), (x - size//3, y - size//4), int(size * 0.5))
        pygame.draw.circle(self.screen, (255, 255, 255), (x + size//3, y - size//4), int(size * 0.5))
    
    def _draw_button(self, rect: pygame.Rect, text: str, enabled: bool, hover: bool) -> pygame.Rect:
        """Draw a styled button."""
        if enabled:
            if hover:
                bg_color = (255, 220, 50)
                text_color = (180, 0, 0)
                border_color = (200, 150, 0)
            else:
                bg_color = (255, 200, 0)
                text_color = (200, 0, 0)
                border_color = (180, 140, 0)
        else:
            bg_color = (100, 100, 100)
            text_color = (160, 160, 160)
            border_color = (70, 70, 70)
        
        # Shadow
        shadow_rect = rect.copy()
        shadow_rect.x += 4
        shadow_rect.y += 4
        pygame.draw.rect(self.screen, (0, 0, 0, 100), shadow_rect, border_radius=8)
        
        # Main button
        pygame.draw.rect(self.screen, bg_color, rect, border_radius=8)
        pygame.draw.rect(self.screen, border_color, rect, 3, border_radius=8)
        
        # Text
        text_surf = self.font_button.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)
        
        return rect
    
    def render_menu(self):
        """Render the main menu screen."""
        # Sky gradient
        for y in range(self.screen_height // 2):
            ratio = y / (self.screen_height // 2)
            r = int(100 + (135 - 100) * ratio)
            g = int(180 + (206 - 180) * ratio)
            b = int(255 + (250 - 255) * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.screen_width, y))
        
        # Ground
        pygame.draw.rect(self.screen, (34, 139, 34), 
                        (0, self.screen_height // 2, self.screen_width, self.screen_height // 2))
        
        # Rolling hills
        for x, y, r, color in self.hills:
            pygame.draw.circle(self.screen, color, (x, y), r)
        
        # Clouds
        for x, y, size in self.clouds:
            self._draw_cloud(x, y, size)
        
        # Title with wave effect
        self.title_wave += 0.1
        title = "SUPER MARIO 64 DS"
        subtitle = "XD EDITION"
        
        # Main title with shadow
        title_surf = self.font_title.render(title, True, (255, 255, 255))
        title_shadow = self.font_title.render(title, True, (0, 0, 0))
        title_x = self.screen_width // 2 - title_surf.get_width() // 2
        title_y = 40 + math.sin(self.title_wave) * 3
        
        self.screen.blit(title_shadow, (title_x + 3, title_y + 3))
        self.screen.blit(title_surf, (title_x, title_y))
        
        # Subtitle
        sub_surf = self.font_button.render(subtitle, True, (255, 220, 0))
        sub_shadow = self.font_button.render(subtitle, True, (100, 80, 0))
        sub_x = self.screen_width // 2 - sub_surf.get_width() // 2
        self.screen.blit(sub_shadow, (sub_x + 2, 92))
        self.screen.blit(sub_surf, (sub_x, 90))
        
        # Center text - SAMSOFT PRESENTS
        center_y = self.screen_height // 2 - 40
        
        # "SAMSOFT PRESENTS" text
        presents_font = pygame.font.SysFont('arial', 32, bold=True)
        presents_text = "SAMSOFT PRESENTS"
        presents_surf = presents_font.render(presents_text, True, (255, 255, 255))
        presents_shadow = presents_font.render(presents_text, True, (0, 0, 0))
        presents_x = self.screen_width // 2 - presents_surf.get_width() // 2
        self.screen.blit(presents_shadow, (presents_x + 2, center_y + 2))
        self.screen.blit(presents_surf, (presents_x, center_y))
        
        # "(C) 2025 SM64 PY PORT" text
        copyright_font = pygame.font.SysFont('arial', 24, bold=True)
        copyright_text = "(C) 2025 SM64 PY PORT"
        copyright_surf = copyright_font.render(copyright_text, True, (255, 220, 0))
        copyright_shadow = copyright_font.render(copyright_text, True, (80, 60, 0))
        copyright_x = self.screen_width // 2 - copyright_surf.get_width() // 2
        self.screen.blit(copyright_shadow, (copyright_x + 2, center_y + 42))
        self.screen.blit(copyright_surf, (copyright_x, center_y + 40))
        
        # Buttons - fixed spacing
        btn_width = 220
        btn_height = 50
        btn_x = self.screen_width // 2 - btn_width // 2
        btn_spacing = 60
        btn_start_y = self.screen_height - 200
        
        mouse_pos = pygame.mouse.get_pos()
        
        # START button
        self.start_rect = pygame.Rect(btn_x, btn_start_y, btn_width, btn_height)
        self.hover_start = self.start_rect.collidepoint(mouse_pos)
        self._draw_button(self.start_rect, "START", True, self.hover_start)
        
        # OPTIONS button (greyed)
        self.options_rect = pygame.Rect(btn_x, btn_start_y + btn_spacing, btn_width, btn_height)
        self.hover_options = self.options_rect.collidepoint(mouse_pos)
        self._draw_button(self.options_rect, "OPTIONS", False, False)
        
        # EXIT button
        self.exit_rect = pygame.Rect(btn_x, btn_start_y + btn_spacing * 2, btn_width, btn_height)
        self.hover_exit = self.exit_rect.collidepoint(mouse_pos)
        self._draw_button(self.exit_rect, "EXIT", True, self.hover_exit)
        
        # Footer
        footer = self.font_small.render("(C) 2025 SAMSOFT", True, (255, 255, 255))
        footer_shadow = self.font_small.render("(C) 2025 SAMSOFT", True, (0, 0, 0))
        self.screen.blit(footer_shadow, (self.screen_width // 2 - footer.get_width() // 2 + 1, self.screen_height - 21))
        self.screen.blit(footer, (self.screen_width // 2 - footer.get_width() // 2, self.screen_height - 22))
    
    def render_warning(self):
        """Render the warning/WIP screen."""
        self.screen.fill((0, 0, 0))
        
        # Hazard stripes border
        stripe_size = 25
        
        # Draw hazard pattern
        for x in range(0, self.screen_width + stripe_size, stripe_size):
            offset = (x // stripe_size) % 2
            for y_pos in [0, self.screen_height - stripe_size]:
                color = (255, 200, 0) if offset else (30, 30, 30)
                pygame.draw.rect(self.screen, color, (x, y_pos, stripe_size, stripe_size))
        
        for y in range(stripe_size, self.screen_height - stripe_size, stripe_size):
            offset = (y // stripe_size) % 2
            for x_pos in [0, self.screen_width - stripe_size]:
                color = (255, 200, 0) if offset else (30, 30, 30)
                pygame.draw.rect(self.screen, color, (x_pos, y, stripe_size, stripe_size))
        
        # Glitch effect
        self.glitch_timer += 1
        if self.glitch_timer % 4 == 0:
            self.glitch_color = random.choice([
                (255, 50, 50), (255, 255, 50), (255, 100, 100), (200, 200, 50)
            ])
            self.glitch_offset_x = random.randint(-3, 3)
            self.glitch_offset_y = random.randint(-3, 3)
        
        # Warning icon
        icon_size = 60
        icon_x = self.screen_width // 2
        icon_y = self.screen_height // 2 - 80
        
        # Triangle
        points = [
            (icon_x, icon_y - icon_size//2),
            (icon_x - icon_size//2, icon_y + icon_size//2),
            (icon_x + icon_size//2, icon_y + icon_size//2)
        ]
        pygame.draw.polygon(self.screen, (255, 200, 0), points)
        pygame.draw.polygon(self.screen, (0, 0, 0), points, 4)
        
        # Exclamation mark
        exc_font = pygame.font.SysFont('arial', 40, bold=True)
        exc = exc_font.render("!", True, (0, 0, 0))
        self.screen.blit(exc, (icon_x - exc.get_width()//2, icon_y - 5))
        
        # Warning message - with glitch
        message = "[ AREA UNDER CONSTRUCTION ]"
        text = self.font_warning.render(message, True, self.glitch_color)
        text_x = self.screen_width // 2 - text.get_width() // 2 + self.glitch_offset_x
        text_y = self.screen_height // 2 + self.glitch_offset_y
        self.screen.blit(text, (text_x, text_y))
        
        # Sub message
        sub_msg = "STANLEY HASN'T FINISHED THIS LEVEL"
        sub_text = self.font_small.render(sub_msg, True, (180, 180, 180))
        self.screen.blit(sub_text, (self.screen_width // 2 - sub_text.get_width() // 2, text_y + 35))
        
        # Contact info
        contact = "Contact SAMSOFT Support on Discord"
        contact_text = self.font_small.render(contact, True, (100, 150, 255))
        self.screen.blit(contact_text, (self.screen_width // 2 - contact_text.get_width() // 2, text_y + 60))
        
        # ESC hint
        esc_hint = self.font_small.render("Press ESC to return", True, (120, 120, 120))
        self.screen.blit(esc_hint, (self.screen_width // 2 - esc_hint.get_width() // 2, self.screen_height - 60))
    
    def render_game(self):
        """Render the actual game (placeholder)."""
        self.screen.fill((50, 50, 80))
        
        placeholder = self.font_title.render("GAME MODE", True, (255, 255, 255))
        self.screen.blit(placeholder, 
                        (self.screen_width // 2 - placeholder.get_width() // 2,
                         self.screen_height // 2 - placeholder.get_height() // 2))
        
        hint = self.font_small.render("Press ESC to return to menu", True, (180, 180, 180))
        self.screen.blit(hint, (self.screen_width // 2 - hint.get_width() // 2, self.screen_height - 50))
    
    def handle_events(self):
        """Process input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.current_state in (MenuState.WARNING, MenuState.GAME):
                        self.current_state = MenuState.MAIN_MENU
                    else:
                        self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    
                    if self.current_state == MenuState.MAIN_MENU:
                        if self.start_rect.collidepoint(mouse_pos):
                            self.current_state = MenuState.WARNING
                        elif self.exit_rect.collidepoint(mouse_pos):
                            self.running = False
    
    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()
            
            # Render current state
            if self.current_state == MenuState.MAIN_MENU:
                self.render_menu()
            elif self.current_state == MenuState.WARNING:
                self.render_warning()
            elif self.current_state == MenuState.GAME:
                self.render_game()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    print("=" * 50)
    print("  SUPER MARIO 64 DS - XD EDITION")
    print("  Ultra Mario 4KX v1.0.1")
    print("  (C) 2025 SAMSOFT")
    print("=" * 50)
    
    game = SM64DSGame()
    game.run()
