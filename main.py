#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI末日生存求生向导软件
主程序入口
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
import json
import sqlite3
from pathlib import Path

# 添加模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from modules.ui.main_window import MainWindow
from modules.database.db_manager import DatabaseManager
from modules.utils.config_manager import ConfigManager

class SurvivalGuideApp:
    """主应用程序类"""
    
    def __init__(self):
        self.root = None
        self.config_manager = None
        self.db_manager = None
        self.main_window = None
        
    def initialize(self):
        """初始化应用程序"""
        try:
            # 创建必要的目录
            self._create_directories()
            
            # 初始化配置管理器
            self.config_manager = ConfigManager()
            
            # 初始化数据库管理器
            self.db_manager = DatabaseManager()
            self.db_manager.initialize_database()
            
            # 创建主窗口
            self.root = tk.Tk()
            self.main_window = MainWindow(self.root, self.config_manager, self.db_manager)
            
            return True
            
        except Exception as e:
            messagebox.showerror("初始化错误", f"应用程序初始化失败：{str(e)}")
            return False
    
    def _create_directories(self):
        """创建必要的目录结构"""
        directories = [
            'config',
            'data',
            'modules/ui',
            'modules/ai',
            'modules/database',
            'modules/utils',
            'resources'
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def run(self):
        """运行应用程序"""
        if self.initialize():
            try:
                self.root.mainloop()
            except KeyboardInterrupt:
                self.shutdown()
            except Exception as e:
                messagebox.showerror("运行错误", f"应用程序运行时发生错误：{str(e)}")
        else:
            sys.exit(1)
    
    def shutdown(self):
        """关闭应用程序"""
        try:
            if self.db_manager:
                self.db_manager.close()
            if self.root:
                self.root.quit()
                self.root.destroy()
        except Exception as e:
            print(f"关闭应用程序时发生错误：{str(e)}")

def main():
    """主函数"""
    print("启动AI末日生存求生向导软件...")
    
    app = SurvivalGuideApp()
    
    try:
        app.run()
    except Exception as e:
        print(f"程序运行失败：{str(e)}")
        sys.exit(1)
    finally:
        app.shutdown()

if __name__ == "__main__":
    main()