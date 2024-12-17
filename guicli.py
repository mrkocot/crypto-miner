from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QLineEdit
from PyQt6.QtCore import Qt, QPropertyAnimation, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont
import sys
import os
import subprocess
import time

os.environ["QT_ENABLE_HIGHDPI_SCALING"]   = "0"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "0"
os.environ["QT_SCALE_FACTOR"] = "1"     

class CLIThread(QThread):
    output_signal = pyqtSignal(str)  # Sygnalizowanie nowych danych do wyświetlenia w GUI

    def __init__(self):
        super().__init__()
        self.process = None
        self.running = False

    def run(self):
        """Uruchamia CLI w osobnym wątku i obsługuje interakcję z terminalem"""
        try:
            # Ustalamy pełną ścieżkę do folderu 'engine'
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            engine_dir = os.path.join(project_root, 'engine')

            # Uruchamiamy cli.py jako moduł Pythona
            self.process = subprocess.Popen(
                [sys.executable, '-m', 'engine.cli'],  # Uruchamiamy cli.py jako moduł
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True
            )

            self.running = True
            
            while self.running:
                # Odczytujemy dane z wyjścia stdout
                output = self.process.stdout.readline()
                if output:
                    self.output_signal.emit(output)  # Wysyłanie danych do GUI
                time.sleep(0.1)  # Małe opóźnienie, aby uniknąć wysokiego zużycia CPU

        except Exception as e:
            self.output_signal.emit(f"Błąd przy uruchamianiu CLI: {e}")
        
    def send_input(self, command: str):
        """Wysyła dane do stdin procesu"""
        if self.process:
            self.process.stdin.write(command + '\n')
            self.process.stdin.flush()  # Wymusza zapis do stdin natychmiast
            time.sleep(0.1)  # Małe opóźnienie na bezpieczeństwo

    def stop(self):
        """Zatrzymuje proces"""
        if self.process:
            self.process.terminate()
        self.running = False

class GameGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Crypto Miner")
        self.setFixedSize(1280, 1024)
        self.cli_thread = CLIThread()
        self.cli_thread.output_signal.connect(self.update_console_output)  # Połącz wątek z GUI
        self.cli_thread.start()  # Rozpoczęcie wątku CLI
        # Ekran powitalny
        self.welcome_screen()

    def welcome_screen(self):
        """Pokazuje ekran powitalny z obrazkiem i napisem"""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout()
        self.central_widget.setLayout(layout)

        # Wyświetlenie obrazka powitalnego
        self.image_label = QLabel(self)

        # Ładowanie obrazka i sprawdzanie błędów
        pixmap = QPixmap('engine/assets/menu.png')
        if pixmap.isNull():
            print("Błąd: Obrazek nie został załadowany. Sprawdź ścieżkę.")
        else:
            self.image_label.setPixmap(pixmap)
            self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(self.image_label)

        # Dodajemy obrazek do layoutu na samym dole
        layout.addWidget(self.image_label)

        # Ruchomy napis
        self.text_label = QLabel(">>> Kliknij aby zacząć grać <<<", self)
        self.text_label.setFont(QFont("Courier", 30))  
        self.text_label.setStyleSheet("color: #FFD700")  # Kolor złoty
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Ustawiamy pozycję napisu na górze
        layout.insertWidget(0, self.text_label)

        # Tworzymy animację do powiększania i pomniejszania napisu
        self.font_size = 30  # Początkowy rozmiar czcionki
        self.growing = True  # Określenie kierunku animacji
        self.text_timer = QTimer(self)
        self.text_timer.timeout.connect(self.animate_text)
        self.text_timer.start(100)  # Animacja co 1 sekundę

        # Oczekiwanie na kliknięcie, aby przejść do gry
        self.text_label.mousePressEvent = self.start_game 
        self.image_label.mousePressEvent = self.start_game

    def animate_text(self):
        """Animacja zmieniająca rozmiar czcionki napisu"""
        if self.growing:
            self.font_size += 1
            if self.font_size >= 40:
                self.growing = False
        else:
            self.font_size -= 1
            if self.font_size <= 30:
                self.growing = True
        
        # Ustawienie rozmiaru czcionki
        self.text_label.setFont(QFont("Courier", self.font_size))
    def start_game(self, event):
        """Rozpoczynanie gry po kliknięciu"""
        self.text_label.setText("> Rozpoczynanie gry... <")  # Zmieniamy tekst na informację o starcie
        self.text_timer.stop()  # Zatrzymanie animacji czcionki

        # Teraz uruchamiamy grę, ukrywając ekran powitalny
        self.image_label.hide()
        self.text_label.hide()

        # Uruchomienie gry
        self.game_screen()

    def game_screen(self):

        # Ustawienie tła (tlo.png)
        self.background_label = QLabel(self)
        self.background_label.setPixmap(QPixmap('engine/assets/terminal.png'))  # Ścieżka do tła
        self.background_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.background_label.setScaledContents(True)  # Tło wypełni okno
        self.background_label.setGeometry(self.rect())  # Dopasowanie tła do rozmiaru okna
        self.background_label.show()

        # Tworzenie terminala w czarnej przestrzeni na tle
        self.console_output = QLabel(self)
        self.console_output.setStyleSheet("background-color: black; color: #7CB9E8; font-family: monospace; padding: 10px;")
        self.console_output.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Tworzenie pola do wprowadzania komend
        self.console_input = QLineEdit(self)
        self.console_input.setStyleSheet("background-color: black; color: #7CB9E8; font-family: monospace; padding: 5px;")
        self.console_input.setGeometry(40, 570, 1200, 30)  # Pozycja pola w GUI
        self.console_input.setFocus()  # Ustawia fokus na pole tekstowe
        self.console_input.setPlaceholderText("Wpisz komendę...")
        self.console_input.show()

        self.console_output.setText("Oto twój terminal, tutaj możesz zarządzać światem kryptowalut\n" + "CryptoMiner~ >\n" + self.console_output.text() if hasattr(self, 'console_output') else "")

        # Ustawienie terminala wewnątrz tła
        self.console_output.setGeometry(40, 130, 1200, 420)  # Pozycja i rozmiar w obrębie czarnej przestrzeni
        self.console_output.show()

    def update_console_output(self, output: str):
        """Aktualizuje wyjście konsoli w GUI"""
        current_text = self.console_output.text()
        new_text = current_text + output
        self.console_output.setText(new_text)

    def send_command_to_cli(self, command: str):
        """Funkcja umożliwiająca wysyłanie komend do CLI"""
        self.cli_thread.send_input(command)

    def keyPressEvent(self, event):
        """Override key press event to capture the Enter key."""
        key = event.key()
        if key == 16777220:  # Kod klawisza Enter (ASCII dla Return / Enter w PyQt6)
            print("Enter key pressed")
            self.run_cli_command()  # Zastąp własną funkcją
    
    def run_cli_command(self):
        """Metoda do uruchamiania komendy w CLI po naciśnięciu Enter."""
        command = self.console_input.text()  # Pobierz tekst z pola wejściowego
        if command:
            print(f"Wysyłanie komendy: {command}")
            self.cli_thread.send_input(command)  # Wysyłanie komendy do CLI
            self.console_input.clear()  # Czyści pole wejściowe po wysłaniu komendy

        def closeEvent(self, event):
            """Zatrzymuje wątek i zamyka aplikację"""
            self.cli_thread.stop()
            super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GameGUI()
    window.show()
    sys.exit(app.exec())
