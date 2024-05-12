#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import typing as t

import psycopg2


def display_trains(punkts: t.List[t.Dict[str, t.Any]]) -> None:
    """
    Отобразить список поездов
    """
    if punkts:
        line = "+-{}-+-{}-+-{}-+-{}-+".format(
            "-" * 4, "-" * 30, "-" * 20, "-" * 17
        )
        print(line)
        print(
            "| {:^4} | {:^30} | {:^20} | {:^17} |".format(
                "№", "Номер поезда", "Пункт назначения", "Время отправления"
            )
        )
        print(line)

        for idx, train in enumerate(punkts, 1):
            print(
                "| {:>4} | {:<30} | {:<20} | {:>8} |".format(
                    idx,
                    train.get("nomer", ""),
                    train.get("punkt", ""),
                    train.get("time", 0),
                )
            )
            print(line)
    else:
        print("Список поездов пуст.")


def create_db() -> None:
    """
    Создать базу данных.
    """
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="PASSWORD",
        host="localhost",
        port=5432,
    )
    cursor = conn.cursor()
    # Создать таблицу с информацией о поездах.
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS nomers (
            nomer_id serial primary key,
            nomer_title TEXT NOT NULL
        )
        """
    )
    # Создать таблицу с информацией о пунктах.
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS punkts (
            punkt_id serial primary key,
            punkt_name TEXT NOT NULL,
            nomer_id INTEGER NOT NULL,
            times_count INTEGER NOT NULL,
            FOREIGN KEY(nomer_id) REFERENCES nomers(nomer_id)
        )
        """
    )
    conn.commit()
    conn.close()


def add_trains(nomer: str, punkts: str, time: int) -> None:
    """
    Добавить поезд в базу данных.
    """
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="PASSWORD",
        host="localhost",
        port=5432,
    )
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT nomer_id FROM nomers WHERE nomer_title = %s
        """,
        (nomer,),
    )
    nomer_id = cursor.lastrowid
    row = cursor.fetchone()
    if row is None:
        cursor.execute(
            """
            INSERT INTO nomers (nomer_title) VALUES (%s)
            """,
            (nomer,),
        )
        nomer_id = cursor.lastrowid
    else:
        nomer_id = row[0]
    conn.commit()
    cursor.execute(
        """
        insert into punkts (punkt_name, nomer_id, times_count)
        values (%s, %s, %s);
        """,
        (punkts, nomer_id, time),
    )
    conn.commit()
    conn.close()


def select_all() -> t.List[t.Dict[str, t.Any]]:
    """
    Выбрать все поезда.
    """
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="PASSWORD",
        host="localhost",
        port=5432,
    )
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT punkts.punkt_name,
        nomers.nomer_title,
        punkts.times_count
        FROM punkts
        INNER JOIN nomers ON nomers.nomer_id = punkts.nomer_id
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "nomer": row[0],
            "punkt": row[1],
            "time": row[2],
        }
        for row in rows
    ]


def select_trains(period):
    """
    Выбрать поезд с заданным временем.
    """
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="PASSWORD",
        host="localhost",
        port=5432,
    )
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT punkts.punkt_name, nomers.nomer_title, punkts.times_count
        FROM punkts
        INNER JOIN nomers ON punkts.nomer_id = nomers.nomer_id
        WHERE punkts.times_count >= %s
        """,
        (period,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "nomer": row[0],
            "punkt": row[1],
            "time": row[2],
        }
        for row in rows
    ]


def main(command_line=None):
    parser = argparse.ArgumentParser("trains")
    parser.add_argument(
        "--version", action="version", version="%(prog)s 0.1.0"
    )

    subparsers = parser.add_subparsers(dest="command")

    add = subparsers.add_parser("add", help="Add a new train")
    add.add_argument(
        "-n",
        "--nomer",
        action="store",
        required=True,
        help="The train's nomer",
    )
    add.add_argument(
        "-p",
        "--punkt",
        action="store",
        required=True,
        help="The punkt's name",
    )
    add.add_argument(
        "-t",
        "--time",
        action="store",
        type=int,
        required=True,
        help="The time",
    )

    _ = subparsers.add_parser("display", help="Display all trains")

    select = subparsers.add_parser("select", help="Select the time of train`s")
    select.add_argument(
        "--sp",
        action="store",
        required=True,
        help="The required name of punkt",
    )
    args = parser.parse_args(command_line)

    create_db()
    if args.command == "add":
        add_trains(args.nomer, args.punkt, args.time)

    elif args.command == "display":
        display_trains(select_all())

    elif args.command == "select":
        display_trains(select_trains(args.sp))
        pass


if __name__ == "__main__":
    main()
