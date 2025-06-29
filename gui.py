from PyQt5 import QtWidgets, QtCore, QtGui
import psutil
import socket
import os
import subprocess
import sys

class FlaskServerThread(QtCore.QThread):
    def __init__(self, host, port, cpf_db, cnpj_db):
        super().__init__()
        self.host = host
        self.port = port
        self.cpf_db = cpf_db
        self.cnpj_db = cnpj_db
        self.process = None

    def run(self):
        env = os.environ.copy()
        env['FLASK_RUN_HOST'] = self.host
        env['FLASK_RUN_PORT'] = str(self.port)
        env['CPF_DB_PATH'] = self.cpf_db
        env['CNPJ_DB_PATH'] = self.cnpj_db
        self.process = subprocess.Popen([sys.executable, 'flask-server.py'], env=env)

    def stop(self):
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()

class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python QT5 Flask Server")
        self.setFixedSize(520, 180)
        self.server_thread = None

        # Attributes for server config
        self.selected_host = None
        self.selected_port = 5000
        self.selected_cpf_db = None
        self.selected_cnpj_db = None

        # CPF DB field
        self.cpf_db_field = QtWidgets.QLineEdit()
        self.cpf_db_field.setReadOnly(True)
        self.cpf_db_field.setPlaceholderText("CPF database path")
        self.cpf_db_button = QtWidgets.QPushButton("Set CPF database")

        # CNPJ DB field
        self.cnpj_db_field = QtWidgets.QLineEdit()
        self.cnpj_db_field.setReadOnly(True)
        self.cnpj_db_field.setPlaceholderText("CNPJ database path")
        self.cnpj_db_button = QtWidgets.QPushButton("Set CNPJ database")

        # Interfaces combo
        self.interface_combo = QtWidgets.QComboBox()
        self.interface_map = {}
        for name, addrs in psutil.net_if_addrs().items():
            ip = None
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    ip = addr.address
                    break
            display = f"{name} ({ip})" if ip else f"{name} (No IPv4 address)"
            self.interface_combo.addItem(display)
            self.interface_map[display] = ip

        # Port field with validator
        self.port_field = QtWidgets.QLineEdit(str(self.selected_port))
        self.port_field.setPlaceholderText("Port")
        self.port_field.setValidator(QtGui.QIntValidator(1, 65535, self))

        # Buttons
        self.start_server_button = QtWidgets.QPushButton("Start Server")
        self.stop_server_button = QtWidgets.QPushButton("Stop Server")
        self.stop_server_button.setEnabled(False)
        self.close_button = QtWidgets.QPushButton("Close")
        self.error_label = QtWidgets.QLabel("")
        self.error_label.setStyleSheet("color: red")
        self.error_label.setAlignment(QtCore.Qt.AlignCenter)
        self.error_label.setWordWrap(True)

        # Layouts
        cpf_layout = QtWidgets.QHBoxLayout()
        cpf_layout.addWidget(self.cpf_db_field)
        cpf_layout.addWidget(self.cpf_db_button)

        cnpj_layout = QtWidgets.QHBoxLayout()
        cnpj_layout.addWidget(self.cnpj_db_field)
        cnpj_layout.addWidget(self.cnpj_db_button)

        hostport_layout = QtWidgets.QHBoxLayout()
        hostport_layout.addWidget(self.interface_combo)
        hostport_layout.addWidget(self.port_field)

        error_layout = QtWidgets.QHBoxLayout()
        error_layout.addWidget(self.error_label)

        startstop_layout = QtWidgets.QHBoxLayout()
        startstop_layout.addWidget(self.start_server_button)
        startstop_layout.addWidget(self.stop_server_button)

        close_layout = QtWidgets.QHBoxLayout()
        close_layout.addStretch()
        close_layout.addWidget(self.close_button)
        close_layout.addStretch()

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(cpf_layout)
        main_layout.addLayout(cnpj_layout)
        main_layout.addLayout(hostport_layout)
        main_layout.addLayout(error_layout)
        main_layout.addLayout(startstop_layout)
        main_layout.addLayout(close_layout)
        self.setLayout(main_layout)

        # Connect signals
        self.cpf_db_button.clicked.connect(self.select_cpf_db)
        self.cnpj_db_button.clicked.connect(self.select_cnpj_db)
        self.interface_combo.currentIndexChanged.connect(self.update_selected_host)
        self.port_field.textChanged.connect(self.update_selected_port)
        self.start_server_button.clicked.connect(self.start_server_handler)
        self.stop_server_button.clicked.connect(self.stop_server_handler)
        self.close_button.clicked.connect(self.close)

        # Initialize selections
        self.update_selected_host()
        self.update_selected_port()

    def select_cpf_db(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select CPF Database")
        if path:
            self.selected_cpf_db = path
            self.cpf_db_field.setText(path)

    def select_cnpj_db(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select CNPJ Database")
        if path:
            self.selected_cnpj_db = path
            self.cnpj_db_field.setText(path)

    def update_selected_host(self):
        display = self.interface_combo.currentText()
        self.selected_host = self.interface_map.get(display, None)

    def update_selected_port(self):
        text = self.port_field.text()
        try:
            port = int(text)
            if 1 <= port <= 65535:
                self.selected_port = port
            else:
                self.selected_port = None
        except ValueError:
            self.selected_port = None

    def validate_inputs(self):
        # Validate all fields and return (True, "") or (False, "error message")
        if not self.selected_host:
            return False, "Please select a valid network interface with an IPv4 address."
        if not self.selected_port:
            return False, "Please enter a valid port number (1-65535)."
        if not self.selected_cpf_db or not os.path.isfile(self.selected_cpf_db):
            return False, "Please select a valid CPF database file."
        if not self.selected_cnpj_db or not os.path.isfile(self.selected_cnpj_db):
            return False, "Please select a valid CNPJ database file."
        return True, ""

    def start_server_handler(self):
        valid, error = self.validate_inputs()
        if not valid:
            self.error_label.setText(error)
            return

        self.server_thread = FlaskServerThread(
            self.selected_host,
            self.selected_port,
            self.selected_cpf_db,
            self.selected_cnpj_db
        )
        self.server_thread.start()
        self.start_server_button.setEnabled(False)
        self.stop_server_button.setEnabled(True)
        self.error_label.setText("Server started.")

    def stop_server_handler(self):
        if self.server_thread:
            self.server_thread.stop()
            self.server_thread = None
            self.start_server_button.setEnabled(True)
            self.stop_server_button.setEnabled(False)
            self.error_label.setText("Server stopped.")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
