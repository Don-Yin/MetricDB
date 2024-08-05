#!/Users/donyin/miniconda3/envs/imperial/bin/python

import sqlite3, pandas
from rich import print
from pathlib import Path


class MetricDB:
    def __init__(self, base_dir: Path, name_datafile: str = "default.db", verbose: bool = True):

        # fmt: off
        self.base_dir, self.verbose = Path(base_dir).mkdir(parents=True, exist_ok=True) or Path(base_dir), verbose
        self.datafile_dir = self.base_dir / name_datafile
        # fmt: on

        self.connect = sqlite3.connect(self.datafile_dir)

        # ---- [1] reporting init progress ----
        if not self.datafile_dir.exists() and self.verbose:
            print(f"[bold green]SQLite3[/bold green] datafile created at: {self.datafile_dir}")

        if self.datafile_dir.exists() and self.verbose:
            print(f"[bold green]SQLite3[/bold green] datafile loaded from: {self.datafile_dir}")
            self.print_header()

    # ---- [ core functional helpers ] ----
    def get_moving_average(self, key: str, name_table: str = "default", window_size: int = 12):
        """get the moving average of the key from the table of the past window_size values that are not None"""
        cursor = self.connect.cursor()

        query = f"""
        SELECT {key}
        FROM {name_table}
        WHERE {key} IS NOT NULL
        ORDER BY id DESC
        LIMIT {window_size}
        """

        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()

        if results:
            values = [float(result[0]) for result in results if result[0] is not None]
            if values:
                moving_average = sum(values) / len(values)
                return moving_average

        return None

    def log(self, data: dict, name_table: str = "default"):
        cursor = self.connect.cursor()

        # ---- [1] create table if not exists ----
        columns = ", ".join([f"{key} TEXT" for key in data.keys()])
        cursor.execute(
            f"""
        CREATE TABLE IF NOT EXISTS {name_table} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            {columns}
        )
        """
        )

        # ---- [2] insert data into the table ----
        cursor.execute(f"PRAGMA table_info({name_table})")
        existing_columns = set(col[1] for col in cursor.fetchall())

        for key in data.keys():
            if key not in existing_columns:
                cursor.execute(f"ALTER TABLE {name_table} ADD COLUMN {key} TEXT")

        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data])
        values = tuple(data.values())

        cursor.execute(
            f"""
        INSERT INTO {name_table} ({columns})
        VALUES ({placeholders})
        """,
            values,
        )

        self.connect.commit()

        if self.verbose:
            print(f"[bold green]SQLite3[/bold green] Inserted data into table: {name_table}: {data}")

        cursor.close()

    def on_end(self):
        self.connect.close()

        if self.verbose:
            print(f"[bold green]SQLite3[/bold green] connection closed for: {self.datafile_dir}")

    # --- [ other useful helpers ] ---
    def save_as_pandas_dataframe(self, name_table: str = "default", save_dir: Path = "default.csv"):
        """
        Save the specified table as a pandas DataFrame and export it to a CSV file.

        Args:
            name_table (str): The name of the table to save. Defaults to "default".
            save_dir (Path): The path where the CSV file will be saved. Defaults to "default.csv".
        """

        cursor = self.connect.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name_table,))
        if not cursor.fetchone():
            raise ValueError(f"Table '{name_table}' does not exist in the database.")

        cursor.execute(f"SELECT * FROM {name_table}")
        rows = cursor.fetchall()

        cursor.execute(f"PRAGMA table_info({name_table})")
        columns = [col[1] for col in cursor.fetchall()]
        df = pandas.DataFrame(rows, columns=columns)
        df.to_csv(save_dir, index=False)
        cursor.close()

        if self.verbose:
            print(f"[bold green]SQLite3[/bold green] Saved table '{name_table}' to {save_dir}")

    # ---- for debugging ----
    def print_header(self):
        """of all existing tables in the database"""
        cursor = self.connect.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        if tables:
            for table in tables:
                print(f"\n[bold cyan]Table: {table[0]}[/bold cyan]")

                cursor.execute(f"PRAGMA table_info({table[0]})")
                columns = cursor.fetchall()
                column_names = [col[1] for col in columns]

                cursor.execute(f"SELECT * FROM {table[0]}")
                rows = cursor.fetchall()

                df = pandas.DataFrame(rows, columns=column_names)
                print(f"{df}\n\nDataFrame Shape: {df.shape}")
        else:
            print("  No tables found in the database.")
        cursor.close()

    def show_last_row(self, name_table: str = "default"):
        """
        Show the last row of the specified table as a dictionary.

        Args:
            name_table (str): The name of the table to show the last row from. Defaults to "default".
        """
        cursor = self.connect.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name_table,))
        if not cursor.fetchone():
            raise ValueError(f"Table '{name_table}' does not exist in the database.")

        cursor.execute(f"PRAGMA table_info({name_table})")
        columns = [col[1] for col in cursor.fetchall()]
        cursor.execute(f"SELECT * FROM {name_table} ORDER BY rowid DESC LIMIT 1")
        last_row = cursor.fetchone()

        if last_row:
            last_row_dict = dict(zip(columns, last_row))
            print(last_row_dict)
        else:
            if self.verbose:
                print(f"[bold yellow]Table '{name_table}' is empty.[/bold yellow]")
        cursor.close()

    # ---- development only ----
    def _write_dummy_data(self, name_table: str = "dummy_table"):
        cursor = self.connect.cursor()

        cursor.execute(
            f"""
        CREATE TABLE IF NOT EXISTS {name_table} (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            value REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
        )

        dummy_data = [("Alice", 42.5), ("Bob", 37.2), ("Charlie", 55.8), ("Diana", 29.9), ("Ethan", 61.3)]

        cursor.executemany(
            f"""
        INSERT INTO {name_table} (name, value)
        VALUES (?, ?)
        """,
            dummy_data,
        )

        self.connect.commit()
        cursor.close()

        if self.verbose:
            print(f"[bold green]Dummy data inserted successfully into {name_table}![/bold green]")
            self.print_header()


if __name__ == "__main__":
    logger = MetricDB(base_dir="data", name_datafile="default.db")
    # logger._write_dummy_data()

    logger.log({"epoch": 1}, name_table="train")
    for i in range(1000):
        logger.log({"train_loss": i}, name_table="train")
        logger.log({"train_accuracy": i / 1000}, name_table="train")
        logger.log({"val_loss": i}, name_table="val")
        loss = logger.get_moving_average(key="train_loss", name_table="train", window_size=12)
        print(f"Moving Average of train_loss: {loss}")

    # logger.print_header()
    # logger.save_as_pandas_dataframe(name_table="train", save_dir="train.csv")
    logger.show_last_row(name_table="train")

    logger.on_end()
