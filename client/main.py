import sys
import requests
from requests import ConnectionError
from PyQt5.QtCore import Qt, QRegExp
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon, QRegExpValidator
from PyQt5.QtWidgets import QDialog, QTableWidget, QTableWidgetItem, QStatusBar, QMessageBox, QLineEdit
from main_window import Ui_MainWindow
from datetime import datetime
from settings import settings


class MainWindow(QtWidgets.QMainWindow):
    num_only_validator = QRegExpValidator(QRegExp(r'[0-9]+'))
    float_num_validator = QRegExpValidator(QRegExp(r'(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?'))
    num_with_dot_validator = QRegExpValidator(QRegExp(r'([0-9]+\.?)+'))


    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.init_ui()


    def init_ui(self):
        self.setWindowTitle('NPV counter')
        self.setFixedSize(800, 370)
        self.ui.btn_close.clicked.connect(self.on_close)
        self.ui.input_host.setPlaceholderText('127.0.0.1')
        self.ui.input_port.setPlaceholderText('8080')
        self.ui.input_year.setPlaceholderText('2036')
        self.ui.input_discount_rate.setPlaceholderText('0.2')
        self.ui.btn_count.clicked.connect(self.npv_count)
        self.statusBar().showMessage('🔴 Ответ от сервера отсутсвует')
        self.ui.input_host.setText(self.get_server_info()[0])
        self.ui.input_port.setText(self.get_server_info()[1])
        self.ui.input_host.setValidator(self.num_with_dot_validator)
        self.ui.input_port.setValidator(self.num_only_validator)
        self.ui.input_year.setValidator(self.num_only_validator)
        self.ui.input_discount_rate.setValidator(self.float_num_validator)
        self.ui.btn_clear.clicked.connect(self.on_clear)
        self.set_table_headers()


    def set_table_headers(self):
        self.ui.tableWidget.setRowCount(4)
        self.ui.tableWidget.setColumnCount(0)
        for row, val in enumerate(["Год", "Доход", "Расход", "NPV"]):
            item = QtWidgets.QTableWidgetItem(val)
            self.ui.tableWidget.setVerticalHeaderItem(row, item)


    def npv_count(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        try:
            year = str(datetime.now().year)
            input_year = int(self.ui.input_year.text())
            input_discount_rate = float(self.ui.input_discount_rate.text())
            url = f'http://{self.ui.input_host.text()}:{self.ui.input_port.text()}/npv'
            r = requests.post(url, json={'year': input_year,
                                         'discount_rate': input_discount_rate,
                                         'income': 1000,
                                         'expense': 500,
                                         'prev_NPV': 0})
            response = r.json()

            if response:
                self.statusBar().showMessage('🟢 Ответ от сервера получен')
            self.ui.tableWidget.setColumnCount(len(response))
            for col, val in enumerate(response):
                self.ui.tableWidget.setItem(0, col, QTableWidgetItem(year))
                self.ui.tableWidget.setItem(1, col, QTableWidgetItem('1000'))
                self.ui.tableWidget.setItem(2, col, QTableWidgetItem('500'))
                self.ui.tableWidget.setItem(3, col, QTableWidgetItem(str(response[col])))
                year = str(int(year) + 1)
        except ValueError:
            self.msg.setText('Ошибка ввода данных')
            self.msg.setInformativeText('Некорректные данные или незаполнены обязательные поля для ввода')
            self.msg.setWindowTitle('Ошибка')
            self.msg.exec_()
        except (ConnectionRefusedError, ConnectionError):
            self.msg.setText('Ошибка подключения к серверу')
            self.msg.setInformativeText('Проверьте корректность ввода данных подключения к серверу')
            self.msg.setWindowTitle('Ошибка')
            self.msg.exec_()


    def get_server_info(self) -> tuple[str]:
        return (str(settings.host), str(settings.port))


    def on_clear(self) -> None:
        for edit in self.findChildren(QLineEdit):
            edit.clear()
        self.ui.tableWidget.clear()
        self.set_table_headers()


    def on_close(self) -> None:
        self.close()


app = QtWidgets.QApplication([])
application = MainWindow()
application.show()
sys.exit(app.exec_())