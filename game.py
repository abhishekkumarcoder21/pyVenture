"""
PyVenture: The Code Warrior - Game Module
Main game loop with collectibles, challenges, and particle effects.
"""

import pygame
import re
import random
from typing import Optional, List
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GAME_TITLE,
    TILE_SIZE, GRID_COLS, GRID_ROWS, GAME_AREA_X, GAME_AREA_Y,
    COLOR_BG_DARK, COLOR_BG_MEDIUM, COLOR_GRID_LINE,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    COLOR_SUCCESS, COLOR_ERROR, COLOR_ACCENT, COLOR_WARNING, COLOR_SECONDARY,
    FONT_NAME, FONT_SIZE_LARGE, FONT_SIZE_SMALL, FONT_SIZE_MEDIUM,
    VALID_HERO_METHODS,
)
from ui import Console
from sprites import (
    Player, GameGrid, Hero, Direction,
    Collectible, Obstacle, ParticleSystem, FloatingText
)


class Challenge:
    """A coding challenge for the player to complete."""
    
    def __init__(self, title: str, description: str, 
                 target_col: int, target_row: int, reward: int = 50):
        self.title = title
        self.description = description
        self.target_col = target_col
        self.target_row = target_row
        self.reward = reward
        self.completed = False
    
    def check_completion(self, player_col: int, player_row: int) -> bool:
        """Check if challenge is completed."""
        if player_col == self.target_col and player_row == self.target_row:
            self.completed = True
            return True
        return False


class Game:
    """
    Main game class with collectibles, obstacles, and challenges.
    """
    
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        pygame.font.init()
        
        # Create display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)
        
        # Clock for frame rate
        self.clock = pygame.time.Clock()
        
        # Game state
        self.running: bool = True
        self.paused: bool = False
        
        # Particle system
        self.particles = ParticleSystem()
        
        # Floating texts
        self.floating_texts: List[FloatingText] = []
        
        # Create obstacles first
        self.obstacles = self._create_obstacles()
        
        # Create collectibles
        self.collectibles = self._create_collectibles()
        
        # Create game objects
        self.grid = GameGrid()
        self.player = Player(obstacles=self.obstacles)
        self.player.particles = self.particles
        self.hero = Hero(self.player)
        
        # Create UI
        self.console = Console()
        self.console.on_command = self._handle_command
        
        # Fonts
        self.font_title = pygame.font.Font(FONT_NAME, FONT_SIZE_LARGE)
        self.font_info = pygame.font.Font(FONT_NAME, FONT_SIZE_SMALL)
        self.font_medium = pygame.font.Font(FONT_NAME, FONT_SIZE_MEDIUM)
        
        # Scoring
        self.score: int = 0
        self.gems_collected: int = 0
        
        # Stats tracking
        self.commands_executed: int = 0
        self.successful_moves: int = 0
        
        # Challenges
        self.challenges = self._create_challenges()
        self.current_challenge_idx = 0
        self.challenges_completed = 0
        
        # Show initial challenge
        self._show_current_challenge()
    
    def _create_obstacles(self) -> List[Obstacle]:
        """Create obstacles for the level."""
        obstacles = []
        
        # Create a fun maze-like pattern
        obstacle_positions = [
            (2, 2, 'rock'),
            (2, 3, 'rock'),
            (3, 6, 'crate'),
            (4, 6, 'crate'),
            (7, 2, 'bush'),
            (8, 2, 'bush'),
            (9, 5, 'rock'),
            (10, 5, 'rock'),
            (6, 4, 'crate'),
        ]
        
        for col, row, obs_type in obstacle_positions:
            obstacles.append(Obstacle(col, row, obs_type))
        
        return obstacles
    
    def _create_collectibles(self) -> List[Collectible]:
        """Create collectible gems."""
        collectibles = []
        
        # Avoid player start position and obstacles
        blocked_positions = {(obs.grid_col, obs.grid_row) for obs in self.obstacles}
        blocked_positions.add((5, 4))  # Player start
        
        # Place gems at specific locations
        gem_positions = [
            (1, 1, 'ruby'),
            (10, 1, 'sapphire'),
            (0, 7, 'emerald'),
            (11, 8, 'gold'),
            (6, 7, 'diamond'),
            (3, 3, 'ruby'),
            (8, 5, 'emerald'),
        ]
        
        for col, row, gem_type in gem_positions:
            if (col, row) not in blocked_positions:
                collectibles.append(Collectible(col, row, gem_type))
        
        return collectibles
    
    def _create_challenges(self) -> List[Challenge]:
        """Create gameplay challenges."""
        return [
            Challenge(
                "First Steps",
                "Move to the ruby gem at (1, 1)!",
                1, 1, 25
            ),
            Challenge(
                "Adventure Awaits",
                "Find the diamond at (6, 7)!",
                6, 7, 50
            ),
            Challenge(
                "Explorer",
                "Reach the corner at (11, 8)!",
                11, 8, 75
            ),
        ]
    
    def _show_current_challenge(self) -> None:
        """Display current challenge in console."""
        if self.current_challenge_idx < len(self.challenges):
            challenge = self.challenges[self.current_challenge_idx]
            self.console.add_output("", COLOR_TEXT_MUTED)
            self.console.add_output("🎯 NEW CHALLENGE!", COLOR_WARNING)
            self.console.add_output(f"   {challenge.title}", COLOR_ACCENT)
            self.console.add_output(f"   {challenge.description}", COLOR_TEXT_SECONDARY)
            self.console.add_output(f"   Reward: {challenge.reward} points", COLOR_SUCCESS)
            self.console.add_output("", COLOR_TEXT_MUTED)
    
    def run(self) -> None:
        """Main game loop."""
        while self.running:
            dt = self.clock.tick(FPS)
            
            self._handle_events()
            
            if not self.paused:
                self._update(dt)
            
            self._render()
        
        self._cleanup()
    
    def _handle_events(self) -> None:
        """Handle all pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_F5:
                    self._reset_game()
                else:
                    self.console.handle_event(event)
    
    def _update(self, dt: int) -> None:
        """Update game state."""
        self.console.update(dt)
        self.player.update(dt)
        
        # Update collectibles
        for gem in self.collectibles:
            gem.update(dt)
        
        # Update particles
        self.particles.update()
        
        # Update floating texts
        for text in self.floating_texts:
            text.update()
        self.floating_texts = [t for t in self.floating_texts if t.alive]
        
        # Check collectible collection
        self._check_collections()
        
        # Check challenge completion
        self._check_challenge()
    
    def _check_collections(self) -> None:
        """Check if player collected any gems."""
        player_col = self.player.grid_col
        player_row = self.player.grid_row
        
        for gem in self.collectibles:
            if not gem.collected and gem.grid_col == player_col and gem.grid_row == player_row:
                gem.collected = True
                self.gems_collected += 1
                self.score += gem.value
                
                # Particle effect
                self.particles.emit_collect(gem.x, gem.y, gem.color)
                
                # Floating text
                self.floating_texts.append(FloatingText(
                    f"+{gem.value}",
                    gem.x, gem.y - 20,
                    COLOR_SUCCESS
                ))
                
                # Console message
                self.console.add_success(f"Collected {gem.gem_type.title()} gem! +{gem.value} points")
    
    def _check_challenge(self) -> None:
        """Check if current challenge is complete."""
        if self.current_challenge_idx >= len(self.challenges):
            return
        
        challenge = self.challenges[self.current_challenge_idx]
        if not challenge.completed:
            if challenge.check_completion(self.player.grid_col, self.player.grid_row):
                self.challenges_completed += 1
                self.score += challenge.reward
                
                # Effects
                self.particles.emit_burst(self.player.x, self.player.y, COLOR_SUCCESS, count=20)
                self.floating_texts.append(FloatingText(
                    f"Challenge Complete! +{challenge.reward}",
                    self.player.x, self.player.y - 40,
                    COLOR_WARNING
                ))
                
                # Console message
                self.console.add_output("", COLOR_TEXT_MUTED)
                self.console.add_output("🏆 CHALLENGE COMPLETE!", COLOR_SUCCESS)
                self.console.add_output(f"   {challenge.title} finished!", COLOR_ACCENT)
                self.console.add_output(f"   +{challenge.reward} bonus points!", COLOR_WARNING)
                
                # Move to next challenge
                self.current_challenge_idx += 1
                if self.current_challenge_idx < len(self.challenges):
                    self._show_current_challenge()
                else:
                    self.console.add_output("", COLOR_TEXT_MUTED)
                    self.console.add_output("🎉 ALL CHALLENGES COMPLETE!", COLOR_SUCCESS)
                    self.console.add_output("   You are a true Code Warrior!", COLOR_ACCENT)
    
    def _render(self) -> None:
        """Render all game elements."""
        self.screen.fill(COLOR_BG_DARK)
        
        self._draw_background_pattern()
        self._draw_title()
        
        # Draw game grid
        self.grid.draw(self.screen)
        
        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        
        # Draw collectibles
        for gem in self.collectibles:
            gem.draw(self.screen)
        
        # Draw particles (under player)
        self.particles.draw(self.screen)
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw floating texts
        for text in self.floating_texts:
            text.draw(self.screen)
        
        # Draw console
        self.console.draw(self.screen)
        
        # Draw command reference panel
        self._draw_command_panel()
        
        # Draw stats
        self._draw_stats()
        
        # Draw challenge indicator
        self._draw_challenge_indicator()
        
        # Draw help text
        self._draw_help()
        
        pygame.display.flip()
    
    def _draw_background_pattern(self) -> None:
        """Draw decorative background."""
        for i in range(0, SCREEN_HEIGHT, 4):
            alpha = int(10 + (i / SCREEN_HEIGHT) * 15)
            pygame.draw.line(self.screen, (*COLOR_BG_MEDIUM[:3], alpha),
                           (0, i), (SCREEN_WIDTH, i))
    
    def _draw_title(self) -> None:
        """Draw the game title."""
        title_surf = self.font_title.render("PyVenture", True, COLOR_ACCENT)
        title_x = (SCREEN_WIDTH - title_surf.get_width()) // 2 - 150
        self.screen.blit(title_surf, (title_x, 8))
        
        subtitle_surf = self.font_info.render("The Code Warrior", True, COLOR_TEXT_SECONDARY)
        subtitle_x = title_x + title_surf.get_width() + 10
        self.screen.blit(subtitle_surf, (subtitle_x, 16))
    
    def _draw_stats(self) -> None:
        """Draw game statistics - now integrated into command panel."""
        # Stats are now drawn as part of command panel
        pass
    
    def _draw_challenge_indicator(self) -> None:
        """Draw current challenge indicator."""
        if self.current_challenge_idx < len(self.challenges):
            challenge = self.challenges[self.current_challenge_idx]
            
            # Draw target marker on grid
            target_x = GAME_AREA_X + challenge.target_col * TILE_SIZE + TILE_SIZE // 2
            target_y = GAME_AREA_Y + challenge.target_row * TILE_SIZE + TILE_SIZE // 2
            
            # Pulsing target indicator
            pulse = abs(pygame.time.get_ticks() % 1000 - 500) / 500
            radius = int(TILE_SIZE // 2 - 5 + pulse * 5)
            
            # Draw target circle
            target_surf = pygame.Surface((radius * 2 + 10, radius * 2 + 10), pygame.SRCALPHA)
            pygame.draw.circle(target_surf, (*COLOR_WARNING, 100),
                             (radius + 5, radius + 5), radius, 3)
            self.screen.blit(target_surf, 
                           (target_x - radius - 5, target_y - radius - 5))
    
    def _draw_command_panel(self) -> None:
        """Draw the command reference panel for students - clean organized layout."""
        # Panel position - below the game grid
        panel_x = GAME_AREA_X
        panel_y = GAME_AREA_Y + (GRID_ROWS * TILE_SIZE) + 10
        panel_width = GRID_COLS * TILE_SIZE
        panel_height = 95
        
        # Draw panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        panel_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (20, 22, 35, 240), panel_surf.get_rect(), border_radius=10)
        self.screen.blit(panel_surf, (panel_x, panel_y))
        
        # Draw border
        pygame.draw.rect(self.screen, COLOR_ACCENT, panel_rect, width=2, border_radius=10)
        
        # === ROW 1: Title and Stats ===
        row1_y = panel_y + 10
        
        # Title
        title_surf = self.font_info.render("Commands:", True, COLOR_WARNING)
        self.screen.blit(title_surf, (panel_x + 15, row1_y))
        
        # Stats on the right side of row 1
        stats_x = panel_x + 180
        score_surf = self.font_info.render(f"Score: {self.score}", True, COLOR_SUCCESS)
        self.screen.blit(score_surf, (stats_x, row1_y))
        
        gems_surf = self.font_info.render(f"Gems: {self.gems_collected}/{len(self.collectibles)}", True, COLOR_ACCENT)
        self.screen.blit(gems_surf, (stats_x + 120, row1_y))
        
        pos_surf = self.font_info.render(f"Pos: ({self.player.grid_col},{self.player.grid_row})", True, COLOR_TEXT_MUTED)
        self.screen.blit(pos_surf, (stats_x + 250, row1_y))
        
        # Separator line
        pygame.draw.line(self.screen, COLOR_GRID_LINE, 
                        (panel_x + 10, row1_y + 25), 
                        (panel_x + panel_width - 10, row1_y + 25), 1)
        
        # === ROW 2: Movement Commands ===
        row2_y = panel_y + 42
        
        # Movement commands with arrows
        move_commands = [
            ("hero.move_up()", COLOR_SUCCESS),
            ("hero.move_down()", COLOR_SUCCESS),
            ("hero.move_left()", COLOR_SUCCESS),
            ("hero.move_right()", COLOR_SUCCESS),
        ]
        
        cmd_spacing = (panel_width - 40) // 4
        
        for i, (cmd, color) in enumerate(move_commands):
            cmd_x = panel_x + 20 + (i * cmd_spacing)
            cmd_surf = self.font_info.render(cmd, True, color)
            self.screen.blit(cmd_surf, (cmd_x, row2_y))
        
        # === ROW 3: Extra Commands ===
        row3_y = panel_y + 68
        
        extra_commands = [
            ("hero.spin()", COLOR_SECONDARY),
            ("hero.dance()", COLOR_SECONDARY),
            ("help", COLOR_TEXT_MUTED),
            ("hint", COLOR_TEXT_MUTED),
        ]
        
        for i, (cmd, color) in enumerate(extra_commands):
            cmd_x = panel_x + 20 + (i * cmd_spacing)
            cmd_surf = self.font_info.render(cmd, True, color)
            self.screen.blit(cmd_surf, (cmd_x, row3_y))
    
    def _draw_help(self) -> None:
        """Draw help text at bottom right."""
        help_y = SCREEN_HEIGHT - 25
        
        help_text = "F5: Reset  |  ESC: Quit"
        help_surf = self.font_info.render(help_text, True, COLOR_TEXT_MUTED)
        help_x = SCREEN_WIDTH - help_surf.get_width() - 50
        self.screen.blit(help_surf, (help_x, help_y))
    
    def _handle_command(self, command: str) -> None:
        """Execute a command from the console."""
        self.commands_executed += 1
        
        command = command.strip()
        
        if not command:
            return
        
        # Special commands
        if command.lower() == "help":
            self._show_help()
            return
        
        if command.lower() == "clear":
            self.console.clear()
            return
        
        if command.lower() == "hint":
            self._show_hint()
            return
        
        try:
            result = self._execute_hero_command(command)
            if result:
                self.console.add_success(result)
                if "Moving" in result:
                    self.successful_moves += 1
        
        except SyntaxError:
            self.console.add_educational_error(command, "syntax")
        
        except NameError:
            self.console.add_educational_error(command, "name")
        
        except AttributeError:
            self.console.add_educational_error(command, "unknown_method")
        
        except Exception as e:
            self.console.add_educational_error(command, "unknown")
    
    def _show_help(self) -> None:
        """Show available commands."""
        self.console.add_output("", COLOR_TEXT_MUTED)
        self.console.add_output("📖 Available Commands:", COLOR_ACCENT)
        self.console.add_output("  hero.move_right()  - Move right", COLOR_TEXT_SECONDARY)
        self.console.add_output("  hero.move_left()   - Move left", COLOR_TEXT_SECONDARY)
        self.console.add_output("  hero.move_up()     - Move up", COLOR_TEXT_SECONDARY)
        self.console.add_output("  hero.move_down()   - Move down", COLOR_TEXT_SECONDARY)
        self.console.add_output("  hero.spin()        - Spin around", COLOR_TEXT_SECONDARY)
        self.console.add_output("  hero.dance()       - Do a dance", COLOR_TEXT_SECONDARY)
        self.console.add_output("  hero.say('text')   - Speak", COLOR_TEXT_SECONDARY)
        self.console.add_output("", COLOR_TEXT_MUTED)
        self.console.add_output("📖 Special Commands:", COLOR_ACCENT)
        self.console.add_output("  help  - Show this help", COLOR_TEXT_SECONDARY)
        self.console.add_output("  hint  - Get a hint", COLOR_TEXT_SECONDARY)
        self.console.add_output("  clear - Clear console", COLOR_TEXT_SECONDARY)
        self.console.add_output("", COLOR_TEXT_MUTED)
    
    def _show_hint(self) -> None:
        """Show a hint for the current challenge."""
        if self.current_challenge_idx >= len(self.challenges):
            self.console.add_info("All challenges complete! Try collecting all gems.")
            return
        
        challenge = self.challenges[self.current_challenge_idx]
        player_col = self.player.grid_col
        player_row = self.player.grid_row
        
        dx = challenge.target_col - player_col
        dy = challenge.target_row - player_row
        
        hints = []
        if dx > 0:
            hints.append(f"Move right {dx} times")
        elif dx < 0:
            hints.append(f"Move left {abs(dx)} times")
        
        if dy > 0:
            hints.append(f"Move down {dy} times")
        elif dy < 0:
            hints.append(f"Move up {abs(dy)} times")
        
        self.console.add_output("", COLOR_TEXT_MUTED)
        self.console.add_output("💡 Hint:", COLOR_WARNING)
        for hint in hints:
            self.console.add_output(f"   {hint}", COLOR_TEXT_SECONDARY)
        self.console.add_output("   (Watch out for obstacles!)", COLOR_TEXT_MUTED)
        self.console.add_output("", COLOR_TEXT_MUTED)
    
    def _execute_hero_command(self, command: str) -> Optional[str]:
        """Safely execute a hero command."""
        if not command:
            return None
        
        if not command.startswith("hero."):
            raise NameError("Command must start with 'hero.'")
        
        pattern = r'^hero\.(\w+)\((.*)\)$'
        match = re.match(pattern, command)
        
        if not match:
            raise SyntaxError("Invalid command syntax")
        
        method_name = match.group(1)
        args_str = match.group(2).strip()
        
        # Extended valid methods
        valid_methods = VALID_HERO_METHODS + ['spin', 'dance', 'collect']
        
        if method_name not in valid_methods:
            raise AttributeError(f"Unknown method: {method_name}")
        
        if not hasattr(self.hero, method_name):
            raise AttributeError(f"Method not implemented: {method_name}")
        
        method = getattr(self.hero, method_name)
        
        if args_str:
            if args_str.startswith('"') and args_str.endswith('"'):
                arg = args_str[1:-1]
                return method(arg)
            elif args_str.startswith("'") and args_str.endswith("'"):
                arg = args_str[1:-1]
                return method(arg)
            else:
                try:
                    arg = eval(args_str)
                    return method(arg)
                except:
                    raise SyntaxError("Invalid argument")
        else:
            return method()
    
    def _reset_game(self) -> None:
        """Reset the game state."""
        self.player.reset_position()
        
        # Reset collectibles
        self.collectibles = self._create_collectibles()
        
        # Reset challenges
        for challenge in self.challenges:
            challenge.completed = False
        self.current_challenge_idx = 0
        
        # Reset scores
        self.score = 0
        self.gems_collected = 0
        self.commands_executed = 0
        self.successful_moves = 0
        self.challenges_completed = 0
        
        # Clear effects
        self.particles.particles.clear()
        self.floating_texts.clear()
        
        # Reset console
        self.console.clear()
        self.console.add_info("Game reset! Ready for new adventure.")
        self._show_current_challenge()
    
    def _cleanup(self) -> None:
        """Clean up resources."""
        pygame.quit()
