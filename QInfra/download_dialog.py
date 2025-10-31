# -*- coding: utf-8 -*-
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QPushButton,
    QCheckBox, QGridLayout
)
from qgis.PyQt.QtCore import Qt

class DownloadDialog(QDialog):
    def __init__(self, parent=None, schatting_functie=None, init_res=0.25):
        super().__init__(parent)
        self.setWindowTitle("QInfra – Download")
        self.schatting_functie = schatting_functie

        # ---------- checkboxes ----------
        self.cb_lucht = QCheckBox("Luchtfoto")
        self.cb_lucht.setChecked(True)
        self.cb_bgt = QCheckBox("BGT (binnenkort)"); self.cb_bgt.setEnabled(False)
        self.cb_brk = QCheckBox("BRK (binnenkort)"); self.cb_brk.setEnabled(False)

        # ---------- slider ----------
        self.slider = QSlider(Qt.Horizontal)
        MIN_V = 5; MAX_V = 200
        self.slider.setMinimum(MIN_V); self.slider.setMaximum(MAX_V)
        # initialise slider so that the provided init_res (m/px) maps to the correct slider value
        # mapping: m_per_px = (MIN_V + MAX_V - v) / 100.0  ->  v = MIN_V + MAX_V - (m_per_px*100)
        v_init = int(round(MIN_V + MAX_V - (init_res * 100.0)))
        self.slider.setValue(max(MIN_V, min(MAX_V, v_init)))
        self.slider.setTickInterval(5); self.slider.setSingleStep(1)

        # a label that will show the size estimate (kept)
        self.lbl_info = QLabel(); self.lbl_info.setWordWrap(True)

        grid = QGridLayout()
        grid.addWidget(self.cb_lucht, 0, 0)
        grid.addWidget(QLabel("Resolutie (px/m)"), 0, 1)
        grid.addWidget(self.slider, 0, 2); grid.setColumnStretch(2, 1)
        grid.addWidget(self.cb_bgt, 1, 0)
        grid.addWidget(self.cb_brk, 2, 0)

        lay = QVBoxLayout()
        lay.addLayout(grid)
        lay.addWidget(self.lbl_info)

        bl = QHBoxLayout()
        btn_ok = QPushButton("Download"); btn_cancel = QPushButton("Annuleren")
        bl.addStretch(1); bl.addWidget(btn_ok); bl.addWidget(btn_cancel)
        lay.addLayout(bl)

        btn_ok.clicked.connect(self.accept); btn_cancel.clicked.connect(self.reject)
        self.setLayout(lay)

        self.slider.valueChanged.connect(self._update_labels)
        self._update_labels()

    def _update_labels(self):
        # slider direction has been inverted for intuitive UI:
        # moving the slider to the right increases image resolution (smaller meters/pixel).
        # mapping: m_per_px = (min + max - v) / 100.0
        v = self.slider.value()
        m_per_px = (self.slider.minimum() + self.slider.maximum() - v) / 100.0
        # safety clamp (avoid zero)
        if m_per_px <= 0:
            m_per_px = 0.01

        if self.schatting_functie:
            px = self.schatting_functie(m_per_px)
            if px:
                w, h, mb = px
                # show KB for sizes below 0.1 MB (more useful than "0.0 MB")
                if mb < 0.1:
                    kb = mb * 1024.0
                    kb_display = int(round(kb)) if kb >= 1 else "<1"
                    self.lbl_info.setText(f"Schatting (Luchtfoto): ~ {w} × {h} px (~{kb_display} KB)")
                else:
                    self.lbl_info.setText(f"Schatting (Luchtfoto): ~ {w} × {h} px (~{mb:.1f} MB)")
            else:
                self.lbl_info.setText("Geen Projectgebied gevonden. Teken eerst een rechthoek.")

    def gekozen_resolutie(self):
        # return meters per pixel, inverted mapping so right = better resolution
        v = self.slider.value()
        m_per_px = (self.slider.minimum() + self.slider.maximum() - v) / 100.0
        if m_per_px <= 0:
            m_per_px = 0.01
        return m_per_px

    def keuzes(self):
        return { "luchtfoto": self.cb_lucht.isChecked(), "bgt": self.cb_bgt.isChecked(), "brk": self.cb_brk.isChecked() }
