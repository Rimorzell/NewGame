"""
Frozen Signal - UI System
HUD, menus, dialogue boxes, and inventory screen
"""

import pygame
import math
from .constants import (
    Colors, RENDER_WIDTH, RENDER_HEIGHT,
    INVENTORY_SLOTS, GameState
)


class UI:
    """Main UI manager"""

    def __init__(self, width, height):
        self.width = width
        self.height = height

        # UI state
        self.show_hud = True
        self.message_queue = []
        self.current_message = None
        self.message_timer = 0

        # Dialogue state
        self.dialogue_text = ""
        self.dialogue_speaker = ""
        self.dialogue_callback = None

        # Document viewer
        self.document_content = ""
        self.document_scroll = 0

        # Menu
        self.menu_options = []
        self.menu_selected = 0

        # Fonts (will use simple rendering)
        self.font_size = 8

        # Animation
        self.animation_timer = 0

        # Pre-render common elements
        self._create_ui_elements()

    def _create_ui_elements(self):
        """Create reusable UI elements"""
        # Health bar background
        self.health_bar_bg = pygame.Surface((52, 8), pygame.SRCALPHA)
        pygame.draw.rect(self.health_bar_bg, Colors.UI_BACKGROUND, (0, 0, 52, 8))
        pygame.draw.rect(self.health_bar_bg, Colors.UI_BORDER, (0, 0, 52, 8), 1)

        # Sanity bar background
        self.sanity_bar_bg = pygame.Surface((52, 6), pygame.SRCALPHA)
        pygame.draw.rect(self.sanity_bar_bg, Colors.UI_BACKGROUND, (0, 0, 52, 6))
        pygame.draw.rect(self.sanity_bar_bg, Colors.UI_BORDER, (0, 0, 52, 6), 1)

        # Warmth bar background
        self.warmth_bar_bg = pygame.Surface((52, 6), pygame.SRCALPHA)
        pygame.draw.rect(self.warmth_bar_bg, Colors.UI_BACKGROUND, (0, 0, 52, 6))
        pygame.draw.rect(self.warmth_bar_bg, Colors.UI_BORDER, (0, 0, 52, 6), 1)

        # Inventory slot
        self.inv_slot = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.rect(self.inv_slot, Colors.UI_BACKGROUND, (0, 0, 20, 20))
        pygame.draw.rect(self.inv_slot, Colors.UI_BORDER, (0, 0, 20, 20), 1)

        # Selected inventory slot
        self.inv_slot_selected = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.rect(self.inv_slot_selected, Colors.UI_BACKGROUND, (0, 0, 20, 20))
        pygame.draw.rect(self.inv_slot_selected, Colors.UI_HIGHLIGHT, (0, 0, 20, 20), 1)

    def update(self, dt):
        """Update UI animations and timers"""
        self.animation_timer += dt

        # Update message display
        if self.current_message:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.current_message = None
                if self.message_queue:
                    msg = self.message_queue.pop(0)
                    self.show_message(msg[0], msg[1])

    def show_message(self, text, duration=3.0):
        """Show a temporary message"""
        if self.current_message:
            self.message_queue.append((text, duration))
        else:
            self.current_message = text
            self.message_timer = duration

    def render_hud(self, surface, player):
        """Render the HUD overlay"""
        if not self.show_hud:
            return

        # Status bars in top-left
        x, y = 4, 4

        # Health bar
        surface.blit(self.health_bar_bg, (x, y))
        health_width = int(50 * (player.health / player.max_health))
        if health_width > 0:
            color = Colors.WARNING_RED if player.health < 30 else Colors.BLOOD_RED
            pygame.draw.rect(surface, color, (x + 1, y + 1, health_width, 6))

        # Health icon
        self._draw_text(surface, "HP", x - 1, y, Colors.UI_TEXT, shadow=True)

        y += 10

        # Sanity bar
        surface.blit(self.sanity_bar_bg, (x, y))
        sanity_width = int(50 * (player.sanity / player.max_sanity))
        if sanity_width > 0:
            color = Colors.WARNING_RED if player.sanity < 30 else Colors.ICE_BLUE
            pygame.draw.rect(surface, color, (x + 1, y + 1, sanity_width, 4))

        # Pulsing effect for low sanity
        if player.sanity < 30:
            pulse = (math.sin(self.animation_timer * 5) + 1) / 2
            overlay = pygame.Surface((50, 4), pygame.SRCALPHA)
            overlay.fill((*Colors.WARNING_RED[:3], int(pulse * 100)))
            surface.blit(overlay, (x + 1, y + 1))

        y += 8

        # Warmth bar
        surface.blit(self.warmth_bar_bg, (x, y))
        warmth_width = int(50 * (player.warmth / player.max_warmth))
        if warmth_width > 0:
            if player.warmth > 50:
                color = Colors.AMBER
            elif player.warmth > 20:
                color = Colors.AMBER_DARK
            else:
                color = Colors.FROST
            pygame.draw.rect(surface, color, (x + 1, y + 1, warmth_width, 4))

        # Quick inventory display at bottom
        self._render_quick_inventory(surface, player.inventory)

        # Current message
        if self.current_message:
            self._render_message(surface)

        # Interaction prompt
        # (handled by game engine when near interactable)

    def _render_quick_inventory(self, surface, inventory):
        """Render quick inventory bar"""
        start_x = (self.width - (INVENTORY_SLOTS * 22)) // 2
        y = self.height - 24

        for i in range(INVENTORY_SLOTS):
            x = start_x + i * 22

            # Draw slot
            if i == inventory.selected_slot:
                surface.blit(self.inv_slot_selected, (x, y))
            else:
                surface.blit(self.inv_slot, (x, y))

            # Draw item icon
            item = inventory.items[i]
            if item:
                surface.blit(item.icon, (x + 2, y + 2))

                # Stack count
                if item.stackable and item.quantity > 1:
                    self._draw_text(surface, str(item.quantity),
                                   x + 14, y + 12, Colors.STERILE_WHITE)

    def _render_message(self, surface):
        """Render current message"""
        if not self.current_message:
            return

        # Calculate text box size
        text_width = len(self.current_message) * 6 + 8
        text_width = min(text_width, self.width - 20)

        x = (self.width - text_width) // 2
        y = self.height - 50

        # Background
        bg = pygame.Surface((text_width, 14), pygame.SRCALPHA)
        bg.fill((*Colors.UI_BACKGROUND[:3], 200))
        pygame.draw.rect(bg, Colors.UI_BORDER, (0, 0, text_width, 14), 1)
        surface.blit(bg, (x, y))

        # Text
        self._draw_text(surface, self.current_message, x + 4, y + 3, Colors.UI_TEXT)

    def render_inventory_screen(self, surface, inventory, player):
        """Render full inventory screen"""
        # Darken background
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((*Colors.BLACK[:3], 200))
        surface.blit(overlay, (0, 0))

        # Inventory panel
        panel_width = 200
        panel_height = 160
        panel_x = (self.width - panel_width) // 2
        panel_y = (self.height - panel_height) // 2

        # Panel background
        pygame.draw.rect(surface, Colors.UI_BACKGROUND,
                        (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(surface, Colors.UI_BORDER,
                        (panel_x, panel_y, panel_width, panel_height), 1)

        # Title
        self._draw_text(surface, "INVENTORY", panel_x + 70, panel_y + 6, Colors.FROST)

        # Separator
        pygame.draw.line(surface, Colors.UI_BORDER,
                        (panel_x + 4, panel_y + 18),
                        (panel_x + panel_width - 4, panel_y + 18))

        # Item grid (2 rows of 3)
        grid_x = panel_x + 20
        grid_y = panel_y + 26

        for i in range(INVENTORY_SLOTS):
            row = i // 3
            col = i % 3
            x = grid_x + col * 54
            y = grid_y + row * 54

            # Slot background
            slot_size = 48
            pygame.draw.rect(surface, Colors.DARK_BLUE, (x, y, slot_size, slot_size))
            if i == inventory.selected_slot:
                pygame.draw.rect(surface, Colors.UI_HIGHLIGHT, (x, y, slot_size, slot_size), 2)
            else:
                pygame.draw.rect(surface, Colors.UI_BORDER, (x, y, slot_size, slot_size), 1)

            # Item
            item = inventory.items[i]
            if item:
                # Center icon
                icon_x = x + (slot_size - 16) // 2
                icon_y = y + (slot_size - 16) // 2
                scaled_icon = pygame.transform.scale2x(item.icon)
                surface.blit(scaled_icon, (icon_x, icon_y))

                # Stack count
                if item.stackable and item.quantity > 1:
                    self._draw_text(surface, str(item.quantity),
                                   x + slot_size - 12, y + slot_size - 10,
                                   Colors.STERILE_WHITE)

        # Selected item description
        selected_item = inventory.get_selected_item()
        if selected_item:
            desc_y = panel_y + panel_height - 40
            self._draw_text(surface, selected_item.name,
                           panel_x + 10, desc_y, Colors.FROST)
            # Wrap description
            desc = selected_item.description[:40]
            self._draw_text(surface, desc,
                           panel_x + 10, desc_y + 12, Colors.UI_TEXT)

        # Controls hint
        hint_y = panel_y + panel_height - 12
        self._draw_text(surface, "[ARROWS] Select  [E] Use  [ESC] Close",
                       panel_x + 10, hint_y, Colors.DEEP_BLUE)

    def render_dialogue(self, surface, text, speaker=""):
        """Render dialogue box"""
        # Box at bottom of screen
        box_height = 60
        box_y = self.height - box_height - 4

        # Background
        pygame.draw.rect(surface, Colors.UI_BACKGROUND,
                        (4, box_y, self.width - 8, box_height))
        pygame.draw.rect(surface, Colors.UI_BORDER,
                        (4, box_y, self.width - 8, box_height), 1)

        # Speaker name
        if speaker:
            pygame.draw.rect(surface, Colors.UI_BACKGROUND,
                            (8, box_y - 10, len(speaker) * 6 + 8, 12))
            pygame.draw.rect(surface, Colors.UI_BORDER,
                            (8, box_y - 10, len(speaker) * 6 + 8, 12), 1)
            self._draw_text(surface, speaker, 12, box_y - 8, Colors.FROST)

        # Text with word wrapping
        words = text.split(' ')
        lines = []
        current_line = ""
        max_chars = (self.width - 24) // 6

        for word in words:
            if len(current_line) + len(word) + 1 <= max_chars:
                current_line += (" " if current_line else "") + word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        for i, line in enumerate(lines[:4]):  # Max 4 lines
            self._draw_text(surface, line, 12, box_y + 8 + i * 12, Colors.UI_TEXT)

        # Continue prompt
        if int(self.animation_timer * 2) % 2:
            prompt_x = self.width - 20
            prompt_y = box_y + box_height - 12
            pygame.draw.polygon(surface, Colors.FROST,
                              [(prompt_x, prompt_y),
                               (prompt_x + 6, prompt_y + 4),
                               (prompt_x, prompt_y + 8)])

    def render_document(self, surface, content, title="DOCUMENT"):
        """Render document viewer"""
        # Full screen document
        margin = 20

        # Background
        pygame.draw.rect(surface, Colors.UI_BACKGROUND,
                        (margin, margin, self.width - margin * 2, self.height - margin * 2))
        pygame.draw.rect(surface, Colors.UI_BORDER,
                        (margin, margin, self.width - margin * 2, self.height - margin * 2), 1)

        # Title
        self._draw_text(surface, title, margin + 8, margin + 6, Colors.FROST)
        pygame.draw.line(surface, Colors.UI_BORDER,
                        (margin + 4, margin + 18),
                        (self.width - margin - 4, margin + 18))

        # Content with word wrapping
        words = content.split(' ')
        lines = []
        current_line = ""
        max_chars = (self.width - margin * 2 - 16) // 6

        for word in words:
            # Handle newlines
            if '\n' in word:
                parts = word.split('\n')
                for j, part in enumerate(parts):
                    if j > 0:
                        lines.append(current_line)
                        current_line = ""
                    if len(current_line) + len(part) + 1 <= max_chars:
                        current_line += (" " if current_line else "") + part
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = part
            elif len(current_line) + len(word) + 1 <= max_chars:
                current_line += (" " if current_line else "") + word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        # Render visible lines
        max_lines = (self.height - margin * 2 - 40) // 10
        visible_lines = lines[self.document_scroll:self.document_scroll + max_lines]

        for i, line in enumerate(visible_lines):
            self._draw_text(surface, line,
                           margin + 8, margin + 24 + i * 10, Colors.UI_TEXT)

        # Scroll indicator
        if len(lines) > max_lines:
            scroll_height = self.height - margin * 2 - 40
            thumb_height = max(10, scroll_height * max_lines // len(lines))
            thumb_pos = margin + 22 + int((scroll_height - thumb_height) *
                                          self.document_scroll / (len(lines) - max_lines))

            pygame.draw.rect(surface, Colors.DEEP_BLUE,
                            (self.width - margin - 6, margin + 22, 4, scroll_height))
            pygame.draw.rect(surface, Colors.FROST,
                            (self.width - margin - 6, thumb_pos, 4, thumb_height))

        # Close hint
        self._draw_text(surface, "[ESC] Close",
                       self.width - margin - 60, self.height - margin - 10,
                       Colors.DEEP_BLUE)

    def render_menu(self, surface, title, options, selected):
        """Render menu screen"""
        # Darken background
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((*Colors.BLACK[:3], 220))
        surface.blit(overlay, (0, 0))

        # Title
        title_x = (self.width - len(title) * 8) // 2
        self._draw_text(surface, title, title_x, 40, Colors.FROST, scale=2)

        # Subtitle
        subtitle = "OUTPOST EREBUS"
        sub_x = (self.width - len(subtitle) * 6) // 2
        self._draw_text(surface, subtitle, sub_x, 60, Colors.ICE_BLUE)

        # Options
        start_y = 100
        for i, option in enumerate(options):
            x = (self.width - len(option) * 6) // 2
            y = start_y + i * 20

            if i == selected:
                # Selection indicator
                pygame.draw.rect(surface, Colors.UI_HIGHLIGHT,
                               (x - 10, y - 2, len(option) * 6 + 20, 14), 1)
                color = Colors.FROST
            else:
                color = Colors.UI_TEXT

            self._draw_text(surface, option, x, y, color)

        # Decorative line
        pygame.draw.line(surface, Colors.DEEP_BLUE,
                        (40, self.height - 30), (self.width - 40, self.height - 30))

    def render_game_over(self, surface, message="SIGNAL LOST"):
        """Render game over screen"""
        # Red tinted overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((*Colors.BLOOD_RED[:3], 150))
        surface.blit(overlay, (0, 0))

        # Glitch effect on text
        offset = int(math.sin(self.animation_timer * 10) * 2)

        # Message
        msg_x = (self.width - len(message) * 8) // 2
        self._draw_text(surface, message, msg_x + offset, self.height // 2 - 20,
                       Colors.ALARM_RED, scale=2)

        # Subtitle
        sub = "Press ENTER to continue"
        sub_x = (self.width - len(sub) * 6) // 2
        self._draw_text(surface, sub, sub_x, self.height // 2 + 20, Colors.WARNING_RED)

    def render_ending(self, surface, ending_text, ending_title):
        """Render ending screen"""
        # Fade to black
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((*Colors.BLACK[:3], 240))
        surface.blit(overlay, (0, 0))

        # Title
        title_x = (self.width - len(ending_title) * 8) // 2
        self._draw_text(surface, ending_title, title_x, 40, Colors.FROST, scale=2)

        # Render ending text with wrapping
        words = ending_text.split(' ')
        lines = []
        current_line = ""
        max_chars = (self.width - 60) // 6

        for word in words:
            if len(current_line) + len(word) + 1 <= max_chars:
                current_line += (" " if current_line else "") + word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        start_y = 80
        for i, line in enumerate(lines):
            x = (self.width - len(line) * 6) // 2
            self._draw_text(surface, line, x, start_y + i * 12, Colors.UI_TEXT)

    def _draw_text(self, surface, text, x, y, color, scale=1, shadow=False):
        """Draw text using simple pixel font"""
        # Simple character rendering
        char_width = 5 * scale
        char_height = 7 * scale

        if shadow:
            self._draw_text_simple(surface, text, x + 1, y + 1, Colors.BLACK, scale)

        self._draw_text_simple(surface, text, x, y, color, scale)

    def _draw_text_simple(self, surface, text, x, y, color, scale=1):
        """Simplified text rendering with basic font"""
        # Use a minimal pixel font representation
        char_width = 6 * scale

        for i, char in enumerate(text.upper()):
            char_x = x + i * char_width
            self._draw_char(surface, char, char_x, y, color, scale)

    def _draw_char(self, surface, char, x, y, color, scale=1):
        """Draw a single character"""
        # Minimal 5x7 pixel font patterns
        patterns = {
            'A': [(1,1),(2,0),(3,1),(1,2),(2,2),(3,2),(1,3),(3,3),(1,4),(3,4)],
            'B': [(1,0),(2,0),(1,1),(3,1),(1,2),(2,2),(1,3),(3,3),(1,4),(2,4)],
            'C': [(2,0),(3,0),(1,1),(1,2),(1,3),(2,4),(3,4)],
            'D': [(1,0),(2,0),(1,1),(3,1),(1,2),(3,2),(1,3),(3,3),(1,4),(2,4)],
            'E': [(1,0),(2,0),(3,0),(1,1),(1,2),(2,2),(1,3),(1,4),(2,4),(3,4)],
            'F': [(1,0),(2,0),(3,0),(1,1),(1,2),(2,2),(1,3),(1,4)],
            'G': [(2,0),(3,0),(1,1),(1,2),(3,2),(1,3),(3,3),(2,4),(3,4)],
            'H': [(1,0),(3,0),(1,1),(3,1),(1,2),(2,2),(3,2),(1,3),(3,3),(1,4),(3,4)],
            'I': [(1,0),(2,0),(3,0),(2,1),(2,2),(2,3),(1,4),(2,4),(3,4)],
            'J': [(3,0),(3,1),(3,2),(1,3),(3,3),(2,4)],
            'K': [(1,0),(3,0),(1,1),(2,1),(1,2),(1,3),(2,3),(1,4),(3,4)],
            'L': [(1,0),(1,1),(1,2),(1,3),(1,4),(2,4),(3,4)],
            'M': [(1,0),(3,0),(1,1),(2,1),(3,1),(1,2),(3,2),(1,3),(3,3),(1,4),(3,4)],
            'N': [(1,0),(3,0),(1,1),(2,1),(3,1),(1,2),(3,2),(1,3),(3,3),(1,4),(3,4)],
            'O': [(2,0),(1,1),(3,1),(1,2),(3,2),(1,3),(3,3),(2,4)],
            'P': [(1,0),(2,0),(1,1),(3,1),(1,2),(2,2),(1,3),(1,4)],
            'Q': [(2,0),(1,1),(3,1),(1,2),(3,2),(1,3),(2,3),(2,4),(3,4)],
            'R': [(1,0),(2,0),(1,1),(3,1),(1,2),(2,2),(1,3),(2,3),(1,4),(3,4)],
            'S': [(2,0),(3,0),(1,1),(2,2),(3,3),(1,4),(2,4)],
            'T': [(1,0),(2,0),(3,0),(2,1),(2,2),(2,3),(2,4)],
            'U': [(1,0),(3,0),(1,1),(3,1),(1,2),(3,2),(1,3),(3,3),(2,4)],
            'V': [(1,0),(3,0),(1,1),(3,1),(1,2),(3,2),(2,3),(2,4)],
            'W': [(1,0),(3,0),(1,1),(3,1),(1,2),(2,2),(3,2),(1,3),(2,3),(3,3),(1,4),(3,4)],
            'X': [(1,0),(3,0),(1,1),(3,1),(2,2),(1,3),(3,3),(1,4),(3,4)],
            'Y': [(1,0),(3,0),(1,1),(3,1),(2,2),(2,3),(2,4)],
            'Z': [(1,0),(2,0),(3,0),(3,1),(2,2),(1,3),(1,4),(2,4),(3,4)],
            '0': [(2,0),(1,1),(3,1),(1,2),(3,2),(1,3),(3,3),(2,4)],
            '1': [(2,0),(1,1),(2,1),(2,2),(2,3),(1,4),(2,4),(3,4)],
            '2': [(1,0),(2,0),(3,1),(2,2),(1,3),(1,4),(2,4),(3,4)],
            '3': [(1,0),(2,0),(3,1),(2,2),(3,3),(1,4),(2,4)],
            '4': [(1,0),(3,0),(1,1),(3,1),(1,2),(2,2),(3,2),(3,3),(3,4)],
            '5': [(1,0),(2,0),(3,0),(1,1),(1,2),(2,2),(3,3),(1,4),(2,4)],
            '6': [(2,0),(3,0),(1,1),(1,2),(2,2),(1,3),(3,3),(2,4)],
            '7': [(1,0),(2,0),(3,0),(3,1),(2,2),(2,3),(2,4)],
            '8': [(2,0),(1,1),(3,1),(2,2),(1,3),(3,3),(2,4)],
            '9': [(2,0),(1,1),(3,1),(2,2),(3,2),(3,3),(1,4),(2,4)],
            ' ': [],
            '.': [(2,4)],
            ',': [(2,4),(1,5)],
            ':': [(2,1),(2,3)],
            '!': [(2,0),(2,1),(2,2),(2,4)],
            '?': [(1,0),(2,0),(3,1),(2,2),(2,4)],
            '-': [(1,2),(2,2),(3,2)],
            '_': [(1,4),(2,4),(3,4)],
            '[': [(2,0),(3,0),(2,1),(2,2),(2,3),(2,4),(3,4)],
            ']': [(1,0),(2,0),(2,1),(2,2),(2,3),(1,4),(2,4)],
            '/': [(3,0),(3,1),(2,2),(1,3),(1,4)],
            "'": [(2,0),(2,1)],
            '"': [(1,0),(3,0),(1,1),(3,1)],
        }

        pattern = patterns.get(char, [])
        for px, py in pattern:
            for sy in range(scale):
                for sx in range(scale):
                    draw_x = x + px * scale + sx
                    draw_y = y + py * scale + sy
                    if 0 <= draw_x < surface.get_width() and 0 <= draw_y < surface.get_height():
                        surface.set_at((draw_x, draw_y), color)

    def render_interaction_prompt(self, surface, text="[E] Interact"):
        """Render interaction prompt near player"""
        x = (self.width - len(text) * 6) // 2
        y = self.height // 2 + 30

        # Background
        bg = pygame.Surface((len(text) * 6 + 8, 12), pygame.SRCALPHA)
        bg.fill((*Colors.UI_BACKGROUND[:3], 180))
        surface.blit(bg, (x - 4, y - 2))

        self._draw_text(surface, text, x, y, Colors.AMBER)
