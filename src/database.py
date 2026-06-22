import sqlite3


def get_connection():

    conn = sqlite3.connect(
        "tv_schedule.db"
    )

    return conn
