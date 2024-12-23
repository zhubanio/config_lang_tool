import unittest
import os
import json
from config_tool import ConfigParser

class TestConfigParser(unittest.TestCase):
    def setUp(self):
        # Путь к папке с тестовыми конфигурациями
        self.configs_path = "config/"
        self.test_files = [
            "weather_config.txt",
            "task_config.txt",
            "web_config.txt",
            "task_test_config.txt",
            "database_config.txt",
            "ecommerce_config.txt",
            "iot_config.txt",
            "network_config.txt",
            "app_config.txt",
            "user_profiles.txt"
        ]
        self.expected_results = {
            # Пример ожидаемого результата для weather_config.txt
            "weather_config.txt": {
                "weather_api": "OpenWeatherMap",
                "default_city": "Moscow",
                "temperature_unit": "Celsius",
                "config": {
                    "api_name": "OpenWeatherMap",
                    "city": "Moscow",
                    "units": "Celsius"
                }
            },
            # Добавьте ожидаемые результаты для других файлов
        }

    def test_all_configs(self):
        for test_file in self.test_files:
            with self.subTest(test_file=test_file):
                file_path = os.path.join(self.configs_path, test_file)
                parser = ConfigParser(file_path)
                result = json.loads(parser.to_json())

                # Проверяем, если ожидаемый результат для файла известен
                if test_file in self.expected_results:
                    expected = self.expected_results[test_file]
                    self.assertEqual(result, expected, f"Mismatch for {test_file}")
                else:
                    # Если ожидаемого результата нет, проверяем базовую структуру
                    self.assertIsInstance(result, dict, f"Result for {test_file} is not a dictionary")

if __name__ == "__main__":
    unittest.main()
