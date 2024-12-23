import json
import re
import sys

class ConfigParser:
    def __init__(self, filepath):
        self.filepath = filepath
        self.constants = {}

    def parse(self):
        with open(self.filepath, 'r', encoding='utf-8') as file:
            text = file.read()

        # 1. Удаляем многострочные комментарии {{! ... }}
        text = re.sub(r'\{\{!.*?\}\}', '', text, flags=re.DOTALL)

        # 2. Убираем лишние пробелы и пустые строки
        text = text.strip()

        # 3. Парсим все объявления констант вида: имя <- значение;
        def replace_constants(match):
            name, value = match.groups()
            evaluated_value = self.evaluate(value.strip())
            self.constants[name] = evaluated_value
            # Удаляем строчку объявления константы из итогового текста
            return ''

        text = re.sub(
            r'([a-z][a-z0-9_]*)\s*<-\s*(.*?);',
            replace_constants,
            text,
            flags=re.MULTILINE | re.DOTALL
        )

        # Если после удаления объявлений констант остался пустой текст,
        # значит, нет root-структуры; вернём только константы.
        if not text.strip():
            return self.constants

        # 5. Заменяем ссылки на константы |имя| в тексте (которые остались)
        def constant_replacer(match):
            const_name = match.group(1)
            if const_name in self.constants:
                # Серелизуем в JSON (чтобы, например, строки обернуть в кавычки)
                value = json.dumps(self.constants[const_name])
                return value
            raise ValueError(f"Undefined constant: {const_name}")

        text = re.sub(r'\|([a-z][a-z0-9_]*)\|', constant_replacer, text)

        # 6. Ищем корневую структуру вида: root_name <- значение;
        match = re.search(
            r'([a-z][a-z0-9_]*)\s*<-\s*(.*?);\s*$',
            text,
            flags=re.MULTILINE | re.DOTALL
        )
        if match:
            root_name, root_value = match.groups()
            root_value = root_value.strip()
            return {root_name: self.evaluate(root_value)}

        # Иначе — синтаксическая ошибка
        raise ValueError(f"Invalid root structure: {text}")

    def evaluate(self, value):
        """
        Рекурсивно разбираем значение в зависимости от формата:
         - Словарь вида [ key => value, key => value, ... ]
         - Массив вида << val, val, val >>
         - Ссылка вида |имя|
         - «Голое» имя константы
         - Числа
         - Строки @"..." или "..."
         - Булевы значения: true, false
        """
        value = value.strip()

        # 1. Словарь: [ key => value, key => value, ... ]
        if value.startswith('[') and value.endswith(']') and '=>' in value:
            # Убираем внешние скобки
            inner = value[1:-1].strip()
            return self.parse_dictionary(inner)

        # 2. Массив: << val, val, val >>
        elif value.startswith('<<') and value.endswith('>>'):
            inner = value[2:-2].strip()
            return self.parse_array(inner)

        # 3. Ссылка вида |имя|
        elif re.match(r'^\|([a-z][a-z0-9_]*)\|$', value):
            const_name = re.match(r'^\|([a-z][a-z0-9_]*)\|$', value).group(1)
            if const_name in self.constants:
                return self.constants[const_name]
            else:
                raise ValueError(f"Undefined constant: {const_name}")

        # 4. «Голое» имя константы (пример: device_id)
        elif value in self.constants:
            return self.constants[value]

        # 5. Строки вида @"..."
        elif re.match(r'^@\".*\"$', value):
            return value[2:-1]

        # 6. Обычные строки "..."
        elif re.match(r'^\".*\"$', value):
            return value[1:-1]

        # 7. Булевы значения true/false
        elif value == "true":
            return True
        elif value == "false":
            return False

        # 8. Целые числа
        elif re.match(r'^\d+$', value):
            return int(value)

        # 9. Если ничего не подошло
        raise ValueError(f"Invalid value: {value}")

    def parse_dictionary(self, dict_text):
        """
        Разбираем словарь, учитывая вложенные структуры.
        1) Разбиваем dict_text на элементы по «верхнеуровневым» запятым.
        2) Для каждой части ищем "key => value".
        3) Вызываем self.evaluate(value) для разбора значения.
        """
        items = self.split_by_top_level_commas(dict_text)
        result = {}

        for item in items:
            item = item.strip()
            # Каждый элемент словаря должен иметь вид: key => value
            m = re.match(r'^([a-z][a-z0-9_]*)\s*=>\s*(.+)$', item, flags=re.DOTALL)
            if not m:
                raise ValueError(f"Invalid dictionary item: {item}")
            key, raw_value = m.groups()
            parsed_value = self.evaluate(raw_value.strip())
            result[key] = parsed_value

        return result

    def parse_array(self, array_text):
        """
        Аналогично словарю, разбираем массив << ... >>,
        разделяя по запятым на верхнем уровне.
        """
        items = self.split_by_top_level_commas(array_text)
        return [self.evaluate(item.strip()) for item in items if item.strip()]

    def split_by_top_level_commas(self, text):
        """
        Разбиваем строку text на элементы по запятым, но только на верхнем
        уровне вложенности. Учитываем скобки [ ... ] и << ... >>.
        """
        parts = []
        current = []
        depth_square = 0  # счётчик для [ ... ]
        depth_angle = 0   # счётчик для << ... >>
        i = 0
        length = len(text)

        while i < length:
            c = text[i]

            # --- Обработка вложенных скобок [ ... ] ---
            if c == '[':
                depth_square += 1
                current.append(c)
                i += 1
                continue
            elif c == ']':
                depth_square -= 1
                current.append(c)
                i += 1
                continue

            # --- Обработка вложенных скобок << ... >> ---
            if c == '<' and (i + 1 < length and text[i+1] == '<'):
                depth_angle += 1
                current.append('<<')
                i += 2
                continue
            elif c == '>' and (i + 1 < length and text[i+1] == '>'):
                depth_angle -= 1
                current.append('>>')
                i += 2
                continue

            # Если это верхнеуровневая запятая (не внутри скобок)
            if c == ',' and depth_square == 0 and depth_angle == 0:
                # Завершаем текущий фрагмент
                part = "".join(current).strip()
                if part:
                    parts.append(part)
                current = []
                i += 1
                continue

            # Иначе просто добавляем символ к текущему фрагменту
            current.append(c)
            i += 1

        # Добавляем последний кусок (если есть)
        tail = "".join(current).strip()
        if tail:
            parts.append(tail)

        return parts

    def to_json(self):
        try:
            parsed_data = self.parse()
            return json.dumps(parsed_data, indent=4, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=4)


def main():
    if len(sys.argv) != 2:
        print("Usage: python config_tool.py <path_to_config_file>")
        sys.exit(1)

    filepath = sys.argv[1]
    parser = ConfigParser(filepath)
    result = parser.to_json()
    print(result)

if __name__ == "__main__":
    main()
