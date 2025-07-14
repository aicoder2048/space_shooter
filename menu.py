import os
import pygame
import random
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
                font = pygame.font.Font(font_path, font_size)
                test_surface = font.render('中文测试', True, (255, 255, 255))
                if test_surface.get_width() > 0:
                    return font
            except:
                continue
        
        # Try system fonts as fallback
        system_fonts = ['STHeiti', 'Hiragino Sans GB', 'Arial Unicode MS']
        for font_name in system_fonts:
            try:
                font = pygame.font.SysFont(font_name, font_size)
                test_surface = font.render('中文测试', True, (255, 255, 255))
                if test_surface.get_width() > 0:
                    return font
            except:
                continue
        
        # Fallback to default font
        return pygame.font.Font(None, font_size)
        
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
                title_font = pygame.font.Font(font_path, 84)
                text_font = pygame.font.Font(font_path, 36)
                button_font = pygame.font.Font(font_path, 48)
                
                # Test if the font can render Chinese characters
                test_surface = text_font.render('中文测试', True, (255, 255, 255))
                if test_surface.get_width() > 0:
                    font_name = font_path.split('/')[-1]
                    cprint(f"菜单成功加载中文字体: {font_name}", "green")
                    return title_font, text_font, button_font
            except Exception as e:
                cprint(f"无法加载字体 {font_path}: {e}", "yellow")
                continue
        
        # Try system fonts as fallback
        system_fonts = ['STHeiti', 'Hiragino Sans GB', 'Arial Unicode MS']
        for font_name in system_fonts:
            try:
                title_font = pygame.font.SysFont(font_name, 84)
                text_font = pygame.font.SysFont(font_name, 36)
                button_font = pygame.font.SysFont(font_name, 48)
                
                test_surface = text_font.render('中文测试', True, (255, 255, 255))
                if test_surface.get_width() > 0:
                    cprint(f"菜单成功加载系统字体: {font_name}", "green")
                    return title_font, text_font, button_font
            except:
                continue
        
        # If no Chinese font works, use default font
        cprint("菜单警告：无法加载中文字体，使用默认字体。中文可能显示为方块。", "yellow")
        return pygame.font.Font(None, 84), pygame.font.Font(None, 36), pygame.font.Font(None, 48)
    
    def init_ui_elements(self):
        """Initialize UI elements after fonts are loaded"""
        # Title text
        self.title_text = self.title_font.render("太空射手", True, self.BLUE)
        self.title_rect = self.title_text.get_rect(center=(self.width // 2, self.height // 4))
        
        # Ship selection text
        self.ship_text = self.text_font.render("选择飞船:", True, self.GREEN)
        self.ship_rect = self.ship_text.get_rect(center=(self.width // 2, self.height // 2 - 50))
        
        # Control hints
        self.control_text = self.text_font.render("← →", True, self.GREEN)
        self.control_rect = self.control_text.get_rect(center=(self.width // 2, self.height // 2))
        
        # Start game button
        button_width = 300
        button_height = 60
        
        self.start_button = Button(self.width // 2 - button_width // 2, 
                                 self.height * 3 // 4,
                                 button_width, button_height, 
                                 "开始游戏", 36)
        
        # Quit button
        self.quit_text = self.text_font.render("退出", True, self.WHITE)
        self.quit_rect = self.quit_text.get_rect(center=(self.width - 60, self.height - 40))
        self.quit_button = pygame.Rect(self.quit_rect.x - 10,
                                     self.quit_rect.y - 5,
                                     self.quit_rect.width + 20,
                                     self.quit_rect.height + 10)
        
        # Ship names (添加中文名称)
        self.ship_names = {
            'interceptor': '拦截机',
            'striker': '突击者',
            'phantom': '幻影',
            'guardian': '守护者',
            'avenger': '复仇者',
            'stealth': '隐形舰'
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
                
    def draw(self, screen):
        # Draw background stars
        for x, y, _ in self.stars:
            pygame.draw.circle(screen, self.WHITE, (int(x), int(y)), 1)
            
        # Draw title with glow effect
        glow_surface = pygame.Surface((self.title_rect.width + 20, self.title_rect.height + 20), pygame.SRCALPHA)
        glow_text = self.title_font.render("太空射手", True, (100, 149, 237, 128))
        glow_rect = glow_text.get_rect(center=(glow_surface.get_width() // 2, glow_surface.get_height() // 2))
        glow_surface.blit(glow_text, glow_rect)
        screen.blit(glow_surface, (self.title_rect.x - 10, self.title_rect.y - 10))
        screen.blit(self.title_text, self.title_rect)
        
        # Draw ship selection text with current ship name
        current_ship_name = self.ship_names[self.ships[self.current_ship]]
        ship_text = self.text_font.render(f"选择飞船: {current_ship_name}", True, self.GREEN)
        ship_rect = ship_text.get_rect(center=(self.width // 2, self.height // 2 - 50))
        screen.blit(ship_text, ship_rect)
        
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
        
        # Draw current ship preview (placeholder)
        ship_preview_rect = pygame.Rect(self.width // 2 - 30, self.height // 2 - 30, 60, 60)
        pygame.draw.circle(screen, self.BLUE, ship_preview_rect.center, 30, 2)
        
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
