import os
import pygame
import random
from termcolor import cprint
from dotenv import load_dotenv
from math import sin, pi
from array import array
from sprites import Player, Bullet, Enemy, Particle, Explosion, PowerUp
from menu import Menu

# Initialize pygame and its mixer for sound
pygame.init()
pygame.mixer.init()

# Load environment variables
load_dotenv()

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60
INITIAL_LIVES = 5  # 初始生命数

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)

# Initialize game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()

class ResourceLoader:
    """Handles loading and managing game resources"""
    def __init__(self):
        self.images = {}
        self.sounds = {}
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        
        # 设置音量
        pygame.mixer.music.set_volume(0.5)  # BGM音量
        
        # 加载背景音乐
        self.menu_bgm_path = os.path.join(self.base_path, 'resources', 'sounds', 'menu_bgm.mp3')
        self.game_bgm_path = os.path.join(self.base_path, 'resources', 'sounds', 'game_bgm.mp3')
        
        # 加载武器音效
        # 武器音效文件名映射
        weapon_sounds = {
            'machine_gun': 'machine_gun.mp3',
            'laser': 'laser.mp3',
            'cannon': 'cannon.mp3',
            'shotgun': 'missle.mp3',  # 散弹使用原来的missile音效
            'missile': 'missle.mp3'   # 导弹也使用相同音效
        }
        for weapon, filename in weapon_sounds.items():
            self.load_sound(weapon, filename)
        
    def load_image(self, name, filename):
        """Load an image and store it in the images dictionary"""
        try:
            path = os.path.join(self.base_path, 'resources', 'images', filename)
            image = pygame.image.load(path).convert_alpha()
            self.images[name] = image
            cprint(f"Loaded image: {name}", "green")
            return image
        except pygame.error as e:
            cprint(f"Could not load image {filename}: {e}", "red")
            return None

    def load_sound(self, name, filename):
        """Load a sound and store it in the sounds dictionary"""
        try:
            path = os.path.join(self.base_path, 'resources', 'sounds', filename)
            sound = pygame.mixer.Sound(path)
            sound.set_volume(0.3)  # 设置音效音量
            self.sounds[name] = sound
            cprint(f"Loaded sound: {name}", "green")
            return sound
        except pygame.error as e:
            cprint(f"Could not load sound {filename}: {e}", "red")
            return None

    def get_image(self, name):
        """Get a loaded image by name"""
        return self.images.get(name)

    def get_sound(self, name):
        """Get a loaded sound by name"""
        return self.sounds.get(name)
        
    def play_bgm(self, state):
        """Play background music based on game state"""
        try:
            pygame.mixer.music.stop()
            if state == 'menu':
                pygame.mixer.music.load(self.menu_bgm_path)
            else:  # 'playing', 'paused', 'game_over'
                pygame.mixer.music.load(self.game_bgm_path)
            pygame.mixer.music.play(-1)  # -1表示循环播放
            cprint(f"开始播放BGM: {state}", "green")
        except Exception as e:
            cprint(f"无法播放BGM: {e}", "red")
    
    def play_weapon_sound(self, weapon_type):
        """Play weapon sound effect"""
        if weapon_type in self.sounds:
            self.sounds[weapon_type].play()
            cprint(f"播放武器音效: {weapon_type}", "cyan")

class ScreenShake:
    def __init__(self):
        self.shake_intensity = 0
        self.shake_duration = 0
        self.shake_timer = 0

    def start_shake(self, intensity, duration):
        self.shake_intensity = intensity
        self.shake_duration = duration
        self.shake_timer = pygame.time.get_ticks()

    def update(self):
        if pygame.time.get_ticks() - self.shake_timer < self.shake_duration:
            return (random.randint(-self.shake_intensity, self.shake_intensity),
                    random.randint(-self.shake_intensity, self.shake_intensity))
        else:
            return (0, 0)

class Game:
    def __init__(self):
        self.running = True
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.resource_loader = ResourceLoader()
        self.load_resources()
        
        # Screen shake
        self.screen_shake = ScreenShake()
        
        # Power-ups
        self.power_ups = pygame.sprite.Group()
        self.power_up_spawn_chance = 0.2  # 20% chance to spawn power-up from destroyed enemies
        
        # Formation management
        self.formation_type = 1
        self.player_ships = []  # List to hold all player ships
        self.ship_spacing = 80  # Horizontal spacing between ships
        
        # Round management
        self.current_round = 1
        self.round_score = 0  # Score in current round
        self.score_for_boss = 1000  # Base score needed for boss
        self.round_multiplier = 1.5  # Difficulty increase per round
        self.showing_round_announcement = False
        self.round_announcement_start = 0
        self.round_announcement_duration = 3000  # 3 seconds
        self.round_transition = False  # Flag for round transition
        
        # 音量控制
        self.volume = 0.5  # 初始音量为50%
        self.volume_display_time = 0
        self.volume_display_duration = 2000  # 显示2秒
        
        # 信息面板控制
        self.show_info_panel = True  # 信息面板显示状态
        self.update_volume()  # 初始化音量
        
        # Game states
        self.state = 'menu'  # 'menu', 'playing', 'paused', 'game_over'
        self.menu = Menu(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.selected_ship = 'interceptor'  # 默认飞船
        self.lives = INITIAL_LIVES  # 剩余生命数
        self.boss = None  # Track the boss enemy
        self.boss_spawned = False  # Flag to track if boss has been spawned
        self.last_health_check = 100  # Track last health percentage for redcross spawning
        
        
        # 开始播放菜单BGM
        self.resource_loader.play_bgm('menu')
        
        self.init_game()
    
    def create_life_icon(self):
        """创建生命值图标"""
        size = 24
        icon = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # 飞船主体 - 更环保的设计
        ship_color = (30, 144, 255)  # 亮蓝色
        pygame.draw.polygon(icon, ship_color, [
            (size//2, 4),          # 头部
            (size//4, size-6),     # 左下
            (size*3//4, size-6)    # 右下
        ])
        
        # 驱动器翅膀
        wing_color = (135, 206, 250)  # 浅蓝色
        pygame.draw.polygon(icon, wing_color, [
            (size//4, size-6),      # 左翅膀连接点
            (2, size-10),           # 左翅膀外点
            (size//3, size-6)       # 左翅膀内点
        ])
        pygame.draw.polygon(icon, wing_color, [
            (size*3//4, size-6),    # 右翅膀连接点
            (size-2, size-10),      # 右翅膀外点
            (size*2//3, size-6)     # 右翅膀内点
        ])
        
        # 驱动器光效
        engine_color = (0, 191, 255)  # 深蓝色
        pygame.draw.polygon(icon, engine_color, [
            (size//3, size-6),      # 左发光点
            (size//2, size-2),      # 中心发光点
            (size*2//3, size-6)     # 右发光点
        ])
        
        # 驱动器内核
        core_color = (255, 255, 0)  # 黄色
        pygame.draw.polygon(icon, core_color, [
            (size*2//5, size-6),
            (size//2, size-4),
            (size*3//5, size-6)
        ])
        
        # 驱动舱室
        cockpit_color = (173, 216, 230)  # 浅蓝色
        pygame.draw.ellipse(icon, cockpit_color, 
                           [size*3//8, size//2-2, size//4, size//3])
        
        # 添加发光效果
        glow = pygame.Surface((size+4, size+4), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 255, 255, 30), (size//2+2, size//2+2), size//2)
        icon.blit(glow, (-2, -2))
        
        return icon

    def init_game(self):
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()
        
        # Initialize player ships
        self.update_formation(1)  # Start with single ship
        
        # Reset round-related variables
        self.current_round = 1
        self.round_score = 0
        self.boss = None
        self.boss_spawned = False
        self.score_for_boss = 1000  # Reset base score
        self.showing_round_announcement = True
        self.round_announcement_start = pygame.time.get_ticks()
        
        # Reset lives
        self.lives = INITIAL_LIVES
        cprint(f"重置生命值为：{self.lives}", "green")
        
        # Create life icons
        self.life_icon = self.create_life_icon()
        self.life_icon_gray = self.life_icon.copy()
        # 创建灰色版本
        gray_surface = pygame.Surface(self.life_icon.get_size(), pygame.SRCALPHA)
        gray_surface.fill((128, 128, 128, 128))
        self.life_icon_gray.blit(gray_surface, (0, 0))
        
        # Spawn initial enemies
        for _ in range(8):
            self.spawn_enemy()
            
        # Score and UI with Chinese font support
        self.score = 0
        self.font, self.round_font = self.load_chinese_fonts()
        
        # Background stars
        self.stars = []
        for _ in range(50):
            x = random.randrange(SCREEN_WIDTH)
            y = random.randrange(SCREEN_HEIGHT)
            speed = random.uniform(0.5, 2.0)
            self.stars.append([x, y, speed])
        
    def load_chinese_fonts(self):
        """Load Chinese-compatible fonts with fallback options"""
        # Try project fonts first
        project_fonts = [
            os.path.join(os.path.dirname(__file__), 'resources', 'fonts', 'Hiragino Sans GB.ttc'),
        ]
        
        # System fonts as fallback
        system_font_files = [
            '/System/Library/Fonts/Hiragino Sans GB.ttc',
            '/System/Library/Fonts/STHeiti Medium.ttc',
            '/System/Library/Fonts/STHeiti Light.ttc',
            '/System/Library/Fonts/CJKSymbolsFallback.ttc',
        ]
        
        chinese_font_files = project_fonts + system_font_files
        
        # Try to load each font file directly
        for font_path in chinese_font_files:
            try:
                font = pygame.font.Font(font_path, 30)
                round_font = pygame.font.Font(font_path, 64)
                # Test if the font can render Chinese characters
                test_surface = font.render('中文测试', True, (255, 255, 255))
                if test_surface.get_width() > 0:
                    font_name = font_path.split('/')[-1]
                    cprint(f"成功加载中文字体: {font_name}", "green")
                    return font, round_font
            except Exception as e:
                cprint(f"无法加载字体 {font_path}: {e}", "yellow")
                continue
        
        # Try system fonts as fallback
        system_fonts = ['STHeiti', 'Hiragino Sans GB', 'Arial Unicode MS']
        for font_name in system_fonts:
            try:
                font = pygame.font.SysFont(font_name, 30)
                round_font = pygame.font.SysFont(font_name, 64)
                test_surface = font.render('中文测试', True, (255, 255, 255))
                if test_surface.get_width() > 0:
                    cprint(f"成功加载系统字体: {font_name}", "green")
                    return font, round_font
            except:
                continue
        
        # If no Chinese font works, use default font
        cprint("警告：无法加载中文字体，使用默认字体。中文可能显示为方块。", "yellow")
        return pygame.font.Font(None, 36), pygame.font.Font(None, 74)
    
    def load_ui_fonts(self):
        """Load UI fonts with different sizes based on Chinese font"""
        # Try project fonts first
        project_fonts = [
            os.path.join(os.path.dirname(__file__), 'resources', 'fonts', 'Hiragino Sans GB.ttc'),
        ]
        
        # System fonts as fallback
        system_font_files = [
            '/System/Library/Fonts/Hiragino Sans GB.ttc',
            '/System/Library/Fonts/STHeiti Medium.ttc',
            '/System/Library/Fonts/STHeiti Light.ttc',
            '/System/Library/Fonts/CJKSymbolsFallback.ttc',
        ]
        
        chinese_font_files = project_fonts + system_font_files
        
        # Try to load each font file directly
        for font_path in chinese_font_files:
            try:
                title_font = pygame.font.Font(font_path, 32)   # 标题字体
                main_font = pygame.font.Font(font_path, 24)    # 主要信息字体
                small_font = pygame.font.Font(font_path, 20)   # 小字体
                
                # Test if the font can render Chinese characters
                test_surface = main_font.render('中文测试', True, (255, 255, 255))
                if test_surface.get_width() > 0:
                    return title_font, main_font, small_font
            except Exception as e:
                continue
        
        # Try system fonts as fallback
        system_fonts = ['STHeiti', 'Hiragino Sans GB', 'Arial Unicode MS']
        for font_name in system_fonts:
            try:
                title_font = pygame.font.SysFont(font_name, 32)
                main_font = pygame.font.SysFont(font_name, 24)
                small_font = pygame.font.SysFont(font_name, 20)
                
                test_surface = main_font.render('中文测试', True, (255, 255, 255))
                if test_surface.get_width() > 0:
                    return title_font, main_font, small_font
            except:
                continue
        
        # If no Chinese font works, use default font
        cprint("警告：无法加载UI中文字体，使用默认字体。中文可能显示为方块。", "yellow")
        return pygame.font.Font(None, 32), pygame.font.Font(None, 24), pygame.font.Font(None, 20)

    def load_resources(self):
        """Load all game resources"""
        cprint("Loading game resources...", "yellow")
    
    def handle_events(self):
        """Handle game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif self.state == 'menu':
                result = self.menu.handle_event(event)
                if result[0] is not None:
                    action, data = result
                    
                    if action == 'start':
                        self.state = 'playing'
                        self.selected_ship = data
                        self.init_game()
                        self.resource_loader.play_bgm('game')  # 切换到游戏背景音乐
                    elif action == 'quit':
                        self.running = False
                    
            elif self.state == 'playing':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = 'paused'
                    elif event.key == pygame.K_SPACE:
                        for ship in self.player_ships:
                            ship.shoot()
                    elif event.key == pygame.K_TAB:
                        for ship in self.player_ships:
                            ship.switch_weapon()
                    elif event.key == pygame.K_MINUS:
                        self.volume = max(0.0, self.volume - 0.1)
                        self.update_volume()
                    elif event.key == pygame.K_EQUALS:
                        self.volume = min(1.0, self.volume + 0.1)
                        self.update_volume()
                    elif event.key == pygame.K_i:
                        self.show_info_panel = not self.show_info_panel
                        cprint(f"信息面板{'显示' if self.show_info_panel else '隐藏'}", "cyan")
                    # Formation control with number keys
                    elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                        formation_type = event.key - pygame.K_1 + 1
                        self.update_formation(formation_type)
                        
            elif self.state == 'paused':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = 'playing'
                    elif event.key == pygame.K_q:
                        self.state = 'menu'
                        self.resource_loader.play_bgm('menu')  # 返回菜单时切换回菜单音乐
                        
            elif self.state == 'game_over':
                if event.type == pygame.KEYDOWN:
                    self.state = 'menu'
                    self.resource_loader.play_bgm('menu')  # Return to menu music

    def spawn_enemy(self):
        """Spawn a new enemy"""
        # Enemy type weights
        weights = {
            'scout': 0.3,    # 30% chance
            'fighter': 0.2,  # 20% chance
            'striker': 0.2,  # 20% chance for green ship
            'elite': 0.15,   # 15% chance
            'bomber': 0.15   # 15% chance
        }
        
        enemy_type = random.choices(list(weights.keys()), 
                                  weights=list(weights.values()))[0]
        
        # Create enemy at random position at top of screen
        x = random.randrange(SCREEN_WIDTH - 40)
        enemy = Enemy(enemy_type, self.current_round)
        enemy.rect.x = x
        enemy.rect.y = random.randrange(-100, -40)
        
        self.all_sprites.add(enemy)
        self.enemies.add(enemy)
        cprint(f"Spawned a {enemy_type} enemy!", "red")

    def start_new_round(self):
        """Start a new round with increased difficulty"""
        self.current_round += 1
        self.round_score = 0
        self.boss_spawned = False
        self.boss = None
        
        # Reset player ships to starting positions
        main_ship = self.player_ships[0]
        main_ship.rect.centerx = SCREEN_WIDTH // 2
        main_ship.rect.bottom = SCREEN_HEIGHT - 20
        
        # Reset wing ships if they exist
        if len(self.player_ships) >= 2:
            self.player_ships[1].rect.centerx = main_ship.rect.centerx - self.ship_spacing
            self.player_ships[1].rect.bottom = main_ship.rect.bottom
            
        if len(self.player_ships) == 3:
            self.player_ships[2].rect.centerx = main_ship.rect.centerx + self.ship_spacing
            self.player_ships[2].rect.bottom = main_ship.rect.bottom
        
        # Increase difficulty
        self.score_for_boss = int(1000 * (self.round_multiplier ** (self.current_round - 1)))
        
        # Show round announcement
        self.showing_round_announcement = True
        self.round_announcement_start = pygame.time.get_ticks()
        self.round_transition = False
        
        # Clear all enemies
        for enemy in self.enemies:
            enemy.kill()
        
        # Spawn new enemies for the round
        for _ in range(8):
            self.spawn_enemy()
        
        cprint(f"Starting Round {self.current_round}!", "yellow", attrs=['bold'])

    def update(self):
        """Update game state"""
        # Get the time since the last frame
        now = pygame.time.get_ticks()
        
        # Update background stars
        for star in self.stars:
            star[1] += star[2]
            if star[1] > SCREEN_HEIGHT:
                star[1] = 0
                star[0] = random.randrange(SCREEN_WIDTH)
        
        if self.state == 'menu':
            self.menu.update_stars()
            
        elif self.state == 'playing':
            # Update all sprites
            self.all_sprites.update()
            
            # Check for collisions
            self.check_collisions()
            
            # Spawn enemies if needed
            if len(self.enemies) < 5 + self.current_round and not self.boss_spawned:
                self.spawn_enemy()
            
            # Check if it's time to spawn a boss
            if self.round_score >= self.score_for_boss and not self.boss_spawned:
                self.spawn_boss()
            
            # Check if round is complete
            if self.boss_spawned and self.boss is None:
                # Boss was spawned but is now dead, advance to next round
                self.advance_round()
            
            # Update screen shake
            self.shake_offset = self.screen_shake.update()
            
            # Get screen shake offset
            shake_offset = self.screen_shake.update()
            
            # Update ship positions in formation
            if len(self.player_ships) > 0:
                main_ship = self.player_ships[0]
                if len(self.player_ships) == 2:
                    # Two ship formation
                    self.player_ships[1].rect.centerx = main_ship.rect.centerx - self.ship_spacing
                    self.player_ships[1].rect.centery = main_ship.rect.centery
                elif len(self.player_ships) == 3:
                    # Three ship formation
                    self.player_ships[1].rect.centerx = main_ship.rect.centerx - self.ship_spacing
                    self.player_ships[1].rect.centery = main_ship.rect.centery
                    self.player_ships[2].rect.centerx = main_ship.rect.centerx + self.ship_spacing
                    self.player_ships[2].rect.centery = main_ship.rect.centery
            
            # Handle round announcement
            if self.showing_round_announcement:
                if pygame.time.get_ticks() - self.round_announcement_start > self.round_announcement_duration:
                    self.showing_round_announcement = False
                return  # Don't update game while showing announcement
            
            # Handle round transition
            if self.round_transition:
                self.start_new_round()
                return
            
            # Add bullets and their particles from all ships to all_sprites
            for ship in self.player_ships:
                for bullet in ship.bullets:
                    if bullet not in self.all_sprites:
                        self.all_sprites.add(bullet)
                    for particle in bullet.particles:
                        if particle not in self.all_sprites:
                            self.all_sprites.add(particle)
            
            # Check if player health has dropped by 25% or more
            current_health_percent = (self.player_ships[0].health / self.player_ships[0].max_health) * 100
            health_drop = self.last_health_check - current_health_percent
            
            if health_drop >= 25:
                self.spawn_redcross()
                self.last_health_check = current_health_percent
                cprint("Spawning a healing redcross ship!", "green")
            
            # Update particles
            self.particles.update()
            
            # Add new particles to all_sprites
            for particle in self.particles:
                if particle not in self.all_sprites:
                    self.all_sprites.add(particle)
            
            # Add particles from all player ships
            for ship in self.player_ships:
                for particle in ship.particles:
                    if particle not in self.all_sprites:
                        self.all_sprites.add(particle)
            
            # Add enemy bullets and their particles to all_sprites
            for enemy in self.enemies:
                for particle in enemy.particles:
                    if particle not in self.all_sprites:
                        self.all_sprites.add(particle)
                for bullet in enemy.bullets:
                    if bullet not in self.all_sprites:
                        self.all_sprites.add(bullet)
                    for particle in bullet.particles:
                        if particle not in self.all_sprites:
                            self.all_sprites.add(particle)
            
            # Remove dead particles
            for sprite in self.all_sprites.copy():
                if isinstance(sprite, (Particle, Explosion)) and not sprite.alive():
                    self.all_sprites.remove(sprite)
            
            # 检查玩家与敌人的碰撞
            for ship in self.player_ships:
                hits = pygame.sprite.spritecollide(ship, self.enemies, False,
                                                 pygame.sprite.collide_circle)
                if hits:
                    # 玩家与敌人相撞，立即死亡
                    self.handle_player_death(ship)
                    return

            # 检查敌人子弹与玩家的碰撞
            for enemy in self.enemies:
                for ship in self.player_ships:
                    hits = pygame.sprite.spritecollide(ship, enemy.bullets, True,
                                                     pygame.sprite.collide_circle)
                    for bullet in hits:
                        ship.take_damage(bullet.damage)
                        explosion = Explosion(bullet.rect.center, 10, self.particles)
                        if ship.health <= 0:
                            self.handle_player_death(ship)
                            return
            
            # Spawn boss when round score reaches threshold
            if not self.boss_spawned and self.round_score >= self.score_for_boss:
                self.spawn_boss()

            # Check power-up collisions with player ships
            for ship in self.player_ships:
                hits = pygame.sprite.spritecollide(ship, self.power_ups, True)
                for power_up in hits:
                    self.apply_power_up(ship, power_up.type)
                    # Add collection particles
                    for _ in range(10):
                        particle = Particle(power_up.rect.centerx, power_up.rect.centery,
                                         power_up.config['color'],
                                         random.uniform(-2, 2),
                                         random.uniform(-2, 2))
                        self.particles.add(particle)
                        self.all_sprites.add(particle)

    def draw(self):
        """Draw the game screen"""
        screen.fill(BLACK)
        
        if self.state == 'menu':
            self.menu.draw(screen)
            
        elif self.state in ['playing', 'paused']:
            # Apply screen shake offset
            shake_offset = self.screen_shake.update()
            
            # Create a surface for the game view
            game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            game_surface.fill(BLACK)
            
            # Draw background stars
            for x, y, _ in self.stars:
                pygame.draw.circle(game_surface, WHITE, (int(x), int(y)), 1)
            
            # Draw game objects on the game surface
            # 先绘制非子弹对象
            for sprite in self.all_sprites:
                if not hasattr(sprite, 'weapon_type'):  # 非子弹对象
                    game_surface.blit(sprite.image, sprite.rect)
            
            # 然后绘制子弹（使用自定义draw方法显示轨迹）
            for ship in self.player_ships:
                for bullet in ship.bullets:
                    if hasattr(bullet, 'draw'):
                        bullet.draw(game_surface)
                    else:
                        game_surface.blit(bullet.image, bullet.rect)
            
            # Apply the shake offset when blitting to the screen
            screen.blit(game_surface, shake_offset)
            
            # Draw UI elements directly on the screen (no shake)
            # Round, Score, and Weapon in Chinese with better formatting
            # 添加文字阴影效果
            shadow_color = (50, 50, 50)
            shadow_offset = 2
            
            # 使用不同字体大小创建更美观的UI（基于已加载的中文字体）
            title_font, main_font, small_font = self.load_ui_fonts()
            
            # 关卡显示 - 使用主要字体保持一致
            round_shadow = main_font.render(f'第 {self.current_round} 关', True, shadow_color)
            round_text = main_font.render(f'第 {self.current_round} 关', True, (255, 215, 0))  # 金色
            
            # 总分显示 - 使用中等字体
            score_shadow = main_font.render(f'总分: {self.score}', True, shadow_color)
            score_text = main_font.render(f'总分: {self.score}', True, (135, 206, 250))  # 天蓝色
            
            # 当前关卡分数显示 - 使用中等字体
            round_score_shadow = main_font.render(f'关卡分数: {self.round_score}', True, shadow_color)
            round_score_text = main_font.render(f'关卡分数: {self.round_score}', True, (144, 238, 144))  # 浅绿色
            
            # 武器名称中文化和颜色映射
            weapon_names = {
                'machine_gun': ('机枪', (255, 165, 0)),    # 橙色
                'laser': ('激光', (0, 255, 255)),         # 青色
                'cannon': ('炮弹', (255, 69, 0)),         # 红橙色
                'shotgun': ('散弹', (255, 50, 50)),       # 红色
                'missile': ('导弹', (50, 205, 50)),        # 绿色
                'beam': ('光束', (255, 0, 255))           # 紫色
            }
            weapon_name, weapon_color = weapon_names.get(
                self.player_ships[0].current_weapon, 
                (self.player_ships[0].current_weapon, WHITE)
            )
            weapon_shadow = main_font.render(f'武器: {weapon_name} (TAB切换)', True, shadow_color)
            weapon_text = main_font.render(f'武器: {weapon_name} (TAB切换)', True, weapon_color)
            
            # 信息面板切换功能
            if self.show_info_panel:
                # 完整信息面板
                current_y = 10
                
                # 1. 关卡显示
                screen.blit(round_shadow, (10 + shadow_offset, current_y + shadow_offset))
                screen.blit(round_text, (10, current_y))
                current_y += 30  # 减少间距，保持一致
            else:
                # 隐藏状态，只显示提示
                hint_shadow = small_font.render('按 i 打开信息面板', True, shadow_color)
                hint_text = small_font.render('按 i 打开信息面板', True, (200, 200, 200))
                
                screen.blit(hint_shadow, (10 + shadow_offset, 10 + shadow_offset))
                screen.blit(hint_text, (10, 10))
                
                # 跳过所有其他UI元素的渲染
                current_y = -1  # 标记为隐藏状态
            
            # 只有在显示信息面板时才渲染其他UI元素
            if self.show_info_panel and current_y != -1:
                # 2. Boss进度条 - 紧跟在关卡信息后面
                if not self.boss_spawned:
                    boss_progress = min(1.0, self.round_score / self.score_for_boss)
                    boss_text = f'Boss进度: {self.round_score}/{self.score_for_boss}'
                    boss_shadow = main_font.render(boss_text, True, shadow_color)
                    boss_text_surface = main_font.render(boss_text, True, (255, 150, 150))  # 浅红色
                    
                    screen.blit(boss_shadow, (10 + shadow_offset, current_y + shadow_offset))
                    screen.blit(boss_text_surface, (10, current_y))
                    current_y += 27  # 增加间距，避免重叠
                    
                    # 进度条 - 增加高度
                    progress_bar_width = 180
                    progress_bar_height = 10
                    progress_x = 10
                    progress_y = current_y
                    
                    # 背景
                    pygame.draw.rect(screen, (60, 60, 60), 
                                   (progress_x, progress_y, progress_bar_width, progress_bar_height))
                    # 进度
                    progress_width = int(progress_bar_width * boss_progress)
                    if boss_progress < 0.6:
                        color = (100, 255, 100)  # 绿色
                    elif boss_progress < 0.8:
                        color = (255, 255, 100)  # 黄色
                    else:
                        color = (255, 100, 100)  # 红色
                    pygame.draw.rect(screen, color, 
                                   (progress_x, progress_y, progress_width, progress_bar_height))
                    # 边框
                    pygame.draw.rect(screen, (200, 200, 200), 
                                   (progress_x, progress_y, progress_bar_width, progress_bar_height), 1)
                    
                    current_y += 25  # 增加间距，为下一个元素留出空间
                else:
                    boss_shadow = main_font.render('🔥 Boss已出现！', True, shadow_color)
                    boss_text_surface = main_font.render('🔥 Boss已出现！', True, (255, 80, 80))  # 深红色
                    
                    screen.blit(boss_shadow, (10 + shadow_offset, current_y + shadow_offset))
                    screen.blit(boss_text_surface, (10, current_y))
                    current_y += 30
                    
                # 3. 总分显示
                screen.blit(score_shadow, (10 + shadow_offset, current_y + shadow_offset))
                screen.blit(score_text, (10, current_y))
                current_y += 27  # 统一间距
                
                # 4. 当前关卡分数显示
                screen.blit(round_score_shadow, (10 + shadow_offset, current_y + shadow_offset))
                screen.blit(round_score_text, (10, current_y))
                current_y += 27  # 统一间距
                
                # 5. 武器信息显示
                weapon_y = current_y
                
                screen.blit(weapon_shadow, (10 + shadow_offset, weapon_y + shadow_offset))
                screen.blit(weapon_text, (10, weapon_y))
            
                # 6. 编队信息显示
                formation_names = {1: '单机', 2: '双机', 3: '三机'}
                formation_name = formation_names.get(self.formation_type, '未知')
                formation_shadow = small_font.render(f'编队: {formation_name} (1/2/3键)', True, shadow_color)
                formation_text = small_font.render(f'编队: {formation_name} (1/2/3键)', True, (200, 200, 200))
                
                formation_y = weapon_y + 27  # 统一间距
                screen.blit(formation_shadow, (10 + shadow_offset, formation_y + shadow_offset))
                screen.blit(formation_text, (10, formation_y))
                
                # 7. 射击提示
                shoot_shadow = small_font.render('空格键: 发射子弹', True, shadow_color)
                shoot_text = small_font.render('空格键: 发射子弹', True, (200, 200, 200))
                
                shoot_y = formation_y + 23  # 小字体间距稍小
                screen.blit(shoot_shadow, (10 + shadow_offset, shoot_y + shadow_offset))
                screen.blit(shoot_text, (10, shoot_y))
                
                # 8. 隐藏面板提示
                hide_shadow = small_font.render('按 i 隐藏信息面板', True, shadow_color)
                hide_text = small_font.render('按 i 隐藏信息面板', True, (150, 150, 150))  # 更浅的灰色
                
                hide_y = shoot_y + 23  # 小字体间距稍小
                screen.blit(hide_shadow, (10 + shadow_offset, hide_y + shadow_offset))
                screen.blit(hide_text, (10, hide_y))
            
            # UI elements are now positioned in the render code above
            
            # Health bar
            health_width = 200
            health_height = 20
            health_x = SCREEN_WIDTH - health_width - 10
            health_y = 20
            
            # Background
            pygame.draw.rect(screen, RED, (health_x, health_y, health_width, health_height))
            # Health
            current_health = max(0, self.player_ships[0].health / self.player_ships[0].max_health * health_width)
            pygame.draw.rect(screen, GREEN, (health_x, health_y, current_health, health_height))
            
            # Draw life icons with background - match health bar width
            health_width = 200  # 与血条相同的宽度
            icon_section_height = 40  # 高度保持不变
            
            # 计算图标间距，使其均匀分布
            total_icons = INITIAL_LIVES
            icon_size = 24  # 图标大小
            spacing = (health_width - (total_icons * icon_size)) // (total_icons + 1)
            
            # 绘制背景板
            icon_bg_x = SCREEN_WIDTH - health_width - 10  # 与血条对齐
            icon_bg_y = health_y + health_height + 10
            
            # 半透明背景
            bg_surface = pygame.Surface((health_width, icon_section_height), pygame.SRCALPHA)
            pygame.draw.rect(bg_surface, (0, 0, 0, 128), bg_surface.get_rect(), border_radius=5)
            screen.blit(bg_surface, (icon_bg_x, icon_bg_y))
            
            # 添加边框
            pygame.draw.rect(screen, (255, 255, 255, 64), 
                           (icon_bg_x, icon_bg_y, health_width, icon_section_height),
                           1, border_radius=5)
            
            # 绘制生命图标
            start_y = icon_bg_y + (icon_section_height - icon_size) // 2  # 垂直居中
            
            # 从左到右绘制图标
            for i in range(INITIAL_LIVES):
                # 计算每个图标的X坐标
                icon_x = icon_bg_x + spacing + (i * (icon_size + spacing))
                
                # 添加发光效果
                if i >= (INITIAL_LIVES - self.lives):  # 从右边开始显示活跃图标
                    # 活跃生命图标的光效
                    glow_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surface, (0, 255, 255, 30), (16, 16), 14)
                    screen.blit(glow_surface, (icon_x-4, start_y-4))
                    screen.blit(self.life_icon, (icon_x, start_y))
                else:
                    screen.blit(self.life_icon_gray, (icon_x, start_y))
            
            # Draw round announcement if active
            if self.showing_round_announcement:
                # Create semi-transparent overlay
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.fill(BLACK)
                overlay.set_alpha(128)
                screen.blit(overlay, (0, 0))
                
                # Calculate animation progress (0 to 1)
                progress = min(1.0, (pygame.time.get_ticks() - self.round_announcement_start) / 1000)
                
                # Animate the text scaling and fading
                scale = 1.5 - (0.5 * progress)  # Start large and shrink
                alpha = 255 if progress < 0.7 else int(255 * (1 - (progress - 0.7) / 0.3))
                
                # Render the round announcement in Chinese
                round_text = self.round_font.render(f"第 {self.current_round} 关", True, WHITE)
                round_text.set_alpha(alpha)
                
                # Scale and position the text
                scaled_size = (int(round_text.get_width() * scale), 
                             int(round_text.get_height() * scale))
                scaled_text = pygame.transform.scale(round_text, scaled_size)
                text_rect = scaled_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                
                screen.blit(scaled_text, text_rect)
            
            # 绘制BGM音量条
            if pygame.time.get_ticks() - self.volume_display_time < self.volume_display_duration:
                # 创建半透明的背景
                volume_surface = pygame.Surface((200, 30))
                volume_surface.fill(BLACK)
                volume_surface.set_alpha(128)
                
                # 绘制音量条
                bar_width = int(180 * self.volume)
                pygame.draw.rect(volume_surface, (100, 100, 100), [10, 10, 180, 10])
                pygame.draw.rect(volume_surface, GREEN, [10, 10, bar_width, 10])
                
                # 显示在屏幕上方
                volume_text = self.font.render('BGM Volume', True, WHITE)
                screen.blit(volume_text, (300, 15))
                screen.blit(volume_surface, (400, 10))
            
            # If paused, draw pause menu
            if self.state == 'paused':
                s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                s.set_alpha(128)
                s.fill(BLACK)
                screen.blit(s, (0,0))
                
                pause_text = self.font.render('PAUSED', True, WHITE)
                resume_text = self.font.render('Press ESC to Resume', True, WHITE)
                quit_text = self.font.render('Press Q to Quit to Menu', True, WHITE)
                
                screen.blit(pause_text, 
                           (SCREEN_WIDTH//2 - pause_text.get_width()//2, 
                            SCREEN_HEIGHT//2 - 60))
                screen.blit(resume_text, 
                           (SCREEN_WIDTH//2 - resume_text.get_width()//2, 
                            SCREEN_HEIGHT//2))
                screen.blit(quit_text, 
                           (SCREEN_WIDTH//2 - quit_text.get_width()//2, 
                            SCREEN_HEIGHT//2 + 40))
                
        elif self.state == 'game_over':
            game_over_text = self.font.render('GAME OVER', True, RED)
            score_text = self.font.render(f'Final Score: {self.score}', True, WHITE)
            continue_text = self.font.render('Press any key to continue', True, WHITE)
            
            screen.blit(game_over_text, 
                       (SCREEN_WIDTH//2 - game_over_text.get_width()//2, 
                        SCREEN_HEIGHT//2 - 60))
            screen.blit(score_text, 
                       (SCREEN_WIDTH//2 - score_text.get_width()//2, 
                        SCREEN_HEIGHT//2))
            screen.blit(continue_text, 
                       (SCREEN_WIDTH//2 - continue_text.get_width()//2, 
                        SCREEN_HEIGHT//2 + 60))
        
        pygame.display.flip()

    def update_volume(self):
        """Update BGM volume"""
        pygame.mixer.music.set_volume(self.volume)  # 只调整BGM音量
            
        # 更新显示计时器
        self.volume_display_time = pygame.time.get_ticks()
        cprint(f"BGM音量调整为: {int(self.volume * 100)}%", "cyan")
    
    def run(self):
        """Main game loop"""
        global clock
        clock = pygame.time.Clock()
        
        # Main game loop
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            
            # Cap the frame rate
            clock.tick(FPS)
        
        # Clean up
        pygame.quit()

    def spawn_boss(self):
        """Spawn a boss enemy"""
        cprint("警告：Boss出现！", "red", attrs=['bold'])
        self.boss = Enemy('boss', self.current_round)
        self.boss.player = self.player_ships[0]  # Add reference to player for aiming
        self.all_sprites.add(self.boss)
        self.enemies.add(self.boss)
        self.boss_spawned = True

    def spawn_redcross(self):
        """Spawn a healing redcross ship"""
        enemy = Enemy('redcross', self.current_round)  # Round number won't affect redcross
        self.all_sprites.add(enemy)
        self.enemies.add(enemy)
        cprint("生成了一个医疗救援船！", "green")

    def update_formation(self, formation_type):
        """Update the player ship formation"""
        # Clear existing ships
        for ship in self.player_ships:
            ship.kill()
        self.player_ships.clear()
        
        self.formation_type = formation_type
        available_ships = list(Player.SHIP_DESIGNS.keys())
        available_ships.remove(self.selected_ship)  # Remove current ship type
        
        # Create main ship
        main_ship = Player(self.resource_loader, self.selected_ship)
        main_ship.rect.centerx = SCREEN_WIDTH // 2
        main_ship.rect.bottom = SCREEN_HEIGHT - 20
        self.player_ships.append(main_ship)
        
        # Add additional ships based on formation type
        if formation_type >= 2:
            wing_ship1 = Player(self.resource_loader, random.choice(available_ships))
            wing_ship1.rect.centerx = main_ship.rect.centerx - self.ship_spacing
            wing_ship1.rect.bottom = main_ship.rect.bottom
            self.player_ships.append(wing_ship1)
            
        if formation_type == 3:
            remaining_ships = [s for s in available_ships if s != self.player_ships[1].ship_type]
            wing_ship2 = Player(self.resource_loader, random.choice(remaining_ships))
            wing_ship2.rect.centerx = main_ship.rect.centerx + self.ship_spacing
            wing_ship2.rect.bottom = main_ship.rect.bottom
            self.player_ships.append(wing_ship2)
        
        # Add all ships to sprite groups and set enemies list
        for ship in self.player_ships:
            self.all_sprites.add(ship)
            ship.enemies = self.enemies  # 为导弹追踪设置敌人列表
            
        cprint(f"Formation updated: {len(self.player_ships)} ships", "cyan")

    def handle_player_death(self, ship):
        """处理玩家死亡"""
        # 创建爆炸效果
        explosion = Explosion(ship.rect.center, 40, self.particles)
        
        # 减少生命数
        self.lives -= 1
        cprint(f"玩家死亡！剩余生命：{self.lives}", "red")
        
        if self.lives <= 0:
            # 没有生命了，游戏结束
            cprint("游戏结束！", "red")
            self.state = 'game_over'
            self.resource_loader.play_bgm('menu')
        else:
            # 还有生命，重置玩家位置和状态
            ship.health = ship.max_health
            ship.rect.centerx = SCREEN_WIDTH // 2
            ship.rect.bottom = SCREEN_HEIGHT - 20
            ship.is_invulnerable = True
            ship.invulnerable_timer = pygame.time.get_ticks()
            
            # 清除所有敌人和子弹
            for enemy in self.enemies:
                enemy.kill()
            for enemy_bullet in [bullet for enemy in self.enemies for bullet in enemy.bullets]:
                enemy_bullet.kill()
            
            # 重新生成敌人
            for _ in range(4):
                self.spawn_enemy()
    
    def apply_power_up(self, ship, power_type):
        """Apply power-up effects to the ship"""
        if power_type == 'shield':
            ship.shield = 50
            cprint("Shield power-up activated!", "cyan")
        elif power_type == 'speed':
            ship.speed_x *= 1.5
            ship.speed_y *= 1.5
            # Reset speed after duration
            pygame.time.set_timer(pygame.USEREVENT + 1, PowerUp.TYPES['speed']['duration'])
            cprint("Speed boost activated!", "yellow")
        elif power_type == 'weapon':
            # Store current weapon and switch to enhanced version
            ship.previous_weapon = ship.current_weapon
            if ship.current_weapon == 'machine_gun':
                ship.weapons['machine_gun'].damage *= 2
                ship.weapons['machine_gun'].shoot_delay //= 2
            elif ship.current_weapon == 'laser':
                ship.weapons['laser'].damage *= 1.5
            elif ship.current_weapon == 'cannon':
                ship.weapons['cannon'].damage *= 1.5
            elif ship.current_weapon == 'missile':
                ship.weapons['missile'].damage *= 1.5
            # Reset weapon after duration
            pygame.time.set_timer(pygame.USEREVENT + 2, PowerUp.TYPES['weapon']['duration'])
            cprint("Weapon power-up activated!", "magenta")


    def check_collisions(self):
        """检查所有碰撞"""
        # 检查子弹与敌人的碰撞
        for ship in self.player_ships:
            for bullet in ship.bullets:
                hits = pygame.sprite.spritecollide(bullet, self.enemies, False, 
                                                 pygame.sprite.collide_circle)
                for enemy in hits:
                    if enemy.take_damage(bullet.damage):
                        # 生成道具的概率
                        if random.random() < self.power_up_spawn_chance:
                            power_type = random.choice(['shield', 'speed', 'weapon'])
                            power_up = PowerUp(enemy.rect.centerx, enemy.rect.centery, power_type)
                            self.power_ups.add(power_up)
                            self.all_sprites.add(power_up)
                            cprint(f"生成了 {power_type} 道具!", "cyan")
                        
                        # 添加屏幕震动效果
                        shake_intensity = 10 if enemy.enemy_type == 'boss' else 5
                        self.screen_shake.start_shake(shake_intensity, 250)
                        
                        # 处理红十字敌人的治疗效果
                        if enemy.enemy_type == 'redcross':
                            heal_amount = enemy.design['heal_amount']
                            # 治疗编队中的所有飞船
                            for player_ship in self.player_ships:
                                player_ship.health = min(player_ship.max_health, 
                                                       player_ship.health + heal_amount)
                            cprint(f"从红十字敌人获得了 {heal_amount} 点治疗!", "green")
                            self.last_health_check = (self.player_ships[0].health / self.player_ships[0].max_health) * 100
                        else:
                            self.score += enemy.points
                            self.round_score += enemy.points
                            
                            # 如果击败了Boss，触发下一轮
                            if enemy.enemy_type == 'boss':
                                self.round_transition = True
                                continue
                        
                        # 创建爆炸效果
                        explosion = Explosion(enemy.rect.center, 
                                           60 if enemy.enemy_type == 'boss' else 
                                           40 if enemy.enemy_type == 'elite' else 
                                           30 if enemy.enemy_type == 'bomber' else 
                                           20, 
                                           self.particles)
                        enemy.kill()
                        if enemy.enemy_type not in ['boss', 'redcross']:
                            self.spawn_enemy()
                        cprint(f"击毁了{enemy.enemy_type}敌人！得分：{enemy.points}", "yellow")
                    # 如果不是激光，子弹在命中后消失
                    if bullet.weapon_type != 'laser':
                        bullet.kill()
                        # 创建小爆炸效果
                        explosion = Explosion(bullet.rect.center, 10, self.particles)
        
        # 检查玩家与敌人的碰撞
        for ship in self.player_ships:
            hits = pygame.sprite.spritecollide(ship, self.enemies, False,
                                             pygame.sprite.collide_circle)
            for enemy in hits:
                # 玩家与敌人碰撞，双方都受伤
                if ship.shield > 0:
                    # 如果有护盾，先消耗护盾
                    ship.shield -= enemy.collision_damage
                    if ship.shield < 0:
                        ship.health += ship.shield  # 溢出伤害传递给生命值
                        ship.shield = 0
                else:
                    ship.health -= enemy.collision_damage
                
                # 敌人受到碰撞伤害
                if hasattr(ship, 'collision_damage'):
                    collision_damage = ship.collision_damage
                else:
                    collision_damage = 20  # 默认碰撞伤害
                
                if enemy.take_damage(collision_damage):
                    # 创建爆炸效果
                    explosion = Explosion(enemy.rect.center, 
                                       40 if enemy.enemy_type == 'elite' else 
                                       30 if enemy.enemy_type == 'bomber' else 
                                       20, 
                                       self.particles)
                    enemy.kill()
                    if enemy.enemy_type != 'boss':
                        self.spawn_enemy()
                
                # 添加屏幕震动效果
                self.screen_shake.start_shake(10, 250)
                
                # 检查玩家是否死亡
                if ship.health <= 0:
                    # 创建爆炸效果
                    explosion = Explosion(ship.rect.center, 50, self.particles)
                    ship.kill()
                    self.player_ships.remove(ship)
                    
                    # 减少生命数
                    self.lives -= 1
                    cprint(f"玩家飞船被摧毁！剩余生命：{self.lives}", "red")
                    
                    # 如果还有生命，重生玩家
                    if self.lives > 0:
                        self.respawn_player()
                    else:
                        self.state = 'game_over'
                        cprint("游戏结束！", "red")
        
        # 检查玩家与道具的碰撞
        for ship in self.player_ships:
            hits = pygame.sprite.spritecollide(ship, self.power_ups, True)
            for power_up in hits:
                self.apply_power_up(power_up.type, ship)
                # Add collection particles
                for _ in range(10):
                    particle = Particle(power_up.rect.centerx, power_up.rect.centery,
                                     power_up.config['color'],
                                     random.uniform(-2, 2),
                                     random.uniform(-2, 2))
                    self.particles.add(particle)
                    self.all_sprites.add(particle)

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
