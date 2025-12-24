"""
Frozen Signal - Inventory System
Limited inventory with item management
"""

import pygame
from .constants import Colors, INVENTORY_SLOTS, MAX_STACK_SIZE, ItemType


class Item:
    """Base item class"""

    def __init__(self, item_id, name, item_type, description="", stackable=False,
                 max_stack=1, usable=False, data=None):
        self.item_id = item_id
        self.name = name
        self.item_type = item_type
        self.description = description
        self.stackable = stackable
        self.max_stack = max_stack if stackable else 1
        self.usable = usable
        self.quantity = 1
        self.data = data or {}

        # Create icon
        self._create_icon()

    def _create_icon(self):
        """Create item icon sprite"""
        self.icon = pygame.Surface((16, 16), pygame.SRCALPHA)

        if self.item_type == ItemType.KEY:
            pygame.draw.rect(self.icon, Colors.AMBER, (2, 6, 12, 4))
            pygame.draw.circle(self.icon, Colors.AMBER, (12, 8), 4)
            pygame.draw.circle(self.icon, Colors.DARK_BLUE, (12, 8), 2)

        elif self.item_type == ItemType.WEAPON:
            if 'pistol' in self.item_id:
                pygame.draw.rect(self.icon, Colors.DARK_BLUE, (2, 5, 10, 6))
                pygame.draw.rect(self.icon, Colors.DEEP_BLUE, (5, 9, 4, 5))
            else:
                pygame.draw.rect(self.icon, Colors.RUST, (6, 2, 4, 12))
                pygame.draw.rect(self.icon, Colors.DARK_BLUE, (4, 12, 8, 3))

        elif self.item_type == ItemType.AMMO:
            pygame.draw.rect(self.icon, Colors.AMBER_DARK, (3, 4, 10, 8))
            for i in range(3):
                pygame.draw.rect(self.icon, Colors.AMBER, (4 + i * 3, 5, 2, 6))

        elif self.item_type == ItemType.HEALING:
            pygame.draw.rect(self.icon, Colors.STERILE_WHITE, (3, 3, 10, 10))
            pygame.draw.rect(self.icon, Colors.WARNING_RED, (6, 4, 4, 8))
            pygame.draw.rect(self.icon, Colors.WARNING_RED, (4, 6, 8, 4))

        elif self.item_type == ItemType.DOCUMENT:
            pygame.draw.rect(self.icon, Colors.STERILE_WHITE, (3, 2, 10, 12))
            for i in range(4):
                pygame.draw.line(self.icon, Colors.DARK_BLUE,
                               (4, 4 + i * 2), (12, 4 + i * 2))

        elif self.item_type == ItemType.AUDIO_LOG:
            pygame.draw.rect(self.icon, Colors.DARK_BLUE, (2, 4, 12, 8))
            pygame.draw.circle(self.icon, Colors.RUST, (5, 8), 2)
            pygame.draw.circle(self.icon, Colors.RUST, (11, 8), 2)

        elif self.item_type == ItemType.WARMTH:
            pygame.draw.rect(self.icon, Colors.AMBER_DARK, (4, 2, 8, 12))
            pygame.draw.rect(self.icon, Colors.AMBER, (5, 3, 6, 4))

        elif self.item_type == ItemType.PUZZLE:
            pygame.draw.polygon(self.icon, Colors.ICE_BLUE,
                              [(8, 2), (14, 8), (8, 14), (2, 8)])
            pygame.draw.polygon(self.icon, Colors.FROST,
                              [(8, 4), (12, 8), (8, 12), (4, 8)])

        else:
            pygame.draw.rect(self.icon, Colors.UI_BORDER, (2, 2, 12, 12))

    def use(self, player, game):
        """Use the item"""
        if not self.usable:
            return False

        if self.item_type == ItemType.HEALING:
            heal_amount = self.data.get('heal_amount', 30)
            player.heal(heal_amount)
            return True

        elif self.item_type == ItemType.WARMTH:
            warm_amount = self.data.get('warm_amount', 40)
            player.warm_up(warm_amount)
            return True

        elif self.item_type == ItemType.DOCUMENT:
            game.show_document(self.data.get('content', self.description))
            return False  # Don't consume

        elif self.item_type == ItemType.AUDIO_LOG:
            game.play_audio_log(self.data.get('audio_id', self.item_id))
            return False  # Don't consume

        return False

    def copy(self):
        """Create a copy of this item"""
        new_item = Item(
            self.item_id, self.name, self.item_type,
            self.description, self.stackable, self.max_stack,
            self.usable, self.data.copy()
        )
        new_item.quantity = self.quantity
        return new_item


class Inventory:
    """Limited slot inventory system"""

    def __init__(self, slots=INVENTORY_SLOTS):
        self.slots = slots
        self.items = [None] * slots
        self.selected_slot = 0

    def add_item(self, item_or_dict):
        """Add item to inventory, returns True if successful"""
        # Convert dict to Item if needed
        if isinstance(item_or_dict, dict):
            item = Item(
                item_or_dict.get('id', 'unknown'),
                item_or_dict.get('name', 'Unknown Item'),
                item_or_dict.get('type', ItemType.PUZZLE),
                item_or_dict.get('description', ''),
                item_or_dict.get('stackable', False),
                item_or_dict.get('max_stack', 1),
                item_or_dict.get('usable', False),
                item_or_dict.get('data', {})
            )
            if 'quantity' in item_or_dict:
                item.quantity = item_or_dict['quantity']
        else:
            item = item_or_dict

        if item is None:
            return False

        # Try to stack with existing item
        if item.stackable:
            for i, slot_item in enumerate(self.items):
                if slot_item and slot_item.item_id == item.item_id:
                    space = slot_item.max_stack - slot_item.quantity
                    if space > 0:
                        to_add = min(space, item.quantity)
                        slot_item.quantity += to_add
                        item.quantity -= to_add
                        if item.quantity <= 0:
                            return True

        # Find empty slot
        for i, slot_item in enumerate(self.items):
            if slot_item is None:
                self.items[i] = item.copy() if isinstance(item, Item) else item
                return True

        # Inventory full
        return False

    def remove_item(self, slot_index):
        """Remove item from slot"""
        if 0 <= slot_index < self.slots:
            item = self.items[slot_index]
            self.items[slot_index] = None
            return item
        return None

    def use_item(self, slot_index, player, game):
        """Use item in slot"""
        if 0 <= slot_index < self.slots:
            item = self.items[slot_index]
            if item and item.usable:
                consumed = item.use(player, game)
                if consumed:
                    item.quantity -= 1
                    if item.quantity <= 0:
                        self.items[slot_index] = None
                return True
        return False

    def has_item(self, item_id):
        """Check if inventory contains item"""
        for item in self.items:
            if item and item.item_id == item_id:
                return True
        return False

    def get_item(self, item_id):
        """Get item by ID"""
        for item in self.items:
            if item and item.item_id == item_id:
                return item
        return None

    def get_item_count(self, item_id):
        """Get total count of item type"""
        count = 0
        for item in self.items:
            if item and item.item_id == item_id:
                count += item.quantity
        return count

    def get_ammo_count(self, ammo_type):
        """Get ammo count for weapon type"""
        ammo_id = f"ammo_{ammo_type}"
        return self.get_item_count(ammo_id)

    def use_ammo(self, ammo_type, amount=1):
        """Use ammo, returns True if successful"""
        ammo_id = f"ammo_{ammo_type}"
        for i, item in enumerate(self.items):
            if item and item.item_id == ammo_id:
                if item.quantity >= amount:
                    item.quantity -= amount
                    if item.quantity <= 0:
                        self.items[i] = None
                    return True
        return False

    def get_selected_item(self):
        """Get currently selected item"""
        if 0 <= self.selected_slot < self.slots:
            return self.items[self.selected_slot]
        return None

    def select_next(self):
        """Select next slot"""
        self.selected_slot = (self.selected_slot + 1) % self.slots

    def select_prev(self):
        """Select previous slot"""
        self.selected_slot = (self.selected_slot - 1) % self.slots

    def is_full(self):
        """Check if inventory is full"""
        return all(item is not None for item in self.items)

    def get_occupied_slots(self):
        """Get count of occupied slots"""
        return sum(1 for item in self.items if item is not None)


# Predefined items
ITEMS = {
    # Keys
    'key_lab': {
        'id': 'key_lab',
        'name': 'Lab Keycard',
        'type': ItemType.KEY,
        'description': 'Access card for laboratory sections. Level 2 clearance.'
    },
    'key_storage': {
        'id': 'key_storage',
        'name': 'Storage Key',
        'type': ItemType.KEY,
        'description': 'Rusted key for storage areas.'
    },
    'key_reactor': {
        'id': 'key_reactor',
        'name': 'Reactor Access Card',
        'type': ItemType.KEY,
        'description': 'Emergency access to reactor control. Handle with care.'
    },
    'key_deep': {
        'id': 'key_deep',
        'name': 'Excavation Pass',
        'type': ItemType.KEY,
        'description': 'Authorization for deep excavation levels. CLASSIFIED.'
    },

    # Weapons
    'weapon_pipe': {
        'id': 'weapon_pipe',
        'name': 'Metal Pipe',
        'type': ItemType.WEAPON,
        'description': 'A frozen metal pipe. Better than nothing.',
        'data': {'weapon_type': 'melee', 'damage': 25}
    },
    'weapon_pistol': {
        'id': 'weapon_pistol',
        'name': 'Makarov Pistol',
        'type': ItemType.WEAPON,
        'description': 'Standard Soviet sidearm. 8 round magazine.',
        'data': {'weapon_type': 'pistol', 'damage': 40}
    },

    # Ammo
    'ammo_pistol': {
        'id': 'ammo_pistol',
        'name': 'Pistol Ammo',
        'type': ItemType.AMMO,
        'description': '9x18mm ammunition.',
        'stackable': True,
        'max_stack': 24,
        'quantity': 8
    },

    # Healing
    'medkit': {
        'id': 'medkit',
        'name': 'Medical Kit',
        'type': ItemType.HEALING,
        'description': 'Field medical supplies. Restores health.',
        'usable': True,
        'data': {'heal_amount': 50}
    },
    'bandage': {
        'id': 'bandage',
        'name': 'Bandage',
        'type': ItemType.HEALING,
        'description': 'Basic wound dressing.',
        'usable': True,
        'stackable': True,
        'max_stack': 3,
        'data': {'heal_amount': 25}
    },

    # Warmth
    'heat_pack': {
        'id': 'heat_pack',
        'name': 'Heat Pack',
        'type': ItemType.WARMTH,
        'description': 'Chemical heating pad. Single use.',
        'usable': True,
        'stackable': True,
        'max_stack': 3,
        'data': {'warm_amount': 40}
    },
    'flask': {
        'id': 'flask',
        'name': 'Hot Flask',
        'type': ItemType.WARMTH,
        'description': 'Thermos of hot liquid. Still warm somehow.',
        'usable': True,
        'data': {'warm_amount': 60}
    },

    # Puzzle items
    'fuse': {
        'id': 'fuse',
        'name': 'Fuse',
        'type': ItemType.PUZZLE,
        'description': 'Replacement fuse for electrical systems.'
    },
    'tape_reel': {
        'id': 'tape_reel',
        'name': 'Data Tape',
        'type': ItemType.PUZZLE,
        'description': 'Magnetic tape reel. Contains unknown data.'
    },
    'crystal': {
        'id': 'crystal',
        'name': 'Strange Crystal',
        'type': ItemType.PUZZLE,
        'description': 'An unusual crystalline structure. It pulses faintly.'
    },
}


def create_item(item_id, quantity=1):
    """Create an item instance from predefined items"""
    if item_id in ITEMS:
        data = ITEMS[item_id].copy()
        data['quantity'] = quantity
        return data
    return None
