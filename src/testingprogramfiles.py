import unittest
from unittest.mock import Mock, patch
from main import PersonDetector
import uasyncio

class TestPersonDetector(unittest.TestCase):
    def setUp(self):
        self.on_person_detected = Mock()
        self.on_person_not_detected = Mock()
        self.detector = PersonDetector(self.on_person_detected, self.on_person_not_detected)

    @patch('main.uasyncio.StreamReader')
    @patch('main.UART')
    def test_person_moved(self, mock_uart, mock_stream_reader):
        mock_stream_reader.readline.return_value = b'\x02'
        uasyncio.run(self.detector._receiver())
        self.on_person_detected.assert_called_once_with("Somebody moved")

    @patch('main.uasyncio.StreamReader')
    @patch('main.UART')
    def test_person_stopped_moving(self, mock_uart, mock_stream_reader):
        mock_stream_reader.readline.return_value = b'\x01'
        uasyncio.run(self.detector._receiver())
        self.on_person_detected.assert_called_once_with("Somebody stopped moving")

    @patch('main.uasyncio.StreamReader')
    @patch('main.UART')
    def test_person_close(self, mock_uart, mock_stream_reader):
        mock_stream_reader.readline.return_value = b'\x01'
        uasyncio.run(self.detector._receiver())
        self.on_person_detected.assert_called_once_with("Somebody is close")

    @patch('main.uasyncio.StreamReader')
    @patch('main.UART')
    def test_person_away(self, mock_uart, mock_stream_reader):
        mock_stream_reader.readline.return_value = b'\x02'
        uasyncio.run(self.detector._receiver())
        self.on_person_detected.assert_called_once_with("Somebody is away")

    @patch('main.uasyncio.StreamReader')
    @patch('main.UART')
    def test_no_human_activity(self, mock_uart, mock_stream_reader):
        mock_stream_reader.readline.return_value = b'\x03'
        uasyncio.run(self.detector._receiver())
        self.on_person_not_detected.assert_called_once_with("No human activity detected")

if __name__ == '__main__':
    unittest.main()