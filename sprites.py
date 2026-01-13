"""
PyVenture: The Code Warrior - Sprites Module
Player, tiles, collectibles, obstacles, and particle effects.
"""

import pygame
import math
import random
from typing import Tuple, Optional, List
from enum import Enum
from settings import (
    TILE_SIZE, GRID_COLS, GRID_ROWS,
    GAME_AREA_X, GAME_AREA_Y,
    PLAYER_START_COL, PLAYER_START_ROW, PLAYER_MOVE_SPEED,
    PLAYER_ANIMATION_FRAMES,
    COLOR_PLAYER, COLOR_PLAYER_GLOW,
    COLOR_BG_LIGHT, COLOR_GRID_LINE, COLOR_GRID_ACCENT,
    COLOR_SUCCESS, COLOR_ACCENT, COLOR_WARNING, COLOR_ERROR,
    COLOR_TEXT_PRIMARY, COLOR_SECONDARY,
    FONT_SIZE_SMALL, FONT_NAME,
)


class Direction(Enum):
    """Movement directions."""
    NONE = 0
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


class Particle:
    """A single particle for visual effects."""
    
    def __init__(self, x: float, y: float, color: Tuple[int, int, int],
                 velocity: Tuple[float, float], lifetime: int = 30,
                 size: float = 4.0, gravity: float = 0.0):
        self.x = x
        self.y = y
        self.color = color
        self.vx, self.vy = velocity
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.gravity = gravity
        self.alive = True
    
    def update(self) -> None:
        """Update particle position and lifetime."""
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.alive = False
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the particle with fading alpha."""
        if not self.alive:
            return
        
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        current_size = int(self.size * (self.lifetime / self.max_lifetime))
        if current_size < 1:
            current_size = 1
        
        # Create particle surface with alpha
        particle_surf = pygame.Surface((current_size * 2, current_size * 2), pygame.SRCALPHA)
        particle_color = (*self.color, alpha)
        pygame.draw.circle(particle_surf, particle_color, 
                          (current_size, current_size), current_size)
        surface.blit(particle_surf, (int(self.x - current_size), int(self.y - current_size)))


class ParticleSystem:
    """Manages multiple particle effects."""
    
    def __init__(self):
        self.particles: List[Particle] = []
    
    def emit_burst(self, x: float, y: float, color: Tuple[int, int, int],
                   count: int = 10, speed: float = 3.0) -> None:
        """Emit a burst of particles."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            vel_speed = random.uniform(speed * 0.5, speed)
            vx = math.cos(angle) * vel_speed
            vy = math.sin(angle) * vel_speed
            size = random.uniform(3, 6)
            lifetime = random.randint(20, 40)
            self.particles.append(Particle(x, y, color, (vx, vy), lifetime, size))
    
    def emit_trail(self, x: float, y: float, color: Tuple[int, int, int],
                   direction: Direction) -> None:
        """Emit trail particles behind movement."""
        for _ in range(2):
            offset_x = random.uniform(-5, 5)
            offset_y = random.uniform(-5, 5)
            vx = random.uniform(-0.5, 0.5)
            vy = random.uniform(-0.5, 0.5)
            
            # Add velocity opposite to direction
            if direction == Direction.RIGHT:
                vx -= 1.5
            elif direction == Direction.LEFT:
                vx += 1.5
            elif direction == Direction.UP:
                vy += 1.5
            elif direction == Direction.DOWN:
                vy -= 1.5
            
            self.particles.append(Particle(
                x + offset_x, y + offset_y, color,
                (vx, vy), lifetime=15, size=4
            ))
    
    def emit_collect(self, x: float, y: float, color: Tuple[int, int, int]) -> None:
        """Emit collection sparkle effect."""
        for i in range(12):
            angle = (2 * math.pi / 12) * i
            speed = random.uniform(2, 4)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            self.particles.append(Particle(
                x, y, color, (vx, vy), 
                lifetime=25, size=5, gravity=-0.1
            ))
    
    def emit_spin(self, x: float, y: float) -> None:
        """Emit spinning effect around the player."""
        colors = [COLOR_ACCENT, COLOR_SUCCESS, COLOR_WARNING, COLOR_SECONDARY]
        for i in range(20):
            angle = (2 * math.pi / 20) * i
            radius = 30
            px = x + math.cos(angle) * radius
            py = y + math.sin(angle) * radius
            # Particles move outward
            vx = math.cos(angle) * 2
            vy = math.sin(angle) * 2
            color = random.choice(colors)
            self.particles.append(Particle(px, py, color, (vx, vy), lifetime=30, size=5))
    
    def update(self) -> None:
        """Update all particles."""
        for particle in self.particles:
            particle.update()
        # Remove dead particles
        self.particles = [p for p in self.particles if p.alive]
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw all particles."""
        for particle in self.particles:
            particle.draw(surface)


class FloatingText:
    """Floating text that rises and fades."""
    
    def __init__(self, text: str, x: float, y: float, 
                 color: Tuple[int, int, int] = COLOR_SUCCESS):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = 60  # frames
        self.max_lifetime = 60
        self.vy = -1.5  # Rise speed
        self.alive = True
        self.font = pygame.font.Font(FONT_NAME, FONT_SIZE_SMALL)
    
    def update(self) -> None:
        """Update position and lifetime."""
        self.y += self.vy
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.alive = False
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw with fading effect."""
        if not self.alive:
            return
        
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        text_surf = self.font.render(self.text, True, self.color)
        text_surf.set_alpha(alpha)
        
        # Center the text
        rect = text_surf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(text_surf, rect)


class Collectible(pygame.sprite.Sprite):
    """A collectible gem that the player can pick up."""
    
    GEM_COLORS = {
        'ruby': (239, 68, 68),      # Red
        'emerald': (52, 211, 153),  # Green
        'sapphire': (59, 130, 246), # Blue
        'gold': (251, 191, 36),     # Gold
        'diamond': (226, 232, 240), # White/Diamond
    }
    
    GEM_VALUES = {
        'ruby': 10,
        'emerald': 15,
        'sapphire': 20,
        'gold': 25,
        'diamond': 50,
    }
    
    def __init__(self, col: int, row: int, gem_type: str = 'ruby'):
        super().__init__()
        self.grid_col = col
        self.grid_row = row
        self.gem_type = gem_type
        self.color = self.GEM_COLORS.get(gem_type, self.GEM_COLORS['ruby'])
        self.value = self.GEM_VALUES.get(gem_type, 10)
        
        # Position
        self.x = GAME_AREA_X + col * TILE_SIZE + TILE_SIZE // 2
        self.y = GAME_AREA_Y + row * TILE_SIZE + TILE_SIZE // 2
        
        # Animation
        self.bob_offset = random.uniform(0, 2 * math.pi)
        self.bob_timer = self.bob_offset
        self.rotation = 0
        self.glow_alpha = 100
        
        # Create image
        self.size = 24
        self._create_image()
        
        self.collected = False
    
    def _create_image(self) -> None:
        """Create the gem sprite."""
        padding = 10
        full_size = self.size + padding * 2
        self.image = pygame.Surface((full_size, full_size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))
    
    def update(self, dt: int = 16) -> None:
        """Update gem animation."""
        if self.collected:
            return
        
        # Bob up and down
        self.bob_timer += 0.08
        bob_y = math.sin(self.bob_timer) * 4
        
        # Rotate
        self.rotation += 2
        if self.rotation >= 360:
            self.rotation -= 360
        
        # Pulsing glow
        self.glow_alpha = 80 + int(math.sin(self.bob_timer * 1.5) * 40)
        
        # Update rect for bobbing
        self.rect.centery = int(self.y + bob_y)
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the gem with effects."""
        if self.collected:
            return
        
        x, y = self.rect.center
        
        # Draw glow
        glow_size = self.size + 12
        glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        glow_color = (*self.color, self.glow_alpha)
        pygame.draw.circle(glow_surf, glow_color, (glow_size, glow_size), glow_size)
        surface.blit(glow_surf, (x - glow_size, y - glow_size))
        
        # Draw gem (diamond shape)
        half = self.size // 2
        points = [
            (x, y - half),      # Top
            (x + half, y),      # Right
            (x, y + half),      # Bottom
            (x - half, y),      # Left
        ]
        pygame.draw.polygon(surface, self.color, points)
        
        # Inner highlight
        inner_half = half - 4
        inner_points = [
            (x, y - inner_half + 2),
            (x + inner_half - 2, y),
            (x, y + inner_half - 4),
            (x - inner_half + 2, y - 2),
        ]
        highlight_color = tuple(min(c + 60, 255) for c in self.color)
        pygame.draw.polygon(surface, highlight_color, inner_points)
        
        # Sparkle
        if random.random() < 0.05:
            spark_x = x + random.randint(-half, half)
            spark_y = y + random.randint(-half, half)
            pygame.draw.circle(surface, (255, 255, 255), (spark_x, spark_y), 2)


class Obstacle(pygame.sprite.Sprite):
    """An obstacle that blocks player movement."""
    
    OBSTACLE_TYPES = {
        'rock': (100, 100, 110),
        'crate': (139, 90, 43),
        'bush': (34, 139, 34),
    }
    
    def __init__(self, col: int, row: int, obstacle_type: str = 'rock'):
        super().__init__()
        self.grid_col = col
        self.grid_row = row
        self.obstacle_type = obstacle_type
        self.color = self.OBSTACLE_TYPES.get(obstacle_type, (100, 100, 110))
        
        # Position
        self.x = GAME_AREA_X + col * TILE_SIZE + TILE_SIZE // 2
        self.y = GAME_AREA_Y + row * TILE_SIZE + TILE_SIZE // 2
        
        self.size = TILE_SIZE - 8
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.rect.center = (int(self.x), int(self.y))
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the obstacle."""
        x, y = int(self.x), int(self.y)
        half = self.size // 2
        
        if self.obstacle_type == 'rock':
            # Draw rock shape
            pygame.draw.ellipse(surface, self.color,
                               (x - half, y - half + 5, self.size, self.size - 10))
            # Highlight
            pygame.draw.ellipse(surface, (130, 130, 140),
                               (x - half + 8, y - half + 10, self.size - 20, self.size - 25))
        
        elif self.obstacle_type == 'crate':
            # Draw crate
            rect = pygame.Rect(x - half, y - half, self.size, self.size)
            pygame.draw.rect(surface, self.color, rect, border_radius=4)
            # Cross lines
            pygame.draw.line(surface, (100, 60, 30),
                           (x - half, y - half), (x + half, y + half), 3)
            pygame.draw.line(surface, (100, 60, 30),
                           (x + half, y - half), (x - half, y + half), 3)
            # Border
            pygame.draw.rect(surface, (100, 60, 30), rect, width=3, border_radius=4)
        
        elif self.obstacle_type == 'bush':
            # Draw bush (multiple circles)
            pygame.draw.circle(surface, self.color, (x - 10, y + 5), 18)
            pygame.draw.circle(surface, self.color, (x + 10, y + 5), 18)
            pygame.draw.circle(surface, self.color, (x, y - 8), 20)
            # Darker core
            pygame.draw.circle(surface, (24, 100, 24), (x, y), 12)


class Player(pygame.sprite.Sprite):
    """
    Hero character with grid-based movement.
    
    Features:
    - Smooth animation between grid cells
    - Visual glow effect
    - Direction tracking
    - Boundary checking
    - Special actions (spin, dance)
    """
    
    def __init__(self, col: int = PLAYER_START_COL, row: int = PLAYER_START_ROW,
                 obstacles: List[Obstacle] = None):
        super().__init__()
        
        # Grid position
        self.grid_col: int = col
        self.grid_row: int = row
        
        # Pixel position (for smooth animation)
        self.x: float = self._grid_to_pixel_x(col)
        self.y: float = self._grid_to_pixel_y(row)
        
        # Target position for smooth movement
        self.target_x: float = self.x
        self.target_y: float = self.y
        
        # Movement state
        self.is_moving: bool = False
        self.direction: Direction = Direction.NONE
        self.move_speed: float = PLAYER_MOVE_SPEED
        
        # Special actions
        self.is_spinning: bool = False
        self.spin_timer: float = 0
        self.is_dancing: bool = False
        self.dance_timer: float = 0
        self.dance_offset: float = 0
        
        # Obstacles reference
        self.obstacles = obstacles or []
        
        # Visual properties
        self.size: int = TILE_SIZE - 16
        self.color: Tuple[int, int, int] = COLOR_PLAYER
        self.glow_color: Tuple[int, int, int] = COLOR_PLAYER_GLOW
        
        # Animation
        self.pulse_timer: float = 0
        self.pulse_speed: float = 0.05
        self.eye_direction: Direction = Direction.NONE
        
        # Particle system reference (set by game)
        self.particles: Optional[ParticleSystem] = None
        
        # Create sprite image
        self._create_image()
    
    def _create_image(self) -> None:
        """Create the player sprite image."""
        padding = 8
        full_size = self.size + padding * 2
        self.image = pygame.Surface((full_size, full_size), pygame.SRCALPHA)
        
        # Draw glow effect
        glow_surf = pygame.Surface((full_size, full_size), pygame.SRCALPHA)
        for i in range(3, 0, -1):
            alpha = 30 * i
            glow_rect = pygame.Rect(
                padding - i * 2, padding - i * 2,
                self.size + i * 4, self.size + i * 4
            )
            glow_color = (*self.glow_color, alpha)
            pygame.draw.rect(glow_surf, glow_color, glow_rect, border_radius=12)
        self.image.blit(glow_surf, (0, 0))
        
        # Draw main body
        body_rect = pygame.Rect(padding, padding, self.size, self.size)
        pygame.draw.rect(self.image, self.color, body_rect, border_radius=10)
        
        # Draw inner highlight
        highlight_rect = pygame.Rect(
            padding + 4, padding + 4,
            self.size - 8, self.size // 2 - 4
        )
        highlight_color = (*COLOR_ACCENT, 100)
        highlight_surf = pygame.Surface((highlight_rect.width, highlight_rect.height), 
                                        pygame.SRCALPHA)
        pygame.draw.rect(highlight_surf, highlight_color, 
                        highlight_surf.get_rect(), border_radius=6)
        self.image.blit(highlight_surf, highlight_rect.topleft)
        
        # Draw eyes
        eye_y = padding + self.size // 3
        eye_size = 8
        left_eye_x = padding + self.size // 3 - eye_size // 2
        right_eye_x = padding + 2 * self.size // 3 - eye_size // 2
        
        pygame.draw.ellipse(self.image, (255, 255, 255),
                           (left_eye_x, eye_y, eye_size, eye_size + 2))
        pygame.draw.ellipse(self.image, (255, 255, 255),
                           (right_eye_x, eye_y, eye_size, eye_size + 2))
        
        # Eye pupils (will be updated based on direction)
        pupil_size = 4
        pupil_offset_x = 0
        pupil_offset_y = 0
        
        if self.eye_direction == Direction.LEFT:
            pupil_offset_x = -2
        elif self.eye_direction == Direction.RIGHT:
            pupil_offset_x = 2
        elif self.eye_direction == Direction.UP:
            pupil_offset_y = -2
        elif self.eye_direction == Direction.DOWN:
            pupil_offset_y = 2
        
        pygame.draw.ellipse(self.image, (30, 30, 40),
                           (left_eye_x + 2 + pupil_offset_x, 
                            eye_y + 2 + pupil_offset_y, pupil_size, pupil_size + 1))
        pygame.draw.ellipse(self.image, (30, 30, 40),
                           (right_eye_x + 2 + pupil_offset_x, 
                            eye_y + 2 + pupil_offset_y, pupil_size, pupil_size + 1))
        
        # Create rect for positioning
        self.rect = self.image.get_rect()
        self._update_rect()
    
    def _grid_to_pixel_x(self, col: int) -> float:
        """Convert grid column to pixel X coordinate."""
        return GAME_AREA_X + col * TILE_SIZE + TILE_SIZE // 2
    
    def _grid_to_pixel_y(self, row: int) -> float:
        """Convert grid row to pixel Y coordinate."""
        return GAME_AREA_Y + row * TILE_SIZE + TILE_SIZE // 2
    
    def _update_rect(self) -> None:
        """Update rect position based on pixel coordinates."""
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y + self.dance_offset)
    
    def _is_blocked(self, col: int, row: int) -> bool:
        """Check if a grid position is blocked by an obstacle."""
        for obstacle in self.obstacles:
            if obstacle.grid_col == col and obstacle.grid_row == row:
                return True
        return False
    
    def move_right(self) -> bool:
        """Move one tile to the right."""
        return self._try_move(1, 0, Direction.RIGHT)
    
    def move_left(self) -> bool:
        """Move one tile to the left."""
        return self._try_move(-1, 0, Direction.LEFT)
    
    def move_up(self) -> bool:
        """Move one tile up."""
        return self._try_move(0, -1, Direction.UP)
    
    def move_down(self) -> bool:
        """Move one tile down."""
        return self._try_move(0, 1, Direction.DOWN)
    
    def _try_move(self, dx: int, dy: int, direction: Direction) -> bool:
        """
        Try to move in the given direction.
        
        Returns:
            True if movement started, False if blocked or already moving.
        """
        if self.is_moving or self.is_spinning or self.is_dancing:
            return False
        
        new_col = self.grid_col + dx
        new_row = self.grid_row + dy
        
        # Check boundaries
        if not (0 <= new_col < GRID_COLS and 0 <= new_row < GRID_ROWS):
            return False
        
        # Check obstacles
        if self._is_blocked(new_col, new_row):
            return False
        
        # Start movement
        self.grid_col = new_col
        self.grid_row = new_row
        self.target_x = self._grid_to_pixel_x(new_col)
        self.target_y = self._grid_to_pixel_y(new_row)
        self.direction = direction
        self.eye_direction = direction
        self.is_moving = True
        self._create_image()  # Update eye direction
        
        return True
    
    def spin(self) -> bool:
        """Perform a spin action."""
        if self.is_moving or self.is_spinning or self.is_dancing:
            return False
        
        self.is_spinning = True
        self.spin_timer = 0
        
        if self.particles:
            self.particles.emit_spin(self.x, self.y)
        
        return True
    
    def dance(self) -> bool:
        """Perform a dance action."""
        if self.is_moving or self.is_spinning or self.is_dancing:
            return False
        
        self.is_dancing = True
        self.dance_timer = 0
        return True
    
    def update(self, dt: int) -> None:
        """Update player position and animation."""
        # Smooth movement animation
        if self.is_moving:
            # Emit trail particles
            if self.particles and random.random() < 0.5:
                self.particles.emit_trail(self.x, self.y, self.glow_color, self.direction)
            
            # Calculate distance to target
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            
            if distance < self.move_speed:
                # Snap to target
                self.x = self.target_x
                self.y = self.target_y
                self.is_moving = False
                self.direction = Direction.NONE
            else:
                # Move towards target
                self.x += (dx / distance) * self.move_speed
                self.y += (dy / distance) * self.move_speed
            
            self._update_rect()
        
        # Spin animation
        if self.is_spinning:
            self.spin_timer += 1
            if self.spin_timer >= 30:  # 0.5 second spin
                self.is_spinning = False
                self.spin_timer = 0
        
        # Dance animation
        if self.is_dancing:
            self.dance_timer += 1
            self.dance_offset = math.sin(self.dance_timer * 0.3) * 8
            if self.dance_timer >= 60:  # 1 second dance
                self.is_dancing = False
                self.dance_timer = 0
                self.dance_offset = 0
            self._update_rect()
        
        # Pulse animation
        self.pulse_timer += self.pulse_speed
        if self.pulse_timer > 2 * 3.14159:
            self.pulse_timer -= 2 * 3.14159
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the player."""
        if self.is_spinning:
            # Draw rotated during spin
            angle = self.spin_timer * 12
            rotated = pygame.transform.rotate(self.image, angle)
            rect = rotated.get_rect(center=self.rect.center)
            surface.blit(rotated, rect)
        else:
            surface.blit(self.image, self.rect)
    
    def reset_position(self) -> None:
        """Reset player to starting position."""
        self.grid_col = PLAYER_START_COL
        self.grid_row = PLAYER_START_ROW
        self.x = self._grid_to_pixel_x(self.grid_col)
        self.y = self._grid_to_pixel_y(self.grid_row)
        self.target_x = self.x
        self.target_y = self.y
        self.is_moving = False
        self.is_spinning = False
        self.is_dancing = False
        self.direction = Direction.NONE
        self.dance_offset = 0
        self._update_rect()


class GameGrid:
    """
    Visual grid for the game area.
    """
    
    def __init__(self):
        self.cols = GRID_COLS
        self.rows = GRID_ROWS
        self.tile_size = TILE_SIZE
        self.x = GAME_AREA_X
        self.y = GAME_AREA_Y
        self.width = self.cols * self.tile_size
        self.height = self.rows * self.tile_size
        
        # Pre-render grid surface
        self._create_surface()
    
    def _create_surface(self) -> None:
        """Create the pre-rendered grid surface."""
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Fill background
        self.surface.fill(COLOR_BG_LIGHT)
        
        # Draw grid pattern
        for col in range(self.cols + 1):
            x = col * self.tile_size
            width = 2 if col % 3 == 0 else 1
            color = COLOR_GRID_ACCENT if col % 3 == 0 else COLOR_GRID_LINE
            pygame.draw.line(self.surface, color, (x, 0), (x, self.height), width)
        
        for row in range(self.rows + 1):
            y = row * self.tile_size
            width = 2 if row % 3 == 0 else 1
            color = COLOR_GRID_ACCENT if row % 3 == 0 else COLOR_GRID_LINE
            pygame.draw.line(self.surface, color, (0, y), (self.width, y), width)
        
        # Draw corner accents
        accent_size = 8
        accent_color = COLOR_ACCENT
        
        pygame.draw.line(self.surface, accent_color, (0, 0), (accent_size, 0), 3)
        pygame.draw.line(self.surface, accent_color, (0, 0), (0, accent_size), 3)
        pygame.draw.line(self.surface, accent_color, 
                        (self.width - accent_size, 0), (self.width, 0), 3)
        pygame.draw.line(self.surface, accent_color,
                        (self.width - 1, 0), (self.width - 1, accent_size), 3)
        pygame.draw.line(self.surface, accent_color,
                        (0, self.height - 1), (accent_size, self.height - 1), 3)
        pygame.draw.line(self.surface, accent_color,
                        (0, self.height - accent_size), (0, self.height), 3)
        pygame.draw.line(self.surface, accent_color,
                        (self.width - accent_size, self.height - 1), 
                        (self.width, self.height - 1), 3)
        pygame.draw.line(self.surface, accent_color,
                        (self.width - 1, self.height - accent_size),
                        (self.width - 1, self.height), 3)
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the grid."""
        surface.blit(self.surface, (self.x, self.y))
        
        border_rect = pygame.Rect(self.x - 2, self.y - 2, 
                                  self.width + 4, self.height + 4)
        pygame.draw.rect(surface, COLOR_GRID_ACCENT, border_rect, 2, border_radius=4)


class Hero:
    """
    Hero API wrapper for the console commands.
    """
    
    def __init__(self, player: Player):
        self._player = player
        self._last_command_result: Optional[str] = None
    
    def move_right(self) -> str:
        """Move the hero one tile to the right."""
        if self._player.move_right():
            self._last_command_result = "Moving right! →"
            return self._last_command_result
        else:
            if self._player.is_moving:
                self._last_command_result = "Wait! Still moving..."
            elif self._player.is_spinning or self._player.is_dancing:
                self._last_command_result = "Wait! Hero is busy performing..."
            else:
                self._last_command_result = "Can't move right - blocked!"
            return self._last_command_result
    
    def move_left(self) -> str:
        """Move the hero one tile to the left."""
        if self._player.move_left():
            self._last_command_result = "Moving left! ←"
            return self._last_command_result
        else:
            if self._player.is_moving:
                self._last_command_result = "Wait! Still moving..."
            elif self._player.is_spinning or self._player.is_dancing:
                self._last_command_result = "Wait! Hero is busy performing..."
            else:
                self._last_command_result = "Can't move left - blocked!"
            return self._last_command_result
    
    def move_up(self) -> str:
        """Move the hero one tile up."""
        if self._player.move_up():
            self._last_command_result = "Moving up! ↑"
            return self._last_command_result
        else:
            if self._player.is_moving:
                self._last_command_result = "Wait! Still moving..."
            elif self._player.is_spinning or self._player.is_dancing:
                self._last_command_result = "Wait! Hero is busy performing..."
            else:
                self._last_command_result = "Can't move up - blocked!"
            return self._last_command_result
    
    def move_down(self) -> str:
        """Move the hero one tile down."""
        if self._player.move_down():
            self._last_command_result = "Moving down! ↓"
            return self._last_command_result
        else:
            if self._player.is_moving:
                self._last_command_result = "Wait! Still moving..."
            elif self._player.is_spinning or self._player.is_dancing:
                self._last_command_result = "Wait! Hero is busy performing..."
            else:
                self._last_command_result = "Can't move down - blocked!"
            return self._last_command_result
    
    def say(self, message: str = "Hello!") -> str:
        """Make the hero say something."""
        self._last_command_result = f'Hero says: "{message}"'
        return self._last_command_result
    
    def spin(self) -> str:
        """Make the hero spin around."""
        if self._player.spin():
            self._last_command_result = "Wheeeee! 🌀"
            return self._last_command_result
        else:
            self._last_command_result = "Can't spin right now!"
            return self._last_command_result
    
    def dance(self) -> str:
        """Make the hero dance."""
        if self._player.dance():
            self._last_command_result = "💃 Dancing! 🕺"
            return self._last_command_result
        else:
            self._last_command_result = "Can't dance right now!"
            return self._last_command_result
    
    def jump(self) -> str:
        """Make the hero jump."""
        self._last_command_result = "Jump! 🦘 (Visual coming soon...)"
        return self._last_command_result
    
    def attack(self) -> str:
        """Make the hero attack."""
        self._last_command_result = "Attack! ⚔️ (Combat coming soon...)"
        return self._last_command_result
    
    def defend(self) -> str:
        """Make the hero defend."""
        self._last_command_result = "Defend! 🛡️ (Combat coming soon...)"
        return self._last_command_result
    
    def collect(self) -> str:
        """Try to collect an item at current position."""
        self._last_command_result = "Looking for items... (Use auto-collect by walking!)"
        return self._last_command_result
