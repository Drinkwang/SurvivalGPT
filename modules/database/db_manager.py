#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库管理器
负责SQLite数据库的创建、连接和基本操作
"""

import sqlite3
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

class DatabaseManager:
    """数据库管理器类"""
    
    def __init__(self, db_path: str = "data/survival_guide.db"):
        self.db_path = db_path
        self.connection = None
        self.cursor = None
    
    def connect(self) -> bool:
        """连接数据库"""
        try:
            # 确保数据目录存在
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # 使结果可以通过列名访问
            self.cursor = self.connection.cursor()
            return True
        except Exception as e:
            print(f"数据库连接失败: {e}")
            return False
    
    def close(self):
        """关闭数据库连接"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
        except Exception as e:
            print(f"关闭数据库连接时发生错误: {e}")
    
    def initialize_database(self) -> bool:
        """初始化数据库，创建所有必要的表"""
        if not self.connect():
            return False
        
        try:
            # 创建生存知识表
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS survival_knowledge (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    difficulty_level INTEGER DEFAULT 1,
                    priority INTEGER DEFAULT 1,
                    tags TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建求生技能表
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS survival_skills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    category TEXT NOT NULL,
                    steps TEXT NOT NULL,
                    required_materials TEXT,
                    difficulty_level INTEGER DEFAULT 1,
                    estimated_time INTEGER,
                    safety_notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建紧急情况处理表
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS emergency_procedures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    emergency_type TEXT NOT NULL,
                    severity_level INTEGER NOT NULL,
                    immediate_actions TEXT NOT NULL,
                    detailed_steps TEXT NOT NULL,
                    required_resources TEXT,
                    prevention_tips TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建用户查询历史表
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS query_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query_text TEXT NOT NULL,
                    response_text TEXT,
                    query_type TEXT,
                    satisfaction_rating INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建用户偏好设置表
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    preference_key TEXT UNIQUE NOT NULL,
                    preference_value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建资源清单表
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS resource_inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    quantity INTEGER DEFAULT 0,
                    unit TEXT,
                    importance_level INTEGER DEFAULT 1,
                    expiry_date DATE,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建生存场景表
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS survival_scenarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scenario_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    threat_level INTEGER DEFAULT 1,
                    special_considerations TEXT,
                    required_equipment TEXT,
                    survival_tips TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建场景特定知识表
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS scenario_knowledge (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scenario_type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    difficulty_level INTEGER DEFAULT 1,
                    priority INTEGER DEFAULT 1,
                    tags TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建场景特定技能表
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS scenario_skills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scenario_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    category TEXT NOT NULL,
                    steps TEXT NOT NULL,
                    required_materials TEXT,
                    difficulty_level INTEGER DEFAULT 1,
                    estimated_time INTEGER,
                    safety_notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建场景威胁表
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS scenario_threats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scenario_type TEXT NOT NULL,
                    threat_name TEXT NOT NULL,
                    threat_type TEXT NOT NULL,
                    danger_level INTEGER NOT NULL,
                    description TEXT,
                    identification_signs TEXT,
                    countermeasures TEXT,
                    avoidance_tips TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.connection.commit()
            
            # 初始化科幻场景数据
            self._initialize_scenario_data()
            
            # 初始化基础数据
            self._initialize_basic_data()
            
            return True
            
        except Exception as e:
            print(f"初始化数据库失败: {e}")
            self.connection.rollback()
            return False
    
    def _initialize_basic_data(self):
        """初始化基础数据"""
        # 检查是否已有数据
        self.cursor.execute("SELECT COUNT(*) FROM survival_knowledge")
        if self.cursor.fetchone()[0] > 0:
            return  # 已有数据，不需要初始化
        
        # 插入基础生存知识
        basic_knowledge = [
            ("水源", "寻找安全水源", "在野外生存中，水是最重要的资源。人体可以在没有食物的情况下生存数周，但没有水只能生存3-5天。寻找水源的方法包括：1. 寻找流动的河流或溪流 2. 收集雨水 3. 寻找地下水源 4. 从植物中提取水分", 2, 5, "水源,生存,基础"),
            ("食物", "可食用植物识别", "在野外识别可食用植物是重要的生存技能。安全原则：1. 避免有毒植物 2. 进行可食性测试 3. 少量尝试 4. 观察身体反应。常见可食用植物包括蒲公英、车前草、野葱等。", 3, 4, "食物,植物,识别"),
            ("庇护所", "搭建临时庇护所", "庇护所能保护你免受恶劣天气影响。基本原则：1. 选择合适位置 2. 保持干燥 3. 保温隔热 4. 通风良好。可以使用树枝、树叶、石头等自然材料搭建。", 2, 4, "庇护所,搭建,保暖"),
            ("医疗", "基础急救知识", "掌握基础急救技能可以在紧急情况下挽救生命。包括：1. 止血处理 2. 骨折固定 3. 烧伤处理 4. 中毒处理 5. 心肺复苏等。", 4, 5, "医疗,急救,治疗")
        ]
        
        for knowledge in basic_knowledge:
            self.cursor.execute("""
                INSERT INTO survival_knowledge (category, title, content, difficulty_level, priority, tags)
                VALUES (?, ?, ?, ?, ?, ?)
            """, knowledge)
        
        # 插入基础求生技能
        basic_skills = [
            ("生火技能", "在野外生存中生火的基本技能", "生火", 
             json.dumps(["收集干燥的引火材料", "准备火绒和引火物", "搭建火堆结构", "点燃火绒", "逐步添加燃料"]),
             json.dumps(["火绒", "引火物", "干燥木材", "打火工具"]), 2, 30, "注意防火安全，选择合适地点"),
            ("净水技术", "将不安全的水源净化为可饮用水", "水源",
             json.dumps(["过滤大颗粒杂质", "煮沸消毒", "使用净水片", "自然沉淀", "紫外线消毒"]),
             json.dumps(["过滤材料", "容器", "热源", "净水片"]), 2, 20, "确保水源彻底净化后再饮用")
        ]
        
        for skill in basic_skills:
            self.cursor.execute("""
                INSERT INTO survival_skills (name, description, category, steps, required_materials, difficulty_level, estimated_time, safety_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, skill)
        
        # 插入紧急情况处理
        emergency_procedures = [
            ("外伤出血", 3, "立即压迫止血", 
             json.dumps(["评估伤情", "清洁双手", "直接压迫伤口", "抬高受伤部位", "包扎固定", "监测生命体征"]),
             json.dumps(["干净布料", "绷带", "消毒用品"]), "避免接触污染物，保持伤口清洁"),
            ("食物中毒", 2, "停止进食，大量饮水",
             json.dumps(["停止进食可疑食物", "大量饮用清水", "诱导呕吐（如适用）", "保持温暖", "监测症状", "寻求医疗帮助"]),
             json.dumps(["清水", "保温材料"]), "严重症状时立即寻求专业医疗帮助")
        ]
        
        for procedure in emergency_procedures:
            self.cursor.execute("""
                INSERT INTO emergency_procedures (emergency_type, severity_level, immediate_actions, detailed_steps, required_resources, prevention_tips)
                VALUES (?, ?, ?, ?, ?, ?)
            """, procedure)
        
        self.connection.commit()
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[sqlite3.Row]:
        """执行查询并返回结果"""
        try:
            if not self.connection:
                self.connect()
            
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"执行查询失败: {e}")
            return []
    
    def execute_update(self, query: str, params: Tuple = ()) -> bool:
        """执行更新操作"""
        try:
            if not self.connection:
                self.connect()
            
            self.cursor.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            print(f"执行更新失败: {e}")
            self.connection.rollback()
            return False
    
    def search_knowledge(self, keyword: str, category: str = None) -> List[Dict]:
        """搜索生存知识"""
        query = "SELECT * FROM survival_knowledge WHERE (title LIKE ? OR content LIKE ? OR tags LIKE ?)"
        params = [f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"]
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        query += " ORDER BY priority DESC, difficulty_level ASC"
        
        results = self.execute_query(query, tuple(params))
        return [dict(row) for row in results]
    
    def get_skills_by_category(self, category: str) -> List[Dict]:
        """根据类别获取技能"""
        query = "SELECT * FROM survival_skills WHERE category = ? ORDER BY difficulty_level ASC"
        results = self.execute_query(query, (category,))
        return [dict(row) for row in results]
    
    def get_emergency_procedures(self, emergency_type: str = None) -> List[Dict]:
        """获取紧急情况处理程序"""
        if emergency_type:
            query = "SELECT * FROM emergency_procedures WHERE emergency_type LIKE ? ORDER BY severity_level DESC"
            params = (f"%{emergency_type}%",)
        else:
            query = "SELECT * FROM emergency_procedures ORDER BY severity_level DESC"
            params = ()
        
        results = self.execute_query(query, params)
        return [dict(row) for row in results]
    
    def add_query_history(self, query_text: str, response_text: str, query_type: str = None) -> bool:
        """添加查询历史"""
        query = """
            INSERT INTO query_history (query_text, response_text, query_type)
            VALUES (?, ?, ?)
        """
        return self.execute_update(query, (query_text, response_text, query_type))
    
    def _initialize_scenario_data(self):
        """初始化场景数据"""
        # 检查是否已有场景数据
        self.cursor.execute("SELECT COUNT(*) FROM survival_scenarios")
        if self.cursor.fetchone()[0] > 0:
            return  # 已有数据，不需要初始化
        
        # 插入基础场景信息
        scenarios = [
            ("zombie", "僵尸末日", "僵尸病毒爆发，死者复活攻击活人", 5, 
             "避免噪音、群体行动、寻找安全区域", 
             json.dumps(["近战武器", "防护装备", "医疗用品", "食物储备", "通讯设备"]),
             "保持安静、避开人群密集区、建立防御工事"),
            ("biochemical", "生化危机", "生化武器泄露，环境被污染", 4,
             "防护服必需、空气过滤、去污处理",
             json.dumps(["防护服", "防毒面具", "检测仪器", "去污剂", "密封容器"]),
             "穿戴防护装备、避免接触污染物、定期检测"),
            ("nuclear", "核辐射", "核事故导致大范围辐射污染", 4,
             "辐射防护、碘片服用、避难所选择",
             json.dumps(["辐射检测仪", "碘片", "防护服", "铅板", "密封食物"]),
             "远离辐射源、服用碘片、寻找地下避难所"),
            ("alien", "外星入侵", "外星生物入侵地球", 5,
             "隐蔽行动、避免探测、团队合作",
             json.dumps(["隐蔽装备", "通讯干扰器", "能量武器", "探测设备", "急救包"]),
             "保持隐蔽、避免使用电子设备、寻找地下庇护所")
        ]
        
        for scenario in scenarios:
            self.cursor.execute("""
                INSERT INTO survival_scenarios (scenario_type, name, description, threat_level, special_considerations, required_equipment, survival_tips)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, scenario)
        
        # 插入僵尸场景知识
        zombie_knowledge = [
            ("zombie", "防御", "僵尸防御策略", 
             "僵尸通过咬伤传播病毒，具有强烈的攻击性但行动缓慢。防御要点：1. 建立高墙或障碍物 2. 设置陷阱和警报系统 3. 准备近战武器 4. 保持安静避免吸引注意 5. 建立多个逃生路线", 
             3, 5, "僵尸,防御,安全"),
            ("zombie", "医疗", "僵尸咬伤处理", 
             "被僵尸咬伤后病毒潜伏期约6-24小时。处理方法：1. 立即清洗伤口 2. 使用消毒剂处理 3. 服用抗病毒药物（如有） 4. 隔离观察 5. 准备最坏情况的应对措施。注意：一旦出现发热、意识模糊等症状，感染已不可逆转。", 
             4, 5, "僵尸,咬伤,感染,医疗"),
            ("zombie", "觅食", "僵尸环境下的食物获取", 
             "在僵尸横行的环境中获取食物需要极度谨慎。策略：1. 夜间行动，僵尸视力较差 2. 搜索被遗弃的商店和住宅 3. 建立室内种植系统 4. 捕捉小动物 5. 储存罐头和干粮。避免在僵尸聚集区域觅食。", 
             3, 4, "僵尸,食物,觅食,夜间")
        ]
        
        for knowledge in zombie_knowledge:
            self.cursor.execute("""
                INSERT INTO scenario_knowledge (scenario_type, category, title, content, difficulty_level, priority, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, knowledge)
        
        # 插入生化场景知识
        biochemical_knowledge = [
            ("biochemical", "防护", "生化防护装备使用", 
             "生化环境中防护装备是生存关键。使用要点：1. 穿戴全封闭防护服 2. 使用正压式呼吸器 3. 定期检查装备密封性 4. 建立去污程序 5. 准备备用装备。进入污染区前必须检查所有装备完整性。", 
             4, 5, "生化,防护,装备,安全"),
            ("biochemical", "去污", "生化去污程序", 
             "接触生化污染物后的去污程序：1. 在安全区域建立去污站 2. 使用去污剂清洗装备 3. 按顺序脱除防护装备 4. 全身清洗消毒 5. 销毁污染物品。整个过程需要同伴协助，避免二次污染。", 
             4, 5, "生化,去污,清洗,程序")
        ]
        
        for knowledge in biochemical_knowledge:
            self.cursor.execute("""
                INSERT INTO scenario_knowledge (scenario_type, category, title, content, difficulty_level, priority, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, knowledge)
        
        # 插入场景威胁数据
        threats = [
            ("zombie", "普通僵尸", "感染者", 3, "行动缓慢但数量众多的感染者", 
             "腐烂气味、呻吟声、缓慢移动", "保持距离、使用长武器、攻击头部", "避免噪音、绕行群体"),
            ("zombie", "快速僵尸", "变异感染者", 4, "速度较快的变异僵尸", 
             "快速移动、敏捷反应、更强攻击性", "使用远程武器、设置陷阱、团队配合", "提前发现、快速撤离"),
            ("biochemical", "毒气云", "化学污染", 5, "致命的化学毒气云团", 
             "异常颜色气体、刺激性气味、植物枯萎", "佩戴防毒面具、快速撤离、逆风行进", "监测风向、避开低洼地区"),
            ("nuclear", "辐射热点", "高辐射区域", 4, "辐射强度极高的危险区域", 
             "检测仪器报警、金属物品发热、生物异常", "立即撤离、服用碘片、寻求医疗", "使用检测设备、规划安全路线")
        ]
        
        for threat in threats:
            self.cursor.execute("""
                INSERT INTO scenario_threats (scenario_type, threat_name, threat_type, danger_level, description, identification_signs, countermeasures, avoidance_tips)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, threat)
        
        self.connection.commit()
    
    def get_scenario_knowledge(self, scenario_type: str, category: str = None) -> List[Dict]:
        """获取特定场景的知识"""
        query = "SELECT * FROM scenario_knowledge WHERE scenario_type = ?"
        params = [scenario_type]
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        query += " ORDER BY priority DESC, difficulty_level ASC"
        
        results = self.execute_query(query, tuple(params))
        return [dict(row) for row in results]
    
    def get_scenario_threats(self, scenario_type: str) -> List[Dict]:
        """获取特定场景的威胁信息"""
        query = "SELECT * FROM scenario_threats WHERE scenario_type = ? ORDER BY danger_level DESC"
        results = self.execute_query(query, (scenario_type,))
        return [dict(row) for row in results]
    
    def get_scenario_info(self, scenario_type: str) -> Optional[Dict]:
        """获取场景基本信息"""
        query = "SELECT * FROM survival_scenarios WHERE scenario_type = ?"
        results = self.execute_query(query, (scenario_type,))
        
        if results:
            scenario = dict(results[0])
            try:
                scenario['required_equipment_list'] = json.loads(scenario.get('required_equipment', '[]'))
            except:
                scenario['required_equipment_list'] = []
            return scenario
        return None
    
    def search_scenario_content(self, scenario_type: str, keyword: str) -> Dict:
        """搜索特定场景的相关内容"""
        # 搜索场景知识
        knowledge_query = """
            SELECT * FROM scenario_knowledge 
            WHERE scenario_type = ? AND (title LIKE ? OR content LIKE ? OR tags LIKE ?)
            ORDER BY priority DESC
        """
        knowledge_params = (scenario_type, f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
        knowledge_results = self.execute_query(knowledge_query, knowledge_params)
        
        # 搜索场景技能
        skills_query = """
            SELECT * FROM scenario_skills 
            WHERE scenario_type = ? AND (name LIKE ? OR description LIKE ?)
            ORDER BY difficulty_level ASC
        """
        skills_params = (scenario_type, f"%{keyword}%", f"%{keyword}%")
        skills_results = self.execute_query(skills_query, skills_params)
        
        # 搜索威胁信息
        threats_query = """
            SELECT * FROM scenario_threats 
            WHERE scenario_type = ? AND (threat_name LIKE ? OR description LIKE ?)
            ORDER BY danger_level DESC
        """
        threats_params = (scenario_type, f"%{keyword}%", f"%{keyword}%")
        threats_results = self.execute_query(threats_query, threats_params)
        
        return {
            "knowledge": [dict(row) for row in knowledge_results],
            "skills": [dict(row) for row in skills_results],
            "threats": [dict(row) for row in threats_results]
        }