# -*- coding: utf-8 -*-
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QCheckBox, QComboBox, QGridLayout, QGroupBox
)
from qgis.PyQt.QtCore import Qt

class AchtergrondMapDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("QInfra – Achtergrond map")
        self.setMinimumWidth(400)
        
        # Main layout
        layout = QVBoxLayout()
        
        # Create group box for background maps
        group_box = QGroupBox("Selecteer achtergrond kaarten:")
        grid_layout = QGridLayout()
        
        # Row headers
        grid_layout.addWidget(QLabel("<b>Kaart</b>"), 0, 0)
        grid_layout.addWidget(QLabel("<b>Laden</b>"), 0, 1)
        grid_layout.addWidget(QLabel("<b>Visualisatie</b>"), 0, 2)
        
        # BRT row (first and default)
        grid_layout.addWidget(QLabel("BRT Achtergrondkaart"), 1, 0)
        self.cb_brt = QCheckBox()
        self.cb_brt.setChecked(True)  # Default selected
        grid_layout.addWidget(self.cb_brt, 1, 1)
        
        self.combo_brt = QComboBox()
        self.combo_brt.addItems([
            "Standaard",
            "Grijs", 
            "Pastel",
            "Water"
        ])
        grid_layout.addWidget(self.combo_brt, 1, 2)
        
        # Luchtfoto row
        grid_layout.addWidget(QLabel("Luchtfoto"), 2, 0)
        self.cb_luchtfoto = QCheckBox()
        grid_layout.addWidget(self.cb_luchtfoto, 2, 1)
        
        self.combo_luchtfoto = QComboBox()
        self.combo_luchtfoto.addItems(["Actueel ortho (8cm)", "Actueel ortho (25cm)"])
        grid_layout.addWidget(self.combo_luchtfoto, 2, 2)
        
        # BGT row
        grid_layout.addWidget(QLabel("BGT"), 3, 0)
        self.cb_bgt = QCheckBox()
        grid_layout.addWidget(self.cb_bgt, 3, 1)
        
        self.combo_bgt = QComboBox()
        self.combo_bgt.addItems([
            "Standaard visualisatie",
            "Achtergrond visualisatie", 
            "Icoon visualisatie",
            "Omtrek visualisatie",
            "Pastel visualisatie"
        ])
        grid_layout.addWidget(self.combo_bgt, 3, 2)
        
        # BRK row
        grid_layout.addWidget(QLabel("BRK (Kadastrale kaart)"), 4, 0)
        self.cb_brk = QCheckBox()
        grid_layout.addWidget(self.cb_brk, 4, 1)
        
        self.combo_brk = QComboBox()
        self.combo_brk.addItems([
            "Standaard kaart",
            "Kwaliteits visualisatie"
        ])
        grid_layout.addWidget(self.combo_brk, 4, 2)
        
        # Enable/disable combos based on checkboxes
        self.cb_brt.toggled.connect(self.combo_brt.setEnabled)
        self.cb_luchtfoto.toggled.connect(self.combo_luchtfoto.setEnabled)
        self.cb_bgt.toggled.connect(self.combo_bgt.setEnabled)
        self.cb_brk.toggled.connect(self.combo_brk.setEnabled)
        
        # Initial state - set enabled based on checkbox states
        self.combo_brt.setEnabled(self.cb_brt.isChecked())
        self.combo_luchtfoto.setEnabled(self.cb_luchtfoto.isChecked())
        self.combo_bgt.setEnabled(self.cb_bgt.isChecked())
        self.combo_brk.setEnabled(self.cb_brk.isChecked())
        
        group_box.setLayout(grid_layout)
        layout.addWidget(group_box)
        
        # Info label
        info_label = QLabel("Alle kaarten gebruiken EPSG:28992 (RD New) coördinatensysteem.")
        info_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(info_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        btn_ok = QPushButton("Laden")
        btn_cancel = QPushButton("Annuleren")
        
        button_layout.addStretch(1)
        button_layout.addWidget(btn_ok)
        button_layout.addWidget(btn_cancel)
        
        layout.addLayout(button_layout)
        
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        
        self.setLayout(layout)
    
    def get_selections(self):
        """Return dictionary of selected services and their options."""
        selections = {}
        
        if self.cb_brt.isChecked():
            # Map combo selection to layer key
            brt_options = {
                "Standaard": "standaard",
                "Grijs": "grijs",
                "Pastel": "pastel", 
                "Water": "water"
            }
            selected_text = self.combo_brt.currentText()
            selections["brt"] = brt_options.get(selected_text, "standaard")
            
        if self.cb_luchtfoto.isChecked():
            # Map combo selection to layer key - use original layer keys for compatibility
            luchtfoto_options = {
                "Actueel ortho (8cm)": "8cm",
                "Actueel ortho (25cm)": "25cm"
            }
            selected_text = self.combo_luchtfoto.currentText()
            selections["luchtfoto"] = luchtfoto_options.get(selected_text, "8cm")
            
        if self.cb_bgt.isChecked():
            # Map combo selection to layer key
            bgt_options = {
                "Standaard visualisatie": "standaard",
                "Achtergrond visualisatie": "achtergrond", 
                "Icoon visualisatie": "icoon",
                "Omtrek visualisatie": "omtrek",
                "Pastel visualisatie": "pastel"
            }
            selected_text = self.combo_bgt.currentText()
            selections["bgt"] = bgt_options.get(selected_text, "standaard")
            
        if self.cb_brk.isChecked():
            # Map combo selection to layer key
            brk_options = {
                "Standaard kaart": "standaard",
                "Kwaliteits visualisatie": "kwaliteit"
            }
            selected_text = self.combo_brk.currentText()
            selections["brk"] = brk_options.get(selected_text, "standaard")
            
        return selections