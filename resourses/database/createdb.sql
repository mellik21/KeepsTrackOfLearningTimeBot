
create table category(
    codename varchar(255) primary key,
    name varchar(255),
    aliases text
);

create table record(
    id integer primary key,
    created datetime,
    time_count integer,
    category_codename integer,
    raw_text text,
    FOREIGN KEY(category_name) REFERENCES category(codename)
);

insert into category (codename, name, aliases)
values
    ("python", "питон", "язык питон"),
    ("ml", "основы машинного обучения", "теория machine learning, теория машинного обучения, основы ml, теория ml"),
    ("data science", "анализ данных", "обработка данных, аналитика данных, теория анализа данных, основы анализа данных"),
    ("statistic", "мат. статистика", "математическая статистика, статистика, теория математической статистики, основы мат.статистики"),
    ("math", "математика", "матан, мат.анализ, мат. анализ, математический анализ, теория мат.анализа"),
    ("ml algo", "алгоритмы машинного обучения", "ml алгоритмы, алгоритмы ml, алгоритмы machine learning, machine learning алгоритмы, алгоритмы"),
    ("contest", "kaggle", "kaggle соревнования, теория для kaggle"),
    ("coding", "программирование", "кодинг, написание кода"),
    ("cidi", "ci/cd", "докер,  основы ci/cd")
