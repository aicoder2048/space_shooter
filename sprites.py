import pygame
import math
import random
from array import array
from math import sin, pi
from termcolor import cprint

# Global debug function
def debug_print(message, color="white"):
    """Debug信息输出控制"""
    # 从game模块导入DEBUG_MODE
    try:
        from game import DEBUG_MODE
        if DEBUG_MODE:
            cprint(message, color)
    except ImportError:
        # 如果导入失败，不输出debug信息
        pass

class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color, speed_x, speed_y, size=3, gravity=0):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.x = float(x)
        self.y = float(y)
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.gravity = gravity
        self.alpha = 255
        self.fade_speed = random.randint(5, 10)

    def update(self):
        self.speed_y += self.gravity
        self.x += self.speed_x
        self.y += self.speed_y
        self.rect.x = self.x
        self.rect.y = self.y
        self.alpha -= self.fade_speed
        if self.alpha <= 0:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size, particle_group):
        super().__init__()
        self.size = size
        self.center = center
        self.particle_group = particle_group
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50  # 爆炸动画速度
        
        # 创建一个空的surface作为image属性
        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=center)
        
        # 创建爆炸粒子
        self.create_particles()
        
    def create_particles(self):
        particle_count = int(self.size * 1.5)  # 根据爆炸大小调整粒子数量
        
        # 主爆炸圈
        for angle in range(0, 360, 360 // particle_count):
            speed = random.uniform(2, 5) * (self.size / 20)
            rad = math.radians(angle)
            speed_x = math.cos(rad) * speed
            speed_y = math.sin(rad) * speed
            size = random.randint(2, 4) * (self.size / 20)
            # 橙色到红色的随机颜色
            color = (random.randint(200, 255), 
                    random.randint(50, 150), 
                    0)
            particle = Particle(self.center[0], self.center[1], 
                              color, speed_x, speed_y, size, 0.1)
            self.particle_group.add(particle)
        
        # 火花效果
        spark_count = int(self.size * 0.8)
        for _ in range(spark_count):
            speed = random.uniform(3, 8) * (self.size / 20)
            angle = random.uniform(0, 360)
            rad = math.radians(angle)
            speed_x = math.cos(rad) * speed
            speed_y = math.sin(rad) * speed
            size = random.randint(1, 3) * (self.size / 20)
            # 明亮的黄色火花
            color = (255, random.randint(200, 255), 0)
            particle = Particle(self.center[0], self.center[1], 
                              color, speed_x, speed_y, size, 0.2)
            self.particle_group.add(particle)
        
        # 烟雾效果
        smoke_count = int(self.size * 0.6)
        for _ in range(smoke_count):
            speed = random.uniform(1, 3) * (self.size / 20)
            angle = random.uniform(0, 360)
            rad = math.radians(angle)
            speed_x = math.cos(rad) * speed
            speed_y = math.sin(rad) * speed - 1  # 向上飘
            size = random.randint(3, 6) * (self.size / 20)
            # 灰色烟雾
            gray = random.randint(60, 120)
            color = (gray, gray, gray)
            particle = Particle(self.center[0], self.center[1], 
                              color, speed_x, speed_y, size, 0.05)
            self.particle_group.add(particle)

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.kill()  # 爆炸效果完成后移除自身

def generate_sound(frequency, duration, volume=0.5, sample_rate=44100):
    n_samples = int(duration * sample_rate)
    buf = array('h', [0] * n_samples)
    max_sample = 2**(16 - 1) - 1
    for i in range(n_samples):
        t = float(i) / sample_rate
        buf[i] = int(volume * max_sample * sin(2 * pi * frequency * t))
    return pygame.mixer.Sound(buf)

class Weapon:
    def __init__(self, damage, bullet_speed, shoot_delay, bullet_type='normal'):
        self.damage = damage
        self.bullet_speed = bullet_speed
        self.shoot_delay = shoot_delay
        self.bullet_type = bullet_type
        try:
            if bullet_type == 'normal':
                self.sound = generate_sound(1000, 0.1, 0.3)
            elif bullet_type == 'laser':
                self.sound = generate_sound(2000, 0.1, 0.3)
            elif bullet_type == 'shotgun':
                self.sound = generate_sound(500, 0.2, 0.4)
            else:  # missile
                self.sound = generate_sound(300, 0.3, 0.5)
        except:
            self.sound = None
            cprint(f"Could not generate sound for {bullet_type}", "red")

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, weapon_type='normal', angle=0):
        super().__init__()
        self.weapon_type = weapon_type
        self.angle = angle
        
        if weapon_type == 'machine_gun':  # 机枪，双发子弹
            self.image = pygame.Surface((6, 12), pygame.SRCALPHA)
            # 子弹主体
            pygame.draw.rect(self.image, (255, 255, 0), [1, 0, 4, 10])
            # 发光效果
            pygame.draw.circle(self.image, (255, 255, 200), (3, 3), 2)
            self.speed_y = -8
            self.speed_x = math.sin(math.radians(angle)) * 2
            self.damage = 8
            
        elif weapon_type == 'laser':  # 激光，穿透性
            self.image = pygame.Surface((6, 25), pygame.SRCALPHA)
            # 激光主体
            pygame.draw.rect(self.image, (0, 255, 255), [1, 0, 4, 25])
            # 发光核心
            pygame.draw.rect(self.image, (200, 255, 255), [2, 5, 2, 15])
            self.speed_y = -15
            self.speed_x = 0
            self.damage = 15
            
        elif weapon_type == 'beam':  # 连续激光线
            self.image = pygame.Surface((4, 35), pygame.SRCALPHA)
            # 激光线主体
            pygame.draw.rect(self.image, (255, 0, 255), [0, 0, 4, 35])
            # 发光效果
            pygame.draw.rect(self.image, (255, 200, 255), [1, 5, 2, 25])
            self.speed_y = -25
            self.speed_x = math.sin(math.radians(angle)) * 1.5
            self.damage = 12
            
        elif weapon_type == 'cannon':  # 炮弹，大伤害
            self.image = pygame.Surface((14, 14), pygame.SRCALPHA)
            # 炮弹主体
            pygame.draw.circle(self.image, (255, 100, 0), (7, 7), 6)
            # 发光核心
            pygame.draw.circle(self.image, (255, 200, 100), (7, 7), 3)
            self.speed_y = -6
            self.speed_x = 0
            self.damage = 40
            
        elif weapon_type == 'shotgun':  # 散弹
            self.image = pygame.Surface((8, 20), pygame.SRCALPHA)
            # 散弹主体
            pygame.draw.polygon(self.image, (255, 50, 50), 
                              [(4, 0), (0, 20), (8, 20)])
            # 发光效果
            pygame.draw.polygon(self.image, (255, 200, 200),
                              [(4, 5), (2, 15), (6, 15)])
            self.speed_y = -7
            self.speed_x = math.sin(math.radians(angle)) * 3
            self.damage = 25
        
        else:  # missile，追踪导弹
            self.image = pygame.Surface((10, 25), pygame.SRCALPHA)
            # 导弹主体（更大）
            pygame.draw.polygon(self.image, (255, 0, 0), 
                              [(5, 0), (0, 25), (10, 25)])
            # 发光效果
            pygame.draw.polygon(self.image, (255, 150, 150),
                              [(5, 5), (3, 20), (7, 20)])
            # 尾焰效果
            pygame.draw.polygon(self.image, (255, 255, 0),
                              [(5, 20), (2, 25), (8, 25)])
            self.speed_y = -8
            self.speed_x = 0
            self.damage = 30
            self.target = None  # 追踪目标
            self.turn_speed = 0.15  # 转向速度
            self.max_speed = 12  # 最大速度
            self.acceleration = 0.3  # 加速度
            self.current_speed = 8  # 当前速度
            # 曲线飞行参数
            self.curve_factor = 0.8  # 曲线因子
            self.angle = 0  # 当前角度
            self.trail_positions = []  # 轨迹位置记录
            # 确保target属性存在
            if not hasattr(self, 'target'):
                self.target = None
            
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.radius = self.rect.width // 2
        self.x = float(x)
        self.y = float(y)
        
        # 添加拖尾粒子效果
        self.particles = pygame.sprite.Group()
        self.last_particle = pygame.time.get_ticks()
        self.particle_delay = 50  # 每50ms添加一个粒子

    def update(self):
        # 追踪导弹逻辑
        if self.weapon_type == 'missile' and hasattr(self, 'target'):
            # 如果目标不存在或已死亡，寻找新目标
            if self.target is None or not self.target.alive():
                if hasattr(self, 'enemies') and self.enemies:
                    # 寻找最近的敌人作为新目标
                    closest_enemy = None
                    closest_distance = float('inf')
                    for enemy in self.enemies:
                        if enemy.alive():
                            distance = math.sqrt((enemy.rect.centerx - self.rect.centerx)**2 + 
                                               (enemy.rect.centery - self.rect.centery)**2)
                            if distance < closest_distance:
                                closest_distance = distance
                                closest_enemy = enemy
                    self.target = closest_enemy
            
            # 如果有目标，曲线飞行追踪
            if self.target and self.target.alive():
                target_x = self.target.rect.centerx
                target_y = self.target.rect.centery
                
                # 计算到目标的方向
                dx = target_x - self.rect.centerx
                dy = target_y - self.rect.centery
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance > 0:
                    # 计算目标角度
                    target_angle = math.atan2(dy, dx)
                    
                    # 当前运动角度
                    current_angle = math.atan2(self.speed_y, self.speed_x)
                    
                    # 计算角度差
                    angle_diff = target_angle - current_angle
                    
                    # 处理角度差，确保选择最短路径
                    if angle_diff > math.pi:
                        angle_diff -= 2 * math.pi
                    elif angle_diff < -math.pi:
                        angle_diff += 2 * math.pi
                    
                    # 逐渐调整角度（曲线效果）
                    self.angle = current_angle + angle_diff * self.turn_speed * self.curve_factor
                    
                    # 根据距离调整速度
                    if distance < 100:  # 接近目标时加速
                        self.current_speed = min(self.current_speed + self.acceleration, self.max_speed)
                    
                    # 更新速度分量
                    self.speed_x = math.cos(self.angle) * self.current_speed
                    self.speed_y = math.sin(self.angle) * self.current_speed
                    
                    # 记录轨迹位置（用于绘制轨迹）
                    self.trail_positions.append((self.rect.centerx, self.rect.centery))
                    if len(self.trail_positions) > 8:  # 保留最近8个位置
                        self.trail_positions.pop(0)
        
        self.x += self.speed_x
        self.y += self.speed_y
        self.rect.x = self.x
        self.rect.y = self.y
        
        # 更新拖尾粒子
        now = pygame.time.get_ticks()
        if now - self.last_particle > self.particle_delay:
            if self.weapon_type == 'machine_gun':
                color = (255, 255, 100)
            elif self.weapon_type == 'laser':
                color = (100, 255, 255)
            elif self.weapon_type == 'cannon':
                color = (255, 150, 50)
            elif self.weapon_type == 'shotgun':
                color = (255, 100, 100)
            else:  # missile
                color = (255, 0, 0)
                
            particle = Particle(self.rect.centerx, self.rect.bottom,
                              color, random.uniform(-0.5, 0.5), 
                              random.uniform(0.5, 1.5), size=2)
            self.particles.add(particle)
            self.last_particle = now
        
        self.particles.update()
        # 移除消失的粒子
        for particle in self.particles.copy():
            if not particle.alive():
                particle.kill()
    
    def draw(self, screen):
        """绘制子弹和导弹轨迹"""
        # 绘制导弹轨迹
        if self.weapon_type == 'missile' and hasattr(self, 'trail_positions') and len(self.trail_positions) > 1:
            # 绘制轨迹线
            for i in range(1, len(self.trail_positions)):
                start_pos = self.trail_positions[i-1]
                end_pos = self.trail_positions[i]
                # 轨迹颜色渐变
                alpha = int(255 * (i / len(self.trail_positions)))
                color = (255, 100, 100)
                
                # 绘制轨迹线
                pygame.draw.line(screen, color, start_pos, end_pos, 2)
        
        # 绘制子弹本体
        screen.blit(self.image, self.rect)
        
        # 绘制粒子效果
        self.particles.draw(screen)

class Player(pygame.sprite.Sprite):
    SHIP_DESIGNS = {
        'interceptor': {
            'color': (30, 144, 255),  # 蓝色战机
            'wing_color': (135, 206, 250),
            'engine_color': (0, 191, 255),
            'core_color': (255, 255, 0),
            'cockpit_color': (173, 216, 230)
        },
        'striker': {
            'color': (50, 205, 50),    # 绿色突击舰
            'wing_color': (144, 238, 144),
            'engine_color': (0, 255, 127),
            'core_color': (255, 255, 0),
            'cockpit_color': (152, 251, 152)
        },
        'phantom': {
            'color': (147, 112, 219),  # 紫色幽灵舰
            'wing_color': (230, 230, 250),
            'engine_color': (186, 85, 211),
            'core_color': (255, 255, 0),
            'cockpit_color': (221, 160, 221)
        },
        'guardian': {
            'color': (255, 165, 0),    # 橙色守护者
            'wing_color': (255, 218, 185),
            'engine_color': (255, 140, 0),
            'core_color': (255, 255, 0),
            'cockpit_color': (255, 222, 173)
        },
        'avenger': {
            'color': (220, 20, 60),    # 红色复仇者
            'wing_color': (250, 128, 114),
            'engine_color': (255, 69, 0),
            'core_color': (255, 255, 0),
            'cockpit_color': (240, 128, 128)
        },
        'stealth': {
            'color': (75, 0, 130),     # 深紫色隐形舰
            'wing_color': (138, 43, 226),  # 蓝紫色
            'engine_color': (148, 0, 211),  # 暗紫色
            'core_color': (0, 255, 255),   # 青色能量
            'cockpit_color': (186, 85, 211) # 亮紫色
        }
    }
    
    def __init__(self, resource_loader, ship_type='interceptor'):
        super().__init__()
        self.ship_type = ship_type
        self.colors = self.SHIP_DESIGNS[ship_type]
        # Create player ship surface with higher resolution for pixel art
        self.original_image = pygame.Surface((64, 64), pygame.SRCALPHA)
        
        # 根据不同飞船类型绘制酷炫的飞船外形
        self.draw_cool_ship()
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.resource_loader = resource_loader
        self.radius = 20  # For circle collision detection
        
        # Position and movement
        self.rect.centerx = 1024 // 2  # Start at center of screen
        self.rect.bottom = 768 - 100   # Near bottom of screen
        self.speed_x = 8
        self.speed_y = 8
        
        # Health system
        self.max_health = 100
        self.health = self.max_health
        self.collision_damage = 20  # 玩家碰撞伤害
        self.shield = 0
        self.is_invulnerable = False
        self.invulnerable_timer = 0
        
        # Weapon system
        self.weapons = {
            'machine_gun': Weapon(8, -12, 150, 'machine_gun'),   # 机枪，快速连发
            'laser': Weapon(15, -20, 200, 'laser'),    # 激光，穿透
            'cannon': Weapon(40, -8, 500, 'cannon'),   # 炮弹，大伤害
            'beam': Weapon(12, -25, 50, 'beam'),  # 连续激光线，快速射击
            'shotgun': Weapon(25, -10, 400, 'shotgun'), # 散弹，分散
            'missile': Weapon(30, -15, 600, 'missile') # 导弹，追踪
        }
        self.current_weapon = 'machine_gun'
        self.last_shot = pygame.time.get_ticks()
        
        # Beam weapon specific attributes
        self.beam_active = False
        self.beam_start_time = 0
        self.beam_max_duration = 3000  # 3 seconds maximum
        
        # Bullets and particles
        self.bullets = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()
        
        # Shield effect
        self.shield_surface = pygame.Surface((70, 70), pygame.SRCALPHA)
        self.shield_radius = 32
        self.shield_color = (0, 255, 255)  # Cyan
        self.shield_alpha = 128
        self.shield_pulse = 0
        
        # Power-up effects
        self.speed_multiplier = 1.0
        self.damage_multiplier = 1.0
        self.power_up_timers = {
            'speed': 0,
            'weapon': 0
        }

    def update(self):
        # Get pressed keys
        keys = pygame.key.get_pressed()
        
        # Horizontal movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed_x
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed_x
            
        # Vertical movement
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed_y
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed_y
        
        # Keep player on screen with new window size
        if self.rect.right > 1024:
            self.rect.right = 1024
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > 768:
            self.rect.bottom = 768
            
        # Update bullets and particles
        self.bullets.update()
        self.particles.update()
        
        # Remove bullets that are off screen
        for bullet in self.bullets:
            if bullet.rect.bottom < 0:
                bullet.kill()
                
        # Check invulnerability
        if self.is_invulnerable:
            if pygame.time.get_ticks() - self.invulnerable_timer > 1000:
                self.is_invulnerable = False
            
        # Engine particles
        if random.random() < 0.3:
            speed_x = random.uniform(-1, 1)
            speed_y = random.uniform(1, 3)
            particle = Particle(self.rect.centerx, self.rect.bottom,
                              (100, 100, 255), speed_x, speed_y)
            self.particles.add(particle)
        
        # Update shield effect
        if self.shield > 0:
            self.shield_pulse = (self.shield_pulse + 2) % 360
            pulse_intensity = abs(math.sin(math.radians(self.shield_pulse)))
            current_radius = self.shield_radius + (pulse_intensity * 3)
            
            # Clear shield surface
            self.shield_surface.fill((0, 0, 0, 0))
            
            # Draw pulsing shield
            pygame.draw.circle(self.shield_surface, 
                             (*self.shield_color, int(self.shield_alpha * pulse_intensity)),
                             (35, 35), current_radius, 2)
        
        # Update power-up timers
        current_time = pygame.time.get_ticks()
        for effect, timer in self.power_up_timers.items():
            if timer > 0 and current_time > timer:
                self.reset_power_up(effect)

    def draw(self, surface):
        # Draw the ship
        surface.blit(self.image, self.rect)
        # Draw shield if active
        if self.shield > 0:
            surface.blit(self.shield_surface, 
                        (self.rect.centerx - 35, self.rect.centery - 35))
                
    def reset_power_up(self, effect):
        """Reset power-up effects when they expire"""
        if effect == 'speed':
            self.speed_x /= 1.5
            self.speed_y /= 1.5
            self.power_up_timers['speed'] = 0
            cprint("Speed boost expired!", "yellow")
        elif effect == 'weapon':
            if self.current_weapon == 'machine_gun':
                self.weapons['machine_gun'].damage /= 2
                self.weapons['machine_gun'].shoot_delay *= 2
            else:
                self.weapons[self.current_weapon].damage /= 1.5
            self.power_up_timers['weapon'] = 0
            cprint("Weapon power-up expired!", "magenta")
            
    def shoot(self):
        now = pygame.time.get_ticks()
        weapon = self.weapons[self.current_weapon]
        if now - self.last_shot > weapon.shoot_delay:
            self.last_shot = now
            
            # 播放武器音效
            self.resource_loader.play_weapon_sound(self.current_weapon)
            
            if self.current_weapon == 'machine_gun':  # 双发子弹
                bullet1 = Bullet(self.rect.centerx - 10, self.rect.top, self.current_weapon, -5)
                bullet2 = Bullet(self.rect.centerx + 10, self.rect.top, self.current_weapon, 5)
                self.bullets.add(bullet1, bullet2)
                
            elif self.current_weapon == 'shotgun':  # 散弹
                angles = [-30, -15, 0, 15, 30]
                for angle in angles:
                    bullet = Bullet(self.rect.centerx, self.rect.top, self.current_weapon, angle)
                    self.bullets.add(bullet)
            
            elif self.current_weapon == 'missile':  # 追踪导弹
                # 获取最多6个不同的敌人作为目标
                targets = []
                if hasattr(self, 'enemies') and self.enemies:
                    enemies_list = list(self.enemies)
                    # 按距离排序，优先攻击近距离敌人
                    enemies_list.sort(key=lambda e: math.sqrt((e.rect.centerx - self.rect.centerx)**2 + 
                                                            (e.rect.centery - self.rect.centery)**2))
                    targets = enemies_list[:6]  # 取前6个敌人
                
                for i in range(6):  # 发出6个导弹
                    bullet = Bullet(self.rect.centerx + (i-2.5)*8, self.rect.top, self.current_weapon, 0)
                    # 为每个导弹分配不同的目标
                    if i < len(targets):
                        bullet.target = targets[i]
                    else:
                        bullet.target = None
                    # 设置敌人列表用于重新寻找目标
                    if hasattr(self, 'enemies'):
                        bullet.enemies = self.enemies
                    self.bullets.add(bullet)
            
            elif self.current_weapon == 'beam':  # 连续激光线
                # Check if beam has been active for too long
                if self.beam_active and (now - self.beam_start_time) >= self.beam_max_duration:
                    self.beam_active = False
                    return  # Stop firing beam
                
                # If this is the start of beam firing
                if not self.beam_active:
                    self.beam_active = True
                    self.beam_start_time = now
                
                angles = [-5, 0, 5]
                for angle in angles:
                    bullet = Bullet(self.rect.centerx, self.rect.top, self.current_weapon, angle)
                    self.bullets.add(bullet)
                    
            else:  # 激光和炮弹
                bullet = Bullet(self.rect.centerx, self.rect.top, self.current_weapon)
                self.bullets.add(bullet)
            
            # 武器音效已由resource_loader处理
            
            # Add muzzle flash particles
            for _ in range(5):
                speed_x = random.uniform(-2, 2)
                speed_y = random.uniform(-2, 0)
                color = (255, 255, 0) if self.current_weapon == 'machine_gun' else \
                        (0, 255, 255) if self.current_weapon == 'laser' else \
                        (255, 100, 0) if self.current_weapon == 'cannon' else \
                        (255, 50, 50) if self.current_weapon == 'shotgun' else \
                        (255, 0, 0) if self.current_weapon == 'missile' else \
                        (255, 0, 255)  # beam
                particle = Particle(self.rect.centerx, self.rect.top, color, speed_x, speed_y)
                self.particles.add(particle)
            
            debug_print(f"Player fired a {self.current_weapon}!", "yellow")
    
    def draw_cool_ship(self):
        """绘制现代风格的飞船外形"""
        colors = self.colors
        
        if self.ship_type == 'interceptor':
            # 拦截机 - 现代流线型设计
            # 主体 - 椭圆形机身
            pygame.draw.ellipse(self.original_image, colors['color'], [20, 15, 24, 35])
            
            # 机身高光
            pygame.draw.ellipse(self.original_image, colors['wing_color'], [22, 17, 20, 31])
            
            # 驾驶舱窗口
            pygame.draw.ellipse(self.original_image, (20, 20, 40), [28, 22, 8, 12])
            pygame.draw.ellipse(self.original_image, colors['cockpit_color'], [29, 23, 6, 10])
            
            # 侧翼
            pygame.draw.ellipse(self.original_image, colors['wing_color'], [12, 28, 16, 8])
            pygame.draw.ellipse(self.original_image, colors['wing_color'], [36, 28, 16, 8])
            
            # 推进器
            pygame.draw.ellipse(self.original_image, colors['engine_color'], [28, 45, 8, 12])
            pygame.draw.ellipse(self.original_image, colors['core_color'], [30, 47, 4, 8])
            
            # 机头
            pygame.draw.ellipse(self.original_image, colors['core_color'], [30, 12, 4, 8])
            
        elif self.ship_type == 'striker':
            # 突击者 - 重型火箭式设计
            # 主体 - 圆柱形机身
            pygame.draw.ellipse(self.original_image, colors['color'], [24, 12, 16, 40])
            
            # 机身高光
            pygame.draw.ellipse(self.original_image, colors['wing_color'], [26, 14, 12, 36])
            
            # 机头锥形
            pygame.draw.ellipse(self.original_image, colors['core_color'], [28, 8, 8, 12])
            
            # 驾驶舱窗口
            pygame.draw.ellipse(self.original_image, (20, 20, 40), [28, 20, 8, 8])
            pygame.draw.ellipse(self.original_image, colors['cockpit_color'], [29, 21, 6, 6])
            
            # 侧翼推进器
            pygame.draw.ellipse(self.original_image, colors['wing_color'], [16, 35, 12, 6])
            pygame.draw.ellipse(self.original_image, colors['wing_color'], [36, 35, 12, 6])
            
            # 主推进器
            pygame.draw.ellipse(self.original_image, colors['engine_color'], [26, 48, 12, 10])
            pygame.draw.ellipse(self.original_image, colors['core_color'], [28, 50, 8, 6])
            
        elif self.ship_type == 'phantom':
            # 幻影 - 神秘圆盘型设计
            # 主体 - 圆形机身
            pygame.draw.ellipse(self.original_image, colors['color'], [18, 18, 28, 28])
            
            # 内层环
            pygame.draw.ellipse(self.original_image, colors['wing_color'], [22, 22, 20, 20])
            
            # 中央核心
            pygame.draw.ellipse(self.original_image, (20, 20, 40), [28, 28, 8, 8])
            pygame.draw.ellipse(self.original_image, colors['core_color'], [29, 29, 6, 6])
            
            # 方向指示器
            pygame.draw.ellipse(self.original_image, colors['cockpit_color'], [30, 15, 4, 8])
            
            # 推进环
            pygame.draw.ellipse(self.original_image, colors['engine_color'], [24, 46, 16, 8])
            pygame.draw.ellipse(self.original_image, colors['core_color'], [28, 48, 8, 4])
            
        elif self.ship_type == 'guardian':
            # 守护者 - 厚重装甲型设计
            # 主体 - 宽椭圆形
            pygame.draw.ellipse(self.original_image, colors['color'], [16, 16, 32, 32])
            
            # 装甲层
            pygame.draw.ellipse(self.original_image, colors['wing_color'], [18, 18, 28, 28])
            
            # 中央装甲块
            pygame.draw.ellipse(self.original_image, colors['color'], [24, 24, 16, 16])
            
            # 驾驶舱
            pygame.draw.ellipse(self.original_image, (20, 20, 40), [28, 26, 8, 8])
            pygame.draw.ellipse(self.original_image, colors['cockpit_color'], [29, 27, 6, 6])
            
            # 前端武器
            pygame.draw.ellipse(self.original_image, colors['core_color'], [30, 12, 4, 8])
            
            # 多推进器设计
            pygame.draw.ellipse(self.original_image, colors['engine_color'], [20, 44, 8, 6])
            pygame.draw.ellipse(self.original_image, colors['engine_color'], [28, 46, 8, 8])
            pygame.draw.ellipse(self.original_image, colors['engine_color'], [36, 44, 8, 6])
            
        elif self.ship_type == 'avenger':
            # 复仇者 - 双引擎战斗机
            # 主体机身
            pygame.draw.ellipse(self.original_image, colors['color'], [26, 12, 12, 40])
            
            # 机身高光
            pygame.draw.ellipse(self.original_image, colors['wing_color'], [28, 14, 8, 36])
            
            # 侧面引擎舱
            pygame.draw.ellipse(self.original_image, colors['wing_color'], [14, 20, 10, 24])
            pygame.draw.ellipse(self.original_image, colors['wing_color'], [40, 20, 10, 24])
            
            # 引擎舱高光
            pygame.draw.ellipse(self.original_image, colors['color'], [16, 22, 6, 20])
            pygame.draw.ellipse(self.original_image, colors['color'], [42, 22, 6, 20])
            
            # 驾驶舱窗口
            pygame.draw.ellipse(self.original_image, (20, 20, 40), [28, 18, 8, 10])
            pygame.draw.ellipse(self.original_image, colors['cockpit_color'], [29, 19, 6, 8])
            
            # 机头
            pygame.draw.ellipse(self.original_image, colors['core_color'], [30, 8, 4, 8])
            
            # 双引擎推进器
            pygame.draw.ellipse(self.original_image, colors['engine_color'], [16, 44, 6, 8])
            pygame.draw.ellipse(self.original_image, colors['engine_color'], [42, 44, 6, 8])
            pygame.draw.ellipse(self.original_image, colors['core_color'], [18, 46, 2, 4])
            pygame.draw.ellipse(self.original_image, colors['core_color'], [44, 46, 2, 4])
            
        elif self.ship_type == 'stealth':
            # 隐形舰 - 未来科技隐形设计
            # 主体 - 钻石形状
            pygame.draw.ellipse(self.original_image, colors['color'], [20, 8, 24, 48])
            
            # 能量护盾层
            pygame.draw.ellipse(self.original_image, colors['wing_color'], [22, 10, 20, 44])
            
            # 中央能量核心
            pygame.draw.ellipse(self.original_image, colors['color'], [28, 16, 8, 32])
            
            # 量子传感器阵列
            pygame.draw.ellipse(self.original_image, (10, 10, 50), [26, 18, 12, 8])
            pygame.draw.ellipse(self.original_image, colors['cockpit_color'], [27, 19, 10, 6])
            
            # 能量脉冲器
            pygame.draw.ellipse(self.original_image, colors['core_color'], [30, 12, 4, 4])
            pygame.draw.ellipse(self.original_image, colors['core_color'], [30, 30, 4, 4])
            pygame.draw.ellipse(self.original_image, colors['core_color'], [30, 40, 4, 4])
            
            # 量子推进器
            pygame.draw.ellipse(self.original_image, colors['engine_color'], [26, 48, 12, 8])
            pygame.draw.ellipse(self.original_image, colors['core_color'], [28, 50, 8, 4])
            
            # 侧翼能量发射器
            pygame.draw.ellipse(self.original_image, colors['wing_color'], [16, 26, 8, 6])
            pygame.draw.ellipse(self.original_image, colors['wing_color'], [40, 26, 8, 6])
            pygame.draw.ellipse(self.original_image, colors['core_color'], [18, 28, 4, 2])
            pygame.draw.ellipse(self.original_image, colors['core_color'], [42, 28, 4, 2])
            
    def switch_weapon(self):
        # Reset beam state when switching weapons
        self.beam_active = False
        self.beam_start_time = 0
        
        weapons = list(self.weapons.keys())
        current_index = weapons.index(self.current_weapon)
        self.current_weapon = weapons[(current_index + 1) % len(weapons)]
        cprint(f"Switched to {self.current_weapon}", "cyan")
    
    def stop_beam(self):
        """Stop beam firing"""
        self.beam_active = False
        self.beam_start_time = 0
        
    def take_damage(self, amount):
        """Enhanced damage handling with shield effects"""
        if not self.is_invulnerable:
            if self.shield > 0:
                # Shield absorbs 75% of damage
                absorbed = amount * 0.75
                self.shield -= absorbed
                amount -= absorbed
                
                # Shield break effect
                if self.shield <= 0:
                    for _ in range(20):
                        angle = random.uniform(0, math.pi * 2)
                        speed = random.uniform(3, 7)
                        speed_x = math.cos(angle) * speed
                        speed_y = math.sin(angle) * speed
                        particle = Particle(self.rect.centerx, self.rect.centery,
                                         self.shield_color, speed_x, speed_y, size=3)
                        self.particles.add(particle)
                    self.shield = 0
                
            self.health -= amount
            self.is_invulnerable = True
            self.invulnerable_timer = pygame.time.get_ticks()
            
            # 受伤特效 - 红色碎片
            for _ in range(15):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(4, 8)
                speed_x = math.cos(angle) * speed
                speed_y = math.sin(angle) * speed
                color = random.choice([
                    (255, 0, 0),    # 纯红
                    (255, 100, 0),  # 橙红
                    (255, 50, 50)   # 亮红
                ])
                particle = Particle(self.rect.centerx, self.rect.centery,
                                 color, speed_x, speed_y, size=random.randint(2, 4))
                self.particles.add(particle)
            
            # 受伤特效 - 火花
            for _ in range(8):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(2, 5)
                speed_x = math.cos(angle) * speed
                speed_y = math.sin(angle) * speed
                particle = Particle(self.rect.centerx, self.rect.centery,
                                 (255, 255, 0), speed_x, speed_y, 
                                 size=2, gravity=0.2)
                self.particles.add(particle)
                
            # 受伤特效 - 烟雾
            for _ in range(5):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(1, 3)
                speed_x = math.cos(angle) * speed
                speed_y = math.sin(angle) * speed
                particle = Particle(self.rect.centerx, self.rect.centery,
                                 (100, 100, 100), speed_x, speed_y, 
                                 size=5, gravity=-0.1)
                self.particles.add(particle)

class Enemy(pygame.sprite.Sprite):
    ENEMY_DESIGNS = {
        'scout': {
            'color': (255, 0, 0),  # Red base
            'wing_color': (255, 165, 0),  # Orange wings
            'engine_color': (255, 69, 0),  # Red-orange engine
            'core_color': (255, 255, 0),  # Yellow core
            'cockpit_color': (255, 200, 200),  # Light red cockpit
            'size': (40, 40),
            'health': 30,
            'speed': 3,
            'points': 100,
            'shoot_delay': 4000,  # Fast but weak ship, shoots every 4 seconds
            'bullet_type': 'small_laser',  # Fast, low damage
            'bullet_damage': 5,
            'collision_damage': 10
        },
        'striker': {
            'color': (50, 205, 50),  # Green base
            'wing_color': (144, 238, 144),  # Light green wings
            'engine_color': (0, 255, 127),  # Spring green engine
            'core_color': (255, 255, 0),  # Yellow core
            'cockpit_color': (152, 251, 152),  # Light green cockpit
            'size': (45, 45),
            'health': 45,
            'speed': 2.5,
            'points': 150,
            'shoot_delay': 3000,  # Balanced attack speed
            'bullet_type': 'plasma',  # Medium damage plasma shots
            'bullet_damage': 10,
            'collision_damage': 15
        },
        'redcross': {  # New healing ship type
            'color': (255, 255, 255),  # White base
            'wing_color': (255, 0, 0),  # Red wings/cross
            'engine_color': (255, 100, 100),  # Light red engine
            'core_color': (255, 255, 0),  # Yellow core
            'cockpit_color': (200, 200, 255),  # Light blue cockpit
            'size': (45, 45),
            'health': 40,
            'speed': 2,
            'points': 0,  # No points for destroying healing ships
            'shoot_delay': None,  # Healing ships don't shoot
            'bullet_type': None,  # Healing ships don't shoot
            'heal_amount': 25,  # Amount of health restored
            'collision_damage': 5
        },
        'fighter': {
            'color': (148, 0, 211),  # Purple base
            'wing_color': (138, 43, 226),  # Blue-violet wings
            'engine_color': (186, 85, 211),  # Medium purple engine
            'core_color': (255, 255, 0),  # Yellow core
            'cockpit_color': (230, 230, 250),  # Lavender cockpit
            'size': (50, 50),
            'health': 50,
            'speed': 2,
            'points': 150,
            'shoot_delay': 3500,  # Aggressive ship, shoots every 3.5 seconds
            'bullet_type': 'dual_shot',  # Two bullets at once
            'bullet_damage': 8,
            'collision_damage': 20
        },
        'bomber': {
            'color': (0, 100, 0),  # Dark green base
            'wing_color': (34, 139, 34),  # Forest green wings
            'engine_color': (0, 255, 127),  # Spring green engine
            'core_color': (255, 255, 0),  # Yellow core
            'cockpit_color': (144, 238, 144),  # Light green cockpit
            'size': (60, 60),
            'health': 80,
            'speed': 1,
            'points': 200,
            'shoot_delay': 5000,  # Slow but powerful ship, shoots every 5 seconds
            'bullet_type': 'plasma',  # Large, slow, high damage
            'bullet_damage': 15,
            'collision_damage': 30
        },
        'elite': {
            'color': (25, 25, 112),  # Midnight blue base
            'wing_color': (0, 0, 139),  # Dark blue wings
            'engine_color': (65, 105, 225),  # Royal blue engine
            'core_color': (255, 255, 0),  # Yellow core
            'cockpit_color': (135, 206, 250),  # Light blue cockpit
            'size': (55, 55),
            'health': 100,
            'speed': 2.5,
            'points': 300,
            'shoot_delay': 3000,  # Elite ship, shoots every 3 seconds
            'bullet_type': 'spread',  # Three bullets in a spread
            'bullet_damage': 10,
            'collision_damage': 25
        },
        'boss': {
            'color': (128, 0, 0),  # Dark red base
            'wing_color': (255, 69, 0),  # Red-orange wings
            'engine_color': (255, 140, 0),  # Dark orange engine
            'core_color': (255, 215, 0),  # Golden core
            'cockpit_color': (255, 165, 0),  # Orange cockpit
            'size': (150, 120),  # Larger boss size
            'health': 2000,  # Base health
            'speed': 1,
            'points': 1000,
            'shoot_delay': 3000,  # Base shoot delay
            'bullet_damage': 35,  # More powerful bullets
            'collision_damage': 80,  # Higher collision damage
            'phases': [
                {
                    'name': '第一阶段: 火力压制',
                    'health_threshold': 0.8,  # 80% health
                    'color': (255, 50, 50),    # 红色
                    'attack_patterns': ['umbrella', 'spread'],
                    'shoot_delay': 2500,  # Faster shooting
                    'speed_multiplier': 1.0
                },
                {
                    'name': '第二阶段: 狂暴模式',
                    'health_threshold': 0.6,  # 60% health
                    'color': (0, 255, 255),    # 青色
                    'attack_patterns': ['laser_barrage', 'cross_fire'],
                    'shoot_delay': 2000,  # Faster shooting
                    'speed_multiplier': 1.2
                },
                {
                    'name': '第三阶段: 温度过载',
                    'health_threshold': 0.4,  # 40% health
                    'color': (255, 165, 0),    # 橙色
                    'attack_patterns': ['spiral', 'spread'],
                    'shoot_delay': 1600,  # Faster shooting
                    'speed_multiplier': 1.4
                },
                {
                    'name': '第四阶段: 能量爆发',
                    'health_threshold': 0.2,  # 20% health
                    'color': (255, 0, 255),    # 紫色
                    'attack_patterns': ['death_spiral', 'cross_fire'],
                    'shoot_delay': 1200,  # Faster shooting
                    'speed_multiplier': 1.6
                },
                {
                    'name': '最终阶段: 毁灭之力',
                    'health_threshold': 0.0,  # 0% health
                    'color': (255, 255, 255),   # 白色
                    'attack_patterns': ['bullet_hell', 'umbrella'],
                    'shoot_delay': 800,  # Much faster shooting
                    'speed_multiplier': 2.0
                }
            ]
        }
    }

    def __init__(self, enemy_type='scout', round_number=1):
        super().__init__()
        self.enemy_type = enemy_type
        self.round_number = round_number
        self.design = self.ENEMY_DESIGNS[enemy_type].copy()
        
        # Initialize core attributes first
        self.health = self.design['health']
        self.max_health = self.health
        self.points = self.design['points']
        self.collision_damage = self.design.get("collision_damage", 10)  # 默认碰撞伤害为10
        self.shoot_delay = self.design['shoot_delay'] if 'shoot_delay' in self.design else None
        
        # Initialize boss phase system if this is a boss
        if enemy_type == 'boss':
            # 初始化Boss相位系统
            self.phases = self.design['phases']
            self.current_phase = None
            
            # 初始化相位颜色
            self.phase_colors = [phase['color'] for phase in self.phases]
            
            # 初始化每个相位的攻击模式
            for phase in self.phases:
                if 'attack_patterns' not in phase:
                    phase['attack_patterns'] = [
                        'umbrella',      # 伞形弹幕
                        'spread',        # 散射弹幕
                        'laser_barrage', # 激光弹幕
                        'cross_fire',    # 十字弹幕
                        'spiral',        # 螺旋弹幕
                        'death_spiral',  # 死亡螺旋
                        'bullet_hell'    # 地狱弹幕
                    ]
            
            # 根据初始血量设置初始相位
            health_percentage = self.health / self.max_health
            # 从高血量阈值到低血量阈值排序
            sorted_phases = sorted(self.phases, key=lambda x: x['health_threshold'], reverse=True)
            
            # 找到第一个血量阈值低于当前血量的相位
            for phase in sorted_phases:
                if health_percentage >= phase['health_threshold']:
                    self.current_phase = phase
                    break
            
            # 如果没有找到合适的相位，使用最后一个相位
            if self.current_phase is None:
                self.current_phase = sorted_phases[-1]
            
            # 设置初始属性
            self.shoot_delay = self.current_phase['shoot_delay']
            self.speed_x = self.design['speed'] * self.current_phase['speed_multiplier']
            self.speed_y = self.design['speed'] * self.current_phase['speed_multiplier']
            
            # 打印Boss初始化信息
            cprint(f"Boss出现了！进入{self.current_phase['name']}", "yellow")
        
        # Scale enemy attributes based on round number
        if round_number > 1 and enemy_type != 'redcross':  # Don't scale healing ships
            scale = 1 + (round_number - 1) * 0.2  # 20% increase per round
            self.health = int(self.health * scale)
            self.max_health = self.health
            self.design['speed'] = self.design['speed'] * (1 + (round_number - 1) * 0.1)  # 10% speed increase
            self.points = int(self.points * scale)
            
            # Scale boss more aggressively
            if enemy_type == 'boss':
                self.health = int(self.health * (1 + (round_number - 1) * 0.5))  # 50% more health per round
                self.max_health = self.health
                if self.shoot_delay:
                    self.shoot_delay = max(1000, 3000 - (round_number - 1) * 200)  # Shoot faster each round, min 1 second
        
        # Create the enemy ship surface
        self.original_image = pygame.Surface(self.design['size'], pygame.SRCALPHA)
        self.image = self.original_image
        self.rect = self.image.get_rect()
        
        # Draw enemy ship based on type
        if enemy_type == 'boss':
            # 重绘Boss精灵
            self.redraw_boss()
        else:
            # Common measurements
            width, height = self.design['size']
            center_x = width // 2
            center_y = height // 2
            
            # Lower wing structures
            pygame.draw.polygon(self.original_image, self.design['wing_color'], [
                (center_x - 30, height - 20), # Right base
                (center_x - 50, height - 15), # Right tip
                (center_x - 25, height - 30)  # Right top
            ])
            pygame.draw.polygon(self.original_image, self.design['wing_color'], [
                (center_x + 30, height - 20), # Left base
                (center_x + 50, height - 15), # Left tip
                (center_x + 25, height - 30)  # Left top
            ])
            
            # Advanced weapon systems (visible cannons)
            pygame.draw.rect(self.original_image, self.design['engine_color'],
                           [center_x - 25, height - 35, 10, 20])  # Left cannon
            pygame.draw.rect(self.original_image, self.design['engine_color'],
                           [center_x + 15, height - 35, 10, 20])  # Right cannon
            
            # Central cannon
            pygame.draw.polygon(self.original_image, self.design['engine_color'], [
                (center_x - 8, height - 15),
                (center_x + 8, height - 15),
                (center_x + 5, height - 5),
                (center_x - 5, height - 5)
            ])
            
            # Energy core
            pygame.draw.circle(self.original_image, self.design['core_color'],
                             (center_x, center_y), 15)
            pygame.draw.circle(self.original_image, self.design['engine_color'],
                             (center_x, center_y), 10)
            
            # Command bridge
            pygame.draw.polygon(self.original_image, self.design['cockpit_color'], [
                (center_x - 15, center_y + 15),
                (center_x + 15, center_y + 15),
                (center_x + 10, center_y - 5),
                (center_x - 10, center_y - 5)
            ])
            
        # Initialize boss battle variables
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = self.design['shoot_delay'] if 'shoot_delay' in self.design else 3000
        self.bullets = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()
        
        # Health bar properties for boss
        if enemy_type == 'boss':
            self.health_bar_height = 10
            self.health_bar_width = 200
            self.health_bar_surface = pygame.Surface((self.health_bar_width + 4, self.health_bar_height + 4))
            self.phase_text_surface = pygame.Surface((300, 30), pygame.SRCALPHA)
            self.phase_text_color = (255, 255, 255)
        
        if enemy_type == 'scout':
            # Fast, arrow-like ship with swept-back wings
            # Main body (pointed downward)
            pygame.draw.polygon(self.original_image, self.design['color'], [
                (center_x, height - 5),        # Nose (bottom)
                (center_x + 8, 15),            # Right mid
                (center_x, 10),                # Top
                (center_x - 8, 15)             # Left mid
            ])
            
            # Wings (swept forward)
            pygame.draw.polygon(self.original_image, self.design['wing_color'], [
                (center_x - 8, 15),            # Wing root left
                (5, 5),                        # Wing tip left
                (center_x - 5, 18)             # Wing back left
            ])
            pygame.draw.polygon(self.original_image, self.design['wing_color'], [
                (center_x + 8, 15),            # Wing root right
                (width - 5, 5),                # Wing tip right
                (center_x + 5, 18)             # Wing back right
            ])
            
            # Cockpit
            pygame.draw.ellipse(self.original_image, self.design['cockpit_color'],
                              [center_x - 3, height - 18, 6, 8])
            
        elif enemy_type == 'fighter':
            # X-wing style fighter with distinct wings and body
            # Main body (sleek and pointed)
            pygame.draw.polygon(self.original_image, self.design['color'], [
                (center_x, 10),                # Nose
                (center_x + 10, height - 15),  # Right bottom
                (center_x + 8, 15),            # Right top
                (center_x, 10),                # Top
                (center_x - 8, 15),            # Left top
                (center_x - 10, height - 15)   # Left bottom
            ])
            
            # Wings (more defined X-wing style)
            # Left wing
            pygame.draw.polygon(self.original_image, self.design['wing_color'], [
                (center_x - 8, height - 20),   # Wing base
                (5, height - 25),              # Wing tip
                (8, height - 15),              # Wing back
                (center_x - 6, height - 15)    # Wing join
            ])
            # Right wing
            pygame.draw.polygon(self.original_image, self.design['wing_color'], [
                (center_x + 8, height - 20),   # Wing base
                (width - 5, height - 25),      # Wing tip
                (width - 8, height - 15),      # Wing back
                (center_x + 6, height - 15)    # Wing join
            ])
            # Upper wings
            pygame.draw.polygon(self.original_image, self.design['wing_color'], [
                (center_x - 6, 20),            # Left wing
                (10, 5),                       # Left tip
                (center_x - 4, 15)             # Left base
            ])
            pygame.draw.polygon(self.original_image, self.design['wing_color'], [
                (center_x + 6, 20),            # Right wing
                (width - 10, 5),               # Right tip
                (center_x + 4, 15)             # Right base
            ])
            
            # Cockpit (more detailed)
            pygame.draw.ellipse(self.original_image, self.design['cockpit_color'],
                              [center_x - 5, height - 25, 10, 12])
            # Cockpit detail
            pygame.draw.ellipse(self.original_image, self.design['engine_color'],
                              [center_x - 3, height - 23, 6, 8])
            
        elif enemy_type == 'bomber':
            # Heavy bomber with distinct sections and heavy armor
            # Main body (armored and wide)
            pygame.draw.polygon(self.original_image, self.design['color'], [
                (center_x, height - 5),        # Nose (bottom)
                (center_x + 20, height - 15),  # Right bottom
                (center_x + 15, 10),           # Right top
                (center_x, 5),                 # Top
                (center_x - 15, 10),           # Left top
                (center_x - 20, height - 15)   # Left bottom
            ])
            
            # Side armor plates
            pygame.draw.polygon(self.original_image, self.design['wing_color'], [
                (center_x - 20, height - 15),  # Bottom left
                (center_x - 15, height - 25),  # Mid left
                (center_x - 12, 15),           # Top left
                (center_x - 8, 12),            # Inner top left
                (center_x - 10, height - 15)   # Inner bottom left
            ])
            pygame.draw.polygon(self.original_image, self.design['wing_color'], [
                (center_x + 20, height - 15),  # Bottom right
                (center_x + 15, height - 25),  # Mid right
                (center_x + 12, 15),           # Top right
                (center_x + 8, 12),            # Inner top right
                (center_x + 10, height - 15)   # Inner bottom right
            ])
            
            # Top armor section
            pygame.draw.polygon(self.original_image, self.design['wing_color'], [
                (center_x - 8, 15),            # Left
                (center_x, 8),                 # Top
                (center_x + 8, 15),            # Right
                (center_x, 20)                 # Bottom
            ])
            
            # Multiple engine effects (three thrusters)
            for x, size in [(center_x - 12, 4), (center_x, 5), (center_x + 12, 4)]:
                pygame.draw.polygon(self.original_image, self.design['engine_color'], [
                    (x - size, 12),
                    (x, 7),
                    (x + size, 12)
                ])
                # Engine glow
                pygame.draw.circle(self.original_image, self.design['core_color'],
                                 (x, 10), size - 2)
            
            # Cockpit (armored)
            pygame.draw.polygon(self.original_image, self.design['cockpit_color'], [
                (center_x - 6, height - 25),   # Left
                (center_x, height - 30),       # Top
                (center_x + 6, height - 25),   # Right
                (center_x, height - 20)        # Bottom
            ])
            
        elif enemy_type == 'elite':
            # Advanced ship with energy shield and high-tech design
            # Main body (sleek and angular)
            pygame.draw.polygon(self.original_image, self.design['color'], [
                (center_x, height - 5),        # Nose (bottom)
                (center_x + 15, height - 20),  # Right bottom
                (center_x + 12, center_y),     # Right middle
                (center_x + 8, 10),            # Right top
                (center_x, 5),                 # Top
                (center_x - 8, 10),            # Left top
                (center_x - 12, center_y),     # Left middle
                (center_x - 15, height - 20)   # Left bottom
            ])
            
            # Energy shield effect (outer)
            points = [
                (center_x, height - 8),        # Bottom
                (center_x + 18, height - 22),  # Right bottom
                (center_x + 15, center_y),     # Right middle
                (center_x + 10, 8),            # Right top
                (center_x, 3),                 # Top
                (center_x - 10, 8),            # Left top
                (center_x - 15, center_y),     # Left middle
                (center_x - 18, height - 22)   # Left bottom
            ]
            pygame.draw.lines(self.original_image, self.design['wing_color'], True, points, 2)
            
            # Energy field patterns
            for y in range(20, height - 20, 10):
                pygame.draw.line(self.original_image, self.design['engine_color'],
                               (center_x - 10, y), (center_x + 10, y), 1)
            
            # Advanced cockpit with energy glow
            pygame.draw.polygon(self.original_image, self.design['cockpit_color'], [
                (center_x - 5, height - 25),   # Left
                (center_x, height - 30),       # Top
                (center_x + 5, height - 25),   # Right
                (center_x, height - 20)        # Bottom
            ])
            # Cockpit glow
            pygame.draw.polygon(self.original_image, self.design['core_color'], [
                (center_x - 3, height - 24),
                (center_x, height - 28),
                (center_x + 3, height - 24),
                (center_x, height - 22)
            ])
            
            # Side energy emitters
            for x in [center_x - 12, center_x + 12]:
                pygame.draw.circle(self.original_image, self.design['engine_color'],
                                 (x, center_y), 3)
                pygame.draw.circle(self.original_image, self.design['core_color'],
                                 (x, center_y), 1)
        elif enemy_type == 'redcross':
            # Medical ship with cross symbol
            width, height = self.design['size']
            center_x = width // 2
            center_y = height // 2
            
            # Main body (circular white ship)
            pygame.draw.circle(self.original_image, self.design['color'],
                             (center_x, center_y), 20)
            
            # Red cross symbol
            # Vertical bar
            pygame.draw.rect(self.original_image, self.design['wing_color'],
                           [center_x - 4, center_y - 15, 8, 30])
            # Horizontal bar
            pygame.draw.rect(self.original_image, self.design['wing_color'],
                           [center_x - 15, center_y - 4, 30, 8])
            
            # Healing aura effect (concentric circles)
            pygame.draw.circle(self.original_image, self.design['engine_color'],
                             (center_x, center_y), 22, 1)
            pygame.draw.circle(self.original_image, self.design['engine_color'],
                             (center_x, center_y), 24, 1)
            
            # Cockpit
            pygame.draw.circle(self.original_image, self.design['cockpit_color'],
                             (center_x, center_y - 8), 5)
        
        elif enemy_type == 'striker':
            # Striker design - sleek and aggressive green ship
            # Main body (arrow-shaped)
            pygame.draw.polygon(self.original_image, self.design['color'], [
                (center_x, 10),                # Nose
                (center_x + 15, height - 15),  # Right bottom
                (center_x, height - 10),       # Bottom point
                (center_x - 15, height - 15)   # Left bottom
            ])
            
            # Side wings (swept forward)
            pygame.draw.polygon(self.original_image, self.design['wing_color'], [
                (center_x - 15, height - 15),  # Wing base left
                (center_x - 25, height - 25),  # Wing tip left
                (center_x - 10, height - 30)   # Wing top left
            ])
            pygame.draw.polygon(self.original_image, self.design['wing_color'], [
                (center_x + 15, height - 15),  # Wing base right
                (center_x + 25, height - 25),  # Wing tip right
                (center_x + 10, height - 30)   # Wing top right
            ])
            
            # Engine exhausts (three thrusters)
            pygame.draw.polygon(self.original_image, self.design['engine_color'], [
                (center_x - 10, height - 12),
                (center_x - 8, height - 5),
                (center_x - 6, height - 12)
            ])
            pygame.draw.polygon(self.original_image, self.design['engine_color'], [
                (center_x - 2, height - 12),
                (center_x, height - 5),
                (center_x + 2, height - 12)
            ])
            pygame.draw.polygon(self.original_image, self.design['engine_color'], [
                (center_x + 6, height - 12),
                (center_x + 8, height - 5),
                (center_x + 10, height - 12)
            ])
            
            # Cockpit (streamlined)
            pygame.draw.polygon(self.original_image, self.design['cockpit_color'], [
                (center_x - 4, height - 25),
                (center_x, height - 30),
                (center_x + 4, height - 25),
                (center_x, height - 20)
            ])
            
            # Energy core
            pygame.draw.circle(self.original_image, self.design['core_color'],
                             (center_x, height - 25), 3)
        
        # Add engine effects to all ships (now at top)
        self.add_engine_effects()
            
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.radius = min(self.design['size']) // 2
        
        # Initialize sprite properties
        self.bullets = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()
        self.last_shot = pygame.time.get_ticks()
        self.spawn_time = pygame.time.get_ticks()
        
        # Initialize position and movement
        self.rect.x = random.randint(0, pygame.display.get_surface().get_width() - self.rect.width)
        self.rect.y = random.randint(-150, -50) if enemy_type != 'boss' else -100
        self.speed_y = self.design['speed']
        self.speed_x = 0
        
        # Movement pattern variables
        self.movement_pattern = 'boss_pattern' if enemy_type == 'boss' else random.choice(['straight', 'zigzag', 'sine'])
        self.pattern_offset = random.randint(0, 360)
        self.angle = 0
        
        # Initialize shooting variables with type-specific delay
        self.shoot_delay = self.design['shoot_delay']
        if self.shoot_delay is not None:  # Only for shooting ships
            self.shoot_delay = int(self.shoot_delay * (0.9 ** (round_number - 1)))  # 10% faster per round
            self.shoot_delay = max(1500, self.shoot_delay)  # Minimum 1.5 second delay
        self.last_shot = pygame.time.get_ticks()
        self.bullets = pygame.sprite.Group()
        self.spawn_time = pygame.time.get_ticks()
        
        # Initialize sprite properties
        self.bullets = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()
        self.last_shot = pygame.time.get_ticks()
        self.spawn_time = pygame.time.get_ticks()
        
        # Particles
        self.particles = pygame.sprite.Group()

    def add_engine_effects(self):
        """Add engine glow and core effects"""
        width, height = self.design['size']
        center_x = width // 2
        
        if self.enemy_type == 'boss':
            # Engine glow for boss (at the top)
            pygame.draw.polygon(self.original_image, self.design['engine_color'], [
                (center_x - 8, 5),
                (center_x, 15),
                (center_x + 8, 5)
            ])
            
            # Core glow
            pygame.draw.circle(self.original_image, self.design['core_color'],
                             (center_x, 10), 4)
        else:
            # Engine glow for regular enemies
            pygame.draw.polygon(self.original_image, self.design['engine_color'], [
                (center_x - 4, 8),
                (center_x, 3),
                (center_x + 4, 8)
            ])
            
            # Core glow
            pygame.draw.circle(self.original_image, self.design['core_color'],
                             (center_x, 8), 2)

    def rotate(self):
        """Rotate the enemy ship based on its movement pattern"""
        if self.movement_pattern == 'straight':
            return  # No rotation for straight movement
            
        # Calculate rotation angle
        if self.movement_pattern == 'zigzag':
            self.angle = math.sin(pygame.time.get_ticks() * 0.003 + self.pattern_offset) * 30
        elif self.movement_pattern == 'sine':
            self.angle = math.cos(pygame.time.get_ticks() * 0.002 + self.pattern_offset) * 20
            
        # Apply rotation
        rotated_image = pygame.transform.rotate(self.original_image, self.angle)
        old_center = self.rect.center
        self.image = rotated_image
        self.rect = self.image.get_rect()
        self.rect.center = old_center

    def shoot(self):
        """Shoot bullets based on enemy type"""
        if self.enemy_type == 'redcross':
            return  # Healing ships don't shoot
            
        bullet_type = self.design['bullet_type']
        damage = self.design['bullet_damage']
        
        # Add muzzle flash effect
        for _ in range(3):
            particle = Particle(self.rect.centerx, self.rect.bottom,
                             (255, 200, 0), 0, 1)
            self.particles.add(particle)
        
        if bullet_type == 'small_laser':
            # Single fast laser
            bullet = EnemyBullet(self.rect.centerx, self.rect.bottom, 0, 4, 
                               damage, color=(255, 0, 0), size=3)
            self.bullets.add(bullet)
            debug_print(f"Scout fired a laser! Damage: {damage}", "yellow")
            
        elif bullet_type == 'dual_shot':
            # Two bullets side by side
            bullet1 = EnemyBullet(self.rect.centerx - 10, self.rect.bottom, -0.5, 4, 
                                damage, color=(148, 0, 211), size=4)
            bullet2 = EnemyBullet(self.rect.centerx + 10, self.rect.bottom, 0.5, 4, 
                                damage, color=(148, 0, 211), size=4)
            self.bullets.add(bullet1, bullet2)
            debug_print(f"Fighter fired dual shots! Damage: {damage}", "magenta")
            
        elif bullet_type == 'plasma':
            # Large slow plasma ball
            bullet = EnemyBullet(self.rect.centerx, self.rect.bottom, 0, 3, 
                               damage, color=(0, 255, 0), size=8)
            self.bullets.add(bullet)
            debug_print(f"Bomber fired plasma! Damage: {damage}", "green")
            
        elif bullet_type == 'spread':
            # Three bullets in a spread pattern
            for angle in [-30, 0, 30]:
                rad = math.radians(angle)
                speed_x = math.sin(rad) * 3
                speed_y = math.cos(rad) * 3
                bullet = EnemyBullet(self.rect.centerx, self.rect.bottom,
                                   speed_x, speed_y, damage, 
                                   color=(0, 0, 255), size=5)
                self.bullets.add(bullet)
            debug_print(f"Elite fired spread shot! Damage: {damage}", "blue")

    def redraw_boss(self):
        """重绘星际航母Boss - 大型圆盘状母舰"""
        width, height = self.design['size']
        center_x = width // 2
        center_y = height // 2
        
        # 清空原始图像
        self.original_image = pygame.Surface(self.design['size'], pygame.SRCALPHA)
        
        # 主体 - 大型圆盘状船体
        main_radius = min(width, height) // 3
        pygame.draw.ellipse(self.original_image, self.current_phase['color'], 
                          [center_x - main_radius, center_y - main_radius//2, 
                           main_radius*2, main_radius])
        
        # 中央指挥塔
        tower_radius = main_radius // 3
        pygame.draw.ellipse(self.original_image, 
                          tuple(max(0, min(255, c + 30)) for c in self.current_phase['color']),
                          [center_x - tower_radius, center_y - tower_radius//2, 
                           tower_radius*2, tower_radius])
        
        # 外环装甲带
        outer_ring = main_radius + 10
        pygame.draw.ellipse(self.original_image, 
                          tuple(max(0, min(255, c - 30)) for c in self.current_phase['color']),
                          [center_x - outer_ring, center_y - outer_ring//2, 
                           outer_ring*2, outer_ring], 8)
        
        # 舰载机发射舱 - 多个小圆形开口
        hangar_color = (50, 50, 50)
        for i in range(8):
            angle = i * math.pi / 4
            hangar_x = center_x + int(main_radius * 0.7 * math.cos(angle))
            hangar_y = center_y + int(main_radius * 0.3 * math.sin(angle))
            pygame.draw.circle(self.original_image, hangar_color, (hangar_x, hangar_y), 6)
            pygame.draw.circle(self.original_image, (255, 150, 0), (hangar_x, hangar_y), 4)
        
        # 武器炮台 - 周围分布的炮塔
        turret_color = tuple(max(0, min(255, c + 50)) for c in self.current_phase['color'])
        for i in range(12):
            angle = i * math.pi / 6
            turret_x = center_x + int(main_radius * 0.9 * math.cos(angle))
            turret_y = center_y + int(main_radius * 0.4 * math.sin(angle))
            pygame.draw.ellipse(self.original_image, turret_color, 
                              [turret_x-4, turret_y-3, 8, 6])
            pygame.draw.ellipse(self.original_image, (255, 0, 0), 
                              [turret_x-2, turret_y-1, 4, 2])
        
        # 主炮 - 中央大型武器
        main_gun_color = tuple(max(0, min(255, c + 70)) for c in self.current_phase['color'])
        pygame.draw.ellipse(self.original_image, main_gun_color,
                          [center_x-15, center_y-8, 30, 16])
        pygame.draw.ellipse(self.original_image, (255, 255, 100),
                          [center_x-12, center_y-5, 24, 10])
        
        # 能量核心 - 脉动效果
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.01)) * 0.3 + 0.7
        core_color = tuple(int(c * pulse) for c in (255, 255, 255))
        pygame.draw.circle(self.original_image, core_color, (center_x, center_y), 8)
        pygame.draw.circle(self.original_image, (0, 255, 255), (center_x, center_y), 5)
        
        # 推进器阵列 - 后方推进系统
        thruster_color = (0, 150, 255)
        for i in range(6):
            thruster_x = center_x - main_radius + i * (main_radius // 3)
            thruster_y = center_y + main_radius//2 - 5
            pygame.draw.ellipse(self.original_image, thruster_color,
                              [thruster_x, thruster_y, 8, 12])
            pygame.draw.ellipse(self.original_image, (255, 255, 255),
                              [thruster_x+2, thruster_y+2, 4, 8])
        
        # 护盾生成器 - 四个角落的设备
        shield_color = (150, 255, 150)
        shield_positions = [
            (center_x - main_radius//2, center_y - main_radius//3),
            (center_x + main_radius//2, center_y - main_radius//3),
            (center_x - main_radius//2, center_y + main_radius//3),
            (center_x + main_radius//2, center_y + main_radius//3)
        ]
        for shield_x, shield_y in shield_positions:
            pygame.draw.ellipse(self.original_image, shield_color,
                              [shield_x-6, shield_y-6, 12, 12])
            pygame.draw.ellipse(self.original_image, (255, 255, 255),
                              [shield_x-3, shield_y-3, 6, 6])
        
        # 相位指示灯 - 显示当前状态
        phase_light_color = self.current_phase['color'] if self.current_phase else (255, 0, 0)
        for i in range(4):
            light_x = center_x - 20 + i * 13
            light_y = center_y - tower_radius//2 - 10
            pygame.draw.circle(self.original_image, phase_light_color, (light_x, light_y), 3)
        
        # 更新当前图像
        self.image = self.original_image.copy()
    
    def update_phase(self):
        """更新Boss的相位状态"""
        if self.enemy_type == 'boss':
            health_percentage = self.health / self.max_health
            old_phase = self.current_phase
            new_phase = None
            
            # 从高血量阈值到低血量阈值排序
            sorted_phases = sorted(self.phases, key=lambda x: x['health_threshold'], reverse=True)
            
            # 找到当前血量对应的相位
            new_phase = None
            for phase in sorted_phases:
                if health_percentage >= phase['health_threshold']:
                    new_phase = phase
                    break
            
            # 如果没有找到合适的相位，使用最后一个相位
            if new_phase is None:
                new_phase = sorted_phases[-1]
            
            # 如果相位发生变化
            if not old_phase or old_phase.get('name') != new_phase.get('name'):
                self.current_phase = new_phase
                self.shoot_delay = new_phase['shoot_delay']
                
                # 更新速度
                base_speed = self.design['speed']
                self.speed_x = base_speed * new_phase['speed_multiplier']
                self.speed_y = base_speed * new_phase['speed_multiplier']
                
                # 重绘Boss精灵
                self.redraw_boss()
                
                # 打印相位变化信息
                phase_name = new_phase['name']
                health_percent = int(health_percentage * 100)
                speed_mult = new_phase['speed_multiplier']
                attack_patterns = ', '.join(new_phase['attack_patterns'])
                
                cprint(f"\nBoss进入新相位！", "yellow", attrs=['bold'])
                cprint(f"- 相位名称：{phase_name}", "yellow")
                cprint(f"- 当前血量：{health_percent}%", "yellow")
                cprint(f"- 速度倍率：{speed_mult}x", "yellow")
                cprint(f"- 攻击模式：{attack_patterns}", "yellow")
                cprint(f"- 攻击间隔：{new_phase['shoot_delay']}ms\n", "yellow")
                
                # 添加相位转换特效
                for _ in range(30):
                    angle = random.uniform(0, math.pi * 2)
                    speed = random.uniform(3, 7)
                    speed_x = math.cos(angle) * speed
                    speed_y = math.sin(angle) * speed
                    
                    # 使用旧相位和新相位的颜色混合
                    old_color = old_phase['color'] if old_phase else new_phase['color']
                    color = old_color if random.random() < 0.5 else new_phase['color']
                    
                    particle = Particle(self.rect.centerx, self.rect.centery,
                                      color, speed_x, speed_y, 
                                      size=random.randint(3, 6))
                    self.particles.add(particle)
    
    def update(self):
        self.rotate()
        
        # Update position based on movement pattern
        if self.movement_pattern == 'boss_pattern':
            # Boss moves in a slow side-to-side pattern at the top of the screen
            if self.rect.y < 100:  # Move to position first
                self.rect.y += self.speed_y
            else:
                self.rect.x += math.cos(pygame.time.get_ticks() * 0.001) * 2
            
            # Update boss phase
            self.update_phase()
            
            # Boss shooting pattern based on current phase
            now = pygame.time.get_ticks()
            if now - self.last_shot > self.shoot_delay:
                # 根据当前相位选择攻击模式
                if self.current_phase:
                    attack_pattern = random.choice(self.current_phase['attack_patterns'])
                    if attack_pattern == 'umbrella':
                        self.shoot_umbrella()
                        cprint("Boss: 雨伞模式攻击！", "yellow")
                    elif attack_pattern == 'spread':
                        self.shoot_spread()
                        cprint("Boss: 散射攻击！", "cyan")
                    elif attack_pattern == 'laser_barrage':
                        self.shoot_laser_barrage()
                        cprint("Boss: 激光弹幕！", "blue")
                    elif attack_pattern == 'cross_fire':
                        self.shoot_cross_fire()
                        cprint("Boss: 十字火力攻击！", "red")
                    elif attack_pattern == 'spiral':
                        self.shoot_spiral()
                        cprint("Boss: 螺旋攻击！", "magenta")
                    elif attack_pattern == 'death_spiral':
                        self.shoot_death_spiral()
                        cprint("Boss: 死亡螺旋攻击！", "magenta")
                    elif attack_pattern == 'bullet_hell':
                        self.shoot_bullet_hell()
                        cprint("Boss: 弹幕地狱模式！", "white")
                self.last_shot = now
        else:
            if self.movement_pattern == 'straight':
                self.rect.y += self.speed_y
            elif self.movement_pattern == 'zigzag':
                self.rect.x += math.sin(pygame.time.get_ticks() * 0.003 + self.pattern_offset) * 3
                self.rect.y += self.speed_y
            elif self.movement_pattern == 'sine':
                self.rect.x += math.cos(pygame.time.get_ticks() * 0.002 + self.pattern_offset) * 2
                self.rect.y += self.speed_y
            
            # Regular enemy shooting
            now = pygame.time.get_ticks()
            # Only start shooting 1 second after spawning and if ship has shooting capability
            if self.shoot_delay is not None and now - self.spawn_time > 1000:
                if now - self.last_shot > self.shoot_delay:
                    self.shoot()
                    self.last_shot = now
        
        # Update and remove off-screen bullets
        self.bullets.update()
        for bullet in self.bullets.copy():
            if bullet.rect.top > 768 + 50 or bullet.rect.bottom < -50:
                bullet.kill()
        
        # Update particles
        self.particles.update()
        
        # Add engine particles
        if random.random() < 0.2:
            color = {
                'scout': (255, 100, 100),    # Red laser
                'fighter': (200, 100, 255),  # Purple energy
                'bomber': (100, 255, 100),   # Green plasma
                'elite': (100, 100, 255),    # Blue scatter
                'striker': (50, 255, 150),   # Bright green plasma
                'boss': (255, 50, 50),       # Intense red
                'redcross': (255, 255, 255)  # White healing
            }[self.enemy_type]
                
            speed_x = random.uniform(-1, 1)
            speed_y = random.uniform(-3, -1)
            particle = Particle(self.rect.centerx, self.rect.bottom - 5,
                              color, speed_x, speed_y)
            self.particles.add(particle)
        
        # Reset position when off screen (only for non-boss enemies)
        if self.enemy_type != 'boss' and self.rect.top > 768 + 50:  # 给予更大的缓冲区
            self.rect.x = random.randrange(1024 - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speed_y = self.design['speed']
            
        # Bounce off screen edges
        if self.rect.left < 0:
            self.rect.left = 0
            self.speed_x = abs(self.speed_x)
        elif self.rect.right > 1024:
            self.rect.right = 1024
            self.speed_x = -abs(self.speed_x)
            
    def take_damage(self, amount):
        """处理敌人受到伤害的逻辑"""
        self.health = max(0, self.health - amount)  # 确保生命值不会小于0
        
        # 如果是Boss，检查相位变化
        if self.enemy_type == 'boss':
            self.update_phase()
            
            # 根据当前相位添加不同颜色的伤害粒子
            particle_color = self.current_phase['color'] if self.current_phase else (255, 0, 0)
            particle_count = 10  # Boss受伤时产生更多粒子
        else:
            particle_color = (255, 100, 100)
            particle_count = 5
        
        # 添加伤害粒子特效
        for _ in range(particle_count):
            speed_x = random.uniform(-3, 3)
            speed_y = random.uniform(-3, 3)
            size = random.randint(2, 4)
            particle = Particle(self.rect.centerx, self.rect.centery,
                              particle_color, speed_x, speed_y, size)
            self.particles.add(particle)
        
        # 打印伤害信息
        if self.enemy_type == 'boss':
            health_percentage = (self.health / self.max_health) * 100
            cprint(f"Boss受到{amount}点伤害！剩余血量：{int(health_percentage)}%", "red")
        
        return self.health <= 0

    def shoot_umbrella(self):
        """创建伞形弹幕"""
        bullet_count = 12
        spread = 360  # 全圈
        
        for i in range(bullet_count):
            angle = (360 * i / bullet_count)
            rad = math.radians(angle)
            speed_x = math.cos(rad) * 4
            speed_y = math.sin(rad) * 4
            
            # 创建子弹
            bullet = EnemyBullet(self.rect.centerx, self.rect.centery,
                                speed_x, speed_y, self.design['bullet_damage'],
                                color=self.current_phase['color'])
            self.bullets.add(bullet)
    
    def shoot_spread(self):
        """创建散射弹幕"""
        angles = [-45, -30, -15, 0, 15, 30, 45]
        for angle in angles:
            rad = math.radians(angle)
            speed_x = math.sin(rad) * 5
            speed_y = math.cos(rad) * 5
            bullet = EnemyBullet(self.rect.centerx, self.rect.bottom,
                               speed_x, speed_y, self.design['bullet_damage'],
                               color=self.design['color'])
            self.bullets.add(bullet)
    
    def shoot_laser_barrage(self):
        """创建激光弹幕"""
        for i in range(5):
            offset = random.randint(-30, 30)
            speed_x = math.sin(math.radians(offset)) * 6
            speed_y = math.cos(math.radians(offset)) * 6
            bullet = EnemyBullet(self.rect.centerx, self.rect.bottom,
                               speed_x, speed_y, self.design['bullet_damage'],
                               color=self.design['color'], size=3)
            self.bullets.add(bullet)
    
    def shoot_cross_fire(self):
        """十字弹幕"""
        angles = [0, 90, 180, 270]
        for angle in angles:
            rad = math.radians(angle)
            speed_x = math.cos(rad) * 4
            speed_y = math.sin(rad) * 4
            bullet = EnemyBullet(self.rect.centerx, self.rect.centery,
                               speed_x, speed_y, self.design['bullet_damage'],
                               color=self.design['color'])
            self.bullets.add(bullet)
    
    def shoot_spiral(self):
        """螺旋弹幕"""
        now = pygame.time.get_ticks()
        angle = (now / 100) % 360  # 每100ms旋转一圈
        for i in range(3):  # 发射3个子弹
            rad = math.radians(angle + i * 120)
            speed_x = math.cos(rad) * 5
            speed_y = math.sin(rad) * 5
            bullet = EnemyBullet(self.rect.centerx, self.rect.centery,
                               speed_x, speed_y, self.design['bullet_damage'],
                               color=self.design['color'])
            self.bullets.add(bullet)
    
    def shoot_death_spiral(self):
        """死亡螺旋弹幕"""
        now = pygame.time.get_ticks()
        base_angle = (now / 50) % 360  # 更快的旋转
        for i in range(2):  # 两个螺旋
            for j in range(6):  # 每个螺旋6个子弹
                angle = base_angle + i * 180 + j * 60
                rad = math.radians(angle)
                speed = 3 + (j % 2)  # 交替的速度
                speed_x = math.cos(rad) * speed
                speed_y = math.sin(rad) * speed
                bullet = EnemyBullet(self.rect.centerx, self.rect.centery,
                                   speed_x, speed_y, self.design['bullet_damage'],
                                   color=self.current_phase['color'])
                self.bullets.add(bullet)
    
    def shoot_bullet_hell(self):
        """地狱弹幕"""
        bullet_count = 16
        now = pygame.time.get_ticks()
        base_angle = (now / 200) % 360
        
        for i in range(bullet_count):
            angle = base_angle + (360 * i / bullet_count)
            rad = math.radians(angle)
            speed_x = math.cos(rad) * 4
            speed_y = math.sin(rad) * 4
            
            # 创建两圈子弹
            for radius in [30, 60]:
                bullet_x = self.rect.centerx + math.cos(rad) * radius
                bullet_y = self.rect.centery + math.sin(rad) * radius
                bullet = EnemyBullet(bullet_x, bullet_y,
                                   speed_x, speed_y, self.design['bullet_damage'],
                                   color=self.current_phase['color'])
                self.bullets.add(bullet)
            
            # Add muzzle flash particles
            for _ in range(2):
                particle = Particle(self.rect.centerx, self.rect.centery,
                                 (255, 200, 0), speed_x * 0.5, speed_y * 0.5)
                self.particles.add(particle)
                
    def shoot_spread(self):
        """Create a spread shot pattern"""
        bullet_count = 5
        spread = 60
        
        # Calculate base angle towards player if available
        if hasattr(self, 'player') and self.player:
            dx = self.player.rect.centerx - self.rect.centerx
            dy = self.player.rect.centery - self.rect.centery
            base_angle = math.degrees(math.atan2(dy, dx))
        else:
            base_angle = 90
        
        for i in range(bullet_count):
            angle = base_angle - (spread / 2) + (spread * i / (bullet_count - 1))
            rad = math.radians(angle)
            speed_x = math.cos(rad) * 5
            speed_y = math.sin(rad) * 5
            
            bullet = EnemyBullet(self.rect.centerx, self.rect.bottom,
                                speed_x, speed_y, self.design['bullet_damage'] * 0.8,
                                color=self.current_phase['color'])
            self.bullets.add(bullet)
            
    def shoot_laser_barrage(self):
        """Create a laser barrage pattern"""
        for x in range(self.rect.left + 10, self.rect.right - 10, 20):
            bullet = EnemyBullet(x, self.rect.bottom, 0, 6,
                                self.design['bullet_damage'] * 1.2,
                                color=self.current_phase['color'], size=4)
            self.bullets.add(bullet)
            
            # Add laser charging effect
            for _ in range(2):
                particle = Particle(x, self.rect.bottom,
                                 (0, 200, 255),
                                 random.uniform(-0.5, 0.5),
                                 random.uniform(-1, 1))
                self.particles.add(particle)
                
    def shoot_cross_fire(self):
        """Create a cross-shaped bullet pattern"""
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        speed = 4
        
        for dx, dy in directions:
            for i in range(3):
                offset = i * 20
                bullet = EnemyBullet(self.rect.centerx + offset * dx,
                                    self.rect.centery + offset * dy,
                                    dx * speed, dy * speed,
                                    self.design['bullet_damage'],
                                    color=self.current_phase['color'])
                self.bullets.add(bullet)
            
    def shoot_death_spiral(self):
        """Create a spiral pattern of bullets"""
        now = pygame.time.get_ticks()
        angle = (now // 100) % 360
        speed = 4
        
        for i in range(8):
            spiral_angle = angle + i * 45
            rad = math.radians(spiral_angle)
            speed_x = math.cos(rad) * speed
            speed_y = math.sin(rad) * speed
            
            bullet = EnemyBullet(self.rect.centerx, self.rect.centery,
                                speed_x, speed_y,
                                self.design['bullet_damage'] * 1.2,
                                color=(255, 0, 128))
            self.bullets.add(bullet)
            
            # Add spiral effect particles
            particle = Particle(self.rect.centerx, self.rect.centery,
                             (255, 100, 200),
                             speed_x * 0.5, speed_y * 0.5)
            self.particles.add(particle)
            
    def shoot_bullet_hell(self):
        """Create a random bullet hell pattern"""
        for _ in range(12):
            angle = random.randint(0, 360)
            rad = math.radians(angle)
            speed = random.uniform(3, 6)
            speed_x = math.cos(rad) * speed
            speed_y = math.sin(rad) * speed
            
            # Random bullet color for visual variety
            color = (random.randint(200, 255),
                    random.randint(0, 100),
                    random.randint(0, 255))
            
            bullet = EnemyBullet(self.rect.centerx, self.rect.centery,
                                speed_x, speed_y,
                                self.design['bullet_damage'],
                                color=color)
            self.bullets.add(bullet)
            
            # Add chaotic particles
            particle = Particle(self.rect.centerx, self.rect.centery,
                             color,
                             speed_x * 0.3, speed_y * 0.3)
            self.particles.add(particle)

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_x, speed_y, damage=10, color=(255, 100, 0), size=6):
        super().__init__()
        self.image = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        # 子弹主体
        pygame.draw.circle(self.image, color, (size, size), size)
        # 发光效果
        glow_color = tuple(min(c + 100, 255) for c in color[:3])  # 更亮的颜色
        pygame.draw.circle(self.image, glow_color, (size, size), size // 2)
        
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.x = float(x)
        self.y = float(y)
        self.speed_x = speed_x * 0.7  # 降低速度
        self.speed_y = speed_y * 0.7  # 降低速度
        self.damage = damage
        
        # 添加拖尾粒子效果
        self.particles = pygame.sprite.Group()
        self.last_particle = pygame.time.get_ticks()
        self.particle_delay = 50  # 每50ms添加一个粒子
        self.color = color

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.rect.x = self.x
        self.rect.y = self.y
        
        # 更新拖尾粒子
        now = pygame.time.get_ticks()
        if now - self.last_particle > self.particle_delay:
            glow_color = tuple(min(c + 50, 255) for c in self.color[:3])
            particle = Particle(self.rect.centerx, self.rect.centery,
                              glow_color, random.uniform(-0.5, 0.5),
                              random.uniform(-0.5, 0.5), size=2)
            self.particles.add(particle)
            self.last_particle = now
        
        self.particles.update()
        # 移除消失的粒子
        for particle in self.particles.copy():
            if not particle.alive():
                particle.kill()

class PowerUp(pygame.sprite.Sprite):
    TYPES = {
        'shield': {
            'color': (0, 255, 255),  # Cyan
            'duration': 10000,  # 10 seconds
            'effect': 'Temporary shield'
        },
        'speed': {
            'color': (255, 255, 0),  # Yellow
            'duration': 8000,   # 8 seconds
            'effect': 'Speed boost'
        },
        'weapon': {
            'color': (255, 0, 255),  # Magenta
            'duration': 15000,  # 15 seconds
            'effect': 'Weapon power-up'
        }
    }
    
    def __init__(self, x, y, power_type):
        super().__init__()
        self.type = power_type
        self.config = self.TYPES[power_type]
        
        # Create power-up surface with glowing effect
        self.original_image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.original_image, self.config['color'], (10, 10), 8)
        inner_color = tuple(min(c + 100, 255) for c in self.config['color'])
        pygame.draw.circle(self.original_image, inner_color, (10, 10), 4)
        
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))
        
        # Movement properties
        self.y_speed = 2
        self.x_speed = math.sin(pygame.time.get_ticks() * 0.001) * 2
        self.angle = 0
        
        # Particles
        self.particles = pygame.sprite.Group()
        self.last_particle = pygame.time.get_ticks()
        self.particle_delay = 100
        
    def update(self):
        # Rotate the power-up
        self.angle = (self.angle + 2) % 360
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        
        # Update position with floating movement
        self.rect.y += self.y_speed
        self.rect.x += math.sin(pygame.time.get_ticks() * 0.002) * 2
        
        # Add trailing particles
        now = pygame.time.get_ticks()
        if now - self.last_particle > self.particle_delay:
            particle = Particle(self.rect.centerx, self.rect.centery,
                              self.config['color'],
                              random.uniform(-0.5, 0.5),
                              random.uniform(-0.5, 0.5),
                              size=3)
            self.particles.add(particle)
            self.last_particle = now
        
        # Update particles
        self.particles.update()
        for particle in self.particles.copy():
            if not particle.alive():
                particle.kill()

class ScreenShake:
    def __init__(self):
        self.intensity = 0
        self.duration = 0
        self.start_time = 0
        self.offset = [0, 0]
    
    def start_shake(self, intensity, duration):
        self.intensity = intensity
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
    
    def update(self):
        if self.intensity > 0:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.start_time
            
            if elapsed < self.duration:
                # Calculate shake intensity based on remaining duration
                remaining = 1 - (elapsed / self.duration)
                current_intensity = self.intensity * remaining
                
                # Generate random offset
                self.offset = [
                    random.uniform(-current_intensity, current_intensity),
                    random.uniform(-current_intensity, current_intensity)
                ]
            else:
                self.intensity = 0
                self.offset = [0, 0]
        
        return self.offset
