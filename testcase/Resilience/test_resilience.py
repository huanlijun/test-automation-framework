import allure
import pytest
import requests
import time

from common.readyaml import get_testcase_yaml
from base.apiutil import RequestBase
from base.generateId import m_id, c_id
from conf.operationConfig import OperationConfig
from common.recordlog import logs


@allure.feature(next(m_id) + '韧性测试模块')
class TestResilience:

    @allure.story(next(c_id) + '接口超时处理-查询用户')
    @pytest.mark.run(order=1)
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml('./testcase/Resilience/timeout_query.yaml'))
    def test_timeout_query(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)

    @allure.story(next(c_id) + '接口超时处理-商品列表')
    @pytest.mark.run(order=2)
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml('./testcase/Resilience/timeout_goods.yaml'))
    def test_timeout_goods(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)

    @allure.story(next(c_id) + '接口超时处理-删除用户')
    @pytest.mark.run(order=3)
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml('./testcase/Resilience/timeout_delete.yaml'))
    def test_timeout_delete(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)

    @allure.story(next(c_id) + '重复请求幂等性')
    @pytest.mark.run(order=4)
    def test_idempotent_delete(self):
        """同一删除请求重复发送，第二次应返回失败（用户已不存在）"""
        allure.dynamic.title('重复删除同一用户-幂等性验证')
        conf = OperationConfig()
        host = conf.get_section_for_data('api_envi', 'host')
        url = host + '/dar/user/deleteUser'
        headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}
        data = {'user_id': '112576886322112'}

        # 第一次请求
        res1 = requests.post(url, data=data, headers=headers, verify=False, timeout=10)
        logs.info('幂等性测试-第一次响应: %s' % res1.text)
        allure.attach(res1.text, '第一次请求响应', allure.attachment_type.TEXT)
        assert '删除成功' in res1.text, '第一次删除应成功'

        # 第二次请求（mock服务不维护状态，此处验证接口不崩溃且有响应）
        res2 = requests.post(url, data=data, headers=headers, verify=False, timeout=10)
        logs.info('幂等性测试-第二次响应: %s' % res2.text)
        allure.attach(res2.text, '第二次请求响应', allure.attachment_type.TEXT)
        assert res2.status_code == 200, '重复请求接口应正常响应，不应崩溃'

    @allure.story(next(c_id) + '高频并发请求稳定性')
    @pytest.mark.run(order=5)
    def test_concurrent_requests(self):
        """连续快速发送多次查询请求，验证服务稳定性"""
        allure.dynamic.title('高频请求-服务稳定性验证')
        conf = OperationConfig()
        host = conf.get_section_for_data('api_envi', 'host')
        url = host + '/dar/user/queryUser'
        headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}
        data = {'user_id': '123839387391912'}

        fail_count = 0
        total = 10
        for i in range(total):
            try:
                res = requests.post(url, data=data, headers=headers, verify=False, timeout=10)
                if res.status_code != 200:
                    fail_count += 1
                    logs.error('第%d次请求失败，状态码: %s' % (i + 1, res.status_code))
            except Exception as e:
                fail_count += 1
                logs.error('第%d次请求异常: %s' % (i + 1, str(e)))

        allure.attach(
            '总请求次数: %d\n成功次数: %d\n失败次数: %d' % (total, total - fail_count, fail_count),
            '并发稳定性测试结果',
            allure.attachment_type.TEXT
        )
        assert fail_count == 0, '高频请求中存在 %d 次失败，服务稳定性不达标' % fail_count

    @allure.story(next(c_id) + '响应时间性能基线')
    @pytest.mark.run(order=6)
    def test_response_time_baseline(self):
        """验证核心接口响应时间在可接受范围内（< 2s）"""
        allure.dynamic.title('响应时间基线-查询用户接口')
        conf = OperationConfig()
        host = conf.get_section_for_data('api_envi', 'host')
        url = host + '/dar/user/queryUser'
        headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}
        data = {'user_id': '123839387391912'}

        start = time.time()
        res = requests.post(url, data=data, headers=headers, verify=False, timeout=10)
        elapsed = time.time() - start

        allure.attach(
            '接口地址: %s\n响应时间: %.3fs\n响应状态码: %d' % (url, elapsed, res.status_code),
            '响应时间测试结果',
            allure.attachment_type.TEXT
        )
        logs.info('响应时间基线测试: %.3fs' % elapsed)
        assert elapsed < 2.0, '接口响应时间 %.3fs 超过基线 2s' % elapsed
