#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口界面
应用程序的主要用户界面
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
from typing import Dict, Any, List
from datetime import datetime

# 导入AI问答引擎
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from modules.ai.qa_engine import QAEngine

class MainWindow:
    """主窗口类"""
    
    def __init__(self, root: tk.Tk, config_manager, db_manager):
        self.root = root
        self.config_manager = config_manager
        self.db_manager = db_manager
        
        # 初始化AI问答引擎
        self.qa_engine = QAEngine(db_manager, config_manager)
        
        # 界面组件
        self.notebook = None
        self.search_frame = None
        self.result_text = None
        self.query_entry = None
        self.category_combo = None
        
        # 初始化界面
        self._setup_window()
        self._create_widgets()
        self._setup_styles()
    
    def _setup_window(self):
        """设置主窗口"""
        # 窗口标题和图标
        self.root.title(self.config_manager.get("app.name", "AI末日生存求生向导"))
        
        # 窗口大小和位置
        width = self.config_manager.get("app.window_width", 1200)
        height = self.config_manager.get("app.window_height", 800)
        
        # 居中显示
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.minsize(800, 600)
        
        # 窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        
        # 设置主题
        try:
            style.theme_use('clam')
        except:
            pass
        
        # 自定义样式
        style.configure('Title.TLabel', font=('Microsoft YaHei', 16, 'bold'))
        style.configure('Subtitle.TLabel', font=('Microsoft YaHei', 12))
        style.configure('Search.TButton', font=('Microsoft YaHei', 10))
    
    def _create_widgets(self):
        """创建界面组件"""
        # 主容器
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="🔥 AI末日生存求生向导 🔥", style='Title.TLabel')
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # 场景和模型选择区域
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        control_frame.columnconfigure(2, weight=1)
        
        # 场景选择
        ttk.Label(control_frame, text="🎭 当前场景:").grid(row=0, column=0, padx=(0, 5))
        self.scenario_combo = ttk.Combobox(control_frame, state="readonly", width=15)
        self.scenario_combo.grid(row=0, column=1, padx=(0, 20))
        self.scenario_combo.bind('<<ComboboxSelected>>', self._on_scenario_change)
        
        # AI模型选择
        ttk.Label(control_frame, text="🤖 AI模型:").grid(row=0, column=3, padx=(0, 5))
        self.model_combo = ttk.Combobox(control_frame, state="readonly", width=15)
        self.model_combo.grid(row=0, column=4, padx=(0, 10))
        self.model_combo.bind('<<ComboboxSelected>>', self._on_model_change)
        
        # 模型配置按钮
        config_btn = ttk.Button(control_frame, text="⚙️ 配置", command=self._open_model_config)
        config_btn.grid(row=0, column=5)
        
        # 初始化选择框
        self._initialize_combo_boxes()
        
        # 创建选项卡
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.rowconfigure(2, weight=1)
        
        # 智能问答选项卡
        self._create_qa_tab()
        
        # 生存知识选项卡
        self._create_knowledge_tab()
        
        # 求生技能选项卡
        self._create_skills_tab()
        
        # 紧急情况选项卡
        self._create_emergency_tab()
        
        # 资源管理选项卡
        self._create_resources_tab()
        
        # 设置选项卡
        self._create_settings_tab()
    
    def _create_qa_tab(self):
        """创建智能问答选项卡"""
        qa_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(qa_frame, text="🤖 智能问答")
        
        # 配置网格
        qa_frame.columnconfigure(0, weight=1)
        qa_frame.rowconfigure(2, weight=1)
        
        # 说明文字
        info_label = ttk.Label(qa_frame, text="请输入您的生存问题，AI将为您提供专业建议：", style='Subtitle.TLabel')
        info_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # 搜索框架
        search_frame = ttk.Frame(qa_frame)
        search_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(0, weight=1)
        
        # 查询输入框
        self.query_entry = ttk.Entry(search_frame, font=('Microsoft YaHei', 11))
        self.query_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        self.query_entry.bind('<Return>', self._on_search)
        
        # 类别选择
        self.category_combo = ttk.Combobox(search_frame, values=["全部", "水源", "食物", "庇护所", "医疗", "生火", "导航"], state="readonly", width=10)
        self.category_combo.grid(row=0, column=1, padx=(0, 10))
        self.category_combo.set("全部")
        
        # 搜索按钮
        search_btn = ttk.Button(search_frame, text="🔍 搜索", command=self._on_search, style='Search.TButton')
        search_btn.grid(row=0, column=2)
        
        # 结果显示区域
        result_frame = ttk.LabelFrame(qa_frame, text="搜索结果", padding="10")
        result_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        # 结果文本框
        self.result_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, font=('Microsoft YaHei', 10))
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 初始显示欢迎信息
        welcome_text = """欢迎使用AI末日生存求生向导！🎯

这里是您的智能生存助手，可以帮助您：
• 🔍 搜索生存知识和技能
• 💡 获取个性化生存建议
• 🚨 处理紧急情况
• 📋 管理生存资源

请在上方输入您的问题，例如：
- "如何寻找安全的水源？"
- "怎样搭建临时庇护所？"
- "野外可食用植物有哪些？"
- "如何处理外伤？"

开始您的生存之旅吧！💪"""
        
        self.result_text.insert(tk.END, welcome_text)
        self.result_text.config(state=tk.DISABLED)
    
    def _create_knowledge_tab(self):
        """创建生存知识选项卡"""
        knowledge_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(knowledge_frame, text="📚 生存知识")
        
        # 配置网格
        knowledge_frame.columnconfigure(0, weight=1)
        knowledge_frame.rowconfigure(1, weight=1)
        
        # 类别选择框架
        category_frame = ttk.LabelFrame(knowledge_frame, text="知识分类", padding="10")
        category_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 类别按钮
        categories = ["水源", "食物", "庇护所", "医疗", "生火", "导航", "工具制作"]
        for i, category in enumerate(categories):
            btn = ttk.Button(category_frame, text=f"📖 {category}", 
                           command=lambda c=category: self._show_knowledge_category(c))
            btn.grid(row=i//4, column=i%4, padx=5, pady=5, sticky=tk.W)
        
        # 知识显示区域
        self.knowledge_text = scrolledtext.ScrolledText(knowledge_frame, wrap=tk.WORD, font=('Microsoft YaHei', 10))
        self.knowledge_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 显示默认内容
        self._show_knowledge_category("水源")
    
    def _create_skills_tab(self):
        """创建求生技能选项卡"""
        skills_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(skills_frame, text="🛠️ 求生技能")
        
        # 配置网格
        skills_frame.columnconfigure(0, weight=1)
        skills_frame.rowconfigure(1, weight=1)
        
        # 技能类别
        skill_category_frame = ttk.LabelFrame(skills_frame, text="技能分类", padding="10")
        skill_category_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        skill_categories = ["生火", "水源", "食物获取", "庇护所建造", "工具制作", "导航定位"]
        for i, category in enumerate(skill_categories):
            btn = ttk.Button(skill_category_frame, text=f"🔧 {category}",
                           command=lambda c=category: self._show_skills_category(c))
            btn.grid(row=i//3, column=i%3, padx=5, pady=5, sticky=tk.W)
        
        # 技能显示区域
        self.skills_text = scrolledtext.ScrolledText(skills_frame, wrap=tk.WORD, font=('Microsoft YaHei', 10))
        self.skills_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 显示默认技能
        self._show_skills_category("生火")
    
    def _create_emergency_tab(self):
        """创建紧急情况选项卡"""
        emergency_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(emergency_frame, text="🚨 紧急情况")
        
        # 配置网格
        emergency_frame.columnconfigure(0, weight=1)
        emergency_frame.rowconfigure(1, weight=1)
        
        # 紧急情况类型
        emergency_type_frame = ttk.LabelFrame(emergency_frame, text="紧急情况类型", padding="10")
        emergency_type_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        emergency_types = ["外伤出血", "骨折", "烧伤", "中毒", "失温", "中暑", "迷路", "野兽攻击"]
        for i, etype in enumerate(emergency_types):
            btn = ttk.Button(emergency_type_frame, text=f"⚠️ {etype}",
                           command=lambda e=etype: self._show_emergency_procedure(e))
            btn.grid(row=i//4, column=i%4, padx=5, pady=5, sticky=tk.W)
        
        # 紧急处理显示区域
        self.emergency_text = scrolledtext.ScrolledText(emergency_frame, wrap=tk.WORD, font=('Microsoft YaHei', 10))
        self.emergency_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 显示默认紧急情况
        self._show_emergency_procedure("外伤出血")
    
    def _create_resources_tab(self):
        """创建资源管理选项卡"""
        resources_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(resources_frame, text="📦 资源管理")
        
        # 资源清单
        resources_label = ttk.Label(resources_frame, text="生存资源清单管理", style='Subtitle.TLabel')
        resources_label.grid(row=0, column=0, pady=(0, 10))
        
        # 基本资源清单
        resources_text = scrolledtext.ScrolledText(resources_frame, wrap=tk.WORD, font=('Microsoft YaHei', 10))
        resources_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        resources_frame.columnconfigure(0, weight=1)
        resources_frame.rowconfigure(1, weight=1)
        
        resource_content = """🎒 生存资源清单

💧 水源相关：
• 净水片/净水器
• 水壶/水袋
• 收集雨水的容器
• 过滤材料（沙子、木炭、布料）

🍖 食物相关：
• 压缩饼干/能量棒
• 罐头食品
• 钓鱼工具
• 狩猎工具（合法范围内）

🏠 庇护所相关：
• 帐篷/防水布
• 睡袋/毯子
• 绳索/绳子
• 工具（斧头、锯子、铲子）

🔥 生火相关：
• 打火机/火柴
• 火绒/引火物
• 防风火柴
• 燃料（木材、酒精）

🏥 医疗相关：
• 急救包
• 消毒用品
• 绷带/纱布
• 常用药品

🧭 导航相关：
• 指南针
• 地图
• GPS设备
• 信号设备（哨子、镜子）

🔧 工具相关：
• 多功能刀具
• 手电筒
• 电池
• 维修工具

📝 提示：定期检查和更新您的资源清单，确保物品完好且在有效期内。"""
        
        resources_text.insert(tk.END, resource_content)
        resources_text.config(state=tk.DISABLED)
    
    def _create_settings_tab(self):
        """创建设置选项卡"""
        settings_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(settings_frame, text="⚙️ 设置")
        
        # 设置标题
        settings_label = ttk.Label(settings_frame, text="应用程序设置", style='Subtitle.TLabel')
        settings_label.grid(row=0, column=0, pady=(0, 20))
        
        # 设置选项
        ttk.Label(settings_frame, text="界面主题：").grid(row=1, column=0, sticky=tk.W, pady=5)
        theme_combo = ttk.Combobox(settings_frame, values=["浅色", "深色"], state="readonly")
        theme_combo.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        theme_combo.set("浅色")
        
        ttk.Label(settings_frame, text="字体大小：").grid(row=2, column=0, sticky=tk.W, pady=5)
        font_size_combo = ttk.Combobox(settings_frame, values=["小", "中", "大"], state="readonly")
        font_size_combo.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        font_size_combo.set("中")
        
        # 功能开关
        ttk.Label(settings_frame, text="功能设置：").grid(row=3, column=0, sticky=tk.W, pady=(20, 5))
        
        self.tips_var = tk.BooleanVar(value=True)
        tips_check = ttk.Checkbutton(settings_frame, text="显示使用提示", variable=self.tips_var)
        tips_check.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        self.auto_save_var = tk.BooleanVar(value=True)
        auto_save_check = ttk.Checkbutton(settings_frame, text="自动保存查询历史", variable=self.auto_save_var)
        auto_save_check.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # 保存设置按钮
        save_btn = ttk.Button(settings_frame, text="💾 保存设置", command=self._save_settings)
        save_btn.grid(row=6, column=0, columnspan=2, pady=(20, 0))
    
    def _on_search(self, event=None):
        """处理搜索事件"""
        query = self.query_entry.get().strip()
        if not query:
            messagebox.showwarning("提示", "请输入搜索内容")
            return
        
        # 使用AI问答引擎处理问题
        try:
            ai_response = self.qa_engine.process_question(query)
            
            # 显示AI回答
            self.result_text.config(state=tk.NORMAL)
            self.result_text.delete(1.0, tk.END)
            
            self.result_text.insert(tk.END, f"🤖 AI助手回答：\n\n")
            self.result_text.insert(tk.END, ai_response)
            
            # 如果用户选择了特定分类，也显示相关的数据库搜索结果
            category = self.category_combo.get()
            if category != "全部":
                results = self.db_manager.search_knowledge(query, category)
                if results:
                    self.result_text.insert(tk.END, "\n\n" + "="*60 + "\n")
                    self.result_text.insert(tk.END, f"📚 {category}类别的详细信息：\n\n")
                    
                    for i, result in enumerate(results[:2], 1):  # 限制显示2条
                        self.result_text.insert(tk.END, f"📖 {i}. {result['title']}\n")
                        self.result_text.insert(tk.END, f"难度: {'⭐' * result['difficulty_level']} | 重要性: {'🔥' * result['priority']}\n")
                        self.result_text.insert(tk.END, f"{result['content'][:300]}...\n\n")
            
            self.result_text.config(state=tk.DISABLED)
            
            # 保存查询历史
            if hasattr(self, 'auto_save_var') and self.auto_save_var.get():
                self.db_manager.add_query_history(query, ai_response[:200] + "...", "ai_chat")
                
        except Exception as e:
            messagebox.showerror("错误", f"处理问题时发生错误：{str(e)}")
            print(f"AI问答错误: {e}")
    
    def _show_knowledge_category(self, category: str):
        """显示指定类别的知识"""
        results = self.db_manager.search_knowledge("", category)
        
        self.knowledge_text.config(state=tk.NORMAL)
        self.knowledge_text.delete(1.0, tk.END)
        
        self.knowledge_text.insert(tk.END, f"📚 {category} 相关知识\n\n")
        
        if results:
            for i, result in enumerate(results, 1):
                self.knowledge_text.insert(tk.END, f"📖 {i}. {result['title']}\n")
                self.knowledge_text.insert(tk.END, f"难度等级: {'⭐' * result['difficulty_level']} | 重要性: {'🔥' * result['priority']}\n")
                self.knowledge_text.insert(tk.END, f"{result['content']}\n")
                if result['tags']:
                    self.knowledge_text.insert(tk.END, f"标签: {result['tags']}\n")
                self.knowledge_text.insert(tk.END, "=" * 60 + "\n\n")
        else:
            self.knowledge_text.insert(tk.END, f"暂无 {category} 相关知识，请稍后更新。\n")
        
        self.knowledge_text.config(state=tk.DISABLED)
    
    def _show_skills_category(self, category: str):
        """显示指定类别的技能"""
        results = self.db_manager.get_skills_by_category(category)
        
        self.skills_text.config(state=tk.NORMAL)
        self.skills_text.delete(1.0, tk.END)
        
        self.skills_text.insert(tk.END, f"🛠️ {category} 相关技能\n\n")
        
        if results:
            for i, skill in enumerate(results, 1):
                self.skills_text.insert(tk.END, f"🔧 {i}. {skill['name']}\n")
                self.skills_text.insert(tk.END, f"描述: {skill['description']}\n")
                self.skills_text.insert(tk.END, f"难度: {'⭐' * skill['difficulty_level']} | 预计时间: {skill['estimated_time']}分钟\n\n")
                
                # 显示步骤
                try:
                    steps = json.loads(skill['steps'])
                    self.skills_text.insert(tk.END, "📋 操作步骤:\n")
                    for j, step in enumerate(steps, 1):
                        self.skills_text.insert(tk.END, f"  {j}. {step}\n")
                except:
                    self.skills_text.insert(tk.END, f"步骤: {skill['steps']}\n")
                
                # 显示所需材料
                if skill['required_materials']:
                    try:
                        materials = json.loads(skill['required_materials'])
                        self.skills_text.insert(tk.END, "\n🎒 所需材料:\n")
                        for material in materials:
                            self.skills_text.insert(tk.END, f"  • {material}\n")
                    except:
                        self.skills_text.insert(tk.END, f"\n所需材料: {skill['required_materials']}\n")
                
                # 安全提示
                if skill['safety_notes']:
                    self.skills_text.insert(tk.END, f"\n⚠️ 安全提示: {skill['safety_notes']}\n")
                
                self.skills_text.insert(tk.END, "=" * 60 + "\n\n")
        else:
            self.skills_text.insert(tk.END, f"暂无 {category} 相关技能，请稍后更新。\n")
        
        self.skills_text.config(state=tk.DISABLED)
    
    def _show_emergency_procedure(self, emergency_type: str):
        """显示紧急情况处理程序"""
        results = self.db_manager.get_emergency_procedures(emergency_type)
        
        self.emergency_text.config(state=tk.NORMAL)
        self.emergency_text.delete(1.0, tk.END)
        
        self.emergency_text.insert(tk.END, f"🚨 {emergency_type} 处理程序\n\n")
        
        if results:
            for i, procedure in enumerate(results, 1):
                severity_stars = "🔴" * procedure['severity_level']
                self.emergency_text.insert(tk.END, f"⚠️ {procedure['emergency_type']}\n")
                self.emergency_text.insert(tk.END, f"严重程度: {severity_stars}\n\n")
                
                self.emergency_text.insert(tk.END, f"🚨 立即行动: {procedure['immediate_actions']}\n\n")
                
                # 详细步骤
                try:
                    steps = json.loads(procedure['detailed_steps'])
                    self.emergency_text.insert(tk.END, "📋 详细处理步骤:\n")
                    for j, step in enumerate(steps, 1):
                        self.emergency_text.insert(tk.END, f"  {j}. {step}\n")
                except:
                    self.emergency_text.insert(tk.END, f"处理步骤: {procedure['detailed_steps']}\n")
                
                # 所需资源
                if procedure['required_resources']:
                    try:
                        resources = json.loads(procedure['required_resources'])
                        self.emergency_text.insert(tk.END, "\n🎒 所需资源:\n")
                        for resource in resources:
                            self.emergency_text.insert(tk.END, f"  • {resource}\n")
                    except:
                        self.emergency_text.insert(tk.END, f"\n所需资源: {procedure['required_resources']}\n")
                
                # 预防提示
                if procedure['prevention_tips']:
                    self.emergency_text.insert(tk.END, f"\n💡 预防提示: {procedure['prevention_tips']}\n")
                
                self.emergency_text.insert(tk.END, "=" * 60 + "\n\n")
        else:
            self.emergency_text.insert(tk.END, f"暂无 {emergency_type} 相关处理程序，请稍后更新。\n")
        
        self.emergency_text.config(state=tk.DISABLED)
    
    def _save_settings(self):
        """保存设置"""
        # 这里可以添加保存设置的逻辑
        messagebox.showinfo("提示", "设置已保存！")
    
    def _initialize_combo_boxes(self):
        """初始化选择框"""
        try:
            # 初始化场景选择框
            scenarios = self.config_manager.get("scenarios.available_scenarios", {})
            scenario_options = []
            for scenario_id, scenario_info in scenarios.items():
                icon = scenario_info.get("icon", "")
                name = scenario_info.get("name", scenario_id)
                scenario_options.append(f"{icon} {name}")
            
            self.scenario_combo['values'] = scenario_options
            
            # 设置当前场景
            current_scenario = self.config_manager.get("scenarios.current_scenario", "normal")
            current_scenario_info = scenarios.get(current_scenario, {})
            if current_scenario_info:
                icon = current_scenario_info.get("icon", "")
                name = current_scenario_info.get("name", current_scenario)
                self.scenario_combo.set(f"{icon} {name}")
            
            # 初始化AI模型选择框
            if hasattr(self.qa_engine, 'llm_manager') and self.qa_engine.llm_manager:
                models = self.qa_engine.llm_manager.get_available_models()
                model_options = []
                for model_id, model_info in models.items():
                    name = model_info.get("name", model_id)
                    status = "✅" if model_info.get("has_api_key", False) else "❌"
                    model_options.append(f"{status} {name}")
                
                self.model_combo['values'] = model_options
                
                # 设置当前模型
                current_model_info = self.qa_engine.llm_manager.get_current_model_info()
                if current_model_info:
                    name = current_model_info.get("name", "")
                    status = "✅" if current_model_info.get("has_api_key", False) else "❌"
                    self.model_combo.set(f"{status} {name}")
            else:
                self.model_combo['values'] = ["✅ 本地规则引擎"]
                self.model_combo.set("✅ 本地规则引擎")
                
        except Exception as e:
            print(f"初始化选择框失败: {e}")
    
    def _on_scenario_change(self, event=None):
        """场景切换事件处理"""
        try:
            selected = self.scenario_combo.get()
            if not selected:
                return
            
            # 解析选择的场景
            scenarios = self.config_manager.get("scenarios.available_scenarios", {})
            for scenario_id, scenario_info in scenarios.items():
                icon = scenario_info.get("icon", "")
                name = scenario_info.get("name", scenario_id)
                if selected == f"{icon} {name}":
                    # 切换场景
                    if hasattr(self.qa_engine, 'scenario_handler') and self.qa_engine.scenario_handler:
                        success = self.qa_engine.scenario_handler.set_current_scenario(scenario_id)
                        if success:
                            messagebox.showinfo("场景切换", f"已切换到 {name} 场景")
                            # 更新欢迎信息
                            self._update_welcome_message()
                        else:
                            messagebox.showerror("错误", "场景切换失败")
                    break
                    
        except Exception as e:
            messagebox.showerror("错误", f"场景切换时发生错误：{str(e)}")
    
    def _on_model_change(self, event=None):
        """AI模型切换事件处理"""
        try:
            selected = self.model_combo.get()
            if not selected or not hasattr(self.qa_engine, 'llm_manager') or not self.qa_engine.llm_manager:
                return
            
            # 解析选择的模型
            models = self.qa_engine.llm_manager.get_available_models()
            for model_id, model_info in models.items():
                name = model_info.get("name", model_id)
                status = "✅" if model_info.get("has_api_key", False) else "❌"
                if selected == f"{status} {name}":
                    if not model_info.get("has_api_key", False) and model_id != "local":
                        messagebox.showwarning("警告", f"{name} 未配置API密钥，请先配置")
                        return
                    
                    # 切换模型
                    success = self.qa_engine.llm_manager.set_current_model(model_id)
                    if success:
                        messagebox.showinfo("模型切换", f"已切换到 {name}")
                    else:
                        messagebox.showerror("错误", "模型切换失败")
                    break
                    
        except Exception as e:
            messagebox.showerror("错误", f"模型切换时发生错误：{str(e)}")
    
    def _open_model_config(self):
        """打开模型配置窗口"""
        try:
            if not hasattr(self.qa_engine, 'llm_manager') or not self.qa_engine.llm_manager:
                messagebox.showinfo("提示", "当前使用本地规则引擎，无需配置")
                return
            
            # 创建配置窗口
            config_window = tk.Toplevel(self.root)
            config_window.title("AI模型配置")
            config_window.geometry("500x400")
            config_window.transient(self.root)
            config_window.grab_set()
            
            # 配置窗口内容
            self._create_model_config_content(config_window)
            
        except Exception as e:
            messagebox.showerror("错误", f"打开配置窗口失败：{str(e)}")
    
    def _create_model_config_content(self, parent):
        """创建模型配置窗口内容"""
        main_frame = ttk.Frame(parent, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="🤖 AI模型配置", font=('Microsoft YaHei', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # 模型列表
        models = self.qa_engine.llm_manager.get_available_models()
        
        for model_id, model_info in models.items():
            if model_id == "local":
                continue
                
            # 模型框架
            model_frame = ttk.LabelFrame(main_frame, text=f"{model_info['name']}", padding="10")
            model_frame.pack(fill=tk.X, pady=(0, 10))
            
            # API密钥输入
            ttk.Label(model_frame, text="API密钥:").pack(anchor=tk.W)
            
            api_key_var = tk.StringVar()
            api_key_entry = ttk.Entry(model_frame, textvariable=api_key_var, show="*", width=50)
            api_key_entry.pack(fill=tk.X, pady=(5, 10))
            
            # 按钮框架
            btn_frame = ttk.Frame(model_frame)
            btn_frame.pack(fill=tk.X)
            
            # 保存按钮
            save_btn = ttk.Button(btn_frame, text="💾 保存", 
                                command=lambda mid=model_id, var=api_key_var: self._save_api_key(mid, var.get()))
            save_btn.pack(side=tk.LEFT, padx=(0, 10))
            
            # 测试按钮
            test_btn = ttk.Button(btn_frame, text="🧪 测试", 
                                command=lambda mid=model_id: self._test_api_connection(mid))
            test_btn.pack(side=tk.LEFT)
            
            # 状态标签
            status_label = ttk.Label(btn_frame, text="")
            status_label.pack(side=tk.RIGHT)
            
            # 显示当前状态
            if model_info.get("has_api_key", False):
                status_label.config(text="✅ 已配置", foreground="green")
                api_key_entry.insert(0, "*" * 20)  # 显示占位符
            else:
                status_label.config(text="❌ 未配置", foreground="red")
    
    def _save_api_key(self, model_id: str, api_key: str):
        """保存API密钥"""
        try:
            if not api_key.strip():
                messagebox.showwarning("警告", "请输入API密钥")
                return
            
            # 如果是占位符，不保存
            if api_key.strip() == "*" * 20:
                messagebox.showinfo("提示", "API密钥未更改")
                return
            
            success = self.qa_engine.llm_manager.set_api_key(model_id, api_key.strip())
            if success:
                messagebox.showinfo("成功", "API密钥保存成功")
                # 刷新选择框
                self._initialize_combo_boxes()
            else:
                messagebox.showerror("错误", "API密钥保存失败")
                
        except Exception as e:
            messagebox.showerror("错误", f"保存API密钥时发生错误：{str(e)}")
    
    def _test_api_connection(self, model_id: str):
        """测试API连接"""
        try:
            result = self.qa_engine.llm_manager.test_api_connection(model_id)
            if result["success"]:
                messagebox.showinfo("测试成功", result["message"])
            else:
                messagebox.showerror("测试失败", result["message"])
                
        except Exception as e:
            messagebox.showerror("错误", f"测试连接时发生错误：{str(e)}")
    
    def _update_welcome_message(self):
        """更新欢迎信息"""
        try:
            if hasattr(self.qa_engine, 'scenario_handler') and self.qa_engine.scenario_handler:
                scenario_info = self.qa_engine.scenario_handler.get_current_scenario_info()
                scenario_name = scenario_info.get("name", "普通场景")
                scenario_icon = scenario_info.get("icon", "🏕️")
                scenario_desc = scenario_info.get("description", "标准的野外生存环境")
                
                welcome_text = f"""欢迎使用AI末日生存求生向导！🎯

当前场景：{scenario_icon} {scenario_name}
场景描述：{scenario_desc}

这里是您的智能生存助手，可以帮助您：
• 🔍 搜索生存知识和技能
• 💡 获取个性化生存建议
• 🚨 处理紧急情况
• 📋 管理生存资源

请在上方输入您的问题，例如：
- "如何寻找安全的水源？"
- "怎样搭建临时庇护所？"
- "野外可食用植物有哪些？"
- "如何处理外伤？"

开始您的生存之旅吧！💪"""
                
                self.result_text.config(state=tk.NORMAL)
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, welcome_text)
                self.result_text.config(state=tk.DISABLED)
                
        except Exception as e:
            print(f"更新欢迎信息失败: {e}")
    
    def _on_closing(self):
        """窗口关闭事件处理"""
        if messagebox.askokcancel("退出", "确定要退出程序吗？"):
            self.root.quit()
            self.root.destroy()