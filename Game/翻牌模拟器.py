import pygame
import random
import sys
import time
import json
import os
from pygame import mixer

# 初始化pygame
pygame.init()
mixer.init()

# 游戏常量
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
CARD_WIDTH = 120
CARD_HEIGHT = 140
MARGIN = 15
BACKGROUND_COLOR = (30, 30, 40)
CARD_BACK_COLOR = (60, 60, 70)
CARD_FRONT_COLOR = (240, 240, 240)
ACCENT_COLOR = (255, 255, 255)
SUCCESS_COLOR = (100, 180, 100)
TEXT_COLOR = (30, 30, 40)
BUTTON_COLOR = (80, 80, 90)
BUTTON_HOVER_COLOR = (120, 120, 130)

# 关卡配置
LEVELS = [
    {"name": "初级", "rows": 3, "cols": 4, "time_limit": 120},
    {"name": "中级", "rows": 4, "cols": 5, "time_limit": 180},
    {"name": "高级", "rows": 4, "cols": 6, "time_limit": 240},
    {"name": "专家", "rows": 5, "cols": 6, "time_limit": 300}
]

# 单词数据库
WORD_DATABASE = [
    # 初级单词
    [("apple", "苹果"), ("book", "书"), ("cat", "猫"), ("dog", "狗"), 
     ("egg", "鸡蛋"), ("fish", "鱼"), ("goat", "山羊"), ("house", "房子")],
    
    # 中级单词  
    [("abandon", "放弃"), ("benevolent", "仁慈的"), ("courage", "勇气"), ("diligent", "勤奋的"),
     ("eloquent", "雄辩的"), ("fragile", "易碎的"), ("gratitude", "感激"), ("harmony", "和谐"),
     ("illustrious", "著名的"), ("juvenile", "青少年的")],
     
    # 高级单词
    [("ambivalent", "矛盾的"), ("benevolence", "仁慈"), ("cacophony", "刺耳的声音"), ("deleterious", "有害的"),
     ("ephemeral", "短暂的"), ("fastidious", "挑剔的"), ("gregarious", "社交的"), ("hierarchy", "等级制度"),
     ("idiosyncrasy", "特质"), ("juxtaposition", "并列"), ("kaleidoscope", "万花筒"), ("labyrinth", "迷宫")],
     
    # 专家单词
    [("aberration", "异常"), ("bombastic", "夸夸其谈的"), ("cognizant", "认知的"), ("dichotomy", "二分法"),
     ("ebullient", "热情洋溢的"), ("facetious", "滑稽的"), ("garrulous", "喋喋不休的"), ("hegemony", "霸权"),
     ("iconoclast", "反传统者"), ("jettison", "抛弃"), ("kowtow", "叩头"), ("laconic", "简洁的"),
     ("magnanimous", "宽宏大量的"), ("nefarious", "邪恶的"), ("obfuscate", "使困惑"), ("paradigm", "范例")]
]

# 创建屏幕
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("单词闪卡记忆游戏 - 高级版")

# 加载字体
try:
    title_font = pygame.font.Font("simhei.ttf", 48)
    header_font = pygame.font.Font("simhei.ttf", 36)
    normal_font = pygame.font.Font("simhei.ttf", 24)
    small_font = pygame.font.Font("simhei.ttf", 20)
except:
    title_font = pygame.font.SysFont('simhei', 48)
    header_font = pygame.font.SysFont('simhei', 36)
    normal_font = pygame.font.SysFont('simhei', 24)
    small_font = pygame.font.SysFont('simhei', 20)

# 尝试加载音效
try:
    flip_sound = mixer.Sound("flip.wav")
    match_sound = mixer.Sound("match.wav")
    win_sound = mixer.Sound("win.wav")
    has_sound = True
except:
    has_sound = False
    print("音效文件未找到，游戏将以静音模式运行")

# 粒子效果类
class Particle:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.x = random.uniform(0, SCREEN_WIDTH)
        self.y = random.uniform(0, SCREEN_HEIGHT)
        self.radius = random.uniform(1, 3)
        self.speed_x = random.uniform(-0.5, 0.5)
        self.speed_y = random.uniform(-0.5, 0.5)
        self.alpha = random.randint(20, 60)
        self.color = (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255))
    
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        
        # 如果粒子移出屏幕，重置它
        if self.x < -10 or self.x > SCREEN_WIDTH + 10 or self.y < -10 or self.y > SCREEN_HEIGHT + 10:
            self.reset()
    
    def draw(self, surface):
        s = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, self.alpha), (self.radius, self.radius), self.radius)
        surface.blit(s, (self.x, self.y))

class Card:
    def __init__(self, word_pair, index, level):
        self.word_pair = word_pair
        self.index = index
        self.level = level
        self.rect = pygame.Rect(0, 0, CARD_WIDTH, CARD_HEIGHT)
        self.matched = False
        self.face_up = False
        self.flip_angle = 0  # 0-180度，翻牌动画
        self.flipping = False
    
    def update(self):
        if self.flipping:
            self.flip_angle += 15
            if self.flip_angle >= 180:
                self.flip_angle = 0
                self.face_up = not self.face_up
                self.flipping = False
    
    def flip(self):
        if not self.matched and not self.flipping:
            self.flipping = True
            if has_sound:
                flip_sound.play()
    
    def draw(self):
        rows = LEVELS[self.level]["rows"]
        cols = LEVELS[self.level]["cols"]
        
        # 计算卡片位置
        x = self.index % cols
        y = self.index // cols
        
        total_width = cols * CARD_WIDTH + (cols - 1) * MARGIN
        total_height = rows * CARD_HEIGHT + (rows - 1) * MARGIN
        
        start_x = (SCREEN_WIDTH - total_width) // 2
        start_y = 150 + (SCREEN_HEIGHT - 150 - total_height) // 2
        
        self.rect.x = start_x + x * (CARD_WIDTH + MARGIN)
        self.rect.y = start_y + y * (CARD_HEIGHT + MARGIN)
        
        # 绘制卡片（带翻牌动画）
        if self.flipping:
            # 翻牌动画
            if self.flip_angle < 90:
                # 前半段：显示背面
                scale_factor = abs(pygame.math.Vector2(1, 1).rotate(self.flip_angle).x)
                width = int(CARD_WIDTH * scale_factor)
                if width > 0:
                    card_rect = pygame.Rect(self.rect.centerx - width//2, self.rect.y, width, CARD_HEIGHT)
                    pygame.draw.rect(screen, CARD_BACK_COLOR, card_rect, border_radius=10)
                    pygame.draw.rect(screen, ACCENT_COLOR, card_rect, 2, border_radius=10)
                    
                    # 绘制问号
                    question = header_font.render("?", True, (220, 220, 220))
                    question_rect = question.get_rect(center=card_rect.center)
                    screen.blit(question, question_rect)
            else:
                # 后半段：显示正面
                scale_factor = abs(pygame.math.Vector2(1, 1).rotate(180 - self.flip_angle).x)
                width = int(CARD_WIDTH * scale_factor)
                if width > 0:
                    card_rect = pygame.Rect(self.rect.centerx - width//2, self.rect.y, width, CARD_HEIGHT)
                    color = SUCCESS_COLOR if self.matched else CARD_FRONT_COLOR
                    pygame.draw.rect(screen, color, card_rect, border_radius=10)
                    pygame.draw.rect(screen, ACCENT_COLOR, card_rect, 2, border_radius=10)
                    
                    # 绘制单词
                    if width > CARD_WIDTH * 0.7:  # 当卡片足够宽时显示文字
                        text_en = normal_font.render(self.word_pair[0], True, TEXT_COLOR)
                        text_cn = normal_font.render(self.word_pair[1], True, TEXT_COLOR)
                        
                        text_en_rect = text_en.get_rect(center=(card_rect.centerx, card_rect.centery - 15))
                        text_cn_rect = text_cn.get_rect(center=(card_rect.centerx, card_rect.centery + 15))
                        
                        screen.blit(text_en, text_en_rect)
                        screen.blit(text_cn, text_cn_rect)
        else:
            # 静态卡片
            color = SUCCESS_COLOR if self.matched else (CARD_FRONT_COLOR if self.face_up else CARD_BACK_COLOR)
            pygame.draw.rect(screen, color, self.rect, border_radius=10)
            pygame.draw.rect(screen, ACCENT_COLOR, self.rect, 2, border_radius=10)
            
            if self.face_up:
                # 英文单词
                text_en = normal_font.render(self.word_pair[0], True, TEXT_COLOR)
                text_en_rect = text_en.get_rect(center=(self.rect.centerx, self.rect.centery - 15))
                screen.blit(text_en, text_en_rect)
                
                # 中文翻译
                text_cn = normal_font.render(self.word_pair[1], True, TEXT_COLOR)
                text_cn_rect = text_cn.get_rect(center=(self.rect.centerx, self.rect.centery + 15))
                screen.blit(text_cn, text_cn_rect)
            elif not self.matched:
                # 绘制问号
                question = header_font.render("?", True, (220, 220, 220))
                question_rect = question.get_rect(center=self.rect.center)
                screen.blit(question, question_rect)

class Button:
    def __init__(self, x, y, width, height, text, color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
    
    def draw(self):
        # 绘制阴影
        shadow_rect = self.rect.copy()
        shadow_rect.y += 4
        pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=8)
        
        # 绘制按钮
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, ACCENT_COLOR, self.rect, 2, border_radius=8)
        
        text_surf = normal_font.render(self.text, True, ACCENT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
    
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
    
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class Game:
    def __init__(self):
        self.state = "menu"  # menu, playing, game_over, leaderboard
        self.level = 0
        self.cards = []
        self.selected_cards = []
        self.moves = 0
        self.matches = 0
        self.start_time = 0
        self.time_limit = 0
        self.remaining_time = 0
        self.score = 0
        self.player_name = ""
        self.leaderboard = self.load_leaderboard()
        self.particles = [Particle() for _ in range(100)]
        
        # 创建按钮
        button_width, button_height = 220, 50
        center_x = SCREEN_WIDTH // 2 - button_width // 2
        
        self.level_buttons = []
        for i, level in enumerate(LEVELS):
            self.level_buttons.append(Button(center_x, 220 + i * 100, button_width, button_height, 
                                            f"{level['name']}关卡"))
        
        self.menu_button = Button(center_x, 550, button_width, button_height, "返回主菜单")
        self.leaderboard_button = Button(center_x, 480, button_width, button_height, "排行榜")
        self.restart_button = Button(center_x, 550, button_width, button_height, "重新开始")
    
    def draw_gradient_background(self):
        # 绘制黑白渐变背景
        for y in range(SCREEN_HEIGHT):
            gray = int(30 + (y / SCREEN_HEIGHT) * 70)  # 从30到100的灰度
            pygame.draw.line(screen, (gray, gray, gray), (0, y), (SCREEN_WIDTH, y))
    
    def update_particles(self):
        for particle in self.particles:
            particle.update()
    
    def draw_particles(self):
        for particle in self.particles:
            particle.draw(screen)
    
    def load_leaderboard(self):
        try:
            with open("leaderboard.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {str(i): [] for i in range(len(LEVELS))}
    
    def save_leaderboard(self):
        with open("leaderboard.json", "w", encoding="utf-8") as f:
            json.dump(self.leaderboard, f, ensure_ascii=False, indent=2)
    
    def add_to_leaderboard(self):
        level_key = str(self.level)
        if level_key not in self.leaderboard:
            self.leaderboard[level_key] = []
        
        # 添加新记录
        self.leaderboard[level_key].append({
            "name": self.player_name,
            "score": self.score,
            "time": int(time.time() - self.start_time),
            "moves": self.moves,
            "date": time.strftime("%Y-%m-%d %H:%M")
        })
        
        # 排序并保留前10名
        self.leaderboard[level_key].sort(key=lambda x: x["score"], reverse=True)
        self.leaderboard[level_key] = self.leaderboard[level_key][:10]
        
        self.save_leaderboard()
    
    def start_game(self, level):
        self.level = level
        self.state = "playing"
        self.cards = []
        self.selected_cards = []
        self.moves = 0
        self.matches = 0
        self.start_time = time.time()
        self.time_limit = LEVELS[level]["time_limit"]
        
        # 获取当前级别的单词
        level_words = WORD_DATABASE[level]
        rows = LEVELS[level]["rows"]
        cols = LEVELS[level]["cols"]
        total_cards = rows * cols
        
        # 确保有足够的单词
        if len(level_words) < total_cards // 2:
            # 如果单词不够，重复使用一些单词
            needed_pairs = total_cards // 2
            word_pairs = []
            while len(word_pairs) < needed_pairs:
                word_pairs.extend(level_words)
            word_pairs = word_pairs[:needed_pairs]
        else:
            word_pairs = random.sample(level_words, total_cards // 2)
        
        # 创建卡片列表（每对单词有两张卡片）
        word_list = []
        for pair in word_pairs:
            word_list.append(pair)
            word_list.append(pair)
        
        # 打乱卡片顺序
        random.shuffle(word_list)
        
        # 创建卡片对象
        for i, word_pair in enumerate(word_list):
            self.cards.append(Card(word_pair, i, level))
    
    def update(self):
        if self.state == "playing":
            # 更新剩余时间
            self.remaining_time = max(0, self.time_limit - (time.time() - self.start_time))
            
            # 检查时间是否用完
            if self.remaining_time <= 0:
                self.state = "game_over"
                self.player_name = "玩家"  # 默认玩家名
            
            # 更新所有卡片
            for card in self.cards:
                card.update()
            
            # 检查是否所有卡片都已匹配
            if all(card.matched for card in self.cards):
                self.state = "game_over"
                # 计算得分 (时间分数 + 移动效率分数)
                time_used = time.time() - self.start_time
                time_bonus = max(0, self.time_limit - time_used) * 10
                move_penalty = max(0, self.moves - len(self.cards)//2) * 5
                self.score = int(1000 + time_bonus - move_penalty)
                
                if has_sound:
                    win_sound.play()
    
    def handle_click(self, pos, event):
        if self.state == "menu":
            for i, button in enumerate(self.level_buttons):
                if button.is_clicked(pos, event):
                    self.start_game(i)
                    return
            
            if self.leaderboard_button.is_clicked(pos, event):
                self.state = "leaderboard"
        
        elif self.state == "playing":
            for card in self.cards:
                if card.rect.collidepoint(pos) and not card.matched and not card.flipping:
                    # 如果已经选择了两张卡片，先翻回去
                    if len(self.selected_cards) == 2:
                        for c in self.selected_cards:
                            c.flip()
                        self.selected_cards = []
                    
                    # 翻开卡片
                    card.flip()
                    self.selected_cards.append(card)
                    
                    # 如果选择了两张卡片，检查是否匹配
                    if len(self.selected_cards) == 2:
                        self.moves += 1
                        if self.selected_cards[0].word_pair == self.selected_cards[1].word_pair:
                            # 匹配成功
                            for c in self.selected_cards:
                                c.matched = True
                            self.matches += 1
                            self.selected_cards = []
                            
                            if has_sound:
                                match_sound.play()
                        else:
                            # 不匹配，稍后翻回去
                            pygame.time.set_timer(pygame.USEREVENT, 1000, 1)
                    
                    break
        
        elif self.state == "game_over":
            if self.restart_button.is_clicked(pos, event):
                self.state = "menu"
            elif self.leaderboard_button.is_clicked(pos, event):
                self.add_to_leaderboard()
                self.state = "leaderboard"
        
        elif self.state == "leaderboard":
            if self.menu_button.is_clicked(pos, event):
                self.state = "menu"
    
    def draw(self):
        # 绘制渐变背景
        self.draw_gradient_background()
        
        # 绘制粒子效果
        if self.state == "menu":
            self.draw_particles()
        
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "playing":
            self.draw_game()
        elif self.state == "game_over":
            self.draw_game_over()
        elif self.state == "leaderboard":
            self.draw_leaderboard()
        
        # 绘制鼠标悬停效果
        mouse_pos = pygame.mouse.get_pos()
        if self.state == "menu":
            for button in self.level_buttons:
                button.check_hover(mouse_pos)
            self.leaderboard_button.check_hover(mouse_pos)
        elif self.state == "game_over":
            self.restart_button.check_hover(mouse_pos)
            self.leaderboard_button.check_hover(mouse_pos)
        elif self.state == "leaderboard":
            self.menu_button.check_hover(mouse_pos)
    
    def draw_menu(self):
        # 标题
        title = title_font.render("单词闪卡记忆游戏", True, ACCENT_COLOR)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 60))
        
        subtitle = header_font.render("选择关卡开始游戏", True, (200, 200, 200))
        screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 130))
        
        # 绘制关卡按钮
        for i, button in enumerate(self.level_buttons):
            level_info = LEVELS[i]
            button.draw()
            
            # 显示关卡信息
            info_text = small_font.render(f"{level_info['rows']}x{level_info['cols']}卡片 | 时间限制: {level_info['time_limit']}秒", 
                                         True, (200, 200, 200))
            screen.blit(info_text, (SCREEN_WIDTH//2 - info_text.get_width()//2, button.rect.y + 55))
        
        # 绘制排行榜按钮
        self.leaderboard_button.rect.centerx = SCREEN_WIDTH // 2
        self.leaderboard_button.rect.y = SCREEN_HEIGHT - 80
        self.leaderboard_button.draw()
    
    def draw_game(self):
        # 标题
        level_name = LEVELS[self.level]["name"]
        title = header_font.render(f"{level_name}关卡", True, ACCENT_COLOR)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 30))
        
        # 游戏信息
        info_text = normal_font.render(f"移动次数: {self.moves} | 匹配对数: {self.matches}/{len(self.cards)//2}", True, (200, 200, 200))
        screen.blit(info_text, (SCREEN_WIDTH//2 - info_text.get_width()//2, 80))
        
        # 时间条
        time_ratio = self.remaining_time / self.time_limit
        time_bar_width = 400
        time_bar_rect = pygame.Rect(SCREEN_WIDTH//2 - time_bar_width//2, 110, time_bar_width, 20)
        pygame.draw.rect(screen, (100, 100, 100), time_bar_rect, border_radius=10)
        
        if time_ratio > 0:
            time_fill_rect = pygame.Rect(time_bar_rect.x, time_bar_rect.y, 
                                        int(time_bar_width * time_ratio), time_bar_rect.height)
            color = (100, 200, 100) if time_ratio > 0.3 else (200, 100, 100)
            pygame.draw.rect(screen, color, time_fill_rect, border_radius=10)
        
        time_text = small_font.render(f"剩余时间: {int(self.remaining_time)}秒", True, (255, 255, 255))
        screen.blit(time_text, (SCREEN_WIDTH//2 - time_text.get_width()//2, 115))
        
        # 绘制所有卡片
        for card in self.cards:
            card.draw()
    
    def draw_game_over(self):
        # 半透明覆盖层
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # 游戏结果
        if self.remaining_time > 0:
            result_text = title_font.render("恭喜你完成了所有匹配！", True, SUCCESS_COLOR)
            score_text = header_font.render(f"得分: {self.score}", True, ACCENT_COLOR)
        else:
            result_text = title_font.render("时间到！游戏结束", True, (255, 100, 100))
            score_text = header_font.render(f"匹配对数: {self.matches}/{len(self.cards)//2}", True, ACCENT_COLOR)
        
        screen.blit(result_text, (SCREEN_WIDTH//2 - result_text.get_width()//2, 200))
        screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 270))
        
        # 统计信息
        time_used = int(time.time() - self.start_time)
        stats_text = normal_font.render(f"用时: {time_used}秒 | 移动次数: {self.moves}", True, (255, 255, 255))
        screen.blit(stats_text, (SCREEN_WIDTH//2 - stats_text.get_width()//2, 320))
        
        # 按钮
        self.restart_button.draw()
        self.leaderboard_button.draw()
    
    def draw_leaderboard(self):
        # 标题
        title = title_font.render("排行榜", True, ACCENT_COLOR)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 30))
        
        # 选项卡（选择不同关卡）
        tab_width = 200
        for i, level in enumerate(LEVELS):
            tab_rect = pygame.Rect(SCREEN_WIDTH//2 - (len(LEVELS)*tab_width)//2 + i*tab_width, 100, tab_width, 40)
            color = ACCENT_COLOR if i == self.level else BUTTON_COLOR
            pygame.draw.rect(screen, color, tab_rect, border_radius=5)
            pygame.draw.rect(screen, (255, 255, 255), tab_rect, 2, border_radius=5)
            
            tab_text = small_font.render(level["name"], True, (255, 255, 255))
            screen.blit(tab_text, (tab_rect.centerx - tab_text.get_width()//2, 
                                 tab_rect.centery - tab_text.get_height()//2))
            
            # 检查选项卡点击
            mouse_pos = pygame.mouse.get_pos()
            if pygame.mouse.get_pressed()[0] and tab_rect.collidepoint(mouse_pos):
                self.level = i
        
        # 排行榜内容
        level_key = str(self.level)
        if level_key in self.leaderboard and self.leaderboard[level_key]:
            records = self.leaderboard[level_key]
            
            # 表头
            headers = ["排名", "玩家", "得分", "用时", "移动", "日期"]
            header_height = 40
            content_start_y = 160
            
            for i, header in enumerate(headers):
                x = 150 + i * 150
                header_text = normal_font.render(header, True, ACCENT_COLOR)
                screen.blit(header_text, (x, content_start_y - 30))
            
            # 记录
            for i, record in enumerate(records):
                y = content_start_y + i * 40
                color = (255, 255, 255) if i % 2 == 0 else (200, 200, 200)
                
                # 排名
                rank_text = normal_font.render(str(i+1), True, color)
                screen.blit(rank_text, (150, y))
                
                # 玩家名
                name_text = normal_font.render(record["name"], True, color)
                screen.blit(name_text, (300, y))
                
                # 得分
                score_text = normal_font.render(str(record["score"]), True, color)
                screen.blit(score_text, (450, y))
                
                # 用时
                time_text = normal_font.render(f"{record['time']}秒", True, color)
                screen.blit(time_text, (600, y))
                
                # 移动次数
                moves_text = normal_font.render(str(record["moves"]), True, color)
                screen.blit(moves_text, (750, y))
                
                # 日期
                date_text = small_font.render(record["date"], True, color)
                screen.blit(date_text, (900 - date_text.get_width(), y))
        else:
            # 无记录提示
            no_data_text = header_font.render("暂无记录，快来挑战吧！", True, (200, 200, 200))
            screen.blit(no_data_text, (SCREEN_WIDTH//2 - no_data_text.get_width()//2, 300))
        
        # 返回按钮
        self.menu_button.draw()

def main():
    game = Game()
    clock = pygame.time.Clock()
    
    # 自定义事件：翻回不匹配的卡片
    pygame.time.set_timer(pygame.USEREVENT, 100)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.USEREVENT:
                # 翻回不匹配的卡片
                if game.state == "playing" and len(game.selected_cards) == 2:
                    for card in game.selected_cards:
                        card.flip()
                    game.selected_cards = []
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键点击
                    game.handle_click(event.pos, event)
        
        # 更新粒子效果
        game.update_particles()
        
        game.update()
        game.draw()
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()