import os
import pygame
import random
import math
import time
from termcolor import cprint

class Button:
    def __init__(self, x, y, width, height, text, font_size=36):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = self.load_chinese_font(font_size)
        self.normal_color = (41, 128, 185)  # 深蓝色
        self.hover_color = (52, 152, 219)   # 亮蓝色
        self.text_color = (236, 240, 241)   # 浅灰白色
        self.is_hovered = False
        
    def load_chinese_font(self, font_size):
        """Load Chinese-compatible font for button"""
        # Use smaller default size for better proportions
        adjusted_size = max(20, int(font_size * 0.8))
        
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
        
        # Try font files first
        for font_path in chinese_font_files:
            try:
                font = pygame.font.Font(font_path, adjusted_size)
                test_surface = font.render('中文测试', True, (255, 255, 255))
                if test_surface.get_width() > 0:
                    return font
            except:
                continue
        
        # Try system fonts as fallback
        system_fonts = ['STHeiti', 'Hiragino Sans GB', 'Arial Unicode MS']
        for font_name in system_fonts:
            try:
                font = pygame.font.SysFont(font_name, adjusted_size)
                test_surface = font.render('中文测试', True, (255, 255, 255))
                if test_surface.get_width() > 0:
                    return font
            except:
                continue
        
        # Fallback to default font
        return pygame.font.Font(None, adjusted_size)
        
    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.normal_color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def update(self, mouse_pos):
        """更新按钮状态"""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
    def handle_event(self, event):
        """处理按钮事件"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                cprint(f"按钮 '{self.text}' 被点击", "cyan")
                return True
        return False

class Menu:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE = (100, 149, 237)  # Cornflower blue
        self.GREEN = (50, 205, 50)   # Lime green
        
        # Fonts
        self.title_font, self.text_font, self.button_font = self.load_chinese_fonts()
        
        # Initialize UI elements
        self.init_ui_elements()
        
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
        
        # Try font files first
        for font_path in chinese_font_files:
            try:
                title_font = pygame.font.Font(font_path, 72)  # Smaller title
                text_font = pygame.font.Font(font_path, 28)   # Smaller text
                button_font = pygame.font.Font(font_path, 36) # Smaller button font
                
                # Test if the font can render Chinese characters
                test_surface = text_font.render('中文测试', True, (255, 255, 255))
                if test_surface.get_width() > 0:
                    font_name = font_path.split('/')[-1]
                    cprint(f"菜单成功加载中文字体: {font_name}", "green")
                    # Store the successful font path for later use
                    self.chinese_font_path = font_path
                    return title_font, text_font, button_font
            except Exception as e:
                cprint(f"无法加载字体 {font_path}: {e}", "yellow")
                continue
        
        # Try system fonts as fallback
        system_fonts = ['STHeiti', 'Hiragino Sans GB', 'Arial Unicode MS']
        for font_name in system_fonts:
            try:
                title_font = pygame.font.SysFont(font_name, 72)  # Smaller title
                text_font = pygame.font.SysFont(font_name, 28)   # Smaller text
                button_font = pygame.font.SysFont(font_name, 36)  # Smaller button font
                
                test_surface = text_font.render('中文测试', True, (255, 255, 255))
                if test_surface.get_width() > 0:
                    cprint(f"菜单成功加载系统字体: {font_name}", "green")
                    # Store system font name for later use
                    self.chinese_font_name = font_name
                    self.chinese_font_path = None
                    return title_font, text_font, button_font
            except:
                continue
        
        # If no Chinese font works, use default font
        cprint("菜单警告：无法加载中文字体，使用默认字体。中文可能显示为方块。", "yellow")
        self.chinese_font_path = None
        self.chinese_font_name = None
        return pygame.font.Font(None, 72), pygame.font.Font(None, 28), pygame.font.Font(None, 36)
    
    def init_ui_elements(self):
        """Initialize UI elements after fonts are loaded"""
        # Professional layout with proper spacing
        self.title_y = self.height // 6  # Title position
        self.ship_selection_y = self.height // 2 - 100  # Ship selection area
        
        # Title text with better positioning
        self.title_text = self.title_font.render("太空射手", True, (100, 149, 237))  # Cornflower blue
        self.title_rect = self.title_text.get_rect(center=(self.width // 2, self.title_y))
        
        # Ship selection title - even smaller for less crowding
        try:
            # Try to use the same font as text_font but smaller
            title_font_path = None
            for font_path in [
                os.path.join(os.path.dirname(__file__), 'resources', 'fonts', 'Hiragino Sans GB.ttc'),
                '/System/Library/Fonts/Hiragino Sans GB.ttc',
                '/System/Library/Fonts/STHeiti Medium.ttc'
            ]:
                try:
                    test_font = pygame.font.Font(font_path, 28)  # Even smaller
                    test_surface = test_font.render('测试', True, (255, 255, 255))
                    if test_surface.get_width() > 0:
                        title_font_path = font_path
                        break
                except:
                    continue
            
            if title_font_path:
                small_font = pygame.font.Font(title_font_path, 28)
            else:
                small_font = pygame.font.SysFont('STHeiti', 28)
        except:
            small_font = self.text_font
            
        self.ship_title_text = small_font.render("选择你的飞船", True, (255, 215, 0))  # Gold color
        self.ship_title_rect = self.ship_title_text.get_rect(center=(self.width // 2, self.ship_selection_y - 30))
        
        # Ship preview area - more compact
        self.preview_size = 120
        self.preview_rect = pygame.Rect(self.width // 2 - self.preview_size // 2, 
                                      self.ship_selection_y + 5, 
                                      self.preview_size, self.preview_size)
        
        # Ship info display - more spacious layout
        self.ship_info_y = self.ship_selection_y + 150
        self.ship_index_y = self.ship_info_y + 40
        
        # Control hints - smaller font and better spacing
        try:
            # Use Chinese font for control hints
            if hasattr(self, 'chinese_font_path') and self.chinese_font_path:
                hint_font = pygame.font.Font(self.chinese_font_path, 22)
            elif hasattr(self, 'chinese_font_name') and self.chinese_font_name:
                hint_font = pygame.font.SysFont(self.chinese_font_name, 22)
            else:
                hint_font = pygame.font.SysFont('STHeiti', 22)
        except:
            hint_font = self.text_font  # Use the working text font as fallback
            
        self.control_text = hint_font.render("← 切换飞船 →", True, (120, 180, 255))  # Lighter blue
        self.control_rect = self.control_text.get_rect(center=(self.width // 2, self.ship_index_y + 45))
        
        # Button positioning - more space from other elements
        self.button_y = self.height - 110
        
        # Start game button - more refined
        button_width = 280
        button_height = 50
        
        self.start_button = Button(self.width // 2 - button_width // 2, 
                                 self.button_y,
                                 button_width, button_height, 
                                 "开始游戏", 32)
        
        # Quit button
        self.quit_text = self.text_font.render("退出", True, self.WHITE)
        self.quit_rect = self.quit_text.get_rect(center=(self.width - 60, self.height - 40))
        self.quit_button = pygame.Rect(self.quit_rect.x - 10,
                                     self.quit_rect.y - 5,
                                     self.quit_rect.width + 20,
                                     self.quit_rect.height + 10)
        
        # Ship names and descriptions (添加中文名称和描述)
        self.ship_info = {
            'interceptor': {'name': '拦截机', 'desc': '快速轻型战斗机'},
            'striker': {'name': '突击者', 'desc': '重型装甲战舰'},
            'phantom': {'name': '幻影', 'desc': '隐秘侦察舰'},
            'guardian': {'name': '守护者', 'desc': '防御型护卫舰'},
            'avenger': {'name': '复仇者', 'desc': '多用途战斗机'},
            'stealth': {'name': '隐形舰', 'desc': '先进隐形战舰'}
        }
        
        # Ship color schemes (copy from sprites.py)
        self.ship_designs = {
            'interceptor': {'color': (30, 144, 255), 'wing_color': (135, 206, 250), 'engine_color': (0, 191, 255), 'core_color': (255, 255, 0), 'cockpit_color': (173, 216, 230)},
            'striker': {'color': (50, 205, 50), 'wing_color': (144, 238, 144), 'engine_color': (0, 255, 127), 'core_color': (255, 255, 0), 'cockpit_color': (152, 251, 152)},
            'phantom': {'color': (147, 112, 219), 'wing_color': (230, 230, 250), 'engine_color': (186, 85, 211), 'core_color': (255, 255, 0), 'cockpit_color': (221, 160, 221)},
            'guardian': {'color': (255, 165, 0), 'wing_color': (255, 218, 185), 'engine_color': (255, 140, 0), 'core_color': (255, 255, 0), 'cockpit_color': (255, 222, 173)},
            'avenger': {'color': (220, 20, 60), 'wing_color': (250, 128, 114), 'engine_color': (255, 69, 0), 'core_color': (255, 255, 0), 'cockpit_color': (240, 128, 128)},
            'stealth': {'color': (169, 169, 169), 'wing_color': (211, 211, 211), 'engine_color': (128, 128, 128), 'core_color': (255, 255, 0), 'cockpit_color': (192, 192, 192)}
        }
        
        # Ship selection
        self.ships = ['interceptor', 'striker', 'phantom', 'guardian', 'avenger', 'stealth']
        self.current_ship = 0
        
        # Background stars
        self.stars = []
        for _ in range(50):
            x = random.randrange(self.width)
            y = random.randrange(self.height)
            speed = random.uniform(0.5, 2.0)
            self.stars.append([x, y, speed])
            
            
    def update_stars(self):
        for star in self.stars:
            star[1] += star[2]  # Move star down
            if star[1] > self.height:
                star[1] = 0
                star[0] = random.randrange(self.width)
    
    def draw_ship_preview(self, screen, ship_type):
        """绘制飞船预览图"""
        colors = self.ship_designs[ship_type]
        
        # Calculate center position and scale
        center_x = self.preview_rect.centerx
        center_y = self.preview_rect.centery
        scale = 1.5  # 缩放比例
        
        # Helper function to scale and position coordinates
        def scale_point(x, y):
            scaled_x = int((x - 32) * scale + center_x)  # 32 is original center
            scaled_y = int((y - 32) * scale + center_y)
            return (scaled_x, scaled_y)
        
        if ship_type == 'interceptor':
            # 拦截机 - 尖锐的三角战斗机
            main_body = [scale_point(32, 8), scale_point(18, 45), scale_point(28, 50), 
                        scale_point(32, 55), scale_point(36, 50), scale_point(46, 45)]
            pygame.draw.polygon(screen, colors['color'], main_body)
            
            # 侧翼武器舱
            left_wing = [scale_point(15, 35), scale_point(22, 40), scale_point(25, 45), scale_point(18, 45)]
            right_wing = [scale_point(49, 35), scale_point(42, 40), scale_point(39, 45), scale_point(46, 45)]
            pygame.draw.polygon(screen, colors['wing_color'], left_wing)
            pygame.draw.polygon(screen, colors['wing_color'], right_wing)
            
            # 驾驶舱
            cockpit_rect = pygame.Rect(scale_point(28, 20)[0], scale_point(28, 20)[1], int(8*scale), int(12*scale))
            pygame.draw.ellipse(screen, colors['cockpit_color'], cockpit_rect)
            
            # 推进器
            thruster = [scale_point(28, 50), scale_point(32, 62), scale_point(36, 50)]
            core = [scale_point(30, 52), scale_point(32, 58), scale_point(34, 52)]
            pygame.draw.polygon(screen, colors['engine_color'], thruster)
            pygame.draw.polygon(screen, colors['core_color'], core)
            
        elif ship_type == 'striker':
            # 突击者 - 强壮的重型战舰
            main_body = [scale_point(32, 10), scale_point(20, 20), scale_point(16, 45), 
                        scale_point(24, 52), scale_point(40, 52), scale_point(48, 45), scale_point(44, 20)]
            pygame.draw.polygon(screen, colors['color'], main_body)
            
            # 装甲板
            armor = [scale_point(20, 20), scale_point(25, 15), scale_point(39, 15), 
                    scale_point(44, 20), scale_point(40, 25), scale_point(24, 25)]
            pygame.draw.polygon(screen, colors['wing_color'], armor)
            
            # 双推进器
            left_thruster = [scale_point(22, 52), scale_point(26, 62), scale_point(30, 52)]
            right_thruster = [scale_point(34, 52), scale_point(38, 62), scale_point(42, 52)]
            pygame.draw.polygon(screen, colors['engine_color'], left_thruster)
            pygame.draw.polygon(screen, colors['engine_color'], right_thruster)
            
        elif ship_type == 'phantom':
            # 幻影 - 流线型隐身设计
            main_body = [scale_point(32, 5), scale_point(22, 25), scale_point(20, 45), 
                        scale_point(32, 58), scale_point(44, 45), scale_point(42, 25)]
            pygame.draw.polygon(screen, colors['color'], main_body)
            
            # 能量核心
            core_rect = pygame.Rect(scale_point(28, 28)[0], scale_point(28, 28)[1], int(8*scale), int(8*scale))
            pygame.draw.ellipse(screen, colors['core_color'], core_rect)
            
            # 侧翼
            left_wing = [scale_point(20, 30), scale_point(12, 40), scale_point(20, 45)]
            right_wing = [scale_point(44, 30), scale_point(52, 40), scale_point(44, 45)]
            pygame.draw.polygon(screen, colors['wing_color'], left_wing)
            pygame.draw.polygon(screen, colors['wing_color'], right_wing)
            
        elif ship_type == 'guardian':
            # 守护者 - 厚重防御型
            main_body = [scale_point(32, 8), scale_point(18, 30), scale_point(16, 50), 
                        scale_point(32, 58), scale_point(48, 50), scale_point(46, 30)]
            pygame.draw.polygon(screen, colors['color'], main_body)
            
            # 护盾生成器
            shield_rect = pygame.Rect(scale_point(26, 20)[0], scale_point(26, 20)[1], int(12*scale), int(16*scale))
            pygame.draw.rect(screen, colors['wing_color'], shield_rect)
            
            # 三推进器
            thrusters = [
                [scale_point(20, 50), scale_point(24, 60), scale_point(28, 50)],
                [scale_point(30, 58), scale_point(32, 62), scale_point(34, 58)],
                [scale_point(36, 50), scale_point(40, 60), scale_point(44, 50)]
            ]
            for thruster in thrusters:
                pygame.draw.polygon(screen, colors['engine_color'], thruster)
                
        elif ship_type == 'avenger':
            # 复仇者 - X翼战斗机
            main_body = [scale_point(32, 10), scale_point(28, 48), scale_point(36, 48)]
            pygame.draw.polygon(screen, colors['color'], main_body)
            
            # X型机翼
            wings = [
                [scale_point(16, 20), scale_point(24, 35), scale_point(28, 30), scale_point(20, 15)],  # 左上翼
                [scale_point(48, 20), scale_point(40, 35), scale_point(36, 30), scale_point(44, 15)],  # 右上翼
                [scale_point(20, 48), scale_point(28, 40), scale_point(24, 50), scale_point(16, 55)],  # 左下翼
                [scale_point(44, 48), scale_point(36, 40), scale_point(40, 50), scale_point(48, 55)]   # 右下翼
            ]
            for wing in wings:
                pygame.draw.polygon(screen, colors['wing_color'], wing)
                
        elif ship_type == 'stealth':
            # 隐形舰 - 锯齿状隐身设计
            main_body = [scale_point(32, 8), scale_point(24, 20), scale_point(18, 35), 
                        scale_point(22, 48), scale_point(32, 55), scale_point(42, 48), 
                        scale_point(46, 35), scale_point(40, 20)]
            pygame.draw.polygon(screen, colors['color'], main_body)
            
            # 锯齿边缘
            edges = [
                [scale_point(24, 20), scale_point(20, 15), scale_point(28, 25)],
                [scale_point(40, 20), scale_point(44, 15), scale_point(36, 25)],
                [scale_point(18, 35), scale_point(14, 30), scale_point(22, 40)],
                [scale_point(46, 35), scale_point(50, 30), scale_point(42, 40)]
            ]
            for edge in edges:
                pygame.draw.polygon(screen, colors['wing_color'], edge)
                
    def draw(self, screen):
        # Draw background stars
        for x, y, _ in self.stars:
            pygame.draw.circle(screen, self.WHITE, (int(x), int(y)), 1)
            
        # Draw title with refined glow effect
        # Simpler glow layers
        glow_layers = [
            (3, (40, 80, 160)),
            (2, (60, 120, 200)),
            (1, (80, 140, 230))
        ]
        
        for radius, color in glow_layers:
            for angle in range(0, 360, 90):  # Fewer angles for cleaner look
                offset_x = int(radius * math.cos(math.radians(angle)))
                offset_y = int(radius * math.sin(math.radians(angle)))
                glow_text = self.title_font.render("太空射手", True, color)
                glow_rect = glow_text.get_rect(center=(self.title_rect.centerx + offset_x, self.title_rect.centery + offset_y))
                screen.blit(glow_text, glow_rect)
        
        # Main title
        screen.blit(self.title_text, self.title_rect)
        
        # Draw ship selection title
        screen.blit(self.ship_title_text, self.ship_title_rect)
        
        # Draw ship selection indicators - more refined
        pulse = abs(math.sin(time.time() * 2)) * 0.3 + 0.7  # Subtle pulsing
        arrow_color = (
            max(0, min(255, int(200 + 55 * pulse))),
            max(0, min(255, int(200 + 55 * pulse))),
            max(0, min(255, int(100 + 155 * pulse)))
        )  # More subtle animation
        arrow_size = 20  # Smaller arrows
        
        # Left arrow - closer to preview box
        left_arrow = [(self.preview_rect.left - 50, self.preview_rect.centery),
                     (self.preview_rect.left - 25, self.preview_rect.centery - arrow_size),
                     (self.preview_rect.left - 25, self.preview_rect.centery + arrow_size)]
        
        # Right arrow - closer to preview box
        right_arrow = [(self.preview_rect.right + 50, self.preview_rect.centery),
                      (self.preview_rect.right + 25, self.preview_rect.centery - arrow_size),
                      (self.preview_rect.right + 25, self.preview_rect.centery + arrow_size)]
        
        # Draw subtle arrow glows
        for arrow in [left_arrow, right_arrow]:
            for i in range(2):  # Less glow layers
                glow_arrow = [(x + (1-i)*0.5, y + (1-i)*0.5) for x, y in arrow]
                glow_color = (
                    max(0, min(255, arrow_color[0] // (i+3))),
                    max(0, min(255, arrow_color[1] // (i+3))),
                    max(0, min(255, arrow_color[2] // (i+3)))
                )
                pygame.draw.polygon(screen, glow_color, glow_arrow)
        
        pygame.draw.polygon(screen, arrow_color, left_arrow)
        pygame.draw.polygon(screen, arrow_color, right_arrow)
        
        # Draw ship preview background - more minimal
        # Subtle outer glow
        for i in range(4, 0, -1):
            glow_rect = pygame.Rect(self.preview_rect.x - i, self.preview_rect.y - i,
                                  self.preview_rect.width + 2*i, self.preview_rect.height + 2*i)
            alpha = int(20 * (4-i) / 4)
            glow_color = (0, 120, 200, alpha)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, glow_color, (0, 0, glow_rect.width, glow_rect.height), border_radius=15)
            screen.blit(glow_surface, glow_rect)
        
        # Main background with gradient effect
        pygame.draw.rect(screen, (15, 20, 35), self.preview_rect, border_radius=15)
        pygame.draw.rect(screen, (0, 180, 255), self.preview_rect, 4, border_radius=15)
        
        # Inner highlight
        inner_rect = pygame.Rect(self.preview_rect.x + 6, self.preview_rect.y + 6, 
                               self.preview_rect.width - 12, self.preview_rect.height - 12)
        pygame.draw.rect(screen, (30, 40, 60), inner_rect, 2, border_radius=10)
        
        # Minimal corner accents
        corner_size = 10
        corner_color = (255, 215, 0)  # Gold accents
        corners = [
            (self.preview_rect.x + 8, self.preview_rect.y + 8),
            (self.preview_rect.right - corner_size - 8, self.preview_rect.y + 8),
            (self.preview_rect.x + 8, self.preview_rect.bottom - corner_size - 8),
            (self.preview_rect.right - corner_size - 8, self.preview_rect.bottom - corner_size - 8)
        ]
        for corner in corners:
            pygame.draw.rect(screen, corner_color, (corner[0], corner[1], corner_size, 2))
            pygame.draw.rect(screen, corner_color, (corner[0], corner[1], 2, corner_size))
        
        # Draw ship preview
        self.draw_ship_preview(screen, self.ships[self.current_ship])
        
        # Draw current ship info - name and description on one line
        current_ship = self.ships[self.current_ship]
        ship_name = self.ship_info[current_ship]['name']
        ship_desc = self.ship_info[current_ship]['desc']
        
        # Combined name and description with refined styling
        ship_info_text = f"{ship_name} ({ship_desc})"
        
        # Use smaller Chinese font for ship info to reduce crowding
        try:
            if hasattr(self, 'chinese_font_path') and self.chinese_font_path:
                info_font = pygame.font.Font(self.chinese_font_path, 28)  # Smaller font
            elif hasattr(self, 'chinese_font_name') and self.chinese_font_name:
                info_font = pygame.font.SysFont(self.chinese_font_name, 28)
            else:
                info_font = self.text_font  # Use text font as fallback
        except:
            info_font = self.text_font
            
        info_surface = info_font.render(ship_info_text, True, (255, 255, 255))
        info_rect = info_surface.get_rect(center=(self.width // 2, self.ship_info_y))
        
        # Very subtle glow effect
        for offset in [(1, 1), (-1, -1)]:
            glow_surface = info_font.render(ship_info_text, True, (60, 120, 200))
            glow_rect = glow_surface.get_rect(center=(info_rect.centerx + offset[0], info_rect.centery + offset[1]))
            screen.blit(glow_surface, glow_rect)
        
        screen.blit(info_surface, info_rect)
        
        # Ship index indicator - smaller and more subtle
        index_text = f"{self.current_ship + 1} / {len(self.ships)}"
        try:
            if hasattr(self, 'chinese_font_path') and self.chinese_font_path:
                index_font = pygame.font.Font(self.chinese_font_path, 20)
            elif hasattr(self, 'chinese_font_name') and self.chinese_font_name:
                index_font = pygame.font.SysFont(self.chinese_font_name, 20)
            else:
                index_font = pygame.font.Font(None, 20)
        except:
            index_font = pygame.font.Font(None, 20)
            
        index_surface = index_font.render(index_text, True, (150, 150, 150))  # More subtle gray
        index_rect = index_surface.get_rect(center=(self.width // 2, self.ship_index_y))
        screen.blit(index_surface, index_rect)
        
        # Draw control hints
        screen.blit(self.control_text, self.control_rect)
        
        # Draw start game button
        self.start_button.draw(screen)
        
        # Draw quit button with hover effect
        mouse_pos = pygame.mouse.get_pos()
        if self.quit_button.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (200, 50, 50), self.quit_button, border_radius=5)
        else:
            pygame.draw.rect(screen, (200, 50, 50), self.quit_button, 2, border_radius=5)
        screen.blit(self.quit_text, self.quit_rect)
        
    def handle_event(self, event):
        """处理菜单事件"""
        # 更新按钮悬停状态
        mouse_pos = pygame.mouse.get_pos()
        
        # 更新按钮状态
        self.start_button.update(mouse_pos)
        
        # 处理主菜单事件
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            cprint(f"鼠标点击位置: {event.pos}", "yellow")
            
            if self.start_button.handle_event(event):
                cprint("选择了开始游戏", "green")
                return 'start', self.ships[self.current_ship]
            elif self.quit_button.collidepoint(event.pos):
                cprint("选择了退出游戏", "red")
                return 'quit', None
                
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.current_ship = (self.current_ship - 1) % len(self.ships)
            elif event.key == pygame.K_RIGHT:
                self.current_ship = (self.current_ship + 1) % len(self.ships)
            elif event.key == pygame.K_SPACE:
                return 'start', self.ships[self.current_ship]
                
        return None, None
