"""
Frozen Signal - Main Game Engine
Core game loop, state management, and coordination
"""

import pygame
import sys
from .constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, RENDER_WIDTH, RENDER_HEIGHT,
    FPS, TITLE, Colors, GameState, TILE_SIZE
)
from .camera import Camera
from .player import Player
from .effects import VisualEffects, LightingSystem, ParticleSystem
from .tilemap import create_outpost_erebus
from .entities import Enemy, InteractableObject
from .ui import UI
from .narrative import NarrativeManager, get_ending_content, DOCUMENTS, AUDIO_LOGS
from .inventory import create_item


class Game:
    """Main game class"""

    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        # Display setup - render at low res, scale up
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.render_surface = pygame.Surface((RENDER_WIDTH, RENDER_HEIGHT))
        pygame.display.set_caption(TITLE)

        # Clock
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0
        self.time = 0

        # Game state
        self.state = GameState.MENU
        self.previous_state = None

        # Core systems
        self.camera = Camera(RENDER_WIDTH, RENDER_HEIGHT)
        self.effects = VisualEffects(RENDER_WIDTH, RENDER_HEIGHT)
        self.lighting = LightingSystem(RENDER_WIDTH, RENDER_HEIGHT)
        self.particles = ParticleSystem()
        self.ui = UI(RENDER_WIDTH, RENDER_HEIGHT)
        self.narrative = NarrativeManager()

        # Game objects
        self.player = None
        self.level = None
        self.entities = []

        # Menu state
        self.menu_options = ["NEW GAME", "CONTINUE", "QUIT"]
        self.menu_selected = 0

        # Dialogue/document state
        self.current_document = None
        self.current_dialogue = None
        self.dialogue_callback = None

        # Interaction
        self.nearby_interactable = None

        # Game over
        self.game_over_message = ""

    def new_game(self):
        """Start a new game"""
        # Create level
        self.level = create_outpost_erebus()

        # Create player at spawn point
        spawn = self.level.get_spawn_point()
        self.player = Player(spawn[0], spawn[1])

        # Give starting items
        self.player.inventory.add_item(create_item('weapon_pipe'))

        # Setup camera
        self.camera.follow(self.player, instant=True)

        # Populate level with entities
        self._populate_level()

        # Start game
        self.state = GameState.PLAYING
        self.ui.show_message("You awaken in darkness. The cold seeps into your bones.", 5)

    def _populate_level(self):
        """Add enemies and objects to the level"""
        self.entities = []

        # Add objects based on room
        room = self.level.current_room

        if room.room_id == "quarters":
            # Starting area - safe, informative
            # Note on desk
            note = InteractableObject(
                TILE_SIZE * 5, TILE_SIZE * 7, "note",
                {'content': DOCUMENTS['note_wake']['content'],
                 'doc_id': 'note_wake'}
            )
            self.entities.append(note)

            # Heater
            heater = InteractableObject(TILE_SIZE * 15, TILE_SIZE * 5, "heater", {'active': True})
            self.entities.append(heater)

            # Locker with item
            locker = InteractableObject(TILE_SIZE * 3, TILE_SIZE * 10, "locker")
            locker.gives_item = create_item('heat_pack')
            self.entities.append(locker)

            # Save point
            save = InteractableObject(TILE_SIZE * 8, TILE_SIZE * 3, "save_point")
            self.entities.append(save)

        elif room.room_id == "corridor_1":
            # Frozen corpse with keycard
            corpse = InteractableObject(TILE_SIZE * 4, TILE_SIZE * 5, "corpse",
                                       {'examine_text': "A researcher frozen mid-stride. Their face is locked in terror."})
            corpse.gives_item = create_item('key_lab')
            self.entities.append(corpse)

            # Enemy patrol
            enemy = Enemy(TILE_SIZE * 4, TILE_SIZE * 15)
            enemy.set_patrol_points([
                (TILE_SIZE * 4, TILE_SIZE * 15),
                (TILE_SIZE * 4, TILE_SIZE * 8)
            ])
            self.entities.append(enemy)

        elif room.room_id == "lab_1":
            # Terminal with classified document
            terminal = InteractableObject(TILE_SIZE * 6, TILE_SIZE * 3, "terminal",
                                         {'doc_id': 'note_signal',
                                          'content': DOCUMENTS['note_signal']['content']})
            self.entities.append(terminal)

            # Audio log
            audio = InteractableObject(TILE_SIZE * 11, TILE_SIZE * 7, "note",
                                      {'content': AUDIO_LOGS['log_volkov']['content'],
                                       'doc_id': 'log_volkov',
                                       'is_audio': True})
            self.entities.append(audio)

            # Medical supplies
            medkit = InteractableObject(TILE_SIZE * 14, TILE_SIZE * 5, "item_pickup",
                                       {'item': create_item('medkit')})
            self.entities.append(medkit)

            # Heater
            heater = InteractableObject(TILE_SIZE * 3, TILE_SIZE * 11, "heater", {'active': True})
            self.entities.append(heater)

        elif room.room_id == "storage":
            # Dark, cold storage
            # Document about experiments
            note = InteractableObject(TILE_SIZE * 6, TILE_SIZE * 4, "note",
                                     {'content': DOCUMENTS['note_subjects']['content'],
                                      'doc_id': 'note_subjects'})
            self.entities.append(note)

            # Ammo
            ammo = InteractableObject(TILE_SIZE * 9, TILE_SIZE * 6, "item_pickup",
                                     {'item': create_item('ammo_pistol', 8)})
            self.entities.append(ammo)

            # Hidden keycard
            locker = InteractableObject(TILE_SIZE * 4, TILE_SIZE * 7, "locker")
            locker.gives_item = create_item('key_reactor')
            self.entities.append(locker)

        elif room.room_id == "reactor":
            # Reactor room - dark, dangerous
            # Drilling log
            note = InteractableObject(TILE_SIZE * 3, TILE_SIZE * 6, "note",
                                     {'content': DOCUMENTS['note_drilling']['content'],
                                      'doc_id': 'note_drilling'})
            self.entities.append(note)

            # Reactor manual
            terminal = InteractableObject(TILE_SIZE * 12, TILE_SIZE * 6, "terminal",
                                         {'content': DOCUMENTS['note_reactor']['content'],
                                          'doc_id': 'note_reactor'})
            self.entities.append(terminal)

            # Enemies
            enemy1 = Enemy(TILE_SIZE * 3, TILE_SIZE * 3)
            self.entities.append(enemy1)

            enemy2 = Enemy(TILE_SIZE * 12, TILE_SIZE * 9)
            self.entities.append(enemy2)

        elif room.room_id == "deep_excavation":
            # Final area - the signal source
            # Final note
            note = InteractableObject(TILE_SIZE * 5, TILE_SIZE * 5, "note",
                                     {'content': DOCUMENTS['note_finale']['content'],
                                      'doc_id': 'note_finale'})
            self.entities.append(note)

            # The Signal - final choice point
            signal = InteractableObject(TILE_SIZE * 10, TILE_SIZE * 10, "terminal",
                                       {'is_signal': True,
                                        'content': "The crystal pulses with alien light. You feel it calling to you.\n\n[E] Embrace the signal\n[ESC] Destroy it"})
            self.entities.append(signal)

            # Enemies
            for i in range(3):
                enemy = Enemy(TILE_SIZE * (6 + i * 4), TILE_SIZE * 12)
                self.entities.append(enemy)

    def run(self):
        """Main game loop"""
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000.0
            self.time += self.dt

            self._handle_events()
            self._update()
            self._render()

        pygame.quit()
        sys.exit()

    def _handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                self._handle_key(event.key)

    def _handle_key(self, key):
        """Handle key presses based on game state"""
        if self.state == GameState.MENU:
            self._handle_menu_input(key)
        elif self.state == GameState.PLAYING:
            self._handle_gameplay_input(key)
        elif self.state == GameState.INVENTORY:
            self._handle_inventory_input(key)
        elif self.state == GameState.DIALOGUE:
            self._handle_dialogue_input(key)
        elif self.state == GameState.EXAMINING:
            self._handle_examine_input(key)
        elif self.state == GameState.PAUSED:
            self._handle_pause_input(key)
        elif self.state == GameState.GAME_OVER:
            self._handle_game_over_input(key)
        elif self.state == GameState.ENDING:
            self._handle_ending_input(key)

    def _handle_menu_input(self, key):
        """Handle menu navigation"""
        if key == pygame.K_UP or key == pygame.K_w:
            self.menu_selected = (self.menu_selected - 1) % len(self.menu_options)
        elif key == pygame.K_DOWN or key == pygame.K_s:
            self.menu_selected = (self.menu_selected + 1) % len(self.menu_options)
        elif key == pygame.K_RETURN or key == pygame.K_e:
            option = self.menu_options[self.menu_selected]
            if option == "NEW GAME":
                self.new_game()
            elif option == "QUIT":
                self.running = False

    def _handle_gameplay_input(self, key):
        """Handle gameplay controls"""
        if key == pygame.K_ESCAPE:
            self.previous_state = self.state
            self.state = GameState.PAUSED
        elif key == pygame.K_i or key == pygame.K_TAB:
            self.previous_state = self.state
            self.state = GameState.INVENTORY
        elif key == pygame.K_e:
            self._try_interact()
        elif key == pygame.K_SPACE:
            self.player.attack(self)
        elif key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6]:
            slot = key - pygame.K_1
            self.player.inventory.selected_slot = slot

    def _handle_inventory_input(self, key):
        """Handle inventory navigation"""
        inv = self.player.inventory
        if key == pygame.K_ESCAPE or key == pygame.K_i or key == pygame.K_TAB:
            self.state = GameState.PLAYING
        elif key == pygame.K_LEFT or key == pygame.K_a:
            inv.selected_slot = (inv.selected_slot - 1) % inv.slots
        elif key == pygame.K_RIGHT or key == pygame.K_d:
            inv.selected_slot = (inv.selected_slot + 1) % inv.slots
        elif key == pygame.K_UP or key == pygame.K_w:
            inv.selected_slot = (inv.selected_slot - 3) % inv.slots
        elif key == pygame.K_DOWN or key == pygame.K_s:
            inv.selected_slot = (inv.selected_slot + 3) % inv.slots
        elif key == pygame.K_e or key == pygame.K_RETURN:
            inv.use_item(inv.selected_slot, self.player, self)

    def _handle_dialogue_input(self, key):
        """Handle dialogue/document viewing"""
        if key == pygame.K_RETURN or key == pygame.K_e or key == pygame.K_ESCAPE:
            if self.dialogue_callback:
                self.dialogue_callback()
                self.dialogue_callback = None
            self.current_dialogue = None
            self.state = GameState.PLAYING

    def _handle_examine_input(self, key):
        """Handle document examination"""
        if key == pygame.K_ESCAPE or key == pygame.K_e:
            self.current_document = None
            self.ui.document_scroll = 0
            self.state = GameState.PLAYING
        elif key == pygame.K_UP or key == pygame.K_w:
            self.ui.document_scroll = max(0, self.ui.document_scroll - 1)
        elif key == pygame.K_DOWN or key == pygame.K_s:
            self.ui.document_scroll += 1

    def _handle_pause_input(self, key):
        """Handle pause menu"""
        if key == pygame.K_ESCAPE:
            self.state = GameState.PLAYING
        elif key == pygame.K_q:
            self.state = GameState.MENU
            self.player = None
            self.level = None

    def _handle_game_over_input(self, key):
        """Handle game over screen"""
        if key == pygame.K_RETURN:
            self.state = GameState.MENU

    def _handle_ending_input(self, key):
        """Handle ending screen"""
        if key == pygame.K_RETURN or key == pygame.K_ESCAPE:
            self.state = GameState.MENU
            self.player = None
            self.level = None

    def _try_interact(self):
        """Attempt to interact with nearby object"""
        if not self.nearby_interactable:
            return

        result = self.nearby_interactable.interact(self.player, self)
        if not result:
            return

        if result.get('message'):
            self.ui.show_message(result['message'])

        if result.get('show_document') or result.get('show_terminal'):
            content = result.get('document') or result.get('content') or result['data'].get('content', '')
            doc_id = result['data'].get('doc_id')

            # Check for signal ending choice
            if result['data'].get('is_signal'):
                self._handle_signal_choice()
                return

            if doc_id:
                if 'log_' in doc_id:
                    self.narrative.hear_audio_log(doc_id)
                else:
                    self.narrative.find_document(doc_id)

            self.current_document = content
            self.state = GameState.EXAMINING

        if result.get('save_game'):
            self._save_game()

    def _handle_signal_choice(self):
        """Handle the final choice at the signal"""
        # For now, embracing ends the game
        self.narrative.add_flag('embraced')
        self._trigger_ending()

    def _trigger_ending(self):
        """Trigger game ending"""
        ending_id = self.narrative.determine_ending()
        ending = get_ending_content(ending_id)
        self.current_document = ending['content']
        self.game_over_message = ending['title']
        self.state = GameState.ENDING

    def _save_game(self):
        """Save game state (placeholder)"""
        self.ui.show_message("Progress saved to magnetic tape.")

    def _update(self):
        """Update game state"""
        if self.state == GameState.PLAYING:
            self._update_gameplay()
        elif self.state == GameState.MENU:
            self.ui.update(self.dt)
        elif self.state == GameState.INVENTORY:
            self.ui.update(self.dt)

        # Always update effects for animations
        self.effects.update(
            self.dt,
            self.player.sanity if self.player else 100,
            self.player.warmth if self.player else 100
        )

    def _update_gameplay(self):
        """Update gameplay systems"""
        # Handle player input
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys, self.dt)

        # Update cold zone status based on room
        room = self.level.current_room
        self.player.is_in_cold_zone = not room.is_heated
        self.player.is_in_dark = room.is_dark

        # Update player
        self.player.update(self.dt, self)

        # Check room transition
        transition = self.level.check_room_transition(self.player)
        if transition:
            target_room, spawn = transition
            self.level.set_current_room(target_room)
            self.player.x, self.player.y = spawn
            self._populate_level()
            self.camera.follow(self.player, instant=True)

            # Show room name
            room = self.level.current_room
            room_names = {
                'quarters': 'CREW QUARTERS',
                'corridor_1': 'MAIN CORRIDOR',
                'lab_1': 'RESEARCH LABORATORY',
                'storage': 'STORAGE AREA',
                'reactor': 'REACTOR CONTROL',
                'communications': 'COMMUNICATIONS',
                'deep_excavation': 'DEEP EXCAVATION SITE'
            }
            name = room_names.get(room.room_id, room.room_id.upper())
            self.ui.show_message(name, 2)

        # Update camera
        self.camera.follow(self.player)
        self.camera.update(self.dt)

        # Update entities
        self.nearby_interactable = None
        for entity in self.entities:
            if hasattr(entity, 'update'):
                entity.update(self.dt, self)

            # Check for nearby interactable
            if isinstance(entity, InteractableObject):
                if entity.active and entity.can_interact(self.player):
                    dist = entity.distance_to(self.player)
                    if dist < entity.interaction_range:
                        self.nearby_interactable = entity

            # Check for enemy proximity (affects sanity)
            if isinstance(entity, Enemy):
                if entity.active and entity.distance_to(self.player) < 50:
                    self.player.is_near_enemy = True

        # Update particles
        self.particles.update(self.dt)

        # Update UI
        self.ui.update(self.dt)

        # Update lighting
        self.lighting.clear_lights()
        self.lighting.ambient_light = self.level.current_room.ambient_light

        # Player light
        self.lighting.add_light(self.player.x, self.player.y, 60, Colors.AMBER_LIGHT, 0.8, True)

        # Room lights based on type
        if self.level.current_room.is_heated:
            # Add heater lights
            for entity in self.entities:
                if isinstance(entity, InteractableObject) and entity.obj_type == "heater":
                    if entity.data.get('active', True):
                        self.lighting.add_light(entity.x, entity.y, 40, Colors.AMBER, 0.6, True)

        self.lighting.update(self.dt, self.time)

    def trigger_game_over(self, message):
        """Trigger game over state"""
        self.game_over_message = message
        self.state = GameState.GAME_OVER

    def show_document(self, content):
        """Show a document to read"""
        self.current_document = content
        self.previous_state = self.state
        self.state = GameState.EXAMINING

    def play_audio_log(self, log_id):
        """Play an audio log"""
        log = self.narrative.hear_audio_log(log_id)
        if log:
            self.current_dialogue = log['content']
            self.state = GameState.DIALOGUE

    def _render(self):
        """Render the game"""
        # Clear render surface
        self.render_surface.fill(Colors.BLACK)

        if self.state == GameState.MENU:
            self._render_menu()
        elif self.state in [GameState.PLAYING, GameState.INVENTORY,
                           GameState.DIALOGUE, GameState.EXAMINING,
                           GameState.PAUSED]:
            self._render_gameplay()

            # Render overlays based on state
            if self.state == GameState.INVENTORY:
                self.ui.render_inventory_screen(self.render_surface,
                                               self.player.inventory, self.player)
            elif self.state == GameState.DIALOGUE:
                if self.current_dialogue:
                    self.ui.render_dialogue(self.render_surface, self.current_dialogue)
            elif self.state == GameState.EXAMINING:
                if self.current_document:
                    self.ui.render_document(self.render_surface, self.current_document)
            elif self.state == GameState.PAUSED:
                self._render_pause()

        elif self.state == GameState.GAME_OVER:
            self._render_gameplay()
            self.ui.render_game_over(self.render_surface, self.game_over_message)

        elif self.state == GameState.ENDING:
            self.ui.render_ending(self.render_surface, self.current_document,
                                 self.game_over_message)

        # Apply post-processing effects
        final_surface = self.effects.apply(self.render_surface)

        # Scale up to screen size
        scaled = pygame.transform.scale(final_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(scaled, (0, 0))

        pygame.display.flip()

    def _render_menu(self):
        """Render main menu"""
        self.ui.render_menu(self.render_surface, TITLE,
                           self.menu_options, self.menu_selected)

    def _render_gameplay(self):
        """Render gameplay elements"""
        # Render level
        self.level.render(self.render_surface, self.camera)

        # Render entities (sorted by Y position for depth)
        sorted_entities = sorted(self.entities, key=lambda e: e.y)
        for entity in sorted_entities:
            if entity.active:
                entity.render(self.render_surface, self.camera)

        # Render player
        self.player.render(self.render_surface, self.camera)

        # Render particles
        self.particles.render(self.render_surface, self.camera)

        # Render lighting
        if self.level.current_room.is_dark:
            self.lighting.render(self.render_surface, self.camera)

        # Render HUD
        self.ui.render_hud(self.render_surface, self.player)

        # Render interaction prompt
        if self.nearby_interactable:
            self.ui.render_interaction_prompt(self.render_surface)

    def _render_pause(self):
        """Render pause overlay"""
        overlay = pygame.Surface((RENDER_WIDTH, RENDER_HEIGHT), pygame.SRCALPHA)
        overlay.fill((*Colors.BLACK[:3], 180))
        self.render_surface.blit(overlay, (0, 0))

        # Pause text
        text = "PAUSED"
        x = (RENDER_WIDTH - len(text) * 12) // 2
        self.ui._draw_text(self.render_surface, text, x, RENDER_HEIGHT // 2 - 20,
                          Colors.FROST, scale=2)

        hint = "[ESC] Resume   [Q] Quit to Menu"
        hx = (RENDER_WIDTH - len(hint) * 6) // 2
        self.ui._draw_text(self.render_surface, hint, hx, RENDER_HEIGHT // 2 + 20,
                          Colors.UI_TEXT)


def main():
    """Entry point"""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
