"""
Unit tests for Phase 03: Polling Management Command
Tests polling logic, offset management, and error handling.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from io import StringIO
from django.core.management import call_command
from telegram_bot.models import TelegramUpdateOffset


@pytest.mark.django_db
class TestPollTelegramBotCommand:
    """Test polling management command"""

    @patch('telegram_bot.callback_handlers.PaymentCallbackHandler')
    @patch('telegram_bot.services.TelegramService')
    def test_command_processes_callback_queries(self, mock_service_class, mock_handler_class):
        """Test command processes callback queries via handler"""
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_handler = Mock()
        mock_handler_class.return_value = mock_handler
        mock_handler.handle_callback_query.return_value = True

        mock_updates = [{
            'update_id': 100,
            'callback_query': {
                'id': 'cb123',
                'data': 'confirm_payment:1',
                'from': {'id': 123456},
                'message': {'chat': {'id': 123456}}
            }
        }]

        # Mock the polling service method
        with patch('telegram_bot.management.commands.poll_telegram_bot.TelegramService') as cmd_service_class:
            cmd_mock_service = Mock()
            cmd_service_class.return_value = cmd_mock_service
            cmd_mock_service.get_telegram_updates.return_value = mock_updates

            # Create a mock handler for the command
            with patch('telegram_bot.management.commands.poll_telegram_bot.PaymentCallbackHandler') as cmd_handler_class:
                cmd_mock_handler = Mock()
                cmd_handler_class.return_value = cmd_mock_handler
                cmd_mock_handler.handle_callback_query.return_value = True

                call_command('poll_telegram_bot', timeout=5)

                # Verify handler called
                cmd_mock_handler.handle_callback_query.assert_called_once()

                # Verify offset updated
                assert TelegramUpdateOffset.get_offset() == 100

    @patch('telegram_bot.callback_handlers.PaymentCallbackHandler')
    @patch('telegram_bot.services.TelegramService')
    def test_command_updates_offset_on_error(self, mock_service_class, mock_handler_class):
        """Test offset updates even if handler fails"""
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_handler = Mock()
        mock_handler_class.return_value = mock_handler
        mock_handler.handle_callback_query.side_effect = Exception("Test error")

        mock_updates = [{
            'update_id': 200,
            'callback_query': {
                'id': 'cb456',
                'data': 'test',
                'from': {'id': 123}
            }
        }]

        with patch('telegram_bot.management.commands.poll_telegram_bot.TelegramService') as cmd_service_class:
            cmd_mock_service = Mock()
            cmd_service_class.return_value = cmd_mock_service
            cmd_mock_service.get_telegram_updates.return_value = mock_updates

            with patch('telegram_bot.management.commands.poll_telegram_bot.PaymentCallbackHandler') as cmd_handler_class:
                cmd_mock_handler = Mock()
                cmd_handler_class.return_value = cmd_mock_handler
                cmd_mock_handler.handle_callback_query.side_effect = Exception("Test error")

                # Should not raise exception
                call_command('poll_telegram_bot', timeout=5)

                # Offset should still update (prevent infinite loop)
                assert TelegramUpdateOffset.get_offset() == 200

    @patch('telegram_bot.callback_handlers.PaymentCallbackHandler')
    @patch('telegram_bot.services.TelegramService')
    def test_command_skips_regular_messages(self, mock_service_class, mock_handler_class):
        """Test command ignores non-callback updates"""
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_handler = Mock()
        mock_handler_class.return_value = mock_handler

        mock_updates = [{
            'update_id': 300,
            'message': {  # Regular message, not callback
                'text': 'Hello',
                'from': {'id': 123}
            }
        }]

        with patch('telegram_bot.management.commands.poll_telegram_bot.TelegramService') as cmd_service_class:
            cmd_mock_service = Mock()
            cmd_service_class.return_value = cmd_mock_service
            cmd_mock_service.get_telegram_updates.return_value = mock_updates

            with patch('telegram_bot.management.commands.poll_telegram_bot.PaymentCallbackHandler') as cmd_handler_class:
                cmd_mock_handler = Mock()
                cmd_handler_class.return_value = cmd_mock_handler

                call_command('poll_telegram_bot', timeout=5)

                # Handler should NOT be called
                cmd_mock_handler.handle_callback_query.assert_not_called()

                # But offset should still update
                assert TelegramUpdateOffset.get_offset() == 300

    @patch('telegram_bot.services.TelegramService')
    def test_command_handles_no_updates(self, mock_service_class):
        """Test command handles empty update list gracefully"""
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        with patch('telegram_bot.management.commands.poll_telegram_bot.TelegramService') as cmd_service_class:
            cmd_mock_service = Mock()
            cmd_service_class.return_value = cmd_mock_service
            cmd_mock_service.get_telegram_updates.return_value = []

            # Should complete without errors
            call_command('poll_telegram_bot', timeout=5)


@pytest.mark.django_db
class TestOffsetManagement:
    """Test TelegramUpdateOffset model"""

    def test_get_offset_default_zero(self):
        """Test get_offset returns 0 initially"""
        offset = TelegramUpdateOffset.get_offset()
        assert offset == 0

    def test_set_offset_updates_value(self):
        """Test set_offset updates the value"""
        TelegramUpdateOffset.set_offset(100)
        offset = TelegramUpdateOffset.get_offset()
        assert offset == 100

    def test_set_offset_multiple_times(self):
        """Test set_offset can be called multiple times"""
        TelegramUpdateOffset.set_offset(100)
        TelegramUpdateOffset.set_offset(200)
        TelegramUpdateOffset.set_offset(300)
        offset = TelegramUpdateOffset.get_offset()
        assert offset == 300
