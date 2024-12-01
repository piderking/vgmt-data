# Auto-Fetching System

## Todo 
- User Preferences (for services and frequency) (Not Implemented Yet)
- Pooling
- Saving and Loading
- Formatting


## Process

### Unclean Pooling
Pool data in the cleaner worker pool data thread

### Cleaning (#1)

### Sorting (#2)

### Clean Pooling  (#2)

### Table Formatting + Loading (#2)

### Saving (#2)




## Files



### Cleaner.py
- Cleans Data and transformers them to SortedDataModel

### Sorter.py
- Merge into columns w/o time sorting

- When col has large enough speicies of data call it for execution and make it into a Table
- Load corresponding timely files to the data store (stored)
- Save into 24hr increment files