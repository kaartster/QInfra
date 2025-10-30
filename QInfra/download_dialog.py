
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QPushButton, QCheckBox, QGridLayout
)
from qgis.PyQt.QtCore import Qt

class DownloadDialog(QDialog):
    def __init__(self, parent=None, schatting_functie=None, init_res=0.25):
        super().__init__(parent)
        self.setWindowTitle("QInfra – Download")
        self.schatting_functie = schatting_functie

        self.cb_lucht = QCheckBox("Luchtfoto")
        self.cb_lucht.setChecked(True)
        self.cb_bgt = QCheckBox("BGT (binnenkort)"); self.cb_bgt.setEnabled(False)
        self.cb_brk = QCheckBox("BRK (binnenkort)"); self.cb_brk.setEnabled(False)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(5); self.slider.setMaximum(200)
        self.slider.setValue(max(5, min(200, int(round(init_res * 100)))))
        self.slider.setTickInterval(5); self.slider.setSingleStep(1)
        self.lbl_res = QLabel(); self.lbl_info = QLabel(); self.lbl_info.setWordWrap(True)

        grid = QGridLayout()
        grid.addWidget(self.cb_lucht, 0, 0)
        grid.addWidget(QLabel("Resolutie (m/px):"), 0, 1)
        grid.addWidget(self.slider, 0, 2); grid.setColumnStretch(2, 1)
        grid.addWidget(self.cb_bgt, 1, 0)
        grid.addWidget(self.cb_brk, 2, 0)

        lay = QVBoxLayout()
        lay.addLayout(grid)
        lay.addWidget(self.lbl_res)
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
        r = self.slider.value() / 100.0
        self.lbl_res.setText(f"Luchtfoto resolutie: {r:.2f} m/pixel")
        if self.schatting_functie:
            px = self.schatting_functie(r)
            if px:
                w, h, mb = px
                self.lbl_info.setText(f"Schatting (Luchtfoto): ~ {w} × {h} px (~{mb:.1f} MB)")
            else:
                self.lbl_info.setText("Geen Projectgebied gevonden. Teken eerst een rechthoek.")

    def gekozen_resolutie(self):
        return self.slider.value() / 100.0

    def keuzes(self):
        return { "luchtfoto": self.cb_lucht.isChecked(), "bgt": self.cb_bgt.isChecked(), "brk": self.cb_brk.isChecked() }
