"""
PyVenture: The Code Warrior - UI Module
Console class with input handling, command history, and visual output log.
"""

import pygame
from typing import List, Tuple, Optional, Callable
from settings import (
    CONSOLE_X, CONSOLE_Y, CONSOLE_WIDTH, CONSOLE_HEIGHT,
    CONSOLE_PADDING, CONSOLE_MAX_HISTORY, CONSOLE_MAX_OUTPUT_LINES,
    COLOR_CONSOLE_BG, COLOR_CONSOLE_BORDER, COLOR_CONSOLE_INPUT_BG,
    COLOR_CONSOLE_PROMPT, COLOR_CONSOLE_CURSOR,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    COLOR_SUCCESS, COLOR_ERROR, COLOR_WARNING, COLOR_ACCENT,
    FONT_SIZE_CONSOLE, FONT_SIZE_TINY, FONT_NAME,
    CURSOR_BLINK_INTERVAL,
    VALID_HERO_METHODS, METHOD_SUGGESTIONS,
)


class OutputLine:
    """Represents a single line in the console output."""
    
    def __init__(self, text: str, color: Tuple[int, int, int], 
                 line_type: str = "normal"):
        self.text = text
        self.color = color
        self.line_type = line_type  # "normal", "command", "success", "error", "info"


class Console:
    """
    Interactive code console for PyVenture.
    
    Features:
    - Text input with cursor and blinking animation
    - Command history with up/down arrow navigation
    - Output log with colored messages
    - Educational error feedback
    """
    
    def __init__(self):
        # Position and dimensions
        self.rect = pygame.Rect(CONSOLE_X, CONSOLE_Y, 
                                CONSOLE_WIDTH, CONSOLE_HEIGHT)
        
        # Input state
        self.input_text: str = ""
        self.cursor_pos: int = 0
        self.cursor_visible: bool = True
        self.cursor_timer: int = 0
        
        # Command history
        self.command_history: List[str] = []
        self.history_index: int = -1
        self.temp_input: str = ""  # Stores current input when browsing history
        
        # Output log
        self.output_lines: List[OutputLine] = []
        
        # Fonts
        self.font = pygame.font.Font(FONT_NAME, FONT_SIZE_CONSOLE)
        self.font_small = pygame.font.Font(FONT_NAME, FONT_SIZE_TINY)
        
        # Visual elements
        self.prompt = ">>> "
        self.title = "Python Console"
        
        # Callback for command execution
        self.on_command: Optional[Callable[[str], None]] = None
        
        # Add welcome message
        self._add_welcome_message()
    
    def _add_welcome_message(self) -> None:
        """Add initial welcome message to console."""
        self.add_output("╔══════════════════════════════════════╗", COLOR_ACCENT)
        self.add_output("║   Welcome to PyVenture Console!     ║", COLOR_ACCENT)
        self.add_output("╚══════════════════════════════════════╝", COLOR_ACCENT)
        self.add_output("", COLOR_TEXT_MUTED)
        self.add_output("Control the hero with Python commands:", COLOR_TEXT_SECONDARY)
        self.add_output("  hero.move_right()", COLOR_SUCCESS)
        self.add_output("  hero.move_left()", COLOR_SUCCESS)
        self.add_output("  hero.move_up()", COLOR_SUCCESS)
        self.add_output("  hero.move_down()", COLOR_SUCCESS)
        self.add_output("", COLOR_TEXT_MUTED)
        self.add_output("Press ↑/↓ to browse command history", COLOR_TEXT_MUTED)
        self.add_output("─" * 40, COLOR_CONSOLE_BORDER[:3])
    
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """
        Handle keyboard events for console input.
        
        Returns:
            Command string if Enter was pressed, None otherwise.
        """
        if event.type != pygame.KEYDOWN:
            return None
        
        # Reset cursor visibility on any keypress
        self.cursor_visible = True
        self.cursor_timer = 0
        
        if event.key == pygame.K_RETURN:
            return self._execute_command()
        
        elif event.key == pygame.K_BACKSPACE:
            self._handle_backspace()
        
        elif event.key == pygame.K_DELETE:
            self._handle_delete()
        
        elif event.key == pygame.K_LEFT:
            self._move_cursor_left()
        
        elif event.key == pygame.K_RIGHT:
            self._move_cursor_right()
        
        elif event.key == pygame.K_UP:
            self._navigate_history_up()
        
        elif event.key == pygame.K_DOWN:
            self._navigate_history_down()
        
        elif event.key == pygame.K_HOME:
            self.cursor_pos = 0
        
        elif event.key == pygame.K_END:
            self.cursor_pos = len(self.input_text)
        
        elif event.unicode and event.unicode.isprintable():
            self._insert_character(event.unicode)
        
        return None
    
    def _execute_command(self) -> Optional[str]:
        """Execute the current command and add to history."""
        command = self.input_text.strip()
        
        if not command:
            return None
        
        # Add command to output log
        self.add_output(f"{self.prompt}{command}", COLOR_CONSOLE_PROMPT, "command")
        
        # Add to history (avoid duplicates at the end)
        if not self.command_history or self.command_history[-1] != command:
            self.command_history.append(command)
            # Limit history size
            if len(self.command_history) > CONSOLE_MAX_HISTORY:
                self.command_history.pop(0)
        
        # Reset input state
        self.input_text = ""
        self.cursor_pos = 0
        self.history_index = -1
        self.temp_input = ""
        
        # Trigger callback if set
        if self.on_command:
            self.on_command(command)
        
        return command
    
    def _handle_backspace(self) -> None:
        """Delete character before cursor."""
        if self.cursor_pos > 0:
            self.input_text = (self.input_text[:self.cursor_pos - 1] + 
                              self.input_text[self.cursor_pos:])
            self.cursor_pos -= 1
    
    def _handle_delete(self) -> None:
        """Delete character after cursor."""
        if self.cursor_pos < len(self.input_text):
            self.input_text = (self.input_text[:self.cursor_pos] + 
                              self.input_text[self.cursor_pos + 1:])
    
    def _move_cursor_left(self) -> None:
        """Move cursor one position left."""
        if self.cursor_pos > 0:
            self.cursor_pos -= 1
    
    def _move_cursor_right(self) -> None:
        """Move cursor one position right."""
        if self.cursor_pos < len(self.input_text):
            self.cursor_pos += 1
    
    def _navigate_history_up(self) -> None:
        """Navigate to previous command in history."""
        if not self.command_history:
            return
        
        # Save current input when starting to browse
        if self.history_index == -1:
            self.temp_input = self.input_text
        
        # Move up in history
        if self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.input_text = self.command_history[-(self.history_index + 1)]
            self.cursor_pos = len(self.input_text)
    
    def _navigate_history_down(self) -> None:
        """Navigate to next command in history."""
        if self.history_index > 0:
            self.history_index -= 1
            self.input_text = self.command_history[-(self.history_index + 1)]
            self.cursor_pos = len(self.input_text)
        elif self.history_index == 0:
            # Return to the saved input
            self.history_index = -1
            self.input_text = self.temp_input
            self.cursor_pos = len(self.input_text)
    
    def _insert_character(self, char: str) -> None:
        """Insert a character at the cursor position."""
        self.input_text = (self.input_text[:self.cursor_pos] + 
                          char + 
                          self.input_text[self.cursor_pos:])
        self.cursor_pos += 1
    
    def add_output(self, text: str, color: Tuple[int, int, int] = COLOR_TEXT_PRIMARY,
                   line_type: str = "normal") -> None:
        """Add a line to the output log."""
        self.output_lines.append(OutputLine(text, color, line_type))
        
        # Limit output lines
        while len(self.output_lines) > CONSOLE_MAX_OUTPUT_LINES + 20:
            self.output_lines.pop(0)
    
    def add_success(self, text: str) -> None:
        """Add a success message."""
        self.add_output(f"✓ {text}", COLOR_SUCCESS, "success")
    
    def add_error(self, text: str) -> None:
        """Add an error message."""
        self.add_output(f"✗ {text}", COLOR_ERROR, "error")
    
    def add_info(self, text: str) -> None:
        """Add an info message."""
        self.add_output(f"ℹ {text}", COLOR_ACCENT, "info")
    
    def add_educational_error(self, command: str, error_type: str = "unknown") -> None:
        """
        Add educational error feedback for common mistakes.
        
        Provides kid-friendly explanations and suggestions.
        """
        self.add_output("", COLOR_TEXT_MUTED)
        
        # Check for common typos
        stripped_cmd = command.replace("hero.", "").replace("()", "").strip()
        
        if stripped_cmd in METHOD_SUGGESTIONS:
            suggestion = METHOD_SUGGESTIONS[stripped_cmd]
            self.add_error("Oops! That's not quite right.")
            self.add_output(f"  Did you mean: hero.{suggestion}() ?", COLOR_WARNING)
            self.add_output("  Tip: Python is picky about spelling!", COLOR_TEXT_MUTED)
        
        elif error_type == "syntax":
            self.add_error("Syntax Error!")
            self.add_output("  Check your parentheses () and dots .", COLOR_WARNING)
            self.add_output("  Example: hero.move_right()", COLOR_SUCCESS)
        
        elif error_type == "unknown_method":
            self.add_error("Unknown command!")
            self.add_output("  The hero doesn't know how to do that.", COLOR_WARNING)
            self.add_output("  Try: move_right, move_left, move_up, move_down", 
                          COLOR_TEXT_MUTED)
        
        elif error_type == "name":
            self.add_error("Name not recognized!")
            self.add_output("  Did you forget 'hero.' at the start?", COLOR_WARNING)
            self.add_output("  Commands must start with 'hero.'", COLOR_TEXT_MUTED)
        
        else:
            self.add_error("Something went wrong!")
            self.add_output("  Try a command like: hero.move_right()", COLOR_WARNING)
        
        self.add_output("", COLOR_TEXT_MUTED)
    
    def update(self, dt: int) -> None:
        """Update console animations."""
        # Cursor blink
        self.cursor_timer += dt
        if self.cursor_timer >= CURSOR_BLINK_INTERVAL:
            self.cursor_timer = 0
            self.cursor_visible = not self.cursor_visible
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the console to the screen."""
        # Draw semi-transparent background
        console_surface = pygame.Surface((self.rect.width, self.rect.height), 
                                         pygame.SRCALPHA)
        pygame.draw.rect(console_surface, COLOR_CONSOLE_BG, 
                        console_surface.get_rect(), border_radius=12)
        surface.blit(console_surface, self.rect.topleft)
        
        # Draw border
        pygame.draw.rect(surface, COLOR_CONSOLE_BORDER, self.rect, 
                        width=2, border_radius=12)
        
        # Draw title bar
        title_rect = pygame.Rect(self.rect.x, self.rect.y, 
                                self.rect.width, 35)
        pygame.draw.rect(surface, COLOR_CONSOLE_BORDER, title_rect, 
                        border_radius=12)
        pygame.draw.rect(surface, COLOR_CONSOLE_BORDER, 
                        pygame.Rect(self.rect.x, self.rect.y + 20, 
                                   self.rect.width, 15))
        
        # Draw title text
        title_surf = self.font_small.render(self.title, True, COLOR_ACCENT)
        title_x = self.rect.x + (self.rect.width - title_surf.get_width()) // 2
        surface.blit(title_surf, (title_x, self.rect.y + 10))
        
        # Draw output log
        self._draw_output(surface)
        
        # Draw input area
        self._draw_input(surface)
    
    def _draw_output(self, surface: pygame.Surface) -> None:
        """Draw the output log area."""
        output_y = self.rect.y + 45
        output_height = self.rect.height - 100
        max_lines = output_height // (FONT_SIZE_CONSOLE + 4)
        
        # Get visible lines
        visible_lines = self.output_lines[-max_lines:]
        
        for i, line in enumerate(visible_lines):
            y = output_y + i * (FONT_SIZE_CONSOLE + 4)
            
            # Truncate long lines
            text = line.text
            max_chars = (self.rect.width - CONSOLE_PADDING * 2) // (FONT_SIZE_CONSOLE // 2)
            if len(text) > max_chars:
                text = text[:max_chars - 3] + "..."
            
            text_surf = self.font.render(text, True, line.color)
            surface.blit(text_surf, (self.rect.x + CONSOLE_PADDING, y))
    
    def _draw_input(self, surface: pygame.Surface) -> None:
        """Draw the input area with cursor."""
        input_height = 40
        input_rect = pygame.Rect(
            self.rect.x + CONSOLE_PADDING,
            self.rect.bottom - input_height - CONSOLE_PADDING,
            self.rect.width - CONSOLE_PADDING * 2,
            input_height
        )
        
        # Draw input background
        pygame.draw.rect(surface, COLOR_CONSOLE_INPUT_BG, input_rect, 
                        border_radius=8)
        pygame.draw.rect(surface, COLOR_CONSOLE_BORDER, input_rect, 
                        width=1, border_radius=8)
        
        # Draw prompt
        prompt_surf = self.font.render(self.prompt, True, COLOR_CONSOLE_PROMPT)
        prompt_x = input_rect.x + 10
        prompt_y = input_rect.y + (input_height - prompt_surf.get_height()) // 2
        surface.blit(prompt_surf, (prompt_x, prompt_y))
        
        # Draw input text
        text_x = prompt_x + prompt_surf.get_width()
        text_surf = self.font.render(self.input_text, True, COLOR_TEXT_PRIMARY)
        surface.blit(text_surf, (text_x, prompt_y))
        
        # Draw cursor
        if self.cursor_visible:
            cursor_x = text_x + self.font.size(self.input_text[:self.cursor_pos])[0]
            cursor_rect = pygame.Rect(cursor_x, prompt_y, 2, prompt_surf.get_height())
            pygame.draw.rect(surface, COLOR_CONSOLE_CURSOR, cursor_rect)
    
    def clear(self) -> None:
        """Clear the output log."""
        self.output_lines.clear()
        self._add_welcome_message()
