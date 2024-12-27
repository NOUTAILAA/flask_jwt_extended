import pytest
from unittest.mock import patch, MagicMock
from utils import send_email  # Assurez-vous que `send_email` est bien importé depuis le bon module
import smtplib

@pytest.fixture
def email_data():
    return {
        'to': 'test@example.com',
        'subject': 'Test Email',
        'body': 'Ceci est un email de test.'
    }


def test_send_email_success(email_data):
    with patch('smtplib.SMTP') as mock_smtp:
        instance = mock_smtp.return_value
        instance.send_message = MagicMock()

        send_email(email_data['to'], email_data['subject'], email_data['body'])

        instance.starttls.assert_called_once()
        instance.login.assert_called_once_with("ilgazzkaya599@gmail.com", 'brgq esjz adnv tppb')
        instance.send_message.assert_called_once()


def test_send_email_failure(email_data):
    with patch('smtplib.SMTP') as mock_smtp:
        instance = mock_smtp.return_value
        instance.send_message.side_effect = smtplib.SMTPException("Erreur d'envoi")

        with pytest.raises(smtplib.SMTPException):
            send_email(email_data['to'], email_data['subject'], email_data['body'])

        instance.starttls.assert_called_once()
        instance.login.assert_called_once_with("ilgazzkaya599@gmail.com", 'brgq esjz adnv tppb')
