# MetricDB
MetricDB is a lightweight SQLite3 based logger.

## Installation
```pip install MetricDB```

## Usage

### Basic

```python
from MetricDB import MetricDB

logger = MetricDB(base_dir="data", name_datafile="my_project.db")

logger.log({"epoch": 1, "loss": 0.5, "accuracy": 0.85}, name_table="training")

avg_loss = logger.get_moving_average(key="loss", name_table="training", window_size=10)

print(f"Average loss: {avg_loss}")

logger.save_as_pandas_dataframe(name_table="training", save_dir="training_results.csv")

logger.on_end()
```

### Advanced Usage

```python
from MetricDB import MetricDB

# This crease a db file in the base dir
logger = MetricDB(base_dir="data", name_datafile="advanced_example.db", verbose=True)

# Log data to multiple tables
for epoch in range(100):
    logger.log({"epoch": epoch, "train_loss": epoch * 0.01}, name_table="train")
    logger.log({"epoch": epoch, "val_loss": epoch * 0.015}, name_table="validation")

# Calculate moving averages
train_avg = logger.get_moving_average(key="train_loss", name_table="train", window_size=5)
val_avg = logger.get_moving_average(key="val_loss", name_table="validation", window_size=5)

print(f"Train loss moving average: {train_avg}")
print(f"Validation loss moving average: {val_avg}")

# Show the last logged row
logger.show_last_row(name_table="train")
logger.on_end()
logger.save_as_pandas_dataframe(name_table="train", save_dir="train.csv")
```
