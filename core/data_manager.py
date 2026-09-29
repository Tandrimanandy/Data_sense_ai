"""
DataSense AI - Data Manager
Handles data loading, saving, and manipulation
"""

import os
from typing import Optional, Dict, Any
import pandas as pd
import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal


class DataManager(QObject):
    """Manages data loading, saving, and manipulation"""
    
    # Signals
    data_loaded = pyqtSignal(object, str)  # DataFrame, file_name
    data_updated = pyqtSignal(object)  # DataFrame
    error_occurred = pyqtSignal(str)  # error_message
    
    def __init__(self):
        super().__init__()
        self._data: Optional[pd.DataFrame] = None
        self._file_path: Optional[str] = None
        self._file_name: str = ""
    
    @property
    def data(self) -> Optional[pd.DataFrame]:
        """Get the current data"""
        return self._data
    
    def get_data(self) -> pd.DataFrame:
        """Get data as DataFrame"""
        if self._data is None:
            return pd.DataFrame()
        return self._data
    
    def is_empty(self) -> bool:
        """Check if data is empty"""
        return self._data is None or self._data.empty
    
    def load_file(self, file_path: str) -> bool:
        """Load data from file"""
        try:
            self._file_path = file_path
            self._file_name = os.path.basename(file_path)
            
            # Determine file type and load accordingly
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext == '.csv':
                self._data = self._load_csv(file_path)
            elif ext in ['.xlsx', '.xls']:
                self._data = self._load_excel(file_path)
            elif ext == '.json':
                self._data = self._load_json(file_path)
            elif ext == '.tsv':
                self._data = self._load_tsv(file_path)
            else:
                raise ValueError(f"Unsupported file format: {ext}")
            
            # Emit signal
            self.data_loaded.emit(self._data, self._file_name)
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to load file: {str(e)}")
            return False
    
    def _load_csv(self, file_path: str) -> pd.DataFrame:
        """Load CSV file with encoding detection"""
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                return pd.read_csv(file_path, encoding=encoding)
            except UnicodeDecodeError:
                continue
            except Exception as e:
                # Re-raise other exceptions
                raise e
        
        raise ValueError("Could not decode file with any supported encoding")
    
    def _load_excel(self, file_path: str) -> pd.DataFrame:
        """Load Excel file"""
        # Try to load first sheet
        try:
            return pd.read_excel(file_path, sheet_name=0)
        except Exception as e:
            raise ValueError(f"Failed to load Excel file: {str(e)}")
    
    def _load_json(self, file_path: str) -> pd.DataFrame:
        """Load JSON file"""
        try:
            return pd.read_json(file_path)
        except Exception as e:
            raise ValueError(f"Failed to load JSON file: {str(e)}")
    
    def _load_tsv(self, file_path: str) -> pd.DataFrame:
        """Load TSV file"""
        encodings = ['utf-8', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                return pd.read_csv(file_path, sep='\t', encoding=encoding)
            except:
                continue
        
        raise ValueError("Could not decode TSV file")
    
    def export_csv(self, file_path: str) -> bool:
        """Export data to CSV"""
        try:
            if self._data is not None:
                self._data.to_csv(file_path, index=False)
                return True
            return False
        except Exception as e:
            self.error_occurred.emit(f"Failed to export CSV: {str(e)}")
            return False
    
    def export_excel(self, file_path: str) -> bool:
        """Export data to Excel"""
        try:
            if self._data is not None:
                self._data.to_excel(file_path, index=False, engine='openpyxl')
                return True
            return False
        except Exception as e:
            self.error_occurred.emit(f"Failed to export Excel: {str(e)}")
            return False
    
    def clear(self):
        """Clear all data"""
        self._data = None
        self._file_path = None
        self._file_name = ""
    
    def get_column_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about each column"""
        if self._data is None:
            return {}
        
        info = {}
        for col in self._data.columns:
            info[col] = {
                'dtype': str(self._data[col].dtype),
                'null_count': int(self._data[col].isna().sum()),
                'unique_count': int(self._data[col].nunique()),
                'is_numeric': pd.api.types.is_numeric_dtype(self._data[col])
            }
        
        return info
    
    def get_numeric_columns(self) -> list:
        """Get list of numeric columns"""
        if self._data is None:
            return []
        
        return [col for col in self._data.columns 
                if pd.api.types.is_numeric_dtype(self._data[col])]
    
    def get_categorical_columns(self) -> list:
        """Get list of categorical columns"""
        if self._data is None:
            return []
        
        return [col for col in self._data.columns 
                if not pd.api.types.is_numeric_dtype(self._data[col])]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of the data"""
        if self._data is None:
            return {}
        
        return {
            'rows': len(self._data),
            'columns': len(self._data.columns),
            'numeric_columns': len(self.get_numeric_columns()),
            'categorical_columns': len(self.get_categorical_columns()),
            'memory_mb': self._data.memory_usage(deep=True).sum() / (1024 * 1024),
            'null_values': int(self._data.isna().sum().sum())
        }