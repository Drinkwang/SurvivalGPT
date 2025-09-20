#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
科幻生存场景处理模块
专门处理各种科幻场景的特殊逻辑和建议
"""

import json
import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum

class ScenarioType(Enum):
    """场景类型枚举"""
    NORMAL = "normal"
    ZOMBIE = "zombie"
    BIOCHEMICAL = "biochemical"
    NUCLEAR = "nuclear"
    ALIEN = "alien"
    NATURAL_DISASTER = "natural_disaster"

class ThreatLevel(Enum):
    """威胁等级枚举"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EXTREME = 5

class ScenarioHandler:
    """科幻生存场景处理器类"""
    
    def __init__(self, db_manager, config_manager):
        self.db_manager = db_manager
        self.config_manager = config_manager
        
        # 当前场景
        self.current_scenario = self.config_manager.get("scenarios.current_scenario", "normal")
        
        # 场景特定的处理器映射
        self.scenario_processors = {
            "zombie": self._process_zombie_scenario,
            "biochemical": self._process_biochemical_scenario,
            "nuclear": self._process_nuclear_scenario,
            "alien": self._process_alien_scenario,
            "natural_disaster": self._process_natural_disaster_scenario,
            "normal": self._process_normal_scenario
        }
        
        # 场景特定的关键词映射
        self.scenario_keywords = {
            "zombie": {
                "threats": ["僵尸", "感染", "病毒", "咬伤", "群体", "尸群"],
                "survival": ["安静", "武器", "防御", "逃跑", "庇护所", "食物"],
                "medical": ["咬伤", "感染", "隔离", "消毒", "抗病毒"]
            },
            "biochemical": {
                "threats": ["毒气", "污染", "化学", "泄露", "中毒"],
                "survival": ["防护服", "面具", "过滤", "去污", "密封"],
                "medical": ["中毒", "解毒", "呼吸", "皮肤", "清洗"]
            },
            "nuclear": {
                "threats": ["辐射", "核", "放射性", "污染", "泄露"],
                "survival": ["防护", "碘片", "地下", "距离", "时间"],
                "medical": ["辐射病", "碘片", "白细胞", "恶心", "脱发"]
            },
            "alien": {
                "threats": ["外星人", "UFO", "入侵", "绑架", "探测"],
                "survival": ["隐蔽", "电磁", "地下", "信号", "团队"],
                "medical": ["辐射", "未知", "隔离", "观察", "记录"]
            }
        }
    
    def set_current_scenario(self, scenario_type: str) -> bool:
        """设置当前场景"""
        available_scenarios = self.config_manager.get("scenarios.available_scenarios", {})
        
        if scenario_type not in available_scenarios:
            return False
        
        self.current_scenario = scenario_type
        self.config_manager.set("scenarios.current_scenario", scenario_type)
        self.config_manager.save_config()
        
        return True
    
    def get_current_scenario_info(self) -> Dict:
        """获取当前场景信息"""
        scenarios = self.config_manager.get("scenarios.available_scenarios", {})
        scenario_info = scenarios.get(self.current_scenario, {})
        
        # 从数据库获取详细信息
        db_info = self.db_manager.get_scenario_info(self.current_scenario)
        if db_info:
            scenario_info.update(db_info)
        
        scenario_info["scenario_type"] = self.current_scenario
        return scenario_info
    
    def process_scenario_question(self, question: str, context: str = "") -> Dict:
        """处理场景相关问题"""
        processor = self.scenario_processors.get(self.current_scenario, self._process_normal_scenario)
        return processor(question, context)
    
    def get_scenario_threats(self, location: str = "", time_of_day: str = "") -> List[Dict]:
        """获取当前场景的威胁信息"""
        threats = self.db_manager.get_scenario_threats(self.current_scenario)
        
        # 根据位置和时间调整威胁等级
        for threat in threats:
            threat["adjusted_danger_level"] = self._adjust_threat_level(
                threat, location, time_of_day
            )
        
        # 按调整后的危险等级排序
        threats.sort(key=lambda x: x["adjusted_danger_level"], reverse=True)
        
        return threats
    
    def get_scenario_survival_tips(self, situation: str = "") -> List[str]:
        """获取场景生存建议"""
        scenario_info = self.get_current_scenario_info()
        base_tips = scenario_info.get("survival_tips", "").split("、")
        
        # 根据具体情况添加额外建议
        additional_tips = self._get_situation_specific_tips(situation)
        
        return base_tips + additional_tips
    
    def assess_scenario_risk(self, factors: Dict) -> Dict:
        """评估场景风险"""
        base_risk = self._get_base_scenario_risk()
        
        # 考虑各种因素
        location_risk = self._assess_location_risk(factors.get("location", ""))
        time_risk = self._assess_time_risk(factors.get("time", ""))
        group_risk = self._assess_group_risk(factors.get("group_size", 1))
        resource_risk = self._assess_resource_risk(factors.get("resources", []))
        
        total_risk = min(base_risk + location_risk + time_risk + group_risk + resource_risk, 10)
        
        return {
            "total_risk": total_risk,
            "risk_level": self._get_risk_level_description(total_risk),
            "factors": {
                "base_scenario": base_risk,
                "location": location_risk,
                "time": time_risk,
                "group": group_risk,
                "resources": resource_risk
            },
            "recommendations": self._get_risk_recommendations(total_risk)
        }
    
    def _process_zombie_scenario(self, question: str, context: str) -> Dict:
        """处理僵尸场景问题"""
        question_lower = question.lower()
        
        # 僵尸场景特定处理逻辑
        if any(keyword in question_lower for keyword in ["咬伤", "感染", "被咬"]):
            return self._handle_zombie_bite_question(question, context)
        elif any(keyword in question_lower for keyword in ["武器", "战斗", "攻击"]):
            return self._handle_zombie_combat_question(question, context)
        elif any(keyword in question_lower for keyword in ["躲藏", "隐蔽", "安全"]):
            return self._handle_zombie_hiding_question(question, context)
        elif any(keyword in question_lower for keyword in ["食物", "觅食", "补给"]):
            return self._handle_zombie_foraging_question(question, context)
        else:
            return self._handle_general_zombie_question(question, context)
    
    def _process_biochemical_scenario(self, question: str, context: str) -> Dict:
        """处理生化场景问题"""
        question_lower = question.lower()
        
        if any(keyword in question_lower for keyword in ["防护", "防护服", "面具"]):
            return self._handle_biochemical_protection_question(question, context)
        elif any(keyword in question_lower for keyword in ["去污", "清洗", "消毒"]):
            return self._handle_biochemical_decon_question(question, context)
        elif any(keyword in question_lower for keyword in ["中毒", "症状", "治疗"]):
            return self._handle_biochemical_poisoning_question(question, context)
        else:
            return self._handle_general_biochemical_question(question, context)
    
    def _process_nuclear_scenario(self, question: str, context: str) -> Dict:
        """处理核辐射场景问题"""
        question_lower = question.lower()
        
        if any(keyword in question_lower for keyword in ["辐射", "检测", "测量"]):
            return self._handle_nuclear_detection_question(question, context)
        elif any(keyword in question_lower for keyword in ["防护", "屏蔽", "避难"]):
            return self._handle_nuclear_protection_question(question, context)
        elif any(keyword in question_lower for keyword in ["碘片", "药物", "治疗"]):
            return self._handle_nuclear_medical_question(question, context)
        else:
            return self._handle_general_nuclear_question(question, context)
    
    def _process_alien_scenario(self, question: str, context: str) -> Dict:
        """处理外星入侵场景问题"""
        question_lower = question.lower()
        
        if any(keyword in question_lower for keyword in ["隐蔽", "躲藏", "发现"]):
            return self._handle_alien_hiding_question(question, context)
        elif any(keyword in question_lower for keyword in ["通讯", "信号", "联系"]):
            return self._handle_alien_communication_question(question, context)
        elif any(keyword in question_lower for keyword in ["武器", "对抗", "反击"]):
            return self._handle_alien_combat_question(question, context)
        else:
            return self._handle_general_alien_question(question, context)
    
    def _process_natural_disaster_scenario(self, question: str, context: str) -> Dict:
        """处理自然灾害场景问题"""
        return {
            "response": "自然灾害场景下的生存建议：\n\n1. 🌪️ 保持冷静，评估当前威胁\n2. 🏃 立即撤离到安全区域\n3. 📻 收听官方紧急广播\n4. 🎒 准备应急包和重要物品\n5. 👥 与家人朋友保持联系\n\n具体应对措施取决于灾害类型（地震、洪水、台风等）。",
            "scenario": self.current_scenario,
            "threat_level": "high",
            "recommendations": ["立即行动", "寻求安全", "保持通讯"]
        }
    
    def _process_normal_scenario(self, question: str, context: str) -> Dict:
        """处理普通场景问题"""
        return {
            "response": "这是普通野外生存场景的建议。请查看生存知识和技能指导获取详细信息。",
            "scenario": "normal",
            "threat_level": "low",
            "recommendations": ["基础生存技能", "环境适应", "资源管理"]
        }
    
    # 僵尸场景具体处理方法
    def _handle_zombie_bite_question(self, question: str, context: str) -> Dict:
        return {
            "response": "🧟 僵尸咬伤紧急处理：\n\n⚠️ 立即行动：\n1. 🩸 立即清洗伤口，用肥皂和清水冲洗\n2. 🧴 使用酒精或碘酒消毒\n3. 🩹 包扎伤口，避免二次感染\n4. 💊 服用抗生素（如有）\n5. 🌡️ 监测体温和症状\n\n🚨 警告信号：\n• 发热超过38°C\n• 伤口周围红肿\n• 意识模糊\n• 异常攻击性\n\n如出现以上症状，病毒感染可能已开始，需要立即隔离！",
            "scenario": "zombie",
            "threat_level": "critical",
            "recommendations": ["立即处理伤口", "监测症状", "准备隔离"]
        }
    
    def _handle_zombie_combat_question(self, question: str, context: str) -> Dict:
        return {
            "response": "⚔️ 僵尸战斗策略：\n\n🎯 有效武器：\n• 🔨 钝器：棒球棒、锤子、撬棍\n• 🗡️ 利器：砍刀、斧头（攻击头部）\n• 🏹 远程：弓箭、弹弓（安静）\n\n💡 战斗原则：\n1. 避免近身战斗\n2. 攻击头部是唯一有效方法\n3. 保持安静，避免吸引更多僵尸\n4. 准备多个逃生路线\n5. 团队配合，互相掩护\n\n⚠️ 避免使用枪械：噪音会吸引大量僵尸！",
            "scenario": "zombie",
            "threat_level": "high",
            "recommendations": ["选择合适武器", "攻击头部", "保持安静"]
        }
    
    def _handle_zombie_hiding_question(self, question: str, context: str) -> Dict:
        return {
            "response": "🏠 僵尸环境隐蔽策略：\n\n🔒 理想藏身地点：\n• 🏢 高层建筑（摧毁楼梯）\n• 🏭 地下室（多个出入口）\n• 🌉 桥梁下方\n• 🚇 地铁隧道（确认安全）\n\n🛡️ 防御措施：\n1. 堵塞所有入口\n2. 设置警报系统（铃铛、罐子）\n3. 准备安静的逃生路线\n4. 储备食物和水\n5. 保持绝对安静\n\n❌ 避免地点：\n• 医院（感染源）\n• 学校（人群聚集地）\n• 商场（僵尸聚集）",
            "scenario": "zombie",
            "threat_level": "medium",
            "recommendations": ["选择高地", "多重防御", "保持安静"]
        }
    
    def _handle_zombie_foraging_question(self, question: str, context: str) -> Dict:
        return {
            "response": "🍖 僵尸环境觅食指南：\n\n🌙 最佳时机：\n• 夜间行动（僵尸视力差）\n• 雨天（掩盖声音）\n• 僵尸群体移动时\n\n🎯 搜索目标：\n• 🏪 小型便利店\n• 🏠 居民住宅\n• 🚚 被遗弃的货车\n• 🌱 屋顶花园\n\n📦 优先物品：\n1. 罐头食品（长期保存）\n2. 瓶装水\n3. 药品\n4. 电池和手电筒\n5. 安静的工具\n\n⚠️ 安全原则：\n• 永远不要单独行动\n• 设置观察哨\n• 准备快速撤离计划",
            "scenario": "zombie",
            "threat_level": "high",
            "recommendations": ["夜间行动", "团队合作", "快速撤离"]
        }
    
    def _handle_general_zombie_question(self, question: str, context: str) -> Dict:
        return {
            "response": "🧟 僵尸末日生存要点：\n\n🎯 核心原则：\n1. 🤫 保持安静是生存关键\n2. 🏃 机动性比防御更重要\n3. 👥 小团队比单独行动安全\n4. 🧠 智慧比武力更有效\n\n📋 日常注意事项：\n• 定期检查装备\n• 规划多条逃生路线\n• 建立通讯计划\n• 储备必需品\n• 保持身体健康\n\n💡 记住：僵尸数量庞大但智力低下，用智慧战胜它们！",
            "scenario": "zombie",
            "threat_level": "high",
            "recommendations": ["保持安静", "团队合作", "智慧应对"]
        }
    
    # 生化场景具体处理方法
    def _handle_biochemical_protection_question(self, question: str, context: str) -> Dict:
        return {
            "response": "☣️ 生化防护装备指南：\n\n🛡️ 必需装备：\n• 🥽 全面罩防毒面具（P3级别）\n• 🧥 全封闭防护服\n• 🧤 丁腈橡胶手套（双层）\n• 👢 防化靴套\n• 📱 通讯设备（防水密封）\n\n✅ 穿戴顺序：\n1. 内层衣物→防护服\n2. 内层手套→外层手套\n3. 防护靴→靴套\n4. 防毒面具（最后）\n\n🔍 检查要点：\n• 所有接缝密封\n• 面具气密性测试\n• 过滤器有效期\n• 装备完整性",
            "scenario": "biochemical",
            "threat_level": "critical",
            "recommendations": ["全套防护", "正确穿戴", "定期检查"]
        }
    
    def _handle_biochemical_decon_question(self, question: str, context: str) -> Dict:
        return {
            "response": "🚿 生化去污程序：\n\n🏗️ 去污站设置：\n• 🌊 清洁区→缓冲区→污染区\n• 💧 大量清水供应\n• 🧴 去污剂（漂白剂溶液）\n• 🗑️ 污染物收集容器\n\n📋 去污步骤：\n1. 🚿 全身冲洗（穿着防护服）\n2. 🧽 去污剂擦洗\n3. 💦 清水冲洗\n4. 👕 按顺序脱除装备\n5. 🛁 个人清洗\n6. 👔 更换清洁衣物\n\n⚠️ 注意事项：\n• 需要同伴协助\n• 废水需要处理\n• 污染装备要销毁",
            "scenario": "biochemical",
            "threat_level": "high",
            "recommendations": ["建立去污站", "按程序操作", "同伴协助"]
        }
    
    def _handle_biochemical_poisoning_question(self, question: str, context: str) -> Dict:
        return {
            "response": "☠️ 生化中毒处理：\n\n🚨 立即行动：\n1. 🏃 脱离污染区域\n2. 🚿 大量清水冲洗\n3. 👕 脱除污染衣物\n4. 💧 大量饮水稀释\n5. 🤮 诱导呕吐（非腐蚀性）\n\n⚠️ 中毒症状：\n• 呼吸困难\n• 皮肤红肿\n• 恶心呕吐\n• 意识模糊\n• 肌肉痉挛\n\n💊 应急药物：\n• 活性炭（吸附毒素）\n• 阿托品（神经性毒剂）\n• 解毒剂（特定毒物）\n\n🏥 严重时立即寻求医疗救助！",
            "scenario": "biochemical",
            "threat_level": "critical",
            "recommendations": ["立即脱离", "大量冲洗", "寻求救助"]
        }
    
    def _handle_general_biochemical_question(self, question: str, context: str) -> Dict:
        return {
            "response": "☣️ 生化危机生存要点：\n\n🎯 核心原则：\n1. 🛡️ 防护第一，预防为主\n2. 🌊 去污彻底，程序规范\n3. 👥 团队协作，互相监督\n4. 📡 信息收集，了解威胁\n\n📋 生存策略：\n• 避开污染区域\n• 监测风向变化\n• 寻找清洁水源\n• 建立安全区域\n• 定期健康检查\n\n💡 记住：生化威胁看不见摸不着，严格遵守防护程序是生存关键！",
            "scenario": "biochemical",
            "threat_level": "high",
            "recommendations": ["严格防护", "避开污染", "团队协作"]
        }
    
    # 核辐射场景处理方法
    def _handle_nuclear_detection_question(self, question: str, context: str) -> Dict:
        return {
            "response": "☢️ 辐射检测与防护：\n\n📱 检测设备：\n• 盖革计数器\n• 辐射剂量计\n• 个人剂量笔\n• 手机APP（简易）\n\n⚠️ 危险信号：\n• 设备持续报警\n• 金属物品发热\n• 动植物异常死亡\n• 电子设备故障\n\n📏 安全距离：\n• 低辐射：>100米\n• 中辐射：>1公里\n• 高辐射：>10公里\n\n⏰ 时间原则：\n• 暴露时间越短越好\n• 每小时检查剂量\n• 达到限值立即撤离",
            "scenario": "nuclear",
            "threat_level": "high",
            "recommendations": ["使用检测设备", "保持安全距离", "限制暴露时间"]
        }
    
    def _handle_nuclear_protection_question(self, question: str, context: str) -> Dict:
        return {
            "response": "🛡️ 核辐射防护策略：\n\n🏠 庇护所选择：\n• 🏢 混凝土建筑地下室\n• 🚇 地铁站\n• 🏔️ 天然洞穴\n• 🏭 厚墙工业建筑\n\n📐 防护原则：\n1. 🏃 距离：远离辐射源\n2. ⏰ 时间：减少暴露时间\n3. 🛡️ 屏蔽：使用防护材料\n\n🧱 屏蔽材料：\n• 铅板（最佳）\n• 混凝土\n• 钢板\n• 土壤（厚层）\n• 水（大量）\n\n💊 预防药物：\n• 碘片（防甲状腺癌）\n• 普鲁士蓝（铯中毒）",
            "scenario": "nuclear",
            "threat_level": "critical",
            "recommendations": ["寻找地下庇护所", "使用屏蔽材料", "服用防护药物"]
        }
    
    def _handle_nuclear_medical_question(self, question: str, context: str) -> Dict:
        return {
            "response": "💊 核辐射医疗处理：\n\n🚨 急性辐射症状：\n• 恶心呕吐\n• 腹泻\n• 发热\n• 皮肤红肿\n• 脱发\n• 免疫力下降\n\n💉 应急药物：\n• 💊 碘化钾片（KI）\n  - 成人：130mg/天\n  - 儿童：65mg/天\n  - 服用时机：暴露前后24小时内\n\n🩺 支持治疗：\n• 大量饮水\n• 维生素补充\n• 抗生素预防感染\n• 止吐药物\n• 皮肤护理\n\n⚠️ 严重辐射病需要专业医疗救治！",
            "scenario": "nuclear",
            "threat_level": "critical",
            "recommendations": ["及时服用碘片", "支持性治疗", "寻求专业救治"]
        }
    
    def _handle_general_nuclear_question(self, question: str, context: str) -> Dict:
        return {
            "response": "☢️ 核辐射环境生存：\n\n🎯 生存原则：\n1. 🏃 快速撤离高辐射区\n2. 🏠 寻找坚固庇护所\n3. 💊 及时服用防护药物\n4. 📡 收听官方信息\n\n📋 长期策略：\n• 避免污染食物和水\n• 定期监测辐射水平\n• 保持个人卫生\n• 储备医疗用品\n• 规划撤离路线\n\n💡 记住：辐射无色无味，依靠设备检测，严格遵守防护原则！",
            "scenario": "nuclear",
            "threat_level": "high",
            "recommendations": ["快速撤离", "寻找庇护所", "定期监测"]
        }
    
    # 外星入侵场景处理方法
    def _handle_alien_hiding_question(self, question: str, context: str) -> Dict:
        return {
            "response": "👽 外星入侵隐蔽策略：\n\n🕳️ 最佳藏身地点：\n• 🏔️ 深山洞穴\n• 🚇 废弃地铁隧道\n• 🏭 地下工业设施\n• 🌊 水下基地\n• 🌲 密林深处\n\n📡 避免探测：\n1. 🔇 关闭所有电子设备\n2. 🔥 避免使用明火\n3. 🌡️ 控制体温信号\n4. 👥 小群体分散行动\n5. 🌙 夜间活动\n\n🛡️ 反探测措施：\n• 使用法拉第笼\n• 金属屏蔽材料\n• 电磁干扰设备\n• 伪装和掩护\n\n⚠️ 假设外星科技远超人类，隐蔽是最佳策略！",
            "scenario": "alien",
            "threat_level": "extreme",
            "recommendations": ["深度隐蔽", "避免探测", "分散行动"]
        }
    
    def _handle_alien_communication_question(self, question: str, context: str) -> Dict:
        return {
            "response": "📡 外星入侵通讯策略：\n\n🚫 避免使用：\n• 手机网络\n• 无线电\n• 卫星通讯\n• 互联网\n• GPS设备\n\n✅ 安全通讯：\n• 🔦 光信号（莫尔斯码）\n• 🥁 声音信号\n• 🏃 人工传递\n• 🪞 镜子反光\n• 🔥 烟火信号\n\n📋 通讯协议：\n1. 建立暗号系统\n2. 设定联络时间\n3. 确定集合地点\n4. 准备紧急信号\n\n💡 原则：假设所有电子通讯都被监控！",
            "scenario": "alien",
            "threat_level": "high",
            "recommendations": ["避免电子通讯", "使用原始信号", "建立暗号"]
        }
    
    def _handle_alien_combat_question(self, question: str, context: str) -> Dict:
        return {
            "response": "⚔️ 外星入侵对抗策略：\n\n⚠️ 重要提醒：\n直接对抗外星科技可能是自杀行为！\n\n🎯 可行策略：\n• 🕳️ 游击战术\n• 💣 破坏行动\n• 📡 干扰通讯\n• 🏃 打了就跑\n• 👥 协调攻击\n\n🔧 可能有效武器：\n• EMP设备（电磁脉冲）\n• 强酸/强碱\n• 高温/低温\n• 声波武器\n• 生物武器（风险极高）\n\n💡 最佳策略：\n1. 收集外星科技情报\n2. 寻找弱点\n3. 联合其他幸存者\n4. 等待反击时机\n\n记住：智慧比武力更重要！",
            "scenario": "alien",
            "threat_level": "extreme",
            "recommendations": ["避免直接对抗", "游击战术", "收集情报"]
        }
    
    def _handle_general_alien_question(self, question: str, context: str) -> Dict:
        return {
            "response": "👽 外星入侵生存指南：\n\n🎯 核心策略：\n1. 🕳️ 隐蔽为主，避免接触\n2. 📡 断绝电子信号\n3. 👥 小群体行动\n4. 🧠 收集情报信息\n\n📋 生存要点：\n• 假设被全面监控\n• 避免固定模式\n• 准备多个藏身点\n• 储备基础物资\n• 保持心理健康\n\n💭 心理准备：\n• 接受现实\n• 保持希望\n• 团结合作\n• 适应变化\n\n💡 记住：人类的适应能力和团结精神是最大优势！",
            "scenario": "alien",
            "threat_level": "extreme",
            "recommendations": ["保持隐蔽", "收集情报", "团结合作"]
        }
    
    # 辅助方法
    def _adjust_threat_level(self, threat: Dict, location: str, time_of_day: str) -> int:
        """根据环境因素调整威胁等级"""
        base_level = threat["danger_level"]
        adjustment = 0
        
        # 位置因素
        if location:
            if "城市" in location or "市区" in location:
                adjustment += 1  # 城市区域威胁更高
            elif "郊外" in location or "乡村" in location:
                adjustment -= 1  # 郊外相对安全
        
        # 时间因素
        if time_of_day:
            if "夜晚" in time_of_day or "晚上" in time_of_day:
                if self.current_scenario == "zombie":
                    adjustment -= 1  # 僵尸夜间视力差
                else:
                    adjustment += 1  # 其他场景夜间更危险
        
        return max(1, min(5, base_level + adjustment))
    
    def _get_situation_specific_tips(self, situation: str) -> List[str]:
        """根据具体情况获取额外建议"""
        tips = []
        
        if "受伤" in situation:
            tips.append("优先处理伤口，避免感染")
        if "缺水" in situation:
            tips.append("寻找安全水源，净化后饮用")
        if "缺食" in situation:
            tips.append("合理分配食物，寻找补给")
        if "迷路" in situation:
            tips.append("标记路径，寻找地标")
        
        return tips
    
    def _get_base_scenario_risk(self) -> int:
        """获取场景基础风险等级"""
        risk_levels = {
            "normal": 2,
            "zombie": 4,
            "biochemical": 4,
            "nuclear": 4,
            "alien": 5,
            "natural_disaster": 3
        }
        return risk_levels.get(self.current_scenario, 2)
    
    def _assess_location_risk(self, location: str) -> int:
        """评估位置风险"""
        if not location:
            return 0
        
        high_risk_locations = ["城市", "医院", "学校", "商场", "机场"]
        medium_risk_locations = ["郊区", "小镇", "工厂"]
        
        for high_risk in high_risk_locations:
            if high_risk in location:
                return 2
        
        for medium_risk in medium_risk_locations:
            if medium_risk in location:
                return 1
        
        return -1  # 偏远地区相对安全
    
    def _assess_time_risk(self, time: str) -> int:
        """评估时间风险"""
        if not time:
            return 0
        
        if "夜晚" in time or "晚上" in time:
            return 1 if self.current_scenario != "zombie" else -1
        
        return 0
    
    def _assess_group_risk(self, group_size: int) -> int:
        """评估团队规模风险"""
        if group_size == 1:
            return 2  # 单独行动风险高
        elif group_size <= 4:
            return -1  # 小团队最佳
        elif group_size <= 10:
            return 0  # 中等团队
        else:
            return 2  # 大团队目标明显
    
    def _assess_resource_risk(self, resources: List[str]) -> int:
        """评估资源风险"""
        if not resources:
            return 2
        
        essential_resources = ["水", "食物", "医疗", "武器", "通讯"]
        available_count = sum(1 for resource in essential_resources if any(r in resource for r in resources))
        
        if available_count >= 4:
            return -2
        elif available_count >= 2:
            return -1
        elif available_count >= 1:
            return 0
        else:
            return 3
    
    def _get_risk_level_description(self, risk_level: int) -> str:
        """获取风险等级描述"""
        if risk_level <= 2:
            return "低风险 - 相对安全"
        elif risk_level <= 4:
            return "中等风险 - 需要谨慎"
        elif risk_level <= 6:
            return "高风险 - 危险环境"
        elif risk_level <= 8:
            return "极高风险 - 生命危险"
        else:
            return "致命风险 - 立即撤离"
    
    def _get_risk_recommendations(self, risk_level: int) -> List[str]:
        """根据风险等级获取建议"""
        if risk_level <= 2:
            return ["保持警惕", "定期检查装备", "收集信息"]
        elif risk_level <= 4:
            return ["加强防护", "准备撤离计划", "团队行动"]
        elif risk_level <= 6:
            return ["立即加强防护", "寻找安全区域", "减少活动"]
        elif risk_level <= 8:
            return ["准备立即撤离", "启动紧急程序", "寻求支援"]
        else:
            return ["立即撤离", "启动最高级别应急预案", "生存第一"]