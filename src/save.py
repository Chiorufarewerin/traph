import os
from fpdf import FPDF

from data import SAVE_FOLDER


class Save:
    @staticmethod
    def make_dir(path):
        """Создать папку если нет"""
        if not os.path.exists(path):
            os.makedirs(path)

    @staticmethod
    def get_one_path(category):
        """Получить путь для 1х этикеток"""
        return os.path.join(SAVE_FOLDER, category, '1')

    @staticmethod
    def get_three_path(category):
        """Получить путь для 3х этикеток"""
        return os.path.join(SAVE_FOLDER, category, '3')

    @staticmethod
    def get_category_path(category):
        return os.path.join(SAVE_FOLDER, category)

    @classmethod
    def make_category_dir(cls, category):
        # Создаем главную папку save
        cls.make_dir(SAVE_FOLDER)

        # Создаем папку внутри для категории
        cls.make_dir(cls.get_category_path(category))

        # Создаем папки 1 и 3
        cls.make_dir(cls.get_one_path(category))
        cls.make_dir(cls.get_three_path(category))

    @classmethod
    def save_template(cls, template, category, save_name):
        cls.make_category_dir(category)
        image_path = os.path.join(cls.get_category_path(category), save_name + '.jpg')
        pdf_path = os.path.join(cls.get_one_path(category), save_name + '.pdf')
        pdf_three_path = os.path.join(cls.get_three_path(category), save_name + '.pdf')
        template.save(image_path, 'JPEG', quality=100)
        template.save(pdf_path, 'PDF', resolution=100.0)

        pdf = FPDF()
        pdf.add_page()
        # Координаты все подогнаны
        pdf.image(image_path, 25.66875, 10.63316582, 161.25445544, 90.712209302)
        pdf.image(image_path, 25.66875, 102.23316582, 161.25445544, 90.712209302)
        pdf.image(image_path, 25.66875, 193.83316582, 161.25445544, 90.712209302)
        pdf.output(pdf_three_path, 'F')
