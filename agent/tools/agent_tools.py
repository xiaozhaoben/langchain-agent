import os.path
import random
import requests

from langchain_core.tools import tool
from rag.rag_service import RagSummarizeService
from utils.logger_handler import logger
from utils.config_handler import agent_conf
from utils.path_tool import get_abs_path
from agent.tools.weather_service import weather_service

rag = RagSummarizeService()

user_ids = ["1001", "1002", "1003", "1004", "1005", "1006", "1007", "1008", "1009", "1010",]
month_arr = ["2025-01", "2025-02", "2025-03", "2025-04", "2025-05", "2025-06",
             "2025-07", "2025-08", "2025-09", "2025-10", "2025-11", "2025-12", ]

external_data = {}

@tool(description="从向量存储中检索参考资料")
def rag_summarize(query: str) -> str:
    return rag.rag_summarize(query)

@tool(description="获取指定城市的实时天气信息，包括温度、湿度、风速、空气质量等，以字符串形式返回")
def get_weather(city: str) -> str:
    """
    获取指定城市的实时天气信息
    :param city: 城市名称（支持中文，如：北京、上海、深圳）
    :return: 天气信息字符串
    """
    return weather_service.get_weather(city)

def _get_location_by_ip() -> str:
    """
    通过IP地址获取当前城市名称
    使用多个免费API作为备份，确保可用性

    :return: 城市名称，如"深圳市"
    """
    # 禁用代理，避免本地代理导致超时
    proxies = {
        'http': None,
        'https': None,
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
    }

    # 方案1: ip-api.com（免费，支持中文，推荐使用）
    try:
        response = requests.get(
            "http://ip-api.com/json/?lang=zh-CN",
            timeout=5,
            proxies=proxies,
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                city = data.get('city', '')
                if city:
                    logger.info(f"[get_user_location] ip-api.com返回城市: {city}")
                    return city
    except Exception as e:
        logger.warning(f"[get_user_location] ip-api.com调用失败: {e}")

    # 方案2: ipinfo.io（免费额度有限）
    try:
        response = requests.get(
            "https://ipinfo.io/json",
            timeout=5,
            proxies=proxies,
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            city = data.get('city', '')
            if city:
                logger.info(f"[get_user_location] ipinfo.io返回城市: {city}")
                return city
    except Exception as e:
        logger.warning(f"[get_user_location] ipinfo.io调用失败: {e}")

    # 方案3: ip-api.com备用（英文）
    try:
        response = requests.get(
            "http://ip-api.com/json/",
            timeout=5,
            proxies=proxies,
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                city = data.get('city', '')
                if city:
                    logger.info(f"[get_user_location] ip-api.com(英文)返回城市: {city}")
                    return city
    except Exception as e:
        logger.warning(f"[get_user_location] ip-api.com(英文)调用失败: {e}")

    # 如果所有API都失败，返回默认城市
    default_city = "深圳市"
    logger.warning(f"[get_user_location] 所有API调用失败，返回默认城市: {default_city}")
    return default_city


@tool(description="获取用户所在城市的名称，以纯字符串形式返回")
def get_user_location() -> str:
    """
    获取用户当前所在城市
    通过IP定位API自动获取，无需用户输入
    :return: 城市名称字符串
    """
    return _get_location_by_ip()

@tool(description="获取用户的ID，以纯字符串形式返回")
def get_user_id() -> str:
    return random.choice(user_ids)

@tool(description="获取当前月份，以纯字符串形式返回")
def get_current_month() -> str:
    return random.choice(month_arr)

def generate_external_data():
    """
    {
        "user_id": {
            "month": {"特征": xxx, "效率": xxx},
            "month": {"特征": xxx, "效率": xxx},
            "month": {"特征": xxx, "效率": xxx},
        }
    }
    :return:
    """
    if not external_data:
        external_data_path = get_abs_path(agent_conf['external_data_path'])
        if not os.path.exists(external_data_path):
            raise FileNotFoundError(f"外部数据文件{agent_conf['external_data_path']}不存在")
        with open(external_data_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines[1:]: # 跳过表头，从第一条数据读取
                if not line.strip():  # 跳过空行
                    continue
                arr = line.strip().split(",")
                if len(arr) < 6:  # 确保有足够的列
                    continue
                user_id: str = arr[0].replace('"', "")
                feature: str = arr[1].replace('"', "")
                efficiency: str = arr[2].replace('"', "")
                consumables: str = arr[3].replace('"', "")
                comparison: str = arr[4].replace('"', "")
                time: str = arr[5].replace('"', "")

                if user_id not in external_data:
                    external_data[user_id] = {}

                external_data[user_id][time] = {
                    "特征": feature,
                    "效率": efficiency,
                    "耗材": consumables,
                    "对比": comparison,
                }



@tool(description="从外部系统中获取指定用户在指定月份的使用记录，以纯字符串形式返回， 如果未检索到返回空字符串")
def fetch_external_data(user_id: str, month: str) -> str:
    generate_external_data()
    try:
        return external_data[user_id][month]
    except KeyError:
        logger.warning(f"[fetch_external_data]无法检索到用户{user_id}在{month}的数据")
        return ''

@tool(description="无入参，无返回值，调用后触发中间件自动为报告生成的场景动态注入上下文信息，为后续提示词切换提供上下文信息")
def fill_context_for_report():
    return "fill_context_for_report已调用"