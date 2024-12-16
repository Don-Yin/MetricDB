# MetricDB
MetricDB is a lightweight SQLite3 based logger with pandas integration.

## Installation
```pip install MetricDB```

## Usage Examples

### Basic Logging
```python
from MetricDB import MetricDB

# Initialize the logger
logger = MetricDB(datafile_dir="my_project.db")

# Log single metrics
logger.log({"epoch": 1, "loss": 0.5, "accuracy": 0.85})

# Log to different tables
logger.log({"loss": 0.3, "accuracy": 0.9}, name_table="training")
logger.log({"loss": 0.4, "accuracy": 0.87}, name_table="validation")

# Calculate moving averages
train_loss_avg = logger.get_moving_average(key="loss", name_table="training", window_size=10)
print(f"Average training loss: {train_loss_avg}")

# Close the connection when done
logger.on_end()
```

### Data Export and Analysis
```python
from MetricDB import MetricDB

logger = MetricDB(datafile_dir="analysis.db")

# Log some data
for epoch in range(10):
    logger.log({
        "epoch": epoch,
        "train_loss": epoch * 0.1,
        "train_acc": 0.85 + epoch * 0.01
    }, name_table="metrics")

# Export to CSV
logger.save_as_csv(name_table="metrics", save_dir="training_results.csv")

# Get data as pandas DataFrame with automatic type conversion
df = logger.get_dataframe(name_table="metrics")
print(df.dtypes)  # Shows column data types

logger.on_end()
```

### Working with Pandas Integration
```python
from MetricDB import MetricDB

logger = MetricDB(datafile_dir="pandas_example.db")

# Log mixed data types
logger.log({
    "text_data": "hello",
    "numeric_data": 42.5,
    "integer_data": 100
})

# Get as pandas DataFrame with automatic type inference
df = logger.get_dataframe()
print("Data Types:")
print(df.dtypes)

# Perform pandas operations
print("\nDataFrame Summary:")
print(df.describe())

# Export specific tables
logger.save_as_csv(name_table="main", save_dir="output.csv")

logger.on_end()
```

### Debugging and Monitoring
```python
from MetricDB import MetricDB

logger = MetricDB(datafile_dir="debug.db", verbose=True)

# Log some metrics
logger.log({"step": 1, "loss": 0.5})

# Print database structure and contents
logger.print_header()  # Shows all tables and their contents

# Show the most recent logged values
logger.show_last_row(name_table="main")

logger.on_end()
```

### Development Tools
```python
from MetricDB import MetricDB

logger = MetricDB(datafile_dir="dev.db")

# Write dummy data for testing
logger._write_dummy_data(name_table="test_table")

# Print database contents
logger.print_header()

logger.on_end()
```