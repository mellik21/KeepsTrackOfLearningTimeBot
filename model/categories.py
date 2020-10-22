"""Работа с категориями расходов"""
from typing import Dict, List, NamedTuple

from resourses.database import database as db


class Category(NamedTuple):
    codename: str  # id?
    name: str  # имя категории
    aliases: List[str]  # варианты названия категории

class Categories:
    def __init__(self):
        self._categories = self._load_categories()

    def _load_categories(self) -> List[Category]:
        categories = db.fetchall(
            "category", "codename name aliases".split()
        )
        categories = self._fill_aliases(categories)
        return categories

    def _fill_aliases(self, categories: List[Dict]) -> List[Category]:
        #Заполняет по каждой категории aliases
        categories_result = []
        for index, category in enumerate(categories):
            aliases = category["aliases"].split(",")
            aliases = list(filter(None, map(str.strip, aliases)))
            aliases.append(category["codename"])
            aliases.append(category["name"])
            categories_result.append(Category(
                codename=category['codename'],
                name=category['name'],
                aliases=aliases
            ))
        return categories_result

    def get_all_categories(self) -> List[Category]:
        return self._categories

    def get_category(self, category_name: str) -> Category:
        finded = None
        for category in self._categories:
            for alias in category.aliases:
                if category_name in alias:
                    finded = category
        return finded
