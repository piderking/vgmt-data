"""
Data Acceptor:


"""
from .cleaner import DataAcceptorCleaner
from .sorter import DataAcceptorSorter


cleaner = DataAcceptorCleaner(
    [],
    auto_start=False
)
sorter = DataAcceptorSorter(
    cleaner,
    auto_start=False
)