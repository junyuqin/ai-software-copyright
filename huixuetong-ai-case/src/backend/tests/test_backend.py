"""
慧学通 (HuiXueTong) - 单元测试模块
功能：后端 API 测试、服务层测试、工具函数测试
"""

import unittest
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))


class TestDataFusion(unittest.TestCase):
    """数据融合工具测试"""
    
    def setUp(self):
        from utils.data_fusion import calc_3d_scores, hash_student_id, WEIGHTS
        self.calc_3d_scores = calc_3d_scores
        self.hash_student_id = hash_student_id
        self.WEIGHTS = WEIGHTS
    
    def test_calc_3d_scores_default(self):
        """测试默认权重计算"""
        mock_data = {
            'quiz_avg': 75.0,
            'attendance': 0.9,
            'debug_success': 0.65,
            'project_score': 80.0,
            'pep8_score': 85.0
        }
        k, s, l = self.calc_3d_scores(mock_data)
        
        # 验证返回值类型
        self.assertIsInstance(k, float)
        self.assertIsInstance(s, float)
        self.assertIsInstance(l, float)
        
        # 验证分数在合理范围内
        self.assertGreaterEqual(k, 0)
        self.assertLessEqual(k, 100)
        self.assertGreaterEqual(s, 0)
        self.assertLessEqual(s, 100)
        self.assertGreaterEqual(l, 0)
        self.assertLessEqual(l, 100)
    
    def test_calc_3d_scores_custom_weights(self):
        """测试自定义权重计算"""
        mock_data = {
            'quiz_avg': 80.0,
            'attendance': 0.8,
            'debug_success': 0.7,
            'project_score': 75.0,
            'pep8_score': 90.0
        }
        custom_weights = {
            'knowledge': {'quiz_avg': 0.6, 'attendance': 0.2, 'base': 10},
            'skill': {'debug_success': 0.5, 'project_score': 0.5},
            'literacy': {'attendance': 0.3, 'pep8_score': 0.4, 'base': 20}
        }
        k, s, l = self.calc_3d_scores(mock_data, custom_weights)
        
        self.assertIsInstance(k, float)
        self.assertIsInstance(s, float)
        self.assertIsInstance(l, float)
    
    def test_hash_student_id(self):
        """测试学生 ID 哈希脱敏"""
        student_id = "test_student_123"
        hashed = self.hash_student_id(student_id)
        
        # 验证返回字符串长度
        self.assertEqual(len(hashed), 16)
        
        # 验证相同输入产生相同输出
        hashed2 = self.hash_student_id(student_id)
        self.assertEqual(hashed, hashed2)
        
        # 验证不同输入产生不同输出
        hashed3 = self.hash_student_id("different_student")
        self.assertNotEqual(hashed, hashed3)


class TestConfig(unittest.TestCase):
    """配置模块测试"""
    
    def test_config_load(self):
        """测试配置加载"""
        from config import Config, load_config
        
        # 验证配置类存在必要属性
        self.assertTrue(hasattr(Config, 'FLASK_DEBUG'))
        self.assertTrue(hasattr(Config, 'FLASK_PORT'))
        self.assertTrue(hasattr(Config, 'BAIDU_API_KEY'))
        self.assertTrue(hasattr(Config, 'BAIDU_SECRET_KEY'))


class TestLLMService(unittest.TestCase):
    """大模型服务测试"""
    
    def test_llm_service_init(self):
        """测试 LLM 服务初始化"""
        from services.llm_service import LLMService
        
        service = LLMService()
        self.assertIsNotNone(service.token_url)
        self.assertIsNotNone(service.chat_url)
    
    def test_llm_service_fallback(self):
        """测试降级响应（无有效 token）"""
        from services.llm_service import LLMService
        
        service = LLMService()
        report = service.generate_diagnosis(75.0, 70.0, 80.0)
        
        # 验证返回包含 AI 标记
        self.assertIn('[AI 辅助生成]', report)


class TestAppRoutes(unittest.TestCase):
    """Flask 应用路由测试"""
    
    def setUp(self):
        from app import create_app
        self.app = create_app()
        self.client = self.app.test_client()
    
    def test_health_check(self):
        """测试健康检查接口"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['status'], 'ok')
    
    def test_get_profile(self):
        """测试获取学生画像接口"""
        response = self.client.get('/api/profile/test-uuid')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('uuid', data)
        self.assertIn('knowledge_score', data)
        self.assertIn('skill_score', data)
        self.assertIn('literacy_score', data)
    
    def test_get_warnings(self):
        """测试获取预警列表接口"""
        response = self.client.get('/api/warnings')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('warnings', data)
        self.assertIsInstance(data['warnings'], list)
    
    def test_diagnosis_empty_data(self):
        """测试诊断报告接口空数据处理"""
        response = self.client.post('/api/diagnosis', json={})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('diagnosis', data)
        self.assertIn('ai_marked', data)
    
    def test_404_handler(self):
        """测试 404 错误处理"""
        response = self.client.get('/nonexistent-route')
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertEqual(data['code'], 404)


if __name__ == '__main__':
    # 运行所有测试
    unittest.main(verbosity=2)
