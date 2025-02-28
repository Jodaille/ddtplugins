# -*- coding: utf-8 -*-

# (c) 2017

import PyQt5.QtCore as core
import PyQt5.QtWidgets as gui
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem
import ecu
import options

_ = options.translator('ddt4all')

plugin_name = _("Zoe water pump Reset")
category = _("EVC Tools")
need_hw = True
ecufile = "EVC_3180_RH5_510_V1.1_20210422T184714"

class Virginizer(gui.QDialog):
    def __init__(self):
        super(Virginizer, self).__init__()
        self.evc_ecu = ecu.Ecu_file(ecufile, True)
        self.setWindowTitle("Water pump counter")
        self.setGeometry(100, 100, 400, 300)

        layout = gui.QVBoxLayout()

        # Création du tableau
        self.table = QTableWidget()
        self.table.setRowCount(4)  # Nombre de lignes
        self.table.setColumnCount(2)  # Nombre de colonnes
        self.table.setHorizontalHeaderLabels(["Nom", "Valeur"])  # Entêtes de colonnes
        self.table.setColumnWidth(0, 200)

        # Ajout des données dans le tableau
        data = [
            ["Low Speed", ""],
            ["Middle Speed", ""],
            ["High Speed", ""],
            ["V_Timer_DrivWEP_ON", ""], #V_Timer_DrivWEP_ON
        ]

        for row, (nom, valeur) in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(nom))
            self.table.setItem(row, 1, QTableWidgetItem(valeur))

        # Ajout du tableau au layout
        layout.addWidget(self.table)

        infos = gui.QLabel("Zoe water pump counters<br>"
                             "water pump counters RESET")
        infos.setAlignment(core.Qt.AlignHCenter)
        check_button = gui.QPushButton("Check values")
        self.status_check = gui.QLabel("Waiting action")
        self.status_check.setAlignment(core.Qt.AlignHCenter)
        self.virginize_button = gui.QPushButton("Reset counters")
        layout.addWidget(infos)
        layout.addWidget(check_button)
        layout.addWidget(self.status_check)
        layout.addWidget(self.virginize_button)
        self.setLayout(layout)
        self.virginize_button.setEnabled(True)
        self.virginize_button.clicked.connect(self.reset_ecu)
        check_button.clicked.connect(self.get_counters_values)
        self.ecu_connect()

    def ecu_connect(self):
        connection = self.evc_ecu.connect_to_hardware()
        if not connection:
            options.main_window.logview.append(_("Cannot connect to ECU"))
            self.finished()

    def get_counters_values(self):
        self.start_diag_session()
        self.get_low_speed_counter()
        self.get_medium_speed_counter()
        self.get_high_speed_counter()
        self.get_timer_DrivWEP_ON()
        self.status_check.setText(_("<font color='green'>Values read</font>"))


    def get_timer_DrivWEP_ON(self):
        key_name = "($3531) V_Timer_DrivWEP_ON"
        pumptimer_check_request = self.evc_ecu.requests[
            u'DataRead.($3531) V_Timer_DrivWEP_ON']

        options.main_window.logview.append("reading V_Timer_DrivWEP_ON")
        pumptimer_check_values = pumptimer_check_request.send_request()
        print(pumptimer_check_values)
        value = pumptimer_check_values.get(key_name)
        value = str(value)
        self.table.setItem(3, 1, QTableWidgetItem(value))

    def get_low_speed_counter(self):
        key_name = "($3349) Time Counter for the driving WEP in Low Speed"
        lowspeed_check_request = self.evc_ecu.requests[
            u'DataRead.($3349) Time Counter for the driving WEP in Low Speed']
        options.main_window.logview.append("reading Low speed")
        lowspeed_check_values = lowspeed_check_request.send_request()
        print(lowspeed_check_values)
        value = lowspeed_check_values.get(key_name)
        value = str(value)

        options.main_window.logview.append(value)
        self.table.setItem(0, 1, QTableWidgetItem(value))

    def get_medium_speed_counter(self):
        key_name = "($334A) Time Counter for the driving WEP in Middle Speed"
        middlespeed_check_request = self.evc_ecu.requests[
            u'DataRead.($334A) Time Counter for the driving WEP in Middle Speed']

        options.main_window.logview.append("reading Middle speed")

        middlespeed_check_values = middlespeed_check_request.send_request()
        print(middlespeed_check_values)
        value = middlespeed_check_values.get(key_name)
        value = str(value)

        options.main_window.logview.append(value)
        self.table.setItem(1, 1, QTableWidgetItem(value))

    def get_high_speed_counter(self):
        key_name = "($334B) Time Counter for the driving WEP in High Speed"
        highspeed_check_request = self.evc_ecu.requests[
            u'DataRead.($334B) Time Counter for the driving WEP in High Speed']

        options.main_window.logview.append("reading High speed")

        highspeed_check_values = highspeed_check_request.send_request()
        print(highspeed_check_values)
        value = highspeed_check_values.get(key_name)
        value = str(value)

        options.main_window.logview.append(value)
        self.table.setItem(2, 1, QTableWidgetItem(value))

    def start_diag_session(self):
        sds_request = self.evc_ecu.requests[u"StartDiagnosticSession.Default"]

        sds_stream = " ".join(sds_request.build_data_stream({}))
        if options.simulation_mode:
            print("SdS stream", sds_stream)
            return
        options.elm.start_session_can(sds_stream)

    def reset_ecu(self):
        self.start_diag_session()
        self.reset_low_speed_counter()
        self.reset_medium_speed_counter()
        self.reset_high_speed_counter()
        self.reset_timer_DrivWEP()

    def reset_timer_DrivWEP(self):
        reset_request = self.evc_ecu.requests[u"DataWrite.($3531) V_Timer_DrivWEP_ON"]
        request_response = reset_request.send_request()
        print(request_response)
        if request_response is not None:
            self.status_check.setText(_("<font color='green'>CLEAR V_Timer_DrivWEP_ON EXECUTED</font>"))
        else:
            self.status_check.setText(_("<font color='red'>CLEAR V_Timer_DrivWEP_ON FAILED</font>"))
        self.get_timer_DrivWEP_ON()

    def reset_low_speed_counter(self):
        reset_request = self.evc_ecu.requests[u"DataWrite.($3349) Time Counter for the driving WEP in Low Speed"]
        request_response = reset_request.send_request()
        print(request_response)
        if request_response is not None:
            self.status_check.setText(_("<font color='green'>CLEAR Low EXECUTED</font>"))
        else:
            self.status_check.setText(_("<font color='red'>CLEAR Low FAILED</font>"))
        self.get_low_speed_counter()

    def reset_medium_speed_counter(self):
        reset_request = self.evc_ecu.requests[u"DataWrite.($334A) Time Counter for the driving WEP in Middle Speed"]
        request_response = reset_request.send_request()
        print(request_response)
        if request_response is not None:
            self.status_check.setText(_("<font color='green'>CLEAR Medium EXECUTED</font>"))
        else:
            self.status_check.setText(_("<font color='red'>CLEAR Medium FAILED</font>"))
        self.get_medium_speed_counter()

    def reset_high_speed_counter(self):
        reset_request = self.evc_ecu.requests[u"DataWrite.($334B) Time Counter for the driving WEP in High Speed"]
        request_response = reset_request.send_request()
        print(request_response)
        if request_response is not None:
            self.status_check.setText(_("<font color='green'>CLEAR HIGH EXECUTED</font>"))
        else:
            self.status_check.setText(_("<font color='red'>CLEAR HIGH FAILED</font>"))
        self.get_high_speed_counter()

def plugin_entry():
    v = Virginizer()
    v.exec_()