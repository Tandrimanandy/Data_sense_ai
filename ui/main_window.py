"""
DataSense AI - Main Window
The primary application window with all UI components
"""

import os
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QMenuBar, QMenu, QToolBar, QStatusBar, QFileDialog, QMessageBox,
    QLabel, QPushButton, QProgressBar, QTabWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QTreeWidget,
    QTreeWidgetItem, QComboBox, QCheckBox, QGroupBox, QScrollArea,
    QFrame, QSizePolicy, QProgressDialog
)
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QAction, QKeySequence, QFont, QColor, QBrush

# Import core modules
from core.data_manager import DataManager
from core.ml_engine import MLEngine
from core.visualization_engine import VisualizationEngine
from core.statistics_engine import StatisticsEngine
from core.insight_generator import InsightGenerator


class MainWindow(QMainWindow):
    """Main application window for DataSense AI"""
    
    # Color constants from SPEC.md
    COLOR_PRIMARY = "#1E3A5F"
    COLOR_SECONDARY = "#2D5A87"
    COLOR_ACCENT = "#00D4AA"
    COLOR_BACKGROUND = "#F8FAFC"
    COLOR_SURFACE = "#FFFFFF"
    COLOR_TEXT_PRIMARY = "#1A202C"
    COLOR_TEXT_SECONDARY = "#718096"
    COLOR_SUCCESS = "#38A169"
    COLOR_WARNING = "#D69E2E"
    COLOR_ERROR = "#E53E3E"
    
    def __init__(self):
        super().__init__()
        
        # Core components
        self.data_manager = DataManager()
        self.ml_engine = MLEngine()
        self.visualization_engine = VisualizationEngine()
        self.statistics_engine = StatisticsEngine()
        self.insight_generator = InsightGenerator()
        
        # State
        self.current_file_path: Optional[str] = None
        self.is_analysis_running = False
        
        # Initialize UI
        self.init_ui()
        self.setup_connections()
        
        # Set window properties
        self.setWindowTitle("DataSense AI - AI-Powered Data Analyzer")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Center on screen
        self.center_on_screen()
    
    def center_on_screen(self):
        """Center the window on the screen"""
        screen = self.screen().geometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)
    
    def init_ui(self):
        """Initialize all UI components"""
        self.create_menu_bar()
        self.create_toolbar()
        self.create_central_widget()
        self.create_status_bar()
    
    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("&File")
        
        import_action = QAction("&Import Data...", self)
        import_action.setShortcut(QKeySequence.StandardKey.Open)
        import_action.triggered.connect(self.import_data)
        file_menu.addAction(import_action)
        
        file_menu.addSeparator()
        
        export_csv_action = QAction("Export as &CSV...", self)
        export_csv_action.triggered.connect(lambda: self.export_data("csv"))
        file_menu.addAction(export_csv_action)
        
        export_excel_action = QAction("Export as &Excel...", self)
        export_excel_action.triggered.connect(lambda: self.export_data("excel"))
        file_menu.addAction(export_excel_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Data Menu
        data_menu = menubar.addMenu("&Data")
        
        refresh_action = QAction("&Refresh", self)
        refresh_action.setShortcut(QKeySequence.StandardKey.Refresh)
        refresh_action.triggered.connect(self.refresh_data)
        data_menu.addAction(refresh_action)
        
        clear_action = QAction("&Clear Data", self)
        clear_action.triggered.connect(self.clear_data)
        data_menu.addAction(clear_action)
        
        # Analysis Menu
        analysis_menu = menubar.addMenu("&Analysis")
        
        auto_analyze_action = QAction("&AI Auto Analysis", self)
        auto_analyze_action.setShortcut(QKeySequence("Ctrl+A"))
        auto_analyze_action.triggered.connect(self.run_ai_analysis)
        analysis_menu.addAction(auto_analyze_action)
        
        analysis_menu.addSeparator()
        
        correlation_action = QAction("&Correlation Analysis", self)
        correlation_action.triggered.connect(lambda: self.run_specific_analysis("correlation"))
        analysis_menu.addAction(correlation_action)
        
        clustering_action = QAction("&Clustering Analysis", self)
        clustering_action.triggered.connect(lambda: self.run_specific_analysis("clustering"))
        analysis_menu.addAction(clustering_action)
        
        regression_action = QAction("&Regression Analysis", self)
        regression_action.triggered.connect(lambda: self.run_specific_analysis("regression"))
        analysis_menu.addAction(regression_action)
        
        outlier_action = QAction("&Outlier Detection", self)
        outlier_action.triggered.connect(lambda: self.run_specific_analysis("outliers"))
        analysis_menu.addAction(outlier_action)
        
        # Visualize Menu
        visualize_menu = menubar.addMenu("&Visualize")
        
        line_chart_action = QAction("&Line Chart", self)
        line_chart_action.triggered.connect(lambda: self.create_chart("line"))
        visualize_menu.addAction(line_chart_action)
        
        bar_chart_action = QAction("&Bar Chart", self)
        bar_chart_action.triggered.connect(lambda: self.create_chart("bar"))
        visualize_menu.addAction(bar_chart_action)
        
        scatter_action = QAction("&Scatter Plot", self)
        scatter_action.triggered.connect(lambda: self.create_chart("scatter"))
        visualize_menu.addAction(scatter_action)
        
        histogram_action = QAction("&Histogram", self)
        histogram_action.triggered.connect(lambda: self.create_chart("histogram"))
        visualize_menu.addAction(histogram_action)
        
        pie_chart_action = QAction("&Pie Chart", self)
        pie_chart_action.triggered.connect(lambda: self.create_chart("pie"))
        visualize_menu.addAction(pie_chart_action)
        
        box_plot_action = QAction("&Box Plot", self)
        box_plot_action.triggered.connect(lambda: self.create_chart("box"))
        visualize_menu.addAction(box_plot_action)
        
        # Help Menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About DataSense AI", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """Create the toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Import button
        import_btn = QPushButton("📂 Import")
        import_btn.setToolTip("Import data file (CSV, Excel, JSON)")
        import_btn.clicked.connect(self.import_data)
        toolbar.addWidget(import_btn)
        
        toolbar.addSeparator()
        
        # AI Analyze button
        self.ai_analyze_btn = QPushButton("🤖 AI Analyze")
        self.ai_analyze_btn.setToolTip("Run AI-powered analysis")
        self.ai_analyze_btn.clicked.connect(self.run_ai_analysis)
        self.ai_analyze_btn.setEnabled(False)
        toolbar.addWidget(self.ai_analyze_btn)
        
        toolbar.addSeparator()
        
        # Charts dropdown
        self.chart_combo = QComboBox()
        self.chart_combo.addItems(["Line Chart", "Bar Chart", "Scatter", "Histogram", "Pie Chart", "Box Plot"])
        self.chart_combo.setToolTip("Select chart type")
        self.chart_combo.setEnabled(False)
        toolbar.addWidget(self.chart_combo)
        
        chart_btn = QPushButton("📊 Create Chart")
        chart_btn.setToolTip("Create visualization")
        chart_btn.clicked.connect(self.on_create_chart_clicked)
        chart_btn.setEnabled(False)
        toolbar.addWidget(chart_btn)
        self.chart_btn = chart_btn
        
        toolbar.addSeparator()
        
        # Statistics button
        stats_btn = QPushButton("📈 Statistics")
        stats_btn.setToolTip("View descriptive statistics")
        stats_btn.clicked.connect(self.show_statistics)
        stats_btn.setEnabled(False)
        toolbar.addWidget(stats_btn)
        self.stats_btn = stats_btn
    
    def create_central_widget(self):
        """Create the central widget with splitter layout"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        
        # Create splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Data Explorer
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Main Content
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([250, 1050])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
    
    def create_left_panel(self) -> QWidget:
        """Create the left panel with data explorer"""
        panel = QFrame()
        panel.setFrameShape(QFrame.Shape.StyledPanel)
        panel.setMaximumWidth(300)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Title
        title = QLabel("📁 Data Explorer")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {self.COLOR_PRIMARY};")
        layout.addWidget(title)
        
        # File tree
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabel("Files & Variables")
        self.file_tree.setAlternatingRowColors(True)
        layout.addWidget(self.file_tree)
        
        # Data info group
        info_group = QGroupBox("Data Information")
        info_layout = QVBoxLayout(info_group)
        
        self.rows_label = QLabel("Rows: 0")
        info_layout.addWidget(self.rows_label)
        
        self.cols_label = QLabel("Columns: 0")
        info_layout.addWidget(self.cols_label)
        
        self.memory_label = QLabel("Memory: 0 MB")
        info_layout.addWidget(self.memory_label)
        
        layout.addWidget(info_group)
        
        return panel
    
    def create_right_panel(self) -> QWidget:
        """Create the right panel with tabs"""
        panel = QWidget()
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Data Table Tab
        self.data_table_tab = self.create_data_table_tab()
        self.tab_widget.addTab(self.data_table_tab, "📋 Data Table")
        
        # AI Insights Tab
        self.insights_tab = self.create_insights_tab()
        self.tab_widget.addTab(self.insights_tab, "🤖 AI Insights")
        
        # Charts Tab
        self.charts_tab = self.create_charts_tab()
        self.tab_widget.addTab(self.charts_tab, "📊 Visualizations")
        
        # Statistics Tab
        self.stats_tab = self.create_stats_tab()
        self.tab_widget.addTab(self.stats_tab, "📈 Statistics")
        
        return panel
    
    def create_data_table_tab(self) -> QWidget:
        """Create the data table view"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Table widget
        self.data_table = QTableWidget()
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.data_table.setSortingEnabled(True)
        self.data_table.horizontalHeader().setStretchLastSection(True)
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        layout.addWidget(self.data_table)
        
        # Placeholder label
        placeholder = QLabel("📂 Import a data file to get started\n\nSupported formats: CSV, Excel (.xlsx), JSON")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet(f"color: {self.COLOR_TEXT_SECONDARY}; font-size: 14px;")
        layout.addWidget(placeholder)
        self.data_placeholder = placeholder
        
        return widget
    
    def create_insights_tab(self) -> QWidget:
        """Create the AI insights tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Title
        title = QLabel("🤖 AI-Powered Insights")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {self.COLOR_PRIMARY};")
        layout.addWidget(title)
        
        # Scroll area for insights
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        self.insights_container = QWidget()
        insights_layout = QVBoxLayout(self.insights_container)
        insights_layout.setSpacing(12)
        
        # Placeholder
        placeholder = QLabel("👆 Click 'AI Analyze' to generate insights from your data")
        placeholder.setStyleSheet(f"color: {self.COLOR_TEXT_SECONDARY}; font-size: 13px; padding: 20px;")
        insights_layout.addWidget(placeholder)
        self.insights_placeholder = placeholder
        
        scroll.setWidget(self.insights_container)
        layout.addWidget(scroll)
        
        return widget
    
    def create_charts_tab(self) -> QWidget:
        """Create the charts/visualizations tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Placeholder for chart
        placeholder = QLabel("📊 Create charts from the toolbar or Visualize menu\n\nSelect a chart type and click 'Create Chart'")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet(f"color: {self.COLOR_TEXT_SECONDARY}; font-size: 14px;")
        layout.addWidget(placeholder)
        self.chart_placeholder = placeholder
        
        # Chart area (will be populated when chart is created)
        self.chart_layout = layout
        
        return widget
    
    def create_stats_tab(self) -> QWidget:
        """Create the statistics tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Placeholder
        placeholder = QLabel("📈 Descriptive statistics will appear here\n\nClick 'Statistics' button to compute")
        placeholder.setStyleSheet(f"color: {self.COLOR_TEXT_SECONDARY}; font-size: 13px;")
        layout.addWidget(placeholder)
        self.stats_placeholder = placeholder
        
        return widget
    
    def create_status_bar(self):
        """Create the status bar"""
        statusbar = QStatusBar()
        self.setStatusBar(statusbar)
        
        # Status label
        self.status_label = QLabel("Ready")
        statusbar.addWidget(self.status_label)
        
        statusbar.addPermanentWidget(QLabel("│"))
        
        # Data info
        self.status_rows = QLabel("Rows: 0")
        statusbar.addPermanentWidget(self.status_rows)
        
        statusbar.addPermanentWidget(QLabel("│"))
        
        self.status_cols = QLabel("Columns: 0")
        statusbar.addPermanentWidget(self.status_cols)
        
        statusbar.addPermanentWidget(QLabel("│"))
        
        self.status_memory = QLabel("Memory: 0 MB")
        statusbar.addPermanentWidget(self.status_memory)
        
        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        statusbar.addPermanentWidget(self.progress_bar)
    
    def setup_connections(self):
        """Set up signal/slot connections"""
        # Data manager signals
        self.data_manager.data_loaded.connect(self.on_data_loaded)
        self.data_manager.error_occurred.connect(self.on_error)
        
        # ML engine signals
        self.ml_engine.progress_updated.connect(self.on_analysis_progress)
        self.ml_engine.analysis_complete.connect(self.on_analysis_complete)
    
    # ==================== File Operations ====================
    
    def import_data(self):
        """Import data from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Data File",
            "",
            "Data Files (*.csv *.xlsx *.xls *.json *.tsv);;CSV Files (*.csv);;Excel Files (*.xlsx *.xls);;JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            self.load_file(file_path)
    
    def load_file(self, file_path: str):
        """Load a data file"""
        self.set_status(f"Loading {os.path.basename(file_path)}...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        
        try:
            success = self.data_manager.load_file(file_path)
            
            if success:
                self.current_file_path = file_path
                self.set_status(f"Loaded: {os.path.basename(file_path)}")
            else:
                self.on_error("Failed to load file")
                
        except Exception as e:
            self.on_error(f"Error loading file: {str(e)}")
        
        finally:
            self.progress_bar.setVisible(False)
    
    def export_data(self, format: str):
        """Export data to file"""
        if self.data_manager.is_empty():
            QMessageBox.warning(self, "No Data", "No data to export. Please import a data file first.")
            return
        
        if format == "csv":
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export as CSV",
                "",
                "CSV Files (*.csv)"
            )
            if file_path:
                self.data_manager.export_csv(file_path)
                self.set_status(f"Exported to {os.path.basename(file_path)}")
                
        elif format == "excel":
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export as Excel",
                "",
                "Excel Files (*.xlsx)"
            )
            if file_path:
                self.data_manager.export_excel(file_path)
                self.set_status(f"Exported to {os.path.basename(file_path)}")
    
    def refresh_data(self):
        """Refresh current data view"""
        if self.current_file_path:
            self.load_file(self.current_file_path)
    
    def clear_data(self):
        """Clear all data"""
        reply = QMessageBox.question(
            self,
            "Clear Data",
            "Are you sure you want to clear all data?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.data_manager.clear()
            self.current_file_path = None
            self.set_status("Data cleared")
    
    # ==================== Data Display ====================
    
    def on_data_loaded(self, df, file_name: str):
        """Handle data loaded event"""
        # Update data table
        self.update_data_table(df)
        
        # Update file tree
        self.update_file_tree(df, file_name)
        
        # Update info labels
        self.update_data_info(df)
        
        # Enable buttons
        self.ai_analyze_btn.setEnabled(True)
        self.chart_combo.setEnabled(True)
        self.chart_btn.setEnabled(True)
        self.stats_btn.setEnabled(True)
        
        # Switch to data table tab
        self.tab_widget.setCurrentIndex(0)
        
        self.set_status(f"Data loaded: {file_name}")
    
    def update_data_table(self, df):
        """Update the data table view"""
        # Hide placeholder
        self.data_placeholder.setVisible(False)
        
        # Clear table
        self.data_table.clear()
        
        # Set dimensions
        rows, cols = df.shape
        self.data_table.setRowCount(rows)
        self.data_table.setColumnCount(cols)
        
        # Set headers
        self.data_table.setHorizontalHeaderLabels(list(df.columns))
        
        # Populate cells
        for i in range(min(rows, 10000)):  # Limit for performance
            for j in range(cols):
                value = df.iloc[i, j]
                display_value = "" if pd.isna(value) else str(value)
                item = QTableWidgetItem(display_value)
                self.data_table.setItem(i, j, item)
        
        # Resize columns to content
        self.data_table.resizeColumnsToContents()
    
    def update_file_tree(self, df, file_name: str):
        """Update the file tree"""
        self.file_tree.clear()
        
        # Root item - file name
        root = QTreeWidgetItem([f"📄 {file_name}"])
        self.file_tree.addTopLevelItem(root)
        
        # Columns as children
        for col in df.columns:
            dtype = str(df[col].dtype)
            null_count = df[col].isna().sum()
            col_item = QTreeWidgetItem([f"📊 {col} ({dtype})"])
            col_item.setToolTip(0, f"Type: {dtype}\nNulls: {null_count}/{len(df)}")
            root.addChild(col_item)
        
        root.setExpanded(True)
    
    def update_data_info(self, df):
        """Update data information labels"""
        rows, cols = df.shape
        memory = df.memory_usage(deep=True).sum() / (1024 * 1024)  # MB
        
        self.rows_label.setText(f"Rows: {rows:,}")
        self.cols_label.setText(f"Columns: {cols}")
        self.memory_label.setText(f"Memory: {memory:.2f} MB")
        
        self.status_rows.setText(f"Rows: {rows:,}")
        self.status_cols.setText(f"Columns: {cols}")
        self.status_memory.setText(f"Memory: {memory:.2f} MB")
    
    # ==================== AI Analysis ====================
    
    def run_ai_analysis(self):
        """Run AI-powered analysis"""
        if self.data_manager.is_empty():
            QMessageBox.warning(self, "No Data", "Please import data before running analysis.")
            return
        
        if self.is_analysis_running:
            return
        
        self.is_analysis_running = True
        self.set_status("Running AI analysis...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        # Switch to insights tab
        self.tab_widget.setCurrentIndex(1)
        
        # Run analysis in background
        df = self.data_manager.get_data()
        self.ml_engine.run_full_analysis(df)
    
    def run_specific_analysis(self, analysis_type: str):
        """Run a specific type of analysis"""
        if self.data_manager.is_empty():
            QMessageBox.warning(self, "No Data", "Please import data first.")
            return
        
        df = self.data_manager.get_data()
        
        if analysis_type == "correlation":
            result = self.ml_engine.correlation_analysis(df)
        elif analysis_type == "clustering":
            result = self.ml_engine.clustering_analysis(df)
        elif analysis_type == "regression":
            result = self.ml_engine.regression_analysis(df)
        elif analysis_type == "outliers":
            result = self.ml_engine.outlier_detection(df)
        else:
            return
        
        self.display_analysis_result(analysis_type, result)
    
    def on_analysis_progress(self, message: str):
        """Handle analysis progress"""
        self.set_status(message)
    
    def on_analysis_complete(self, results: dict):
        """Handle analysis complete"""
        self.is_analysis_running = False
        self.progress_bar.setVisible(False)
        self.set_status("Analysis complete")
        
        # Display insights
        self.display_insights(results)
    
    def display_insights(self, results: dict):
        """Display AI insights"""
        # Clear placeholder
        self.insights_placeholder.setVisible(False)
        
        # Clear existing insights
        layout = self.insights_container.layout()
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Generate and display insights
        insights_text = self.insight_generator.generate_insights(results)
        
        # Create insight cards
        for insight in insights_text:
            card = self.create_insight_card(insight["title"], insight["content"], insight.get("type", "info"))
            layout.addWidget(card)
        
        layout.addStretch()
    
    def create_insight_card(self, title: str, content: str, insight_type: str = "info") -> QFrame:
        """Create an insight card widget"""
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {self.COLOR_SURFACE};
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                padding: 12px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        
        # Title with icon
        icon = "💡" if insight_type == "info" else "⚠️" if insight_type == "warning" else "✅"
        title_label = QLabel(f"{icon} {title}")
        title_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {self.COLOR_PRIMARY};")
        layout.addWidget(title_label)
        
        # Content
        content_label = QLabel(content)
        content_label.setWordWrap(True)
        content_label.setStyleSheet(f"color: {self.COLOR_TEXT_PRIMARY}; font-size: 12px;")
        layout.addWidget(content_label)
        
        return card
    
    def display_analysis_result(self, analysis_type: str, result: dict):
        """Display analysis result"""
        # Switch to insights tab
        self.tab_widget.setCurrentIndex(1)
        
        # Clear placeholder
        self.insights_placeholder.setVisible(False)
        
        # For now, just show a simple result
        # In a full implementation, this would create proper cards
    
    # ==================== Visualization ====================
    
    def on_create_chart_clicked(self):
        """Handle create chart button click"""
        chart_type = self.chart_combo.currentText().lower()
        
        if "line" in chart_type:
            self.create_chart("line")
        elif "bar" in chart_type:
            self.create_chart("bar")
        elif "scatter" in chart_type:
            self.create_chart("scatter")
        elif "histogram" in chart_type:
            self.create_chart("histogram")
        elif "pie" in chart_type:
            self.create_chart("pie")
        elif "box" in chart_type:
            self.create_chart("box")
    
    def create_chart(self, chart_type: str):
        """Create a chart"""
        if self.data_manager.is_empty():
            QMessageBox.warning(self, "No Data", "Please import data before creating charts.")
            return
        
        df = self.data_manager.get_data()
        
        # Switch to charts tab
        self.tab_widget.setCurrentIndex(2)
        
        # Create chart
        try:
            chart_widget = self.visualization_engine.create_chart(df, chart_type)
            
            # Replace placeholder
            if self.chart_placeholder:
                self.chart_placeholder.setVisible(False)
                self.charts_tab.layout().removeWidget(self.chart_placeholder)
                self.chart_placeholder.deleteLater()
                self.chart_placeholder = None
            
            # Add chart to layout
            self.charts_tab.layout().addWidget(chart_widget)
            
            self.set_status(f"Created {chart_type} chart")
            
        except Exception as e:
            QMessageBox.warning(self, "Chart Error", f"Failed to create chart: {str(e)}")
    
    # ==================== Statistics ====================
    
    def show_statistics(self):
        """Show descriptive statistics"""
        if self.data_manager.is_empty():
            QMessageBox.warning(self, "No Data", "Please import data first.")
            return
        
        df = self.data_manager.get_data()
        
        # Switch to statistics tab
        self.tab_widget.setCurrentIndex(3)
        
        # Calculate statistics
        stats = self.statistics_engine.compute_descriptive_stats(df)
        
        # Display statistics
        self.display_statistics(stats)
    
    def display_statistics(self, stats: dict):
        """Display statistics"""
        # Clear placeholder
        self.stats_placeholder.setVisible(False)
        
        # For a full implementation, this would populate a proper statistics view
        # For now, we'll just update the placeholder
        self.stats_placeholder.setText("Statistics computed. See detailed view above.")
    
    # ==================== Event Handlers ====================
    
    def on_error(self, message: str):
        """Handle errors"""
        self.progress_bar.setVisible(False)
        self.set_status(f"Error: {message}")
        QMessageBox.critical(self, "Error", message)
    
    def set_status(self, message: str):
        """Set status bar message"""
        self.status_label.setText(message)
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About DataSense AI",
            "<h3>DataSense AI v1.0.0</h3>"
            "<p>AI-Powered Data Analyzer</p>"
            "<p>Runs completely offline - No API required</p>"
            "<p>Supported formats: CSV, Excel, JSON</p>"
            "<p>Features:</p>"
            "<ul>"
            "<li>AI-powered pattern detection</li>"
            "<li>Clustering & classification</li>"
            "<li>Correlation & regression analysis</li>"
            "<li>Interactive visualizations</li>"
            "<li>Descriptive statistics</li>"
            "</ul>"
        )


# Import pandas for type checking
import pandas as pd