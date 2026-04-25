import pygame as pg
import json
import tkinter as tk
import threading
import time
import zipfile
import os
import shutil
import input_box
import random
from copy import *
from math import *
import train as nn
from torch.utils.data import DataLoader, TensorDataset, random_split
import torch
from PIL import Image, ImageDraw, ImageEnhance
import sys
import numpy as np
import psutil
import io

# INIT
SCREEN_SIZE = (1024, 768)
COLORS = {
    'background': (40, 40, 40),
    'button': (70, 70, 70),
    'text': (255, 255, 255),
    'highlight': (100, 100, 100),
    'success': (0, 200, 0),
    'explain': (0, 127, 255),
    'error' : "#FF0000",
    'correct': "#00FF00",
    'warning' : "#FFFF00",#tkinter不支持元组rgb？？？
}

ICONS = {
    "search" : ["./icon/search_default.png", "./icon/search.png"],
    "perfect": "./icon/perfect_default.png",
    "good" : "./icon/good_default.png",
    "team_logo" : ["./icon/@me_default.png","./icon/@me.png"],
    "icon" : "./icon/icon.png"
}

class PygameMenu:
    def __init__(self, items, font_path=None):
        self.items = items
        self.buttons = []
        self.times = [False]*len(items)
        
        # 初始化字体系统
        pg.font.init()
        
        try:
            if font_path and os.path.exists(font_path):
                self.font = pg.font.Font(font_path, 24)
            else:
                self.font = pg.font.SysFont(None, 24)
        except:
            self.font = pg.font.SysFont(None, 24)
            
        self._create_buttons()
    
    def _create_buttons(self):
        button_width = 200
        button_height = 40
        start_y = 100
        for i, (text, _, explain_) in enumerate(self.items):
            rect = pg.Rect(
                SCREEN_SIZE[0] - button_width - 20,
                start_y + i*(button_height+10),
                button_width,
                button_height
            )
            self.buttons.append((rect, text, explain_))
    
    def draw(self, surface):
        for i, (rect, text, explain_) in enumerate(self.buttons):
            color = COLORS['button']
            if rect.collidepoint(pg.mouse.get_pos()):
                color = COLORS['highlight']
            pg.draw.rect(surface, color, rect, border_radius=3)
            text_surf = self.font.render(text, True, COLORS['text'])
            surface.blit(text_surf, (rect.x+10, rect.y+10))

        for i, (rect, text, explain_) in enumerate(self.buttons):
            if self.times[i]:
                explain_rect = pg.Rect(
                    rect.x - 300,
                    rect.y - 50,
                    300,
                    60
                )
                explain_surface = pg.Surface((explain_rect.width, explain_rect.height), pg.SRCALPHA)
                
                explain_color_rgb = pg.Color(COLORS['explain'])
                
                explain_color_rgb.a = 70
                explain_surface.fill(explain_color_rgb)
                surface.blit(explain_surface, explain_rect.topleft)
                
                explain_surf = self.font.render(explain_, True, COLORS['text'])
                surface.blit(explain_surf, (explain_rect.x+10, explain_rect.y+10))
    
    def handle_click(self, pos):
        for i, (rect, text, a) in enumerate(self.buttons):
            if rect.collidepoint(pos):
                return self.items[i][1]
        return None
    
    def explains_click(self, pos):
        for i, (rect, text, explain_) in enumerate(self.buttons):
            if rect.collidepoint(pos):
                self.times[i] = True
            else:
                self.times[i] = False
    
class Pygamelog():
    def __init__(self, screen, logs, x, y, height = 24, lenght=5, font_path=None):
        pg.font.init()
        self.buttons = []

        if len(logs) > lenght:
            infos = logs[-lenght:] 
        else:
            infos = logs

        for i, info in enumerate(infos):
            self.draw_info(info, screen, x, y+i*height, font_path)

        self.draw_buttons(screen)

    def _create_buttons(self,x,y,text,height,text_,color):
        button_width = 120
        rect = pg.Rect(
            x,
            y,
            button_width,
            height
        )
        self.buttons.append((rect, text,text_,color))

    def draw_info(self, content, screen, x, y ,font_path=None):
        
        try:
            if font_path and os.path.exists(font_path):
                self.font = pg.font.Font(font_path, content['size'])
            else:
                self.font = pg.font.SysFont(None, content['size'])
        except:
            self.font = pg.font.SysFont(None, content['size'])
        
        t = content['text']
        if len(content['text']) * content['size'] > screen.get_width() - x - 100:
            t = content['text'][:int(screen.get_width() - x - 150)//content['size']]+"..."

            self._create_buttons(screen.get_width() - 130, y-5, "查看详情", content['size']+10, content['text'], content['type'])
        
        text_surf = self.font.render(t, True, COLORS[content['type']])
        screen.blit(text_surf, (x, y))

    def draw_buttons(self, screen):
        for rect, text, text_, color in self.buttons:
            color = COLORS['button']
            if rect.collidepoint(pg.mouse.get_pos()):
                color = COLORS['highlight']
            pg.draw.rect(screen, color, rect)
            text_surf = self.font.render(text, True, COLORS['text'])
            screen.blit(text_surf, (rect.x+10, rect.y))

    def handle_click(self, pos):
        for i, (rect, text, text_, color) in enumerate(self.buttons):#i,text都是凑数字的bushi） 懒得改了
            if rect.collidepoint(pos):
                return (text_,color)
        return None

class DrawingApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()

        pg.init()
        pg.font.init()
        
        with open("./index/screen_config.json", "r") as f:
            self.screen_config = json.load(f)

        if self.screen_config['default_screen'] != "True":
            for color in list(COLORS.keys())[:-3]:
                COLORS[color] = (255-COLORS[color][0], 255-COLORS[color][1], 255-COLORS[color][2])

        if self.screen_config['default_screen'] != "True":
            COLORS['correct'] = "#00AF00"
            COLORS['error'] = "#AF0000"
            COLORS['warning'] = "#AFAF00"
        else:
            COLORS['correct'] = "#00FF00"
            COLORS['error'] = "#FF0000"
            COLORS['warning'] = "#FFFF00"

        self.screen = pg.display.set_mode(SCREEN_SIZE)
#-------------------------------------------------------
        with open("./index/save_data/config.json", "r") as f:
            self.config = json.load(f)
        if 'language' not in self.config:
            self.config['language'] = 'zh'
            self._config_('language', 'zh')
        self.lang = {}
        with open(f"./index/lang/{self.config['language']}.json", "r", encoding='utf-8') as f:
            self.lang = json.load(f)
        self.loading_text(self.lang["loading_config"], 0.2)
#-------------------------------------------------------
        pg.display.set_caption(self.lang["app_title"])
        pg.display.set_icon(pg.image.load("./icon/icon.png"))
        self.clock = pg.time.Clock()
#-------------------------------------------------------
        self.loading_text(self.lang["loading_components"], 0.5)
        self._clear_directory("training_data")
        self._clear_directory("models")
        self._clear_directory("log")
        self._clear_directory("index/%temp%")
#-------------------------------------------------------
        self.logs_info = [] # [{'type','size','text'}]
#-------------------------------------------------------
        self.loading_text(self.lang["loading_model"], 0.8)
        try:
            self._load_model_with_progress(self.config["model_path"])
        except Exception as er:
            self.create_info('error', 24, self.lang["model_load_failed"].format(model_path=self.config["model_path"]))
            self._config_('model_path', './index/save_data/default_model.zip')
            self._load_model_with_progress(self.config["model_path"])

        open("./training_data/data.zip" ,"w")

        #重命名文件夹
        #os.rename(f"./models/{os.path.basename(self.config['model_path']).split('.')[0]}", "./models/models")
#-------------------------------------------------------
        self.board = [[0.0 for _ in range(32)] for _ in range(32)]
        self.screen_page = 'main'
        
        font_path = "font/1.ttc"
        self.menu = PygameMenu([
            (self.lang["clear_board"], self.clear_board, self.lang["clear_board_explain"]),
            (self.lang["save_data"], self.save, self.lang["save_data_explain"]),
            (self.lang["train_model"], self.trainer, self.lang["train_model_explain"]),
            (self.lang["show_log"], self.show_log, self.lang["show_log_explain"]),
            (self.lang["manage_model"], self.manage_model, self.lang["manage_model_explain"]),
            (self.lang["more_setting"], self.more_setting, self.lang["more_setting_explain"]),
            (self.lang["quit_system"], self.quit, self.lang["quit_system_explain"])
        ], font_path=font_path)

        self.menu2 = PygameMenu([
            (self.lang["switch_theme"], self.change_color, self.lang["switch_theme_explain"]),
            (self.lang["test_model"],self.test_model, self.lang["test_model_explain"]),
            (self.lang["switch_language"], self.switch_language, self.lang["switch_language_explain"]),
            (self.lang["previous_page"], self.more_setting, self.lang["previous_page_explain"]),
            (self.lang["back"], self.page_back, self.lang["back_explain"])
        ], font_path=font_path)

        self.menu3 = PygameMenu([
            (self.lang["back"], self.page_back, self.lang["back_explain"])
        ], font_path=font_path)

        self.menu4 = PygameMenu([
            (self.lang["select_model"], self.select_model, self.lang["select_model_explain"]),
            (self.lang["delete_model"], self.delete_model, self.lang["delete_model_explain"]),
            (self.lang["default_model"], self.default_model, self.lang["default_model_explain"]),
            (self.lang["back"], self.page_back, self.lang["back_explain"])
        ], font_path=font_path)
        
        try:self.status_font = pg.font.Font(font_path, 24)
        except:self.status_font = pg.font.SysFont(None, 24)

        try:self.big_status_font = pg.font.Font(font_path, 144)
        except:self.big_status_font = pg.font.SysFont(None, 144)
#-------------------------------------------------------
        self.drawing = False
        self.end_ = True
        self.save_data = {}
        self.percent_page = 1
        self.batch_size = 16
        self.train_list = []
        self.test_list = []
        self.unlist = ["\\","/","|","?","<",">","*",":",'"']# 非法字符
        self.exp_char = "§"
        self.input_text = ''
        self.brush_size = 2

        self.search_input_text = ''
        self.train_data_list = []
        self.test_data_list = []
        self.selected_train_items = set()
        self.selected_test_items = set()
        self.current_train_selection = -1
        self.current_test_selection = -1
        
        self.train_scroll_offset = 0
        self.test_scroll_offset = 0
        self.max_visible_items = 20
        self.item_height = 30

        self.train_data_list = os.listdir("./index/default_train_data/Ziptrain_data")
        self.test_data_list = os.listdir("./index/default_train_data/Ziptest_data")
        self.train_data_list.sort()
        self.test_data_list.sort()

        self.get_result = 0.0
        self.all_count = 0
        self.correct_count = 0
        self.accuracy = 0.0
        self.test_modeling = False
        self.text__ = ''

        self.cpu_data = []
        self.train_loss_data = []
        self.val_loss_data = []
        self.val_acc_data = []

        self.CPU_usepercent = [0.0 for _ in range(120)]

        self.model_list = []
        self.current_model_selection = -1
        self.model_scroll_offset = 0

        self.last_draw_pos = None

        self.is_training = False
        self.training_progress = 0.0  # 0.0 to 1.0
        self.current_epoch = 0
        self.total_batches = 0
        self.current_batch = 0
        self.current_train_loss = 0.0

        if torch.cuda.is_available():self.device = torch.device("cuda")
        else:self.device = torch.device("cpu")
#-------------------------------------------------------
        self.thread = threading.Thread(target=self.get_CPU_usepercent)
        self.thread.daemon = True
        self.thread.start()
        
        self.init_model()
#-------------------------------------------------------
        self.loading_text(self.lang["init_complete"], 1.0)
        self.create_info('correct', 24, self.lang['init_success'])
        

    def clear_board(self):
        self.board = [[0.0 for _ in range(32)] for _ in range(32)]
        self.last_draw_time = None

    def manage_model(self):self.screen_page ='manage'

    def select_model(self):
        if self.current_model_selection >= 0 and self.current_model_selection < len(self.model_list):
            selected_model = self.model_list[self.current_model_selection]
            model_path = f"./save_model/{selected_model}"
            self._config_('model_path', model_path)
            
            try:
                self._load_model_with_progress(model_path,init=False)
                
                self.init_model()
                self.create_info('correct', 24, self.lang['switched_to_model'].format(selected_model=selected_model))
                
                input_box.message_box(
                    text=f"已成功切换到模型: {selected_model}",
                    title="提示",
                    parent=self.root,
                    color='green'
                )
            except Exception as e:
                self.create_info('error', 24, self.lang['model_load_error'].format(error=str(e)))
                input_box.message_box(
                    text=f"模型加载失败: {str(e)}",
                    title="错误",
                    parent=self.root,
                    color='red'
                )
        else:
            input_box.message_box(
                text="请先选择一个模型",
                title="提示",
                parent=self.root,
                color='yellow'
            )

    def delete_model(self):
        if self.current_model_selection >= 0 and self.current_model_selection < len(self.model_list):
            selected_model = self.model_list[self.current_model_selection]
            model_path = f"./save_model/{selected_model}"
            
            confirm = input_box.choose_box(
                self.root,
                title="删除模型",
                text=f"确定要删除模型: {selected_model} 吗?",
                button_1_text="确认",
                button_2_text="取消",
                color='black'
            )
            
            if confirm:
                try:
                    os.remove(model_path)
                    self.model_list.pop(self.current_model_selection)
                    self.current_model_selection = -1
                    self.create_info('correct', 24, self.lang['model_deleted'].format(selected_model=selected_model))
                    
                    input_box.message_box(
                        text=f"已成功删除模型: {selected_model}",
                        title="提示",
                        parent=self.root,
                        color='green'
                    )
                except Exception as e:
                    self.create_info('error', 24, self.lang['delete_failed'].format(error=str(e)))
                    input_box.message_box(
                        text=f"删除失败: {str(e)}",
                        title="错误",
                        parent=self.root,
                        color='red'
                    )
        else:
            input_box.message_box(
                text="请先选择一个模型",
                title="提示",
                parent=self.root,
                color='yellow'
            )

    def default_model(self):
        confirm = input_box.choose_box(
            self.root,
            title="恢复默认模型",
            text="确定要恢复默认模型吗?",
            button_1_text="确认",
            button_2_text="取消",
            color='black'
        )
        
        if confirm:
            try:
                self._config_('model_path', './index/save_data/default_model.zip')
                self._clear_directory("models")
                with open(self.config["model_path"], 'rb') as f:
                    zip_ref = zipfile.ZipFile(f)
                    zip_ref.extractall("./models")
                    zip_ref.close()
                
                self.init_model()
                self.create_info('correct', 24, self.lang['default_model_restored'])
                
                input_box.message_box(
                    text="已成功恢复默认模型",
                    title="提示",
                    parent=self.root,
                    color='green'
                )
            except Exception as e:
                self.create_info('error', 24, self.lang['restore_default_failed'].format(error=str(e)))
                input_box.message_box(
                    text=f"恢复默认模型失败: {str(e)}",
                    title="错误",
                    parent=self.root,
                    color='red'
                )


    def load_loss_data(self):
        try:
            with open("./log/loss.json", "r") as f:
                loss_data = json.load(f)
                self.train_loss_data = loss_data.get("trainLoss", [])
                self.val_loss_data = loss_data.get("valLoss", [])
                self.val_acc_data = loss_data.get("valAcc", [])
        except FileNotFoundError:
            self.train_loss_data = []
            self.val_loss_data = []
            self.val_acc_data = []

    def loading_text(self, text, progress=None, init=True):
        self.screen.fill(COLORS['background'])
        text_surf = self.font_(24).render(text, True, COLORS['text'])
        self.screen.blit(text_surf, (100, 100))

        if init:
        
            if hasattr(self, 'screen_config') and self.screen_config['default_screen'] == "True":
                logo = pg.image.load(ICONS["team_logo"][0])
            else:
                logo = pg.image.load(ICONS["team_logo"][1])
        
            self.screen.blit(logo, (100, 200))
            icon = pg.image.load(ICONS["icon"])
            self.screen.blit(icon, (100, 300))
        
        if progress is not None:
            if init:bar_x, bar_y = 100, 600
            else:bar_x, bar_y = 100, 300
            bar_width, bar_height = 400, 20
            pg.draw.rect(self.screen, COLORS['button'], (bar_x, bar_y, bar_width, bar_height))

            fill_width = int(bar_width * progress)
            pg.draw.rect(self.screen, COLORS['correct'], (bar_x, bar_y, fill_width, bar_height))

            pg.draw.rect(self.screen, COLORS['text'], (bar_x, bar_y, bar_width, bar_height), 1)

            progress_text = f"{progress*100:.1f}%"
            progress_surf = self.font_(16).render(progress_text, True, COLORS['text'])
            progress_rect = progress_surf.get_rect(center=(bar_x + bar_width // 2, bar_y + bar_height // 2))
            self.screen.blit(progress_surf, progress_rect)
        
        pg.display.update()
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()

    def _load_model_with_progress(self, model_path, init=True):
        with open(model_path, 'rb') as f:
            zip_ref = zipfile.ZipFile(f)
            file_list = zip_ref.namelist()
            
            total_size = sum(zip_ref.getinfo(file_name).file_size for file_name in file_list)
            extracted_size = 0
            
            for file_name in file_list:
                file_info = zip_ref.getinfo(file_name)
                # 确保目标目录存在
                target_dir = os.path.join("./models", os.path.dirname(file_name))
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)
                
                with zip_ref.open(file_name) as source, open(os.path.join("./models", file_name), "wb") as target:
                    # 使用 shutil.copyfileobj 进行解压，并实时更新进度
                    buffer_size = int(1024*1024*0.2)
                    while True:
                        buffer = source.read(buffer_size)
                        if not buffer:
                            break
                        target.write(buffer)
                        extracted_size += len(buffer)
                        
                        # 更新进度
                        if init:progress = 0.8 + (extracted_size / total_size) * 0.2 if total_size > 0 else 1.0
                        else:progress = (extracted_size / total_size) if total_size > 0 else 1.0
                        self.loading_text(self.lang["loading_model_progress"].format(extracted_size=self.show_file_size(extracted_size), total_size=self.show_file_size(total_size)), progress, init=init)
            
            zip_ref.close()

    def draw_line_chart(self, surface, data_list, x, y, width, height, 
                       title="", y_min=0, y_max=100, color=(255, 255, 255)):
        
        if title:
            title_surf = self.font_(16).render(title, True, COLORS['text'])
            surface.blit(title_surf, (x + 10, y - 25))
        
        points = []
        max_points = min(len(data_list), 100)
        
        for i, value in enumerate(data_list[-max_points:]):
            x_pos = x + width - (max_points - i) * (width / max_points)
            
            normalized_value = (value - y_min) / (y_max - y_min) if y_max > y_min else 0
            y_pos = y + height - normalized_value * height
            
            points.append((x_pos, y_pos))
        
        if len(points) > 1:
            pg.draw.lines(surface, color, False, points, 2)
        
        font = self.font_(12)
        for i in range(5):
            y_pos = y + height - i * (height / 4)
            value = y_min + i * ((y_max - y_min) / 4)
            value_text = font.render(f"{value:.1f}", True, COLORS['text'])
            surface.blit(value_text, (x - 30, y_pos - 10))
            
            pg.draw.line(surface, (100, 100, 100), (x, y_pos), (x + width, y_pos), 1)
        
        if len(data_list) > 1:
            iterations = len(data_list)
            x_text = font.render(f"迭代: {iterations}", True, COLORS['text'])
            surface.blit(x_text, (x + width - 60, y + height + 5))


    def more_setting(self):
        self.screen_page = 'config'

    def _clear_directory(self, directory):
        if os.path.exists(directory):
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    raise Exception(f'Failed to delete {file_path}. Reason: {e}')
        else:
            os.makedirs(directory, exist_ok=True)

    def quit(self):
        if torch.cuda.is_available():torch.cuda.empty_cache()
        self.root.destroy()
        pg.quit()
        clean_thread = threading.Thread(target=self.clean_temp)
        clean_thread.start()
        sys.exit()

    def clean_temp(self):
        temp_list = ["models","training_data","log","index/%temp%","__pycache__"]
        for temp in temp_list:
            try:
                shutil.rmtree(temp)
            except Exception as e:
                print(f"Failed to delete {temp}. Reason: {e}")

    def change_color(self):
        if self.screen_config['default_screen'] == "True":
            self.screen_config['default_screen'] = "False"
        else:
            self.screen_config['default_screen'] = "True"
        with open("./index/screen_config.json", "w") as f:
            json.dump(self.screen_config, f)
        self.create_info('correct', 24, self.lang['color_settings_saved'])

        for color in list(COLORS.keys())[:-3]:
            COLORS[color] = (255-COLORS[color][0], 255-COLORS[color][1], 255-COLORS[color][2])

        if self.screen_config['default_screen'] != "True":
            COLORS['correct'] = "#00AF00"
            COLORS['error'] = "#AF0000"
            COLORS['warning'] = "#AFAF00"
        else:
            COLORS['correct'] = "#00FF00"
            COLORS['error'] = "#FF0000"
            COLORS['warning'] = "#FFFF00"

    def switch_language(self):
        langs = ['zh', 'en']
        current = langs.index(self.config['language'])
        next_lang = langs[(current + 1) % len(langs)]
        self._config_('language', next_lang)
        with open(f"./index/lang/{next_lang}.json", "r", encoding='utf-8') as f:
            self.lang = json.load(f)
        # 重新创建菜单
        font_path = "font/1.ttc"
        self.menu = PygameMenu([
            (self.lang["clear_board"], self.clear_board, self.lang["clear_board_explain"]),
            (self.lang["save_data"], self.save, self.lang["save_data_explain"]),
            (self.lang["train_model"], self.trainer, self.lang["train_model_explain"]),
            (self.lang["show_log"], self.show_log, self.lang["show_log_explain"]),
            (self.lang["manage_model"], self.manage_model, self.lang["manage_model_explain"]),
            (self.lang["more_setting"], self.more_setting, self.lang["more_setting_explain"]),
            (self.lang["quit_system"], self.quit, self.lang["quit_system_explain"])
        ], font_path=font_path)

        self.menu2 = PygameMenu([
            (self.lang["switch_theme"], self.change_color, self.lang["switch_theme_explain"]),
            (self.lang["test_model"],self.test_model, self.lang["test_model_explain"]),
            (self.lang["switch_language"], self.switch_language, self.lang["switch_language_explain"]),
            (self.lang["previous_page"], self.more_setting, self.lang["previous_page_explain"]),
            (self.lang["back"], self.page_back, self.lang["back_explain"])
        ], font_path=font_path)

        self.menu3 = PygameMenu([
            (self.lang["back"], self.page_back, self.lang["back_explain"])
        ], font_path=font_path)

        self.menu4 = PygameMenu([
            (self.lang["select_model"], self.select_model, self.lang["select_model_explain"]),
            (self.lang["delete_model"], self.delete_model, self.lang["delete_model_explain"]),
            (self.lang["default_model"], self.default_model, self.lang["default_model_explain"]),
            (self.lang["back"], self.page_back, self.lang["back_explain"])
        ], font_path=font_path)
        self.screen_page = 'settings'
        self.create_info('correct', 24, self.lang['language_switched'])
        pg.display.set_caption(self.lang["app_title"])

    def _config_(self, key, value):
        self.config[key] = value
        with open("./index/save_data/config.json", "w") as f:
            json.dump(self.config, f)

    def lock_screen(self):
        screen_locker = pg.rect.Rect(0, 0, *SCREEN_SIZE)
        text = self.big_status_font.render(self.lang["screen_locked"], True, COLORS['text'])
        pg.draw.rect(self.screen, COLORS['background'], screen_locker)
        self.screen.blit(text, (100, 100))
        pg.display.update()

    def unlock_screen(self):pg.display.update()
    def get_CPU_usepercent(self):
        while True:self.CPU_usepercent = [i for i in self.CPU_usepercent[1:]]+[psutil.cpu_percent(interval=1)]
    def show_log(self):self.screen_page = 'log'
    def create_info(self, type, size, text):self.logs_info.append({'type':type,'size':size,'text':f'[{time.strftime("%H:%M:%S", time.localtime())}]{text}'})

    def progress_callback(self, epoch, train_loss, val_loss, val_acc):
        self.create_info('correct', 24, self.lang['epoch_info'].format(epoch=epoch, train_loss=train_loss, val_loss=val_loss, val_acc=val_acc))

    def batch_progress_callback(self, epoch, current_batch, total_batches, current_loss):
        self.current_epoch = epoch
        self.current_batch = current_batch
        self.total_batches = total_batches
        self.current_train_loss = current_loss
        self.training_progress = current_batch / total_batches

    def augment_board(self, board, num_augmentations=63):
        image = Image.new('L', (32, 32))
        draw = ImageDraw.Draw(image)
        
        #转换为灰度图
        for x in range(32):
            for y in range(32):
                brightness = int(board[x][y] * 255)
                draw.point((x, y), fill=brightness)
        
        augmented_boards = []
        
        for _ in range(num_augmentations):
            angle = random.uniform(-10, 10)
            rotated_image = image.rotate(angle, resample=Image.BICUBIC, expand=False, fillcolor=0)
            
            dx = random.randint(-2, 2)
            dy = random.randint(-2, 2)
            translated_image = Image.new('L', (32, 32))

            translated_draw = ImageDraw.Draw(translated_image)
            for x in range(32):
                for y in range(32):
                    nx = x + dx
                    ny = y + dy
                    if 0 <= nx < 32 and 0 <= ny < 32:
                        brightness = rotated_image.getpixel((nx, ny))
                        translated_draw.point((x, y), fill=brightness)

            augmented_boards.append(translated_image)
            
            scaling_factor = random.uniform(0.9, 1.1)
            scaled_size = (int(32 * scaling_factor), int(32 * scaling_factor))
            scaled_image = rotated_image.resize(scaled_size, Image.BICUBIC)
            
            centered_image = Image.new('L', (32, 32))
            centered_draw = ImageDraw.Draw(centered_image)
            offset = ((32 - scaled_size[0]) // 2, (32 - scaled_size[1]) // 2)
            for x in range(min(32, scaled_size[0])):
                for y in range(min(32, scaled_size[1])):
                    brightness = scaled_image.getpixel((x, y))
                    centered_draw.point((x + offset[0], y + offset[1]), fill=brightness)

            #添加噪点
            for _ in range(random.randint(0, 10)):
                x = random.randint(0, 31)
                y = random.randint(0, 31)
                brightness = random.randint(0, 255)
                try:centered_image.putpixel((x, y), brightness)
                except:pass
            
            augmented_boards.append(centered_image)
        
        return augmented_boards

    def save(self):
        label = self._ask_label()
        
        if label and self.exp_char not in label:
            augmented_boards = self.augment_board(self.board, num_augmentations=79)
            with zipfile.ZipFile("training_data/data.zip", 'a') as zip_ref:
                for new_board in augmented_boards:
                    name = f"{time.time()}_{self.label_toname(label)}"
                    bytes_io = io.BytesIO()
                    new_board.save(bytes_io, format="PNG")
                    bytes_io.seek(0)
                    zip_ref.writestr(name, bytes_io.read())
            
            self.create_info('correct', 24, self.lang['save_data_success'].format(label=label, new_data_count=len(augmented_boards)+1))
                
            try:
                self.create_info('warning', 24, self.lang['data_total_size'].format(size=self.show_file_size(os.path.getsize("training_data/data.zip"))))
            except:
                self.create_info('error', 24, self.lang['data_size_read_failed'])
                                    
            input_box.message_box(
                text=f"保存 {label} 标签数据成功",
                title="提示",
                parent=self.root,
                color='green'
            )

        elif label and self.exp_char in label:
            input_box.message_box(
                text="标签不能包含特殊字符 " + self.exp_char,
                title="错误",
                parent=self.root,
                color='red'
            )

        else:
            input_box.message_box(
                text="标签不能为空",
                title="错误",
                parent=self.root,
                color='red'
            )

        
    def show_file_size(self, bit_size):
        if bit_size < 1024:
            return f"{bit_size}B"
        elif bit_size < 1024*1024:
            return f"{round(bit_size/1024,2)}KB"
        elif bit_size < 1024*1024*1024:
            return f"{round(bit_size/1024/1024,2)}MB"
        else:
            return f"{round(bit_size/1024/1024/1024,2)}GB"
        
    def trainer(self):
        if self.end_:
            self.name_ = input_box.get_input(
                text="请输入模型名称",
                title="保存模型",
                color='black'
            )

            if self.name_:
                for char in self.unlist:
                    if char in self.name_:
                        input_box.message_box(
                            text="模型名称不能包含特殊字符 " + char,
                            title="错误",
                            parent=self.root,
                            color='red'
                        )
                        return

                self.intro_ = input_box.get_input(
                    text="请输入模型介绍",
                    title="保存模型",
                    color='black'
                )

                if self.intro_:

                    if (self.name_ + ".zip") not in os.listdir("save_model"):
                        if self.name_:
                            self.is_training = True
                            self.training_progress = 0.0
                            p = threading.Thread(target=self.train)
                            p.daemon = True
                            p.start()
                    else:
                        input_box.message_box(
                            text="模型名称已存在",
                            title="错误",
                            parent=self.root,
                            color='red'
                        )

        else:
            input_box.message_box(
                text="正在训练模型，请等待",
                title="提示",
                parent=self.root,
                color='green'
            )
    def train(self):
        try:
            data = {}
            c = {}
            min_file_count = float('inf')
            # 统计训练数据最少的数量
            for file in self.train_list:
                path = os.path.join("./index/default_train_data/Ziptrain_data", file)
                with zipfile.ZipFile(path, 'r') as zip_ref:
                    c = {}
                    for file in zip_ref.namelist():
                        label = self.name_tolabel(file.split("/")[-1])
                        if label not in c:
                            c[label] = 0
                        c[label] += 1
            try:
                with zipfile.ZipFile("training_data/data.zip", 'r') as zip_ref:
                    for file in zip_ref.namelist():
                        label = self.name_tolabel(file.split("/")[-1])
                        if label not in c:
                            c[label] = 0
                        c[label] += 1
            except zipfile.BadZipFile:pass
            
            min_file_count = min(min_file_count, min(c.values()))
            self.create_info('correct', 24, self.lang['min_train_data_count'].format(count=min_file_count))

            # 读取训练数据
            try:
                with zipfile.ZipFile("training_data/data.zip", 'r') as zip_ref:
                    for file in zip_ref.namelist():
                        label = self.name_tolabel(file.split("/")[-1])
                        if label not in data:
                            data[label] = []
                        if data[label] and len(data[label]) >= min_file_count:continue
                        data[label].append(self.image_tolist(Image.open(zip_ref.open(file))))
            except zipfile.BadZipFile:pass

            for file in self.train_list:
                path = os.path.join("./index/default_train_data/Ziptrain_data", file)
                with zipfile.ZipFile(path, 'r') as zip_ref:
                    for i, file in enumerate(zip_ref.namelist()):
                        label = self.name_tolabel(file.split("/")[-1])
                        if i % (min_file_count // 3) == 1:self.create_info('correct', 24, self.lang['reading_train_data'].format(file=file))
                        if label not in data:
                            data[label] = []
                        if data[label] and len(data[label]) >= min_file_count:continue
                        data[label].append(self.image_tolist(Image.open(zip_ref.open(file))))

            if not data:raise zipfile.BadZipFile("No training data found.")
            self.create_info('correct', 24, self.lang['train_data_read_success'])
            
            with open("./log/loss.json", "w") as f:
                json.dump({"trainLoss":[], "valLoss":[], "valAcc":[]}, f)

            self.create_info('correct', 24, self.lang['start_training'])

            start_time = time.time()

            labels = list(data.keys())
            output_size = len(data)
            ans_ = []
            label_ = []
            _label_ = {}
            for i, label in enumerate(labels):
                _label_[i] = label
                for j in range(len(data[label])):
                    ans_.append(data[label][j])
                    label_.append(i)

            ans_t = torch.tensor(ans_).float().view(-1, 1, 32, 32)
            label_t = torch.tensor(label_).long()
            self.create_info('correct', 24, self.lang['data_prep_complete'])

            dataset_balanced = TensorDataset(ans_t, label_t)
            train_size = int(0.8 * len(dataset_balanced))
            val_size = len(dataset_balanced) - train_size
            self.train_dataset, self.val_dataset = random_split(dataset_balanced, [train_size, val_size])

            self.train_loader = DataLoader(self.train_dataset, batch_size=self.batch_size, shuffle=True, drop_last=True)  # 使用相同的批次大小
            self.val_loader = DataLoader(self.val_dataset, batch_size=self.batch_size, shuffle=False, drop_last=True)  # 使用相同的批次大小

            self.create_info('correct', 24, self.lang['train_set_size'].format(size=len(self.train_dataset)))
            self.create_info('correct', 24, self.lang['val_set_size'].format(size=len(self.val_dataset)))
            self.create_info('correct', 24, self.lang['batch_size_info'].format(size=self.batch_size))
            self.create_info('correct', 24, self.lang['output_size'].format(size=output_size))
            self.create_info('correct', 24, self.lang['device_info'].format(device=self.device))

            self.end_ = False

            self.init__ = nn.Trainer(output_size=output_size, 
                                    device=self.device,
                                    lr=5e-4 / log10(output_size + 1),
                                    lambda_l1=1e-5 * log10(output_size + 1),
                                    lambda_l2=min(1e-4, 1e-6 * sqrt(output_size)),
                                    dropout_prob=0.1 + 0.05 * log10(output_size)
                                    )
            self.create_info('correct', 24, f'开始训练模型')
            self.init__.train( self.train_loader,
                            self.val_loader, 
                            early_stopping=True,
                            progress_callback=self.progress_callback,
                            batch_progress_callback=self.batch_progress_callback
                            )

            with open("./models/label.json", "w") as f:
                json.dump(_label_, f)

            with open("./models/intro.txt", "w") as f:
                f.write(self.intro_)

            zip_file = zipfile.ZipFile(f"save_model/{self.name_}.zip", "w", zipfile.ZIP_STORED)
            zip_file.write("models/label.json")
            zip_file.write("models/model.pth")
            zip_file.write("models/intro.txt")
            zip_file.close()

            self.end_ = True
            end_time = time.time()
            self.create_info('correct', 24, f'训练模型完成，用时{end_time-start_time:.2f}秒')
            self.create_info('correct', 24, f'模型保存成功')
            self.is_training = False
        
        except zipfile.BadZipFile as er:
            self.create_info('error', 24, f'训练数据不存在|{er}')

    def _ask_label(self):
        self.input_text = input_box.get_input(
            text="请输入标签",
            title="标签",
            color='black'
        )
        return self.input_text
    
    def image_tolist(self, image):
        image = ImageEnhance.Contrast(image).enhance(2)
        return [[image.getpixel((x, y)) for x in range(32)] for y in range(32)]
    
    def name_tolabel(self, name):
        a = name.split(".")[-2].split("_")[-1]
        result = ""
        for k,i in enumerate(a[::1]):
            if i == self.exp_char:
                result += self.unlist[int(a[k+1])]
            elif a[max(0,k-1)] != self.exp_char:
                result += i
        return result
    
    def label_toname(self, label):
        result = ""
        for i in label:
            if i in self.unlist:
                result += self.exp_char + str(self.unlist.index(i))
            else:
                result += i
        return result + ".png"
    
    def draw_program(self, program, label, x, y):
        label_text = self.font_(int(24/(len(label)))).render(label, True, COLORS['text'])
        label_rect = label_text.get_rect(center=(x-16, y+8))
        self.screen.blit(label_text, label_rect)

        un_rect = pg.Rect(x, y, 128, 16)
        pg.draw.rect(self.screen, COLORS['error'], un_rect)

        known_rect = pg.Rect(x, y, int(128*program), 16)
        pg.draw.rect(self.screen, COLORS['correct'], known_rect)

        percentage = self.font_(14).render(f"{round(program*100,2)}%", True, COLORS['text'])
        percentage_rect = percentage.get_rect(center=(x+128/2, y+8))
        self.screen.blit(percentage, percentage_rect)
    
    def draw_training_progress(self):
        bar_x, bar_y = 550, 650
        bar_width, bar_height = 400, 30
        
        pg.draw.rect(self.screen, COLORS['button'], (bar_x, bar_y, bar_width, bar_height))
        
        fill_width = int(bar_width * self.training_progress)
        pg.draw.rect(self.screen, COLORS['correct'], (bar_x, bar_y, fill_width, bar_height))
        
        pg.draw.rect(self.screen, COLORS['text'], (bar_x, bar_y, bar_width, bar_height), 2)
        
        progress_text = f"训练进度 - Epoch {self.current_epoch}: {self.current_batch}/{self.total_batches} ({self.training_progress*100:.1f}%) Loss: {self.current_train_loss:.3f}"
        text_surf = self.font_(16).render(progress_text, True, COLORS['text'])
        self.screen.blit(text_surf, (bar_x, bar_y - 35))

    def init_model(self):
        with open("./models/models/label.json", "r") as f:
            _label_ = json.load(f)
            output_size = len(_label_)
        self.use_ = nn.Trainer(device=self.device, output_size=output_size)
        self.use_.load_model('./models/models/model.pth')

    def run(self):
        running = True
        self.ticks = -1
        while running:
            if True:
            #try:
                self.ticks += 1
                
                if self.ticks == 0:self.load_loss_data()
                if self.screen_page == 'main':
                    self.screen.fill(COLORS['background'])
                    
                    for x in range(32):
                        for y in range(32):
                            brightness = 255 - int(self.board[x][y] * 255)
                            if self.screen_config['default_screen'] != 'True':
                                color = (255-brightness, 255-brightness, 255-brightness)
                            else:
                                color = (brightness, brightness, brightness)
                            pg.draw.rect(self.screen, color, (x*10+100, y*10+100, 10, 10))
                    
                    self.log_sys = Pygamelog(self.screen, self.logs_info, 10, 500, 32, 8, font_path='./font/2.ttc')
                    
                    if self.ticks == 0:
                        with open("./models/models/intro.txt", "r") as f:
                            self.intro_text = f.read()

                    self.intro_label = self.status_font.render(f"模型介绍: {self.intro_text}", True, COLORS['text'])
                    self.intro_label_rect = self.intro_label.get_rect(center=(400, 50))
                    self.screen.blit(self.intro_label, self.intro_label_rect)

                    if self.ticks % 30 == 0:#为什么要用张量啊？？？？？？？？？？
                        
                        with open("./models/models/label.json", "r") as f:
                            _label_ = json.load(f)

                        board_ = np.array(self.board)
                        board_ = np.rot90(board_, k=-1)
                        board_ = np.flip(board_, axis=1)
                        # 高对比度
                        board_ = np.array(board_ * 255, dtype=np.uint8)
                        board_ = Image.fromarray(board_)
                        board_ = ImageEnhance.Contrast(board_).enhance(2)

                        board_ = np.array(board_)

                        out_ = self.use_.use_model(TensorDataset(torch.tensor(board_).float().view(-1, 1, 32, 32)))
                        out_ = torch.softmax(out_, dim=1)
                        soft_out = out_.tolist()
                        soft_out = [round(i, 4) for i in soft_out[0]]

                        label = soft_out.index(max(soft_out))
                        self.label = _label_[str(label)]

                        self.temp_max = deepcopy(soft_out)
                        for i, _ in enumerate(self.temp_max):
                            self.temp_max[i] = (_, _label_[str(i)])

                        self.temp_max = sorted(self.temp_max, key=lambda x:x[0], reverse=True)

                    for i, label in enumerate(self.temp_max[:min(self.percent_page*5, len(self.temp_max))]):
                        self.draw_program(label[0], label[1], 500, 300+i*40)

                    self.get_return = self.font_(int(144/(len(self.label)))).render(self.label, True, COLORS['text'])
                    self.get_return_rect = self.get_return.get_rect(center=(500, 200))
                    self.screen.blit(self.get_return, self.get_return_rect)

                    self.percent_label = self.status_font.render(f"置信度: {round(max(soft_out)*100,2)}%", True, COLORS['text'])
                    self.percent_label_rect = self.percent_label.get_rect(center=(650, 200))
                    self.screen.blit(self.percent_label, self.percent_label_rect)

                    self.menu.draw(self.screen)
                    
                    for event in pg.event.get():
                        if event.type == pg.QUIT:
                            running = False
                        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                            self.drawing = True
                            self.last_draw_pos = None
                            
                            back_func = self.menu.handle_click(event.pos)
                            if back_func:
                                self.drawing = False
                                back_func()
                            
                            back_text = self.log_sys.handle_click(event.pos)
                            if back_text:
                                self.drawing = False
                                input_box.message_box(
                                    text=back_text[0],
                                    title=f"详情",
                                    parent=self.root,
                                    color=COLORS[back_text[1]]
                                )
                                
                        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                            self.drawing = False
                            self.last_draw_pos = None
                            
                        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 3:self.menu.explains_click(event.pos)
                        else:self.menu.explains_click((-1,-1))

                        if self.drawing:
                            self.handle_drawing(pg.mouse.get_pos())

                #--------------------------------------------------------------------  
                elif self.screen_page == 'log':
                    self.screen.fill(COLORS['background'])
                    self.menu3.draw(self.screen)
                    self.log_sys = Pygamelog(self.screen, self.logs_info, 10, 550, 32, 7, font_path='./font/2.ttc')
                    
                    if self.is_training:
                        self.draw_training_progress()

                    self.draw_line_chart(
                        self.screen,
                        self.CPU_usepercent,
                        x=50, y=50, width=400, height=200,
                        title="CPU占用率 (%)",
                        y_min=0, y_max=100,
                        color=(0, 200, 0)
                    )
                    
                    combined_loss = self.train_loss_data + self.val_loss_data
                    loss_max = max(combined_loss) if combined_loss else 1.0
                    
                    self.draw_line_chart(
                        self.screen,
                        self.train_loss_data,
                        x=500, y=50, width=400, height=200,
                        title="训练损失 (Train Loss) 验证损失 (Val Loss)",
                        y_min=0, y_max=loss_max,
                        color=(255, 100, 100)
                    )

                    if self.val_loss_data:
                        self.draw_line_chart(
                            self.screen,
                            self.val_loss_data,
                            x=500, y=50, width=400, height=200,
                            title="",
                            y_min=0, y_max=loss_max,
                            color=(100, 100, 255)
                        )
                    
                    acc_max = max(self.val_acc_data) if self.val_acc_data else 1.0
                    self.draw_line_chart(
                        self.screen,
                        self.val_acc_data,
                        x=50, y=300, width=400, height=200,
                        title="验证准确率 (Val Acc)",
                        y_min=0, y_max=1.0,
                        color=(255, 200, 0)
                    )
                    
                    legend_font = self.font_(14)
                    
                    cpu_legend = legend_font.render("CPU占用率", True, (0, 200, 0))
                    self.screen.blit(cpu_legend, (60, 260))
                    
                    train_loss_legend = legend_font.render("训练损失", True, (255, 100, 100))
                    self.screen.blit(train_loss_legend, (510, 260))
                    
                    val_loss_legend = legend_font.render("验证损失", True, (100, 100, 255))
                    self.screen.blit(val_loss_legend, (610, 260))
                    
                    acc_legend = legend_font.render("验证准确率", True, (255, 200, 0))
                    self.screen.blit(acc_legend, (60, 510))
                    
                    for event in pg.event.get():
                        if event.type == pg.QUIT:
                            running = False
                        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                            back_func = self.menu3.handle_click(event.pos)
                            if back_func:
                                back_func()
                        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
                            self.menu3.explains_click(event.pos)
                        else:
                            self.menu3.explains_click((-1,-1))

                elif self.screen_page == 'manage':
                    self.screen.fill(COLORS['background'])
                    self.menu4.draw(self.screen)
                    
                    model_dir = "./save_model"
                    if not os.path.exists(model_dir):
                        os.makedirs(model_dir, exist_ok=True)
                    
                    self.model_list = [f for f in os.listdir(model_dir) if f.endswith(".zip")]
                    self.model_list.sort()
                    
                    title = self.font_(32).render("模型管理", True, COLORS['text'])
                    self.screen.blit(title, (50, 50))
                    
                    current_model = os.path.basename(self.config["model_path"])
                    current_text = self.font_(20).render(f"当前使用模型: {current_model}", True, COLORS['text'])
                    self.screen.blit(current_text, (50, 100))
                    
                    list_rect = pg.Rect(50, 150, 700, 500)
                    pg.draw.rect(self.screen, COLORS['background'], list_rect, border_radius=5)
                    pg.draw.rect(self.screen, COLORS['text'], list_rect, 2, border_radius=5)
                    
                    start_y = 155
                    visible_items = min(self.max_visible_items, len(self.model_list) - self.model_scroll_offset)
                    
                    for i in range(visible_items):
                        idx = i + self.model_scroll_offset
                        if idx >= len(self.model_list):
                            break
                            
                        model_name = self.model_list[idx]
                        item_rect = pg.Rect(55, start_y + i*self.item_height, 690, self.item_height-5)
                        
                        bg_color = COLORS['highlight'] if idx == self.current_model_selection else COLORS['button']
                        text_color = COLORS['success'] if model_name == current_model else COLORS['text']
                        
                        pg.draw.rect(self.screen, bg_color, item_rect, border_radius=3)
                        
                        name_surface = self.font_(18).render(model_name, True, text_color)
                        self.screen.blit(name_surface, (item_rect.x+10, item_rect.y+5))
                        
                        try:
                            model_path = os.path.join(model_dir, model_name)
                            size = os.path.getsize(model_path)
                            size_text = self.show_file_size(size)
                            size_surface = self.font_(14).render(size_text, True, COLORS['text'])
                            self.screen.blit(size_surface, (item_rect.x+400, item_rect.y+7))
                        except:
                            pass
                    
                    if len(self.model_list) > self.max_visible_items:
                        scroll_height = 500 * self.max_visible_items / len(self.model_list)
                        scroll_y = 150 + (500 - scroll_height) * self.model_scroll_offset / max(1, len(self.model_list) - self.max_visible_items)
                        scroll_rect = pg.Rect(755, scroll_y, 5, scroll_height)
                        pg.draw.rect(self.screen, COLORS['text'], scroll_rect)
                    
                    stats_text = self.font_(16).render(f"共{len(self.model_list)}个模型", True, COLORS['text'])
                    self.screen.blit(stats_text, (50, 120))
                    
                    for event in pg.event.get():
                        if event.type == pg.QUIT:
                            running = False
                            
                        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:

                            back_func = self.menu4.handle_click(event.pos)
                            if back_func:
                                back_func()
                            
                            list_area = pg.Rect(50, 150, 700, 500)
                            if list_area.collidepoint(event.pos):
                                click_y = event.pos[1]
                                item_idx = (click_y - 155) // self.item_height + self.model_scroll_offset
                                if 0 <= item_idx < len(self.model_list):
                                    self.current_model_selection = item_idx
                        
                        elif event.type == pg.MOUSEWHEEL:
                            mouse_pos = pg.mouse.get_pos()
                            list_area = pg.Rect(50, 150, 700, 500)
                            if list_area.collidepoint(mouse_pos):
                                self.model_scroll_offset -= event.y * 3
                                self.model_scroll_offset = max(0, min(self.model_scroll_offset, 
                                                                    len(self.model_list) - self.max_visible_items))


                elif self.screen_page == 'config':
                    self.screen.fill(COLORS['background'])

                    self.background = pg.rect.Rect(10, 10, 1004, 748)
                    pg.draw.rect(self.screen, COLORS['highlight'], self.background)

                    self.search = pg.image.load(ICONS['search'][0] if self.screen_config['default_screen'] != 'True' else ICONS['search'][1])
                    self.search_rect = self.search.get_rect(center=(40, 40))
                    self.screen.blit(self.search, self.search_rect)

                    if self.search_input_text:
                        search_text = self.font_(18).render(f"搜索: {self.search_input_text}", True, COLORS['text'])
                        self.screen.blit(search_text, (80, 30))

                    train_title = self.font_(24).render("训练数据集", True, COLORS['text'])
                    test_title = self.font_(24).render("测试数据集", True, COLORS['text'])
                    self.screen.blit(train_title, (50, 80))
                    self.screen.blit(test_title, (550, 80))

                    train_list_rect = pg.Rect(50, 120, 450, 600)
                    pg.draw.rect(self.screen, COLORS['background'], train_list_rect, border_radius=5)
                    pg.draw.rect(self.screen, COLORS['text'], train_list_rect, 2, border_radius=5)

                    start_y = 125
                    visible_train_items = min(self.max_visible_items, len(self.train_data_list) - self.train_scroll_offset)
                    
                    for i in range(visible_train_items):
                        idx = i + self.train_scroll_offset
                        if idx >= len(self.train_data_list):
                            break
                            
                        filename = self.train_data_list[idx]
                        item_rect = pg.Rect(55, start_y + i*self.item_height, 440, self.item_height-5)
                        
                        bg_color = COLORS['highlight'] if idx == self.current_train_selection else COLORS['button']
                        text_color = COLORS['success'] if filename in self.train_list else COLORS['text']
                        
                        pg.draw.rect(self.screen, bg_color, item_rect, border_radius=3)
                        
                        check_rect = pg.Rect(item_rect.x+5, item_rect.y+5, 20, 20)
                        pg.draw.rect(self.screen, COLORS['text'], check_rect, 2)
                        if idx in self.selected_train_items:
                            pg.draw.line(self.screen, COLORS['success'], (check_rect.x+3, check_rect.y+10), (check_rect.x+8, check_rect.y+15), 3)
                            pg.draw.line(self.screen, COLORS['success'], (check_rect.x+8, check_rect.y+15), (check_rect.x+17, check_rect.y+3), 3)
                        
                        filename_surface = self.font_(18).render(filename, True, text_color)
                        self.screen.blit(filename_surface, (item_rect.x+35, item_rect.y+5))

                    if len(self.train_data_list) > self.max_visible_items:
                        scroll_height = 600 * self.max_visible_items / len(self.train_data_list)
                        scroll_y = 120 + (600 - scroll_height) * self.train_scroll_offset / max(1, len(self.train_data_list) - self.max_visible_items)
                        scroll_rect = pg.Rect(495, scroll_y, 5, scroll_height)
                        pg.draw.rect(self.screen, COLORS['text'], scroll_rect)

                    train_stats = self.font_(16).render(f"共{len(self.train_data_list)}项，已选{len(self.selected_train_items)}项，已添加{len(self.train_list)}项", True, COLORS['text'])
                    self.screen.blit(train_stats, (200, 90))

                    test_list_rect = pg.Rect(550, 120, 450, 600)
                    pg.draw.rect(self.screen, COLORS['background'], test_list_rect, border_radius=5)
                    pg.draw.rect(self.screen, COLORS['text'], test_list_rect, 2, border_radius=5)

                    visible_test_items = min(self.max_visible_items, len(self.test_data_list) - self.test_scroll_offset)
                    
                    for i in range(visible_test_items):
                        idx = i + self.test_scroll_offset
                        if idx >= len(self.test_data_list):
                            break
                            
                        filename = self.test_data_list[idx]
                        item_rect = pg.Rect(555, start_y + i*self.item_height, 440, self.item_height-5)
                        bg_color = COLORS['highlight'] if idx == self.current_test_selection else COLORS['button']
                        text_color = COLORS['success'] if filename in self.test_list else COLORS['text']
                        
                        pg.draw.rect(self.screen, bg_color, item_rect, border_radius=3)
                        
                        check_rect = pg.Rect(item_rect.x+5, item_rect.y+5, 20, 20)
                        pg.draw.rect(self.screen, COLORS['text'], check_rect, 2)
                        if idx in self.selected_test_items:
                            pg.draw.line(self.screen, COLORS['success'], (check_rect.x+3, check_rect.y+10), (check_rect.x+8, check_rect.y+15), 3)
                            pg.draw.line(self.screen, COLORS['success'], (check_rect.x+8, check_rect.y+15), (check_rect.x+17, check_rect.y+3), 3)
                        
                        filename_surface = self.font_(18).render(filename, True, text_color)
                        self.screen.blit(filename_surface, (item_rect.x+35, item_rect.y+5))

                    if len(self.test_data_list) > self.max_visible_items:
                        scroll_height = 600 * self.max_visible_items / len(self.test_data_list)
                        scroll_y = 120 + (600 - scroll_height) * self.test_scroll_offset / max(1, len(self.test_data_list) - self.max_visible_items)
                        scroll_rect = pg.Rect(995, scroll_y, 5, scroll_height)
                        pg.draw.rect(self.screen, COLORS['text'], scroll_rect)

                    test_stats = self.font_(16).render(f"共{len(self.test_data_list)}项，已选{len(self.selected_test_items)}项, 已添加{len(self.test_list)}项", True, COLORS['text'])
                    self.screen.blit(test_stats, (700, 90))

                    add_train_btn_rect = self.create_rect("添加到训练列表", 50, 730, 200, 25, COLORS['button'])
                    remove_train_btn_rect = self.create_rect("从训练列表移除", 260, 730, 200, 25, COLORS['button'])
                    add_test_btn_rect = self.create_rect("添加到测试列表", 550, 730, 200, 25, COLORS['button'])
                    remove_test_btn_rect = self.create_rect("从测试列表移除", 760, 730, 200, 25, COLORS['button'])
                    all_choose_train_btn_rect = self.create_rect("全选训练列表", 50, 55, 200, 25, COLORS['button'])
                    all_choose_test_btn_rect = self.create_rect("全选测试列表", 550, 55, 200, 25, COLORS['button'])
                    back_btn_rect = self.create_rect("返回", 300, 55, 200, 25, COLORS['button'])
                    next_page_rect = self.create_rect("下一页", 800, 55, 200, 25, COLORS['button'])

                    for event in pg.event.get():
                        if event.type == pg.QUIT:
                            running = False
                            
                        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                            if self.search_rect.collidepoint(event.pos):
                                self.search_input_text = input_box.get_input(
                                    text="请输入搜索关键词",
                                    title="搜索数据集",
                                    color='black'
                                )
                                if self.search_input_text is not None:
                                    self._perform_search()
                            
                            train_list_area = pg.Rect(50, 120, 450, 600)
                            if train_list_area.collidepoint(event.pos):
                                click_y = event.pos[1]
                                item_idx = (click_y - 125) // self.item_height + self.train_scroll_offset
                                if 0 <= item_idx < len(self.train_data_list):
                                    self.current_train_selection = item_idx
                                    if item_idx in self.selected_train_items:
                                        self.selected_train_items.remove(item_idx)
                                    else:
                                        self.selected_train_items.add(item_idx)
                            
                            test_list_area = pg.Rect(550, 120, 450, 600)
                            if test_list_area.collidepoint(event.pos):
                                click_y = event.pos[1]
                                item_idx = (click_y - 125) // self.item_height + self.test_scroll_offset
                                if 0 <= item_idx < len(self.test_data_list):
                                    self.current_test_selection = item_idx
                                    if item_idx in self.selected_test_items:
                                        self.selected_test_items.remove(item_idx)
                                    else:
                                        self.selected_test_items.add(item_idx)
                            
                            if add_train_btn_rect.collidepoint(event.pos):
                                self._add_to_train_list()
                            elif remove_train_btn_rect.collidepoint(event.pos):
                                self._remove_from_train_list()
                            elif add_test_btn_rect.collidepoint(event.pos):
                                self._add_to_test_list()
                            elif remove_test_btn_rect.collidepoint(event.pos):
                                self._remove_from_test_list()
                            elif all_choose_train_btn_rect.collidepoint(event.pos):
                                self.selected_train_items = set(range(len(self.train_data_list)))
                            elif all_choose_test_btn_rect.collidepoint(event.pos):
                                self.selected_test_items = set(range(len(self.test_data_list)))
                            elif back_btn_rect.collidepoint(event.pos):
                                self.page_back()
                            elif next_page_rect.collidepoint(event.pos):
                                self.screen_page = 'set'

                        elif event.type == pg.MOUSEWHEEL:
                            mouse_pos = pg.mouse.get_pos()
                            
                            train_list_area = pg.Rect(50, 120, 450, 600)
                            if train_list_area.collidepoint(mouse_pos):
                                self.train_scroll_offset -= event.y * 3
                                self.train_scroll_offset = max(0, min(self.train_scroll_offset, 
                                                                    len(self.train_data_list) - self.max_visible_items))
                            
                            test_list_area = pg.Rect(550, 120, 450, 600)
                            if test_list_area.collidepoint(mouse_pos):
                                self.test_scroll_offset -= event.y * 3
                                self.test_scroll_offset = max(0, min(self.test_scroll_offset,
                                                                   len(self.test_data_list) - self.max_visible_items))
                elif self.screen_page == 'set':
                    self.screen.fill(COLORS['background'])

                    all_count_text = self.font_(24).render(f"总数: {self.all_count}", True, COLORS['text'])
                    correct_count_text = self.font_(24).render(f"正确: {self.correct_count}", True, COLORS['text'])
                    accuracy_text = self.font_(24).render(f"准确率: {round(self.accuracy*100,2)}%", True, COLORS['text'])
                    text_text = self.font_(24).render(self.text__, True, COLORS['text'])
                    self.screen.blit(all_count_text, (200, 100))
                    self.screen.blit(correct_count_text, (200, 150))
                    self.screen.blit(accuracy_text, (200, 200))
                    self.screen.blit(text_text, (200, 250))

                    if self.accuracy >= 0.9:
                        perfecticon = pg.image.load(ICONS['perfect'])
                        self.screen.blit(perfecticon, (200, 300))
                    elif self.accuracy >= 0.75:
                        perfecticon = pg.image.load(ICONS['good'])
                        self.screen.blit(perfecticon, (200, 300))

                    for event in pg.event.get():
                        if event.type == pg.QUIT:
                            running = False
                            
                        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                            back_func = self.menu2.handle_click(event.pos)
                            if back_func:
                                back_func()

                        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
                            self.menu2.explains_click(event.pos)
                        else:
                            self.menu2.explains_click((-1,-1))
                    
                    self.menu2.draw(self.screen)

            #except Exception as error:
            #    self.create_info('error', 24, f'程序出错|{error}')

            pg.display.flip()
            self.clock.tick(120)

            if self.ticks == 120:
                self.ticks = -1
            
        self.quit()

    def test_model(self):
        if self.test_modeling:
            input_box.message_box(text="正在测试模型，请稍后", 
                                  title="提示", 
                                  parent=self.root, 
                                  color=COLORS['error']
                                  )
            return
        k = threading.Thread(target=self.test_model_)
        k.daemon = True
        k.start()

    def test_model_(self):
        self.test_modeling = True
        with open("./models/models/label.json", "r") as f:
            label_dict = json.load(f)
        labels = list(label_dict.values())
        self.__model = nn.Trainer(device=self.device, output_size=len(label_dict))
        self.__model.load_model("./models/models/model.pth")
        min_file_count = 50
        count = 0
        tstlst = []
        for i in labels:
            if i.lower() + ".zip" in self.test_list:
                if i.lower() + ".zip" not in tstlst:
                    tstlst.append(i.lower() + ".zip")
                count += 1
        if count == 0:
            self.test_modeling = False
            self.text__ = "没有匹配的测试数据"
            return
        
        self.all_count = 0
        self.correct_count = 0
        data = {}
        
        for file in tstlst:
            path = os.path.join("./index/default_train_data/Ziptest_data", file)
            with zipfile.ZipFile(path, 'r') as zip_ref:
                plst = zip_ref.namelist()
                random.shuffle(plst)
                for i, file in enumerate(plst):
                    try:
                        label = self.name_tolabel(file.split("/")[-1])
                        if label not in data:
                            data[label] = []
                        if data[label] and len(data[label]) >= min_file_count:continue
                        self.all_count += 1
                        img = zip_ref.open(file)  # 直接打开文件
                        img = Image.open(img)
                        img = img.convert("L")
                        enhance = ImageEnhance.Contrast(img)
                        img = enhance.enhance(2)
                        data[label].append(self.image_tolist(img))
                        print(f"正在测试{i+1}/{len(plst)}")
                    except:pass

        for i, (label, imgs) in enumerate(data.items()):
            for img in imgs:
                img = TensorDataset(torch.tensor(img, dtype=torch.float32).view(-1, 1, 32, 32))
                label_get = self.__model.use_model(img)
                soft_get = torch.softmax(label_get, dim=1).tolist()[0]
                idx = soft_get.index(max(soft_get))
                result = label_dict[str(idx)]
                self.text__ = f"{i}/{len(data)}|预测结果: {result}, 实际结果: {label}"
                if result == label:
                    self.correct_count += 1

            self.accuracy = self.correct_count / self.all_count

        self.test_modeling = False
        self.text__ = f"测试完成，准确率为{round(self.accuracy*100,2)}%"


    def handle_drawing(self, pos):
        x = (pos[0] - 100) // 10
        y = (pos[1] - 100) // 10
        
        if not (0 <= x < 32 and 0 <= y < 32):
            self.last_draw_pos = None
            return
        
        if not self.last_draw_pos:
            self.last_draw_pos = (x, y)
            self._draw_point(x, y, 1.0)
            return
        if self.last_draw_pos == (x, y):
            return
        
        x_last, y_last = self.last_draw_pos
        
        distance = sqrt((x - x_last)**2 + (y - y_last)**2)
        
        if distance > 0:
            speed_factor = min(1.5, max(0.5, 2.0 / (distance + 1)))
            brush_size = max(1, min(self.brush_size, int(self.brush_size / speed_factor)))  # 修改这里
            opacity = max(0.7, min(1.0, 1.5 - speed_factor * 0.5))
            points_list = self._get_line_points(x_last, y_last, x, y)
            for i, (px, py) in enumerate(points_list):
                if 0 <= px < 32 and 0 <= py < 32:
                    position_factor = i / max(1, len(points_list) - 1)
                    if position_factor < 0.2 or position_factor > 0.8:
                        current_brush_size = min(brush_size + 1, self.brush_size)  # 修改这里
                        current_opacity = min(opacity + 0.1, 1.0)
                    else:
                        current_brush_size = brush_size
                        current_opacity = opacity
                    self._draw_brush_point(px, py, current_brush_size, current_opacity)
        
        self.last_draw_pos = (x, y)

    def _get_line_points(self, x1, y1, x2, y2):
        points = []
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        while True:
            points.append((x1, y1))
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy
        
        return points

    def _draw_point(self, x, y, intensity=1.0):
        if 0 <= x < 32 and 0 <= y < 32:
            self.board[x][y] = min(1.0, self.board[x][y] + intensity * 0.3)
            
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < 32 and 0 <= ny < 32 and (dx != 0 or dy != 0):
                        distance_factor = 1.0 / (abs(dx) + abs(dy) + 1)
                        self.board[nx][ny] = min(1.0, self.board[nx][ny] + intensity * 0.1 * distance_factor)

    def _draw_brush_point(self, x, y, brush_size, opacity):
        if brush_size == 1:
            self._draw_point(x, y, opacity)
        else:
            radius = brush_size // 2
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    distance = sqrt(dx*dx + dy*dy)
                    if distance <= radius:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < 32 and 0 <= ny < 32:
                            distance_factor = 1.0 - (distance / radius) * 0.5
                            current_intensity = opacity * distance_factor
                            self._draw_point(nx, ny, current_intensity)

    def _perform_search(self):
        self.train_data_list = []
        self.test_data_list = []
        
        for i in self.search_input_text:
            search_term = i.lower() if i else ""
            
            train_data_path = "./index/default_train_data/Ziptrain_data"
            if os.path.exists(train_data_path):
                for file in os.listdir(train_data_path):
                    if file.endswith(".zip") and (search_term in file.lower() or not search_term):
                        if file not in self.train_data_list:
                            self.train_data_list.append(file)
            
            test_data_path = "./index/default_train_data/Ziptest_data"
            if os.path.exists(test_data_path):
                for file in os.listdir(test_data_path):
                    if file.endswith(".zip") and (search_term in file.lower() or not search_term):
                        if file not in self.test_data_list:
                            self.test_data_list.append(file)

        if not self.search_input_text:
            self.train_data_list = os.listdir("./index/default_train_data/Ziptrain_data")
            self.test_data_list = os.listdir("./index/default_train_data/Ziptest_data")

        self.train_data_list.sort()
        self.test_data_list.sort()
            
        self.selected_train_items.clear()
        self.selected_test_items.clear()
        self.current_train_selection = -1
        self.current_test_selection = -1
        self.train_scroll_offset = 0
        self.test_scroll_offset = 0

    def _add_to_train_list(self):
        added_count = 0
        for idx in self.selected_train_items:
            if 0 <= idx < len(self.train_data_list):
                filename = self.train_data_list[idx]
                if filename not in self.train_list:
                    self.train_list.append(filename)
                    added_count += 1
        self.selected_train_items.clear()

    def _remove_from_train_list(self):
        removed_count = 0
        for idx in self.selected_train_items:
            if 0 <= idx < len(self.train_data_list):
                filename = self.train_data_list[idx]
                if filename in self.train_list:
                    self.train_list.remove(filename)
                    removed_count += 1
        self.selected_train_items.clear()

    def _add_to_test_list(self):
        added_count = 0
        for idx in self.selected_test_items:
            if 0 <= idx < len(self.test_data_list):
                filename = self.test_data_list[idx]
                if filename not in self.test_list:
                    self.test_list.append(filename)
                    added_count += 1
        self.selected_test_items.clear()

    def _remove_from_test_list(self):
        removed_count = 0
        for idx in self.selected_test_items:
            if 0 <= idx < len(self.test_data_list):
                filename = self.test_data_list[idx]
                if filename in self.test_list:
                    self.test_list.remove(filename)
                    removed_count += 1
        self.selected_test_items.clear()

    def create_rect(self, text, x, y, width, height, color=COLORS['button']):
        text_rect = pg.Rect(x, y, width, height)
        text_surface = self.font_(24).render(text, True, COLORS['text'])
        idx_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
        pg.draw.rect(self.screen, color, (x, y, width, height))
        self.screen.blit(text_surface, idx_rect)
        return text_rect
    
    def page_back(self):
        self.screen_page = 'main'

    def font_(self, size, type_='./font/2.ttc'):
        return pg.font.Font(type_, size)

if __name__ == "__main__":
    app = DrawingApp()
    app.run()
