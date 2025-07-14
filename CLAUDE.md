# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Space Shooter game built with Python and Pygame. The game features:
- Single-player mode
- Multiple ship types with different weapons
- Boss battles with phases
- Power-ups and particle effects
- Chinese language support

## Development Environment

### Setup Commands
```bash
# Create virtual environment
uv venv --python=3.11

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
uv sync

# Run the game
uv run game.py
```

### Important Development Rules
- Use `cprint` from termcolor to print status messages
- All major variables should be ALL_CAPS at the top of scripts
- Use `encoding="utf-8"` when opening files
- Store API keys in .env file and load with dotenv
- Virtual environment is at `.venv`

## Game Architecture

### Core Components
1. **game.py** - Main game engine with Game class
2. **sprites.py** - All game objects (Player, Enemy, Bullet, PowerUp, Particle)
3. **menu.py** - Menu system with ship selection

### Key Classes
- `Game` - Main game loop, state management, collision detection
- `Player` - Player ship with weapons, movement, health system
- `Enemy` - Enemy ships with AI, different types, boss phases
- `Bullet` - Projectiles with particle effects
- `PowerUp` - Collectible items with temporary effects
- `Menu` - Game menu with Chinese UI

### Game Flow
1. Menu → Ship selection → Start game
2. Initialize game with selected ship
3. Game loop: Update → Collision detection → Drawing
4. Round progression with boss battles

## Technical Features

### Weapon System
- Multiple weapon types: machine_gun, laser, cannon, missile
- Different bullet patterns and damage values
- Sound effects and particle trails

### Enemy System
- Types: scout, fighter, striker, bomber, elite, boss, redcross (healing)
- Boss phases with different colors and attack patterns
- Round-based difficulty scaling


### Visual Effects
- Particle systems for explosions and trails
- Screen shake on impacts
- Animated UI elements

## Common Tasks

### Adding New Weapon Type
1. Add weapon config to `Player.weapons` dictionary
2. Update `Bullet.__init__()` with new weapon rendering
3. Add sound effect to `ResourceLoader.load_sound()`
4. Update weapon switching logic in `Player.switch_weapon()`

### Adding New Enemy Type
1. Add enemy design to `Enemy.ENEMY_DESIGNS`
2. Update enemy rendering in `Enemy.__init__()`
3. Add bullet pattern in `Enemy.shoot()`
4. Update spawn weights in `Game.spawn_enemy()`

### Debugging
- Use `cprint()` for status messages with color coding
- Check collision detection with `pygame.sprite.collide_circle`

### Testing
- Test single-player mode
- Verify weapon switching and power-ups
- Test boss phase transitions

## File Structure
```
SpaceShooter/
├── game.py          # Main game engine
├── sprites.py       # Game objects
├── menu.py         # Menu system
├── pyproject.toml   # Project configuration and dependencies
├── CLAUDE.md       # Development guide
└── resources/      # Assets
    ├── sounds/     # Audio files
    └── images/     # Image files
```

## Audio System
- Background music changes based on game state (menu/game)
- Weapon sound effects mapped to weapon types
- Volume control with real-time adjustment

## Known Considerations
- Chinese font support for UI elements
- Boss phase color transitions
- Particle system performance optimization