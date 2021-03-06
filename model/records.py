from typing import List, NamedTuple
import datetime
import pytz
import re
from resourses.database import database as db
from model.categories import Categories


class Message(NamedTuple):
    time_count: int
    category_text: str


class Record(NamedTuple):
    id: str
    time_count: str  # предположительно всегда в минутах
    category_codename: str
    raw_text: str


class Records:
    def __init__(self):
        self._records = self._load_records()

    @staticmethod
    def load_records() -> List[Record]:
        rows = db.fetchall(
            "record", "id time_count category_codename raw_text".split()
        )
        records = []
        for index, record in enumerate(rows):
            records.append(Record(
                id=record['id'],
                time_count=record['time_count'],
                category_codename=record['category_codename'],
                raw_text=record['raw_text']
            ))
        return records

    def get_all_records(self) -> List[tuple]:
        return self._records

    def get_record(self, record_id: str) -> Record:
        finded = None
        for record in self._records:
            if record.id == record_id:
                finded = record
        return finded

    @classmethod
    def last(cls) -> List[Record]:
        cursor = db.get_cursor()
        cursor.execute(
            "select r.id, r.time_count, r.category_codename, r.raw_text "
            "from record r " +
            "order by r.created desc limit 10")
        rows = cursor.fetchall()
        last_expenses = [Record(id=row[0], time_count=row[1],
                                category_codename=row[2], raw_text=row[3]) for row in rows]
        return last_expenses


def add_record(raw_message: str) -> Record:
    parsed_message = _parse_message(raw_message)
    category = Categories().get_category(
        parsed_message.category_text)

    db.insert("record", {
        "time_count": parsed_message.time_count,
        "created": _get_now_formatted(),
        "category_codename": category.codename,
        "raw_text": raw_message
    })
    return Record(id=None,
                  category_codename=category.codename)


def _parse_message(raw_message: str) -> Message:
    regexp_result = re.match(r"([\d ]+) (.*)", raw_message)
    if not regexp_result or not regexp_result.group(0) \
            or not regexp_result.group(1) or not regexp_result.group(2):
        raise pytz.exceptions.NotCorrectMessage(
            "Не могу понять сообщение. Напишите сообщение в формате, "
            "например:\n1500 метро")

    time_count = regexp_result.group(1).replace(" ", "")
    category_name = regexp_result.group(2).strip().lower()
    return Message(time_count=time_count, category_codename=category_name)


def _get_now_formatted(self) -> str:
    now = datetime.datetime.now(pytz.timezone("Europe/Moscow")).strftime("%Y-%m-%d %H:%M:%S")
    return now.strftime("%Y-%m-%d %H:%M:%S")
