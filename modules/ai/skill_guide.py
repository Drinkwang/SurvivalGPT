#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
求生技能指导系统
提供分步骤的技能教学和指导
"""

import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class SkillGuide:
    """求生技能指导系统类"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.skill_categories = {
            "生火": "fire_making",
            "水源": "water_source", 
            "食物获取": "food_gathering",
            "庇护所建造": "shelter_building",
            "工具制作": "tool_making",
            "导航定位": "navigation",
            "急救医疗": "first_aid",
            "信号求救": "signaling"
        }
        
        # 技能难度等级描述
        self.difficulty_levels = {
            1: "初级 - 适合新手，基础技能",
            2: "中级 - 需要一定经验", 
            3: "高级 - 需要丰富经验和技巧",
            4: "专家 - 需要专业知识和大量练习",
            5: "大师 - 极其困难，需要长期训练"
        }
    
    def get_skill_categories(self) -> Dict[str, str]:
        """获取技能分类"""
        return self.skill_categories.copy()
    
    def get_skills_by_category(self, category: str) -> List[Dict]:
        """根据分类获取技能列表"""
        try:
            skills = self.db_manager.get_skills_by_category(category)
            
            # 为每个技能添加额外信息
            for skill in skills:
                skill['difficulty_desc'] = self.difficulty_levels.get(skill['difficulty_level'], "未知难度")
                skill['estimated_time_desc'] = self._format_time(skill.get('estimated_time', 0))
                
                # 解析JSON字段
                try:
                    skill['steps_list'] = json.loads(skill.get('steps', '[]'))
                    skill['materials_list'] = json.loads(skill.get('required_materials', '[]'))
                except:
                    skill['steps_list'] = []
                    skill['materials_list'] = []
            
            return skills
        except Exception as e:
            print(f"获取技能列表失败: {e}")
            return []
    
    def get_skill_detail(self, skill_id: int) -> Optional[Dict]:
        """获取技能详细信息"""
        try:
            query = "SELECT * FROM survival_skills WHERE id = ?"
            results = self.db_manager.execute_query(query, (skill_id,))
            
            if results:
                skill = dict(results[0])
                skill['difficulty_desc'] = self.difficulty_levels.get(skill['difficulty_level'], "未知难度")
                skill['estimated_time_desc'] = self._format_time(skill.get('estimated_time', 0))
                
                # 解析JSON字段
                try:
                    skill['steps_list'] = json.loads(skill.get('steps', '[]'))
                    skill['materials_list'] = json.loads(skill.get('required_materials', '[]'))
                except:
                    skill['steps_list'] = []
                    skill['materials_list'] = []
                
                return skill
            
            return None
        except Exception as e:
            print(f"获取技能详情失败: {e}")
            return None
    
    def get_step_by_step_guide(self, skill_id: int) -> Dict:
        """获取分步骤指导"""
        skill = self.get_skill_detail(skill_id)
        if not skill:
            return {"error": "技能不存在"}
        
        guide = {
            "skill_name": skill['name'],
            "description": skill['description'],
            "difficulty": skill['difficulty_desc'],
            "estimated_time": skill['estimated_time_desc'],
            "materials_needed": skill['materials_list'],
            "steps": [],
            "safety_notes": skill.get('safety_notes', ''),
            "tips": self._get_skill_tips(skill['category'])
        }
        
        # 格式化步骤
        for i, step in enumerate(skill['steps_list'], 1):
            guide['steps'].append({
                "step_number": i,
                "instruction": step,
                "estimated_time": self._estimate_step_time(skill.get('estimated_time', 0), len(skill['steps_list']), i),
                "key_points": self._get_step_key_points(skill['category'], i, step)
            })
        
        return guide
    
    def get_skill_prerequisites(self, skill_id: int) -> List[Dict]:
        """获取技能前置要求"""
        skill = self.get_skill_detail(skill_id)
        if not skill:
            return []
        
        prerequisites = []
        
        # 根据技能类别和难度确定前置技能
        if skill['difficulty_level'] > 1:
            # 查找同类别的低难度技能
            query = """
                SELECT * FROM survival_skills 
                WHERE category = ? AND difficulty_level < ? 
                ORDER BY difficulty_level ASC
            """
            results = self.db_manager.execute_query(query, (skill['category'], skill['difficulty_level']))
            
            for result in results:
                prerequisites.append({
                    "id": result['id'],
                    "name": result['name'],
                    "difficulty_level": result['difficulty_level'],
                    "reason": f"掌握{result['name']}有助于学习{skill['name']}"
                })
        
        return prerequisites
    
    def get_skill_progression(self, category: str) -> List[Dict]:
        """获取技能进阶路径"""
        skills = self.get_skills_by_category(category)
        
        # 按难度排序
        skills.sort(key=lambda x: x['difficulty_level'])
        
        progression = []
        for i, skill in enumerate(skills):
            progression.append({
                "level": i + 1,
                "skill_id": skill['id'],
                "skill_name": skill['name'],
                "difficulty": skill['difficulty_level'],
                "difficulty_desc": skill['difficulty_desc'],
                "estimated_time": skill['estimated_time_desc'],
                "is_prerequisite": i < len(skills) - 1,
                "next_skills": [skills[i+1]['name']] if i < len(skills) - 1 else []
            })
        
        return progression
    
    def search_skills(self, keyword: str, difficulty_filter: int = None) -> List[Dict]:
        """搜索技能"""
        try:
            query = "SELECT * FROM survival_skills WHERE (name LIKE ? OR description LIKE ?)"
            params = [f"%{keyword}%", f"%{keyword}%"]
            
            if difficulty_filter:
                query += " AND difficulty_level <= ?"
                params.append(difficulty_filter)
            
            query += " ORDER BY difficulty_level ASC, estimated_time ASC"
            
            results = self.db_manager.execute_query(query, tuple(params))
            
            skills = []
            for result in results:
                skill = dict(result)
                skill['difficulty_desc'] = self.difficulty_levels.get(skill['difficulty_level'], "未知难度")
                skill['estimated_time_desc'] = self._format_time(skill.get('estimated_time', 0))
                skills.append(skill)
            
            return skills
        except Exception as e:
            print(f"搜索技能失败: {e}")
            return []
    
    def get_recommended_skills(self, user_level: int = 1) -> List[Dict]:
        """根据用户水平推荐技能"""
        try:
            # 推荐适合用户水平的技能
            query = """
                SELECT * FROM survival_skills 
                WHERE difficulty_level <= ? 
                ORDER BY priority DESC, difficulty_level ASC
                LIMIT 10
            """
            
            # 如果数据库中没有priority字段，使用备用查询
            try:
                results = self.db_manager.execute_query(query, (user_level,))
            except:
                query = """
                    SELECT * FROM survival_skills 
                    WHERE difficulty_level <= ? 
                    ORDER BY difficulty_level ASC
                    LIMIT 10
                """
                results = self.db_manager.execute_query(query, (user_level,))
            
            recommendations = []
            for result in results:
                skill = dict(result)
                skill['difficulty_desc'] = self.difficulty_levels.get(skill['difficulty_level'], "未知难度")
                skill['estimated_time_desc'] = self._format_time(skill.get('estimated_time', 0))
                skill['recommendation_reason'] = self._get_recommendation_reason(skill, user_level)
                recommendations.append(skill)
            
            return recommendations
        except Exception as e:
            print(f"获取推荐技能失败: {e}")
            return []
    
    def _format_time(self, minutes: int) -> str:
        """格式化时间显示"""
        if minutes <= 0:
            return "时间不定"
        elif minutes < 60:
            return f"{minutes}分钟"
        elif minutes < 1440:  # 24小时
            hours = minutes // 60
            mins = minutes % 60
            if mins == 0:
                return f"{hours}小时"
            else:
                return f"{hours}小时{mins}分钟"
        else:
            days = minutes // 1440
            hours = (minutes % 1440) // 60
            if hours == 0:
                return f"{days}天"
            else:
                return f"{days}天{hours}小时"
    
    def _estimate_step_time(self, total_time: int, total_steps: int, step_number: int) -> str:
        """估算单个步骤时间"""
        if total_time <= 0 or total_steps <= 0:
            return "时间不定"
        
        # 简单平均分配，实际可以根据步骤复杂度调整
        step_time = total_time // total_steps
        
        # 前期准备步骤通常耗时较长
        if step_number <= 2:
            step_time = int(step_time * 1.5)
        
        return self._format_time(step_time)
    
    def _get_step_key_points(self, category: str, step_number: int, step_description: str) -> List[str]:
        """获取步骤关键点"""
        key_points = []
        
        # 根据类别和步骤内容提供关键点
        if category == "生火":
            if "准备" in step_description or "收集" in step_description:
                key_points = ["确保材料干燥", "准备不同粗细的燃料", "选择避风位置"]
            elif "点燃" in step_description:
                key_points = ["从小到大逐步添加燃料", "保持适当通风", "准备备用引火物"]
        elif category == "水源":
            if "过滤" in step_description:
                key_points = ["多层过滤效果更好", "定期更换过滤材料", "过滤后仍需消毒"]
            elif "煮沸" in step_description:
                key_points = ["持续煮沸5-10分钟", "使用清洁容器", "冷却后密封保存"]
        elif category == "庇护所":
            if "选择" in step_description or "位置" in step_description:
                key_points = ["避开低洼积水区", "考虑风向和日照", "靠近水源但保持安全距离"]
            elif "搭建" in step_description:
                key_points = ["确保结构稳固", "预留通风口", "做好排水措施"]
        
        # 如果没有特定的关键点，提供通用建议
        if not key_points:
            key_points = ["仔细观察周围环境", "确保安全第一", "如有疑问请寻求帮助"]
        
        return key_points
    
    def _get_skill_tips(self, category: str) -> List[str]:
        """获取技能小贴士"""
        tips_map = {
            "生火": [
                "干燥的材料是成功生火的关键",
                "准备充足的引火物和燃料",
                "选择避风但通风良好的位置",
                "练习不同的生火方法",
                "始终准备灭火材料"
            ],
            "水源": [
                "永远不要直接饮用未处理的自然水源",
                "多种净化方法结合使用效果更好",
                "储存净化后的水要使用清洁容器",
                "学会识别水质的基本方法",
                "节约用水，合理分配"
            ],
            "食物获取": [
                "不确定的食物绝对不要食用",
                "学会基本的可食性测试方法",
                "优先选择熟悉的食物来源",
                "合理搭配营养，避免单一食物",
                "注意食物的保存和处理"
            ],
            "庇护所建造": [
                "位置选择比建造技巧更重要",
                "保温、防水、通风三者缺一不可",
                "就地取材，充分利用自然资源",
                "考虑长期使用的舒适性",
                "定期检查和维护结构"
            ],
            "工具制作": [
                "安全使用工具，避免意外伤害",
                "选择合适的材料很关键",
                "简单实用比复杂精美更重要",
                "定期保养和维护工具",
                "学会多种工具的制作方法"
            ],
            "导航定位": [
                "多种导航方法结合使用",
                "定期确认方向，避免偏离路线",
                "标记重要地点和路径",
                "学会读懂自然界的方向指示",
                "保持冷静，避免恐慌性行动"
            ]
        }
        
        return tips_map.get(category, [
            "多练习，熟能生巧",
            "安全第一，谨慎操作",
            "学会观察和思考",
            "准备充分，有备无患"
        ])
    
    def _get_recommendation_reason(self, skill: Dict, user_level: int) -> str:
        """获取推荐理由"""
        reasons = []
        
        if skill['difficulty_level'] == user_level:
            reasons.append("适合您当前的技能水平")
        elif skill['difficulty_level'] < user_level:
            reasons.append("基础技能，建议优先掌握")
        
        if skill['category'] in ["水源", "庇护所", "生火"]:
            reasons.append("生存必备技能")
        
        if skill.get('estimated_time', 0) <= 60:
            reasons.append("学习时间较短，容易掌握")
        
        if not reasons:
            reasons.append("实用的生存技能")
        
        return "、".join(reasons)
    
    def add_skill_progress(self, user_id: str, skill_id: int, progress: float, notes: str = "") -> bool:
        """记录用户技能学习进度"""
        try:
            # 检查是否已有记录
            query = "SELECT id FROM user_skill_progress WHERE user_id = ? AND skill_id = ?"
            existing = self.db_manager.execute_query(query, (user_id, skill_id))
            
            if existing:
                # 更新现有记录
                update_query = """
                    UPDATE user_skill_progress 
                    SET progress = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ? AND skill_id = ?
                """
                return self.db_manager.execute_update(update_query, (progress, notes, user_id, skill_id))
            else:
                # 创建新记录
                insert_query = """
                    INSERT INTO user_skill_progress (user_id, skill_id, progress, notes)
                    VALUES (?, ?, ?, ?)
                """
                return self.db_manager.execute_update(insert_query, (user_id, skill_id, progress, notes))
        except Exception as e:
            print(f"记录技能进度失败: {e}")
            return False
    
    def get_user_skill_progress(self, user_id: str) -> List[Dict]:
        """获取用户技能学习进度"""
        try:
            query = """
                SELECT usp.*, ss.name, ss.category, ss.difficulty_level
                FROM user_skill_progress usp
                JOIN survival_skills ss ON usp.skill_id = ss.id
                WHERE usp.user_id = ?
                ORDER BY usp.updated_at DESC
            """
            results = self.db_manager.execute_query(query, (user_id,))
            
            progress_list = []
            for result in results:
                progress = dict(result)
                progress['difficulty_desc'] = self.difficulty_levels.get(progress['difficulty_level'], "未知难度")
                progress_list.append(progress)
            
            return progress_list
        except Exception as e:
            print(f"获取用户技能进度失败: {e}")
            return []