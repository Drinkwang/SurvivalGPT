#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
紧急情况处理模块
提供快速响应各种紧急情况的处理方案
"""

import json
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum

class EmergencyLevel(Enum):
    """紧急程度等级"""
    LOW = 1      # 轻微 - 可以自行处理
    MEDIUM = 2   # 中等 - 需要注意观察
    HIGH = 3     # 严重 - 需要立即处理
    CRITICAL = 4 # 危急 - 生命危险，需要专业救助

class EmergencyHandler:
    """紧急情况处理器类"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        
        # 紧急情况关键词映射
        self.emergency_keywords = {
            "外伤出血": ["出血", "流血", "伤口", "割伤", "划伤", "外伤"],
            "骨折": ["骨折", "断骨", "骨头断了", "骨裂", "脱臼"],
            "烧伤": ["烧伤", "烫伤", "灼伤", "火烧", "热水烫"],
            "中毒": ["中毒", "食物中毒", "误食", "恶心", "呕吐", "腹泻"],
            "失温": ["失温", "体温过低", "冻伤", "寒冷", "发抖"],
            "中暑": ["中暑", "热射病", "体温过高", "头晕", "脱水"],
            "迷路": ["迷路", "走失", "找不到路", "方向不明"],
            "野兽攻击": ["野兽", "动物攻击", "咬伤", "抓伤", "熊", "狼", "蛇咬"],
            "溺水": ["溺水", "掉水里", "不会游泳", "呛水"],
            "窒息": ["窒息", "呼吸困难", "喉咙卡住", "气道阻塞"],
            "心脏病发作": ["心脏病", "胸痛", "心绞痛", "心脏不适"],
            "过敏反应": ["过敏", "皮疹", "红肿", "呼吸急促", "过敏性休克"]
        }
        
        # 紧急程度映射
        self.severity_mapping = {
            "外伤出血": EmergencyLevel.HIGH,
            "骨折": EmergencyLevel.HIGH,
            "烧伤": EmergencyLevel.MEDIUM,
            "中毒": EmergencyLevel.HIGH,
            "失温": EmergencyLevel.HIGH,
            "中暑": EmergencyLevel.HIGH,
            "迷路": EmergencyLevel.MEDIUM,
            "野兽攻击": EmergencyLevel.CRITICAL,
            "溺水": EmergencyLevel.CRITICAL,
            "窒息": EmergencyLevel.CRITICAL,
            "心脏病发作": EmergencyLevel.CRITICAL,
            "过敏反应": EmergencyLevel.HIGH
        }
    
    def identify_emergency(self, description: str) -> Optional[Dict]:
        """识别紧急情况类型"""
        description_lower = description.lower()
        
        # 计算每种紧急情况的匹配分数
        scores = {}
        for emergency_type, keywords in self.emergency_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in description_lower:
                    score += len(keyword)  # 长关键词权重更高
            
            if score > 0:
                scores[emergency_type] = score
        
        if not scores:
            return None
        
        # 返回得分最高的紧急情况
        best_match = max(scores.items(), key=lambda x: x[1])
        emergency_type = best_match[0]
        
        return {
            "type": emergency_type,
            "severity": self.severity_mapping.get(emergency_type, EmergencyLevel.MEDIUM),
            "confidence": min(best_match[1] / 10, 1.0)  # 归一化置信度
        }
    
    def get_emergency_response(self, emergency_type: str, additional_info: str = "") -> Dict:
        """获取紧急情况响应方案"""
        try:
            # 从数据库获取处理程序
            procedures = self.db_manager.get_emergency_procedures(emergency_type)
            
            if not procedures:
                return self._get_generic_emergency_response(emergency_type)
            
            # 选择最相关的处理程序
            procedure = procedures[0]  # 假设按相关性排序
            
            response = {
                "emergency_type": procedure['emergency_type'],
                "severity_level": procedure['severity_level'],
                "severity_desc": self._get_severity_description(procedure['severity_level']),
                "immediate_actions": procedure['immediate_actions'],
                "detailed_steps": self._parse_json_field(procedure['detailed_steps']),
                "required_resources": self._parse_json_field(procedure['required_resources']),
                "prevention_tips": procedure.get('prevention_tips', ''),
                "warning_signs": self._get_warning_signs(emergency_type),
                "when_to_seek_help": self._get_help_criteria(emergency_type),
                "estimated_time": self._estimate_response_time(emergency_type),
                "follow_up_care": self._get_follow_up_care(emergency_type)
            }
            
            # 根据附加信息调整响应
            if additional_info:
                response = self._customize_response(response, additional_info)
            
            return response
            
        except Exception as e:
            print(f"获取紧急响应失败: {e}")
            return self._get_generic_emergency_response(emergency_type)
    
    def get_quick_action_guide(self, emergency_type: str) -> Dict:
        """获取快速行动指南"""
        quick_guides = {
            "外伤出血": {
                "priority_actions": [
                    "🚨 立即直接压迫伤口止血",
                    "🤲 用干净布料或手直接按压",
                    "📈 抬高受伤部位高于心脏",
                    "🩹 持续压迫至少10-15分钟"
                ],
                "avoid_actions": [
                    "❌ 不要移除已插入的异物",
                    "❌ 不要使用止血带（除非专业训练）",
                    "❌ 不要频繁查看伤口"
                ],
                "call_for_help_if": [
                    "出血无法控制",
                    "伤口很深或很大",
                    "有异物插入",
                    "患者意识模糊"
                ]
            },
            "骨折": {
                "priority_actions": [
                    "🛑 不要移动患者",
                    "🏥 立即固定受伤部位",
                    "❄️ 冰敷减轻疼痛和肿胀",
                    "📞 尽快寻求医疗帮助"
                ],
                "avoid_actions": [
                    "❌ 不要试图复位骨折",
                    "❌ 不要给患者食物或水",
                    "❌ 不要移动受伤部位"
                ],
                "call_for_help_if": [
                    "骨头穿破皮肤",
                    "肢体变形严重",
                    "患者休克症状",
                    "无法感觉或移动肢体"
                ]
            },
            "中毒": {
                "priority_actions": [
                    "🚫 立即停止接触毒物",
                    "💧 大量饮用清水稀释",
                    "📝 记录毒物种类和时间",
                    "👁️ 密切观察生命体征"
                ],
                "avoid_actions": [
                    "❌ 不要催吐（除非确认安全）",
                    "❌ 不要给昏迷患者喝水",
                    "❌ 不要使用民间偏方"
                ],
                "call_for_help_if": [
                    "患者意识不清",
                    "呼吸困难",
                    "持续呕吐",
                    "皮肤发青或发白"
                ]
            },
            "溺水": {
                "priority_actions": [
                    "🏊 确保自身安全后施救",
                    "🫁 立即检查呼吸和脉搏",
                    "💨 如无呼吸立即人工呼吸",
                    "💓 必要时进行心肺复苏"
                ],
                "avoid_actions": [
                    "❌ 不要贸然下水救人",
                    "❌ 不要试图控水",
                    "❌ 不要放弃抢救"
                ],
                "call_for_help_if": [
                    "患者无意识",
                    "无呼吸或脉搏",
                    "呛水严重",
                    "体温过低"
                ]
            }
        }
        
        return quick_guides.get(emergency_type, {
            "priority_actions": ["🚨 保持冷静", "📞 寻求专业帮助", "🛡️ 确保安全"],
            "avoid_actions": ["❌ 不要恐慌", "❌ 不要盲目行动"],
            "call_for_help_if": ["情况严重", "不确定如何处理"]
        })
    
    def assess_emergency_severity(self, symptoms: List[str], vital_signs: Dict = None) -> Dict:
        """评估紧急情况严重程度"""
        severity_score = 0
        risk_factors = []
        
        # 基于症状评分
        critical_symptoms = [
            "意识不清", "无呼吸", "无脉搏", "大量出血", "休克", 
            "严重呼吸困难", "胸痛", "严重过敏反应"
        ]
        
        high_risk_symptoms = [
            "持续呕吐", "高烧", "严重疼痛", "呼吸急促", 
            "皮肤发青", "意识模糊", "抽搐"
        ]
        
        for symptom in symptoms:
            symptom_lower = symptom.lower()
            
            for critical in critical_symptoms:
                if critical in symptom_lower:
                    severity_score += 10
                    risk_factors.append(f"危急症状：{critical}")
            
            for high_risk in high_risk_symptoms:
                if high_risk in symptom_lower:
                    severity_score += 5
                    risk_factors.append(f"高危症状：{high_risk}")
        
        # 基于生命体征评分
        if vital_signs:
            pulse = vital_signs.get('pulse', 0)
            breathing = vital_signs.get('breathing_rate', 0)
            temperature = vital_signs.get('temperature', 36.5)
            
            if pulse < 50 or pulse > 120:
                severity_score += 5
                risk_factors.append("心率异常")
            
            if breathing < 10 or breathing > 30:
                severity_score += 5
                risk_factors.append("呼吸频率异常")
            
            if temperature < 35 or temperature > 39:
                severity_score += 3
                risk_factors.append("体温异常")
        
        # 确定严重程度等级
        if severity_score >= 15:
            level = EmergencyLevel.CRITICAL
            recommendation = "立即寻求专业医疗救助！"
        elif severity_score >= 10:
            level = EmergencyLevel.HIGH
            recommendation = "需要紧急处理，尽快寻求医疗帮助"
        elif severity_score >= 5:
            level = EmergencyLevel.MEDIUM
            recommendation = "需要关注和处理，建议寻求医疗建议"
        else:
            level = EmergencyLevel.LOW
            recommendation = "可以自行处理，但要密切观察"
        
        return {
            "severity_level": level,
            "severity_score": severity_score,
            "risk_factors": risk_factors,
            "recommendation": recommendation,
            "monitoring_required": severity_score >= 5
        }
    
    def get_emergency_contacts(self) -> Dict:
        """获取紧急联系信息"""
        return {
            "emergency_services": {
                "general_emergency": "120 (中国急救)",
                "fire_department": "119",
                "police": "110",
                "international_emergency": "112 (国际通用)"
            },
            "poison_control": {
                "china": "400-161-9999 (中毒急救咨询)",
                "description": "24小时中毒急救咨询热线"
            },
            "mental_health": {
                "crisis_hotline": "400-161-9995 (心理危机干预)",
                "description": "心理危机干预和自杀预防"
            },
            "important_notes": [
                "拨打急救电话时保持冷静",
                "准确描述位置和情况",
                "按照调度员指示操作",
                "不要挂断电话直到被告知可以"
            ]
        }
    
    def create_emergency_plan(self, location_type: str, group_size: int) -> Dict:
        """创建紧急情况应对计划"""
        plan = {
            "location_type": location_type,
            "group_size": group_size,
            "preparation": [],
            "communication_plan": [],
            "evacuation_procedures": [],
            "emergency_supplies": [],
            "roles_and_responsibilities": []
        }
        
        # 根据位置类型定制计划
        if location_type == "野外":
            plan["preparation"] = [
                "告知他人行程计划",
                "携带通讯设备",
                "准备急救包",
                "学习基本急救技能",
                "了解当地紧急情况"
            ]
            plan["communication_plan"] = [
                "定时报告位置",
                "设置紧急联系人",
                "准备信号设备（哨子、镜子）",
                "学会发送求救信号"
            ]
            plan["emergency_supplies"] = [
                "急救包和常用药品",
                "额外的食物和水",
                "保暖用品",
                "照明设备",
                "多功能工具"
            ]
        
        # 根据团队规模分配角色
        if group_size > 1:
            plan["roles_and_responsibilities"] = [
                "指定团队领导者",
                "分配急救责任人",
                "指定通讯联络员",
                "安排物资管理员"
            ]
        
        return plan
    
    def _parse_json_field(self, json_str: str) -> List[str]:
        """解析JSON字段"""
        try:
            if json_str:
                return json.loads(json_str)
            return []
        except:
            return [json_str] if json_str else []
    
    def _get_severity_description(self, level: int) -> str:
        """获取严重程度描述"""
        descriptions = {
            1: "轻微 - 可自行处理",
            2: "中等 - 需要注意",
            3: "严重 - 立即处理",
            4: "危急 - 生命危险"
        }
        return descriptions.get(level, "未知程度")
    
    def _get_warning_signs(self, emergency_type: str) -> List[str]:
        """获取警告信号"""
        warning_signs = {
            "外伤出血": ["出血不止", "伤口很深", "有异物插入", "患者面色苍白", "意识模糊"],
            "骨折": ["骨头外露", "肢体变形", "无法移动", "剧烈疼痛", "肿胀严重"],
            "中毒": ["意识不清", "呼吸困难", "皮肤发青", "持续呕吐", "抽搐"],
            "烧伤": ["烧伤面积大", "深度烧伤", "呼吸道烧伤", "电击伤", "化学烧伤"]
        }
        return warning_signs.get(emergency_type, ["情况恶化", "症状加重", "新症状出现"])
    
    def _get_help_criteria(self, emergency_type: str) -> List[str]:
        """获取寻求帮助的标准"""
        criteria = {
            "外伤出血": ["无法止血", "伤口很深", "失血过多", "感染迹象"],
            "骨折": ["开放性骨折", "神经血管损伤", "多处骨折", "脊柱损伤可能"],
            "中毒": ["不明毒物", "症状严重", "意识改变", "呼吸心跳异常"],
            "烧伤": ["三度烧伤", "面积超过手掌大小", "特殊部位烧伤", "吸入性损伤"]
        }
        return criteria.get(emergency_type, ["情况超出处理能力", "症状持续恶化", "不确定如何处理"])
    
    def _estimate_response_time(self, emergency_type: str) -> str:
        """估算响应时间"""
        time_estimates = {
            "外伤出血": "立即开始，持续10-20分钟",
            "骨折": "立即固定，等待专业救助",
            "中毒": "立即处理，观察2-4小时",
            "烧伤": "立即冷却，持续处理",
            "溺水": "立即抢救，黄金4-6分钟"
        }
        return time_estimates.get(emergency_type, "根据情况而定")
    
    def _get_follow_up_care(self, emergency_type: str) -> List[str]:
        """获取后续护理建议"""
        follow_up = {
            "外伤出血": ["定期更换敷料", "观察感染迹象", "保持伤口清洁", "适当休息"],
            "骨折": ["遵医嘱固定", "定期复查", "适当功能锻炼", "营养补充"],
            "中毒": ["继续观察症状", "多饮水促进排毒", "清淡饮食", "避免再次接触"],
            "烧伤": ["保持创面清洁", "预防感染", "适当营养", "避免阳光直射"]
        }
        return follow_up.get(emergency_type, ["密切观察", "适当休息", "必要时就医"])
    
    def _customize_response(self, response: Dict, additional_info: str) -> Dict:
        """根据附加信息定制响应"""
        # 这里可以根据附加信息调整响应内容
        # 例如：年龄、性别、既往病史等
        
        if "老人" in additional_info or "elderly" in additional_info.lower():
            response["special_considerations"] = ["老年人恢复较慢", "注意并发症", "药物剂量调整"]
        
        if "儿童" in additional_info or "child" in additional_info.lower():
            response["special_considerations"] = ["儿童剂量不同", "家长陪同", "心理安慰重要"]
        
        if "孕妇" in additional_info or "pregnant" in additional_info.lower():
            response["special_considerations"] = ["避免某些药物", "特殊体位", "考虑胎儿安全"]
        
        return response
    
    def _get_generic_emergency_response(self, emergency_type: str) -> Dict:
        """获取通用紧急响应"""
        return {
            "emergency_type": emergency_type,
            "severity_level": 2,
            "severity_desc": "中等 - 需要注意",
            "immediate_actions": "保持冷静，评估情况，确保安全",
            "detailed_steps": ["评估现场安全", "检查患者状况", "采取适当措施", "寻求专业帮助"],
            "required_resources": ["急救包", "通讯设备", "清洁用品"],
            "prevention_tips": "提前学习急救知识，准备急救用品",
            "warning_signs": ["情况恶化", "症状加重"],
            "when_to_seek_help": ["超出处理能力", "情况不明确"],
            "estimated_time": "根据具体情况而定",
            "follow_up_care": ["密切观察", "适当休息"]
        }