# config_lang_tool
Это учебный проект № 3 по конфигурационному управлению Матюхи Егора Алексеевича, студента ИКБО-42-23 РТУ МИРЭА. В нём реализован инструмент для обработки и трансляции конфигурационных файлов из пользовательского синтаксиса в JSON.

## Особенности
- Поддержка многострочных комментариев (`{{! ... }}`).
- Разбор массивов (`<< ... >>`) и словарей (`[ key => value, ... ]`) с вложенными структурами.
- Поддержка констант и ссылок на них (`|имя|`).
- Распознавание строк, чисел, массивов, словарей и булевых значений (`true`, `false`).

## Установка
1. Склонируйте репозиторий:
   ```bash
   git clone https://github.com/username/config_lang_tool.git
   cd config_lang_tool

2. Убедитесь, что у вас установлен Python 3.6 или выше.

3. (Опционально) Создайте виртуальное окружение:
   ```bash
   python -m venv venv
    source venv/bin/activate    # Linux/macOS
    venv\\Scripts\\activate

4. Установите зависимости:
   ```bash
   pip install -r requirements.txt

## Использование
1. Поместите ваши конфигурационные файлы в папку configs/ или используйте существующие:
    ├── configs/             
│   ├── weather_config.txt
│   ├── task_config.txt
│   ├── web_config.txt
│   ├── task_test_config.txt
│   ├── database_config.txt
│   ├── ecommerce_config.txt
│   ├── iot_config.txt
│   ├── network_config.txt
│   ├── app_config.txt
│   └── user_profiles.txt

2. Запустите инструмент, указав путь к файлу:

       python config_tool.py configs/weather_config.txt

3. Чтобы вывести содержание текстового файла:

       more config/weather_config.txt

## Тестирование
Запустите тесты:
  
    python -m unittest discover tests

## Лицензия
Проект распространяется под лицензией MIT.

