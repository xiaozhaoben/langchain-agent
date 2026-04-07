"""
天气服务模块：提供天气查询功能
支持多种天气API后端
"""

import os
import requests
import random
from typing import Optional
from utils.logger_handler import logger


def get_weather_api_key() -> Optional[str]:
    """
    获取天气API Key，优先从环境变量读取
    :return: API Key 或 None
    """
    # 优先从环境变量获取
    api_key = os.environ.get("WEATHER_API_KEY")
    if api_key:
        return api_key.strip()

    # 回退到配置文件
    try:
        from utils.config_handler import agent_conf
        api_key = agent_conf.get('weather_api_key')
        if api_key:
            return api_key.strip()
    except Exception as e:
        logger.warning(f"[WeatherService] 读取配置文件失败: {str(e)}")

    return None


class WeatherService:
    """天气服务类，封装天气API调用"""

    def __init__(self):
        # 从环境变量或配置文件获取API Key
        self.api_key = get_weather_api_key()
        # wttr.in 免费API，无需API Key
        self.wttr_base_url = "https://wttr.in"
        # OpenWeatherMap API（需要API Key）
        self.owm_base_url = "https://api.openweathermap.org/data/2.5/weather"
        # 模拟天气数据（作为最终回退）
        self._mock_weather_data = {
            "晴天": {"temp_range": (20, 32), "humidity_range": (30, 50), "wind": "微风", "aqi_range": (20, 50)},
            "多云": {"temp_range": (18, 28), "humidity_range": (40, 60), "wind": "微风", "aqi_range": (30, 70)},
            "阴天": {"temp_range": (15, 25), "humidity_range": (50, 70), "wind": "微风", "aqi_range": (40, 80)},
            "小雨": {"temp_range": (12, 22), "humidity_range": (70, 90), "wind": "微风", "aqi_range": (30, 60)},
            "大雨": {"temp_range": (10, 20), "humidity_range": (80, 95), "wind": "中风", "aqi_range": (20, 50)},
        }

    def get_mock_weather(self, city: str) -> str:
        """
        生成模拟天气数据（作为最终回退方案）
        :param city: 城市名称
        :return: 模拟的天气信息字符串
        """
        # 随机选择天气类型
        weather_type = random.choice(list(self._mock_weather_data.keys()))
        data = self._mock_weather_data[weather_type]

        # 生成随机数据
        temp = random.randint(*data["temp_range"])
        feels_like = temp + random.randint(-2, 2)
        humidity = random.randint(*data["humidity_range"])
        aqi = random.randint(*data["aqi_range"])

        # 根据天气类型生成风速和风向
        wind_levels = ["微风", "中风", "强风"]
        wind_dirs = ["东风", "南风", "西风", "北风", "东南风", "西北风", "东北风", "西南风"]
        wind = f"{random.choice(wind_levels)} {random.choice(wind_dirs)}"

        # 降水量（雨天有降水）
        precip = 0
        if "雨" in weather_type:
            precip = round(random.uniform(0.5, 15.0), 1)

        result = (
            f"城市: {city}\n"
            f"天气: {weather_type}\n"
            f"气温: {temp}°C (体感温度: {feels_like}°C)\n"
            f"湿度: {humidity}%\n"
            f"风: {wind}\n"
            f"降水量: {precip} mm\n"
            f"空气质量指数(AQI): {aqi}"
        )

        logger.warning(f"[WeatherService] 使用模拟数据，城市: {city}")
        return result

    def get_weather_by_wttr(self, city: str, lang: str = "zh-CN") -> str:
        """
        使用 wttr.in 免费API获取天气信息
        :param city: 城市名称（支持中文）
        :param lang: 语言代码，默认中文
        :return: 天气信息字符串
        """
        try:
            # wttr.in 支持格式化输出
            url = f"{self.wttr_base_url}/{city}"
            params = {
                "format": "j1",  # JSON格式
                "lang": lang
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # 解析当前天气
            current = data.get("current_condition", [{}])[0]

            # 提取关键信息
            temp_c = current.get("temp_C", "N/A")
            feels_like = current.get("FeelsLikeC", "N/A")
            humidity = current.get("humidity", "N/A")
            weather_desc = current.get("lang_zh", [{}])[0].get("value",
                          current.get("weatherDesc", [{}])[0].get("value", "未知"))
            wind_speed = current.get("windspeedKmph", "N/A")
            wind_dir = current.get("winddir16Point", "N/A")
            precip = current.get("precipMM", "0")

            # 获取空气质量（如果有）
            air_quality = current.get("air_quality", {})
            aqi = air_quality.get("us-epa-index", "N/A")

            # 组装返回信息
            result = (
                f"城市: {city}\n"
                f"天气: {weather_desc}\n"
                f"气温: {temp_c}°C (体感温度: {feels_like}°C)\n"
                f"湿度: {humidity}%\n"
                f"风速: {wind_speed} km/h, 风向: {wind_dir}\n"
                f"降水量: {precip} mm\n"
                f"空气质量指数(EPA): {aqi}"
            )

            logger.info(f"[WeatherService] wttr.in 查询成功: {city}")
            return result

        except requests.exceptions.Timeout:
            logger.error(f"[WeatherService] wttr.in 请求超时: {city}")
            return self.get_mock_weather(city)
        except requests.exceptions.RequestException as e:
            logger.error(f"[WeatherService] wttr.in 请求失败: {str(e)}")
            return self.get_mock_weather(city)
        except (KeyError, IndexError) as e:
            logger.error(f"[WeatherService] 解析天气数据失败: {str(e)}")
            return self.get_mock_weather(city)
        except Exception as e:
            logger.error(f"[WeatherService] 未知错误: {str(e)}", exc_info=True)
            return self.get_mock_weather(city)

    def get_weather_by_openweathermap(self, city: str) -> str:
        """
        使用 OpenWeatherMap API 获取天气信息（需要API Key）
        :param city: 城市名称
        :return: 天气信息字符串
        """
        if not self.api_key:
            logger.warning("[WeatherService] 未配置OpenWeatherMap API Key，回退到wttr.in")
            return self.get_weather_by_wttr(city)

        try:
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric",
                "lang": "zh_cn"
            }

            response = requests.get(self.owm_base_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # 解析天气数据
            main = data.get("main", {})
            weather = data.get("weather", [{}])[0]
            wind = data.get("wind", {})

            temp = main.get("temp", "N/A")
            feels_like = main.get("feels_like", "N/A")
            humidity = main.get("humidity", "N/A")
            pressure = main.get("pressure", "N/A")
            weather_desc = weather.get("description", "未知")
            wind_speed = wind.get("speed", "N/A")

            result = (
                f"城市: {city}\n"
                f"天气: {weather_desc}\n"
                f"气温: {temp}°C (体感温度: {feels_like}°C)\n"
                f"湿度: {humidity}%\n"
                f"气压: {pressure} hPa\n"
                f"风速: {wind_speed} m/s"
            )

            logger.info(f"[WeatherService] OpenWeatherMap 查询成功: {city}")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"[WeatherService] OpenWeatherMap 请求失败: {str(e)}")
            # 回退到 wttr.in
            return self.get_weather_by_wttr(city)
        except Exception as e:
            logger.error(f"[WeatherService] OpenWeatherMap 错误: {str(e)}", exc_info=True)
            return self.get_weather_by_wttr(city)

    def get_weather(self, city: str) -> str:
        """
        获取天气信息的主入口
        优先使用OpenWeatherMap（需API Key），否则使用wttr.in
        :param city: 城市名称
        :return: 天气信息字符串
        """
        if not city or not city.strip():
            return "城市名称不能为空"

        city = city.strip()

        # 如果有API Key，优先使用OpenWeatherMap
        if self.api_key:
            return self.get_weather_by_openweathermap(city)

        # 否则使用免费的wttr.in
        return self.get_weather_by_wttr(city)


# 单例实例
weather_service = WeatherService()


if __name__ == '__main__':
    # 测试天气服务
    print("=" * 50)
    print("测试天气查询服务")
    print("=" * 50)

    test_cities = ["北京", "上海", "深圳", "广州"]
    for city in test_cities:
        print(f"\n查询城市: {city}")
        print("-" * 30)
        result = weather_service.get_weather(city)
        print(result)
        print()
