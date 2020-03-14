from data import Data
from traph import Traph
from utils import replace_quotes


def main():
    """Место, где запускается программа"""

    data = Data.get_csv_data()
    if len(data) < 2:
        print('Неверый CSV файл')
        return
    if any([len(row) <= 13 for row in data]):
        print('Не все колонки имеются')
        return
    for i, row in enumerate(data[1:], start=2):
        # Заменить все кавычки на елочки и убрать лишние пробелы
        row = [replace_quotes(string.strip()) for string in row]

        kwargs = {
            'name': row[0],  # Полное имя
            'short_name': row[1],  # Наименование
            'what': row[2],  # Что за печенье
            'netto': row[3],  # Масса нетто
            'brutto': row[4],  # Масса брутто
            'proteins': row[5],  # Белки
            'fats': row[6],  # Жиры
            'carbohydrates': row[7],  # Углеводы
            'kkal': row[8],  # Килокалории
            'tu': row[9],  # TU
            'category': row[10],  # Категория
            'composition': row[11],  # Состав
            'shelf_life': row[12],  # Срок годности
            'code': row[13],  # Штрих код
        }
        if len(row) > 14:
            kwargs['bold_text'] = row[14]  # Текст жирным
        if len(row) > 15:
            kwargs['top_image'] = row[15]  # Картинка сверху

        if len(kwargs['category']) == 0:
            print('Категория на строке {} не заполнена.'.format(i))
            continue

        traph = Traph(**kwargs)
        traph.make_traph()

        # Очистим память
        del traph

    print('Программа завершила свою работу!')


if __name__ == '__main__':
    main()
