#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI智能问答引擎
基于规则和模式匹配的智能问答系统
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

# 尝试导入jieba，如果失败则使用简单的分词
try:
    import jieba
    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False
    print("警告：jieba未安装，将使用简单分词")
    
    class jieba:
        @staticmethod
        def lcut(text):
            """简单的分词实现"""
            # 简单按空格和标点分词
            import re
            words = re.findall(r'[\w]+', text)
            return words

# 尝试导入fuzzywuzzy，如果失败则使用简单的字符串匹配
try:
    from fuzzywuzzy import fuzz
    FUZZYWUZZY_AVAILABLE = True
except ImportError:
    FUZZYWUZZY_AVAILABLE = False
    print("警告：fuzzywuzzy未安装，将使用简单字符串匹配")
    
    class fuzz:
        @staticmethod
        def ratio(s1, s2):
            """简单的字符串相似度计算"""
            if s1 == s2:
                return 100
            if s1 in s2 or s2 in s1:
                return 80
            return 0

class QAEngine:
    """智能问答引擎类"""
    
    def __init__(self, db_manager, config_manager=None):
        self.db_manager = db_manager
        self.config_manager = config_manager
        
        # 初始化大模型管理器和场景处理器
        if config_manager:
            try:
                from .llm_manager import LLMManager
                from .scenario_handler import ScenarioHandler
                self.llm_manager = LLMManager(config_manager)
                self.scenario_handler = ScenarioHandler(db_manager, config_manager)
                self.use_advanced_ai = True
            except ImportError as e:
                print(f"高级AI功能不可用: {e}")
                self.llm_manager = None
                self.scenario_handler = None
                self.use_advanced_ai = False
        else:
            self.llm_manager = None
            self.scenario_handler = None
            self.use_advanced_ai = False
        
        self.keywords_map = {}
        self.response_templates = {}
        self.question_patterns = []
        self._initialize_engine()
    
    def _initialize_engine(self):
        """初始化问答引擎"""
        # 初始化关键词映射
        self._build_keywords_map()
        
        # 初始化响应模板
        self._build_response_templates()
        
        # 初始化问题模式
        self._build_question_patterns()
    
    def _build_keywords_map(self):
        """构建关键词映射"""
        self.keywords_map = {
            "水源": ["水", "饮水", "净水", "水源", "喝水", "缺水", "找水", "取水"],
            "食物": ["食物", "吃", "饥饿", "觅食", "狩猎", "采集", "植物", "果实", "肉类"],
            "庇护所": ["庇护所", "帐篷", "住所", "避难", "搭建", "房屋", "遮蔽", "过夜"],
            "医疗": ["医疗", "受伤", "伤口", "急救", "治疗", "药物", "包扎", "止血", "骨折"],
            "生火": ["生火", "火", "点火", "取暖", "烹饪", "火堆", "燃料", "打火机"],
            "导航": ["导航", "方向", "迷路", "指南针", "定位", "路线", "地图", "北方"],
            "工具": ["工具", "制作", "武器", "刀具", "绳索", "容器", "陷阱"],
            "天气": ["天气", "下雨", "寒冷", "炎热", "风暴", "雪", "温度"],
            "危险": ["危险", "野兽", "毒蛇", "有毒", "攻击", "防御", "逃跑"]
        }
    
    def _build_response_templates(self):
        """构建响应模板"""
        self.response_templates = {
            "greeting": [
                "您好！我是您的AI生存向导，很高兴为您服务！🎯",
                "欢迎使用AI末日生存求生向导！我将为您提供专业的生存建议。💪",
                "您好！请告诉我您遇到的生存问题，我会尽力帮助您。🔥"
            ],
            "water_advice": [
                "关于水源问题，这是生存中最重要的需求之一。💧",
                "水是生命之源，让我为您提供寻找和净化水源的建议。🌊",
                "在野外获取安全饮用水是关键技能，以下是一些方法：💦"
            ],
            "food_advice": [
                "关于食物获取，我来为您介绍一些野外觅食的方法。🍖",
                "在野外寻找食物需要谨慎，让我分享一些安全的方法。🌿",
                "食物是维持体力的重要来源，以下是一些获取方法：🥜"
            ],
            "shelter_advice": [
                "搭建庇护所是保护自己免受恶劣天气影响的重要技能。🏠",
                "一个好的庇护所能够保命，让我教您如何搭建。⛺",
                "庇护所的选择和搭建有很多要点需要注意：🛡️"
            ],
            "medical_advice": [
                "医疗急救知识在紧急情况下非常重要。🏥",
                "处理伤口和急救是生存技能的重要组成部分。💊",
                "让我为您介绍一些基础的急救处理方法：🩹"
            ],
            "fire_advice": [
                "生火是野外生存的基本技能之一。🔥",
                "火能提供温暖、烹饪食物和信号求救。🔥",
                "掌握生火技巧对野外生存至关重要：🔥"
            ],
            "no_match": [
                "抱歉，我没有完全理解您的问题。请尝试更具体地描述您的情况。🤔",
                "您的问题很有趣，但我需要更多信息才能给出准确建议。💭",
                "请尝试用不同的方式描述您的问题，或者查看其他选项卡中的内容。📚"
            ]
        }
    
    def _build_question_patterns(self):
        """构建问题模式"""
        self.question_patterns = [
            # 问候模式
            (r"(你好|您好|hi|hello)", "greeting"),
            (r"(帮助|help)", "greeting"),
            
            # 水源相关模式
            (r".*(怎么|如何|怎样).*(找|寻找|获得|取得).*(水|水源)", "water_search"),
            (r".*(净化|过滤|消毒).*(水|水源)", "water_purify"),
            (r".*(缺水|没水|渴)", "water_shortage"),
            
            # 食物相关模式
            (r".*(怎么|如何|怎样).*(找|寻找|获得|捕获).*(食物|吃的)", "food_search"),
            (r".*(可以吃|能吃|食用).*(什么|哪些)", "edible_food"),
            (r".*(植物|果实|野菜)", "edible_plants"),
            
            # 庇护所相关模式
            (r".*(怎么|如何|怎样).*(搭建|建造|做).*(庇护所|帐篷|住所)", "shelter_build"),
            (r".*(过夜|睡觉|休息).*(哪里|地方)", "shelter_location"),
            
            # 医疗相关模式
            (r".*(受伤|伤口|出血|骨折)", "medical_injury"),
            (r".*(急救|治疗|处理).*(伤口|外伤)", "medical_treatment"),
            (r".*(中毒|食物中毒)", "medical_poisoning"),
            
            # 生火相关模式
            (r".*(怎么|如何|怎样).*(生火|点火|取火)", "fire_making"),
            (r".*(没有|缺少).*(打火机|火柴)", "fire_no_tools"),
            
            # 导航相关模式
            (r".*(迷路|找不到|方向)", "navigation_lost"),
            (r".*(怎么|如何).*(辨别|识别).*(方向|东南西北)", "navigation_direction"),
            
            # 危险相关模式
            (r".*(野兽|动物|蛇|毒蛇).*(攻击|咬|遇到)", "danger_animals"),
            (r".*(有毒|毒性).*(植物|蘑菇)", "danger_plants")
        ]
    
    def process_question(self, question: str, context: str = "") -> str:
        """处理用户问题并返回回答"""
        if not question.strip():
            return "请输入您的问题，我会尽力为您解答。😊"
        
        # 如果启用了高级AI功能，优先使用
        if self.use_advanced_ai and self.llm_manager and self.scenario_handler:
            return self._process_with_advanced_ai(question, context)
        
        # 回退到基础规则引擎
        return self._process_with_basic_engine(question)
    
    def _process_with_advanced_ai(self, question: str, context: str = "") -> str:
        """使用高级AI处理问题"""
        try:
            # 获取当前场景
            current_scenario = self.scenario_handler.current_scenario
            
            # 首先尝试场景特定处理
            scenario_response = self.scenario_handler.process_scenario_question(question, context)
            if scenario_response and scenario_response.get("response"):
                return scenario_response["response"]
            
            # 使用大模型生成回答
            llm_response = self.llm_manager.generate_response(question, context, current_scenario)
            if llm_response["success"]:
                # 添加场景信息和模型信息
                response = llm_response["response"]
                model_info = self.llm_manager.get_current_model_info()
                
                # 添加场景标识
                scenario_info = self.scenario_handler.get_current_scenario_info()
                scenario_name = scenario_info.get("name", "普通场景")
                scenario_icon = scenario_info.get("icon", "🏕️")
                
                # 格式化最终回答
                formatted_response = f"{scenario_icon} 【{scenario_name}场景】\n\n{response}"
                
                # 如果不是本地模型，添加模型标识
                if model_info["model_id"] != "local":
                    formatted_response += f"\n\n🤖 由 {model_info['name']} 提供支持"
                
                return formatted_response
            else:
                # 大模型失败，回退到场景处理或基础引擎
                return scenario_response.get("response", self._process_with_basic_engine(question))
                
        except Exception as e:
            print(f"高级AI处理失败: {e}")
            return self._process_with_basic_engine(question)
    
    def _process_with_basic_engine(self, question: str) -> str:
        """使用基础规则引擎处理问题"""
        # 预处理问题
        processed_question = self._preprocess_question(question)
        
        # 模式匹配
        matched_type = self._match_question_pattern(processed_question)
        
        if matched_type:
            return self._generate_response(matched_type, processed_question)
        
        # 关键词匹配
        category = self._match_keywords(processed_question)
        if category:
            return self._generate_category_response(category, processed_question)
        
        # 数据库搜索
        search_results = self.db_manager.search_knowledge(processed_question)
        if search_results:
            return self._format_search_results(search_results, processed_question)
        
        # 默认回复
        return self._get_random_template("no_match")
    
    def _preprocess_question(self, question: str) -> str:
        """预处理问题"""
        # 转换为小写
        question = question.lower()
        
        # 移除标点符号
        question = re.sub(r'[^\w\s]', '', question)
        
        return question.strip()
    
    def _match_question_pattern(self, question: str) -> Optional[str]:
        """匹配问题模式"""
        for pattern, question_type in self.question_patterns:
            if re.search(pattern, question):
                return question_type
        return None
    
    def _match_keywords(self, question: str) -> Optional[str]:
        """匹配关键词"""
        # 分词
        words = jieba.lcut(question)
        
        # 计算每个类别的匹配分数
        category_scores = defaultdict(int)
        
        for category, keywords in self.keywords_map.items():
            for word in words:
                for keyword in keywords:
                    # 使用模糊匹配
                    similarity = fuzz.ratio(word, keyword)
                    if similarity > 70:  # 相似度阈值
                        category_scores[category] += similarity
        
        # 返回得分最高的类别
        if category_scores:
            return max(category_scores.items(), key=lambda x: x[1])[0]
        
        return None
    
    def _generate_response(self, question_type: str, question: str) -> str:
        """根据问题类型生成回答"""
        response_map = {
            "greeting": self._handle_greeting,
            "water_search": self._handle_water_search,
            "water_purify": self._handle_water_purify,
            "water_shortage": self._handle_water_shortage,
            "food_search": self._handle_food_search,
            "edible_food": self._handle_edible_food,
            "edible_plants": self._handle_edible_plants,
            "shelter_build": self._handle_shelter_build,
            "shelter_location": self._handle_shelter_location,
            "medical_injury": self._handle_medical_injury,
            "medical_treatment": self._handle_medical_treatment,
            "medical_poisoning": self._handle_medical_poisoning,
            "fire_making": self._handle_fire_making,
            "fire_no_tools": self._handle_fire_no_tools,
            "navigation_lost": self._handle_navigation_lost,
            "navigation_direction": self._handle_navigation_direction,
            "danger_animals": self._handle_danger_animals,
            "danger_plants": self._handle_danger_plants
        }
        
        handler = response_map.get(question_type)
        if handler:
            return handler(question)
        
        return self._get_random_template("no_match")
    
    def _generate_category_response(self, category: str, question: str) -> str:
        """根据类别生成回答"""
        # 搜索该类别的知识
        results = self.db_manager.search_knowledge("", category)
        
        if results:
            template = self._get_random_template(f"{category.lower()}_advice")
            response = template + "\n\n"
            
            # 添加相关知识
            for i, result in enumerate(results[:2], 1):  # 限制显示2条
                response += f"📌 {result['title']}\n{result['content'][:200]}...\n\n"
            
            response += "💡 提示：您可以在'生存知识'选项卡中查看更多详细信息。"
            return response
        
        return f"关于{category}的问题，让我为您查找相关信息...\n\n" + self._get_random_template("no_match")
    
    def _format_search_results(self, results: List[Dict], question: str) -> str:
        """格式化搜索结果"""
        if not results:
            return self._get_random_template("no_match")
        
        response = f"🔍 根据您的问题，我找到了以下相关信息：\n\n"
        
        for i, result in enumerate(results[:3], 1):  # 限制显示3条
            response += f"📖 {i}. {result['title']}\n"
            response += f"分类: {result['category']} | 难度: {'⭐' * result['difficulty_level']}\n"
            response += f"{result['content'][:300]}...\n\n"
        
        if len(results) > 3:
            response += f"还有 {len(results) - 3} 条相关信息，请在搜索框中查看完整结果。\n\n"
        
        response += "💡 提示：您可以在其他选项卡中查看更多专业内容。"
        return response
    
    def _get_random_template(self, template_type: str) -> str:
        """获取随机模板"""
        templates = self.response_templates.get(template_type, ["我会尽力帮助您解决问题。"])
        import random
        return random.choice(templates)
    
    # 具体问题处理方法
    def _handle_greeting(self, question: str) -> str:
        return self._get_random_template("greeting") + "\n\n请告诉我您遇到的具体生存问题，比如：\n• 如何寻找水源？\n• 怎样搭建庇护所？\n• 野外可食用植物有哪些？\n• 如何处理外伤？"
    
    def _handle_water_search(self, question: str) -> str:
        return "🌊 寻找水源的方法：\n\n" + \
               "1. 🏞️ 寻找自然水源：河流、溪流、湖泊\n" + \
               "2. 🌧️ 收集雨水：使用容器、防水布\n" + \
               "3. 🌿 从植物获取：竹子、仙人掌、树液\n" + \
               "4. 💧 地下水：挖掘低洼地带\n" + \
               "5. 🌅 露水收集：清晨用布料收集\n\n" + \
               "⚠️ 重要提醒：任何水源都需要净化后才能饮用！"
    
    def _handle_water_purify(self, question: str) -> str:
        return "🔥 水源净化方法：\n\n" + \
               "1. 🔥 煮沸消毒：煮沸5-10分钟杀死细菌\n" + \
               "2. 🧪 净水片：按说明使用化学净水片\n" + \
               "3. 🏺 过滤净化：沙子、木炭、布料分层过滤\n" + \
               "4. ☀️ 紫外线消毒：透明瓶装水日晒6小时\n" + \
               "5. 🧂 盐水沉淀：加盐静置让杂质沉淀\n\n" + \
               "💡 建议：多种方法结合使用效果更好！"
    
    def _handle_water_shortage(self, question: str) -> str:
        return "💦 缺水应急措施：\n\n" + \
               "1. 🚨 立即寻找水源，优先级最高\n" + \
               "2. 💧 节约用水，小口慢饮\n" + \
               "3. 🌡️ 避免出汗，减少活动\n" + \
               "4. 🍃 寻找含水植物：仙人掌、竹子\n" + \
               "5. 🌧️ 准备收集雨水的容器\n\n" + \
               "⚠️ 警告：人体缺水3天就有生命危险，请尽快找到水源！"
    
    def _handle_food_search(self, question: str) -> str:
        return "🍖 野外觅食方法：\n\n" + \
               "1. 🌿 采集植物：蒲公英、车前草、野葱\n" + \
               "2. 🐟 捕鱼：制作简易鱼叉、陷阱\n" + \
               "3. 🐛 昆虫蛋白：蚂蚱、蚯蚓（去头尾内脏）\n" + \
               "4. 🥜 坚果种子：橡子、松子（需处理）\n" + \
               "5. 🍄 蘑菇：仅采集确认安全的品种\n\n" + \
               "⚠️ 安全第一：不确定的食物绝对不要吃！"
    
    def _handle_edible_food(self, question: str) -> str:
        return "🌱 常见可食用野生植物：\n\n" + \
               "✅ 安全食用：\n" + \
               "• 蒲公英：整株可食，富含维生素\n" + \
               "• 车前草：叶子可生食或煮食\n" + \
               "• 野葱：有葱味，可调味\n" + \
               "• 马齿苋：肉质叶片，可生食\n\n" + \
               "❌ 避免食用：\n" + \
               "• 颜色鲜艳的浆果\n" + \
               "• 有乳白色汁液的植物\n" + \
               "• 三叶植物（可能有毒）\n\n" + \
               "🧪 可食性测试：皮肤→嘴唇→舌尖→少量吞咽"
    
    def _handle_edible_plants(self, question: str) -> str:
        return self._handle_edible_food(question)
    
    def _handle_shelter_build(self, question: str) -> str:
        return "🏠 搭建庇护所步骤：\n\n" + \
               "1. 📍 选择位置：高地、避风、近水源\n" + \
               "2. 🌳 收集材料：树枝、树叶、石头\n" + \
               "3. 🏗️ 搭建框架：A字形或倾斜式\n" + \
               "4. 🍃 覆盖材料：树叶、草、防水布\n" + \
               "5. 🛡️ 防风防雨：加固结构，排水沟\n" + \
               "6. 🔥 保温措施：铺垫干草、反射热源\n\n" + \
               "💡 原则：干燥、保温、通风、隐蔽"
    
    def _handle_shelter_location(self, question: str) -> str:
        return "🗺️ 选择过夜地点原则：\n\n" + \
               "✅ 理想位置：\n" + \
               "• 地势较高，避免积水\n" + \
               "• 背风面，减少风寒\n" + \
               "• 靠近水源但不太近\n" + \
               "• 有天然屏障（岩石、大树）\n\n" + \
               "❌ 避免地点：\n" + \
               "• 河床、低洼地（洪水风险）\n" + \
               "• 山顶（风大寒冷）\n" + \
               "• 动物路径附近\n" + \
               "• 枯树下（倒塌风险）\n\n" + \
               "🌙 夜间安全：保持警觉，准备逃生路线"
    
    def _handle_medical_injury(self, question: str) -> str:
        return "🏥 外伤处理步骤：\n\n" + \
               "1. 🧤 清洁双手，避免感染\n" + \
               "2. 🩸 评估伤情，优先止血\n" + \
               "3. 🧽 清洁伤口，去除异物\n" + \
               "4. 🤲 直接压迫止血\n" + \
               "5. 📈 抬高受伤部位\n" + \
               "6. 🩹 包扎固定，定期检查\n\n" + \
               "🚨 严重情况：大量出血、骨折外露、意识不清时，立即寻求专业医疗帮助！"
    
    def _handle_medical_treatment(self, question: str) -> str:
        return self._handle_medical_injury(question)
    
    def _handle_medical_poisoning(self, question: str) -> str:
        return "☠️ 中毒应急处理：\n\n" + \
               "1. 🚫 立即停止摄入可疑物质\n" + \
               "2. 💧 大量饮用清水稀释毒素\n" + \
               "3. 🤮 诱导呕吐（非腐蚀性毒物）\n" + \
               "4. 🧂 服用活性炭（如有）\n" + \
               "5. 🌡️ 保持体温，观察症状\n" + \
               "6. 📝 记录摄入物质和时间\n\n" + \
               "⚠️ 注意：腐蚀性毒物（强酸强碱）不要催吐！\n" + \
               "🚨 严重症状时立即寻求医疗救助！"
    
    def _handle_fire_making(self, question: str) -> str:
        return "🔥 生火基本步骤：\n\n" + \
               "1. 🍃 准备火绒：干草、纸屑、桦树皮\n" + \
               "2. 🌿 收集引火物：细树枝、干叶\n" + \
               "3. 🪵 准备燃料：粗细不同的干木材\n" + \
               "4. 🏗️ 搭建火堆：锥形或井字形\n" + \
               "5. 🔥 点燃火绒，逐步添加燃料\n" + \
               "6. 💨 适当通风，维持火势\n\n" + \
               "💡 生火三要素：燃料、氧气、热源\n" + \
               "🛡️ 安全提醒：选择安全地点，准备灭火材料"
    
    def _handle_fire_no_tools(self, question: str) -> str:
        return "🔥 无工具生火方法：\n\n" + \
               "1. 🪨 火石打火：硬石头撞击产生火花\n" + \
               "2. 🌳 钻木取火：干木棒快速摩擦\n" + \
               "3. 🔍 放大镜聚焦：阳光聚焦点燃火绒\n" + \
               "4. 🔋 电池短路：电池两极用金属丝连接\n" + \
               "5. 🧊 冰透镜：制作冰块透镜聚光\n\n" + \
               "🎯 关键：准备充足的火绒和引火物\n" + \
               "💪 需要：耐心和持续的努力"
    
    def _handle_navigation_lost(self, question: str) -> str:
        return "🧭 迷路时的应对方法：\n\n" + \
               "1. 🛑 停下来，保持冷静\n" + \
               "2. 🗺️ 回忆来路，寻找地标\n" + \
               "3. 📍 标记当前位置\n" + \
               "4. 🔍 寻找高点观察地形\n" + \
               "5. 🌊 跟随水流下山\n" + \
               "6. 📢 发出求救信号\n\n" + \
               "🚨 重要：不要盲目乱走，消耗体力\n" + \
               "💡 信号方法：三声哨响、烟火、反光镜"
    
    def _handle_navigation_direction(self, question: str) -> str:
        return "🧭 野外辨别方向方法：\n\n" + \
               "☀️ 太阳定位：\n" + \
               "• 日出东方，日落西方\n" + \
               "• 中午太阳在南方（北半球）\n\n" + \
               "⭐ 星座定位：\n" + \
               "• 北极星指向正北\n" + \
               "• 通过北斗七星寻找北极星\n\n" + \
               "🌳 自然指标：\n" + \
               "• 树木南面枝叶茂盛\n" + \
               "• 岩石南面干燥\n" + \
               "• 蚂蚁洞口朝南\n\n" + \
               "🕐 手表定位：时针指向太阳，12点方向的一半是南方"
    
    def _handle_danger_animals(self, question: str) -> str:
        return "🐻 遇到危险动物的应对：\n\n" + \
               "🐻 大型动物（熊、野猪）：\n" + \
               "• 不要跑，缓慢后退\n" + \
               "• 举起双手显得更大\n" + \
               "• 大声说话，不要尖叫\n\n" + \
               "🐍 毒蛇：\n" + \
               "• 保持距离，不要挑逗\n" + \
               "• 缓慢移动，避免突然动作\n" + \
               "• 穿长裤长靴防护\n\n" + \
               "🦎 一般原则：\n" + \
               "• 制造噪音，提前警告\n" + \
               "• 避免在动物活跃时间行动\n" + \
               "• 妥善存放食物"
    
    def _handle_danger_plants(self, question: str) -> str:
        return "☠️ 识别有毒植物：\n\n" + \
               "⚠️ 危险特征：\n" + \
               "• 鲜艳的颜色（红、橙、紫）\n" + \
               "• 乳白色汁液\n" + \
               "• 三叶结构\n" + \
               "• 强烈异味\n" + \
               "• 表面有刺毛\n\n" + \
               "🧪 安全测试：\n" + \
               "1. 皮肤接触测试\n" + \
               "2. 嘴唇轻触测试\n" + \
               "3. 舌尖品尝测试\n" + \
               "4. 少量吞咽测试\n\n" + \
               "🚫 绝对避免：不认识的蘑菇、浆果\n" + \
               "💡 原则：不确定就不吃！"