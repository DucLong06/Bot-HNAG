"""
Unit tests for Phase 01: Telegram Service Extensions
Tests polling, inline keyboards, callback queries, and message editing.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from telegram_bot.services import TelegramService
from telegram_bot.models import TelegramUpdateOffset


class TestTelegramServicePolling:
    """Test get_telegram_updates() method"""

    @patch('django.db.transaction.atomic')
    @patch('telegram_bot.services.requests.post')
    @patch('telegram_bot.models.TelegramUpdateOffset.objects')
    def test_get_telegram_updates_with_correct_offset(self, mock_objects, mock_post, mock_atomic):
        """Test polling uses stored offset + 1"""
        mock_instance = Mock()
        mock_instance.offset = 99
        mock_objects.select_for_update.return_value.get_or_create.return_value = (mock_instance, False)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": [{"update_id": 100, "message": {"text": "test"}}]
        }
        mock_post.return_value = mock_response

        service = TelegramService()
        updates = service.get_telegram_updates()

        # Verify offset parameter
        call_args = mock_post.call_args
        assert call_args[1]["json"]["offset"] == 100  # 99 + 1
        assert len(updates) == 1

    @patch('django.db.transaction.atomic')
    @patch('telegram_bot.services.requests.post')
    @patch('telegram_bot.models.TelegramUpdateOffset.objects')
    def test_get_telegram_updates_with_timeout(self, mock_objects, mock_post, mock_atomic):
        """Test long polling timeout parameter"""
        mock_instance = Mock()
        mock_instance.offset = 0
        mock_objects.select_for_update.return_value.get_or_create.return_value = (mock_instance, False)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": []}
        mock_post.return_value = mock_response

        service = TelegramService()
        service.get_telegram_updates(timeout=30)

        # Verify timeout in payload and request
        call_args = mock_post.call_args
        assert call_args[1]["json"]["timeout"] == 30
        assert call_args[1]["timeout"] == 35  # 30 + 5 buffer

    @patch('django.db.transaction.atomic')
    @patch('telegram_bot.services.requests.post')
    @patch('telegram_bot.models.TelegramUpdateOffset.objects')
    def test_get_telegram_updates_handles_timeout_exception(self, mock_objects, mock_post, mock_atomic):
        """Test that request timeout returns empty list (normal for long polling)"""
        mock_instance = Mock()
        mock_instance.offset = 0
        mock_objects.select_for_update.return_value.get_or_create.return_value = (mock_instance, False)
        mock_post.side_effect = Exception("Timeout")

        service = TelegramService()
        updates = service.get_telegram_updates()

        assert updates == []

    @patch('django.db.transaction.atomic')
    @patch('telegram_bot.services.requests.post')
    @patch('telegram_bot.models.TelegramUpdateOffset.objects')
    def test_get_telegram_updates_handles_api_error(self, mock_objects, mock_post, mock_atomic):
        """Test API error returns empty list"""
        mock_instance = Mock()
        mock_instance.offset = 0
        mock_objects.select_for_update.return_value.get_or_create.return_value = (mock_instance, False)
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        service = TelegramService()
        updates = service.get_telegram_updates()

        assert updates == []


class TestTelegramServiceInlineKeyboards:
    """Test send_message_with_keyboard() method"""

    @patch('telegram_bot.services.requests.post')
    def test_send_message_with_keyboard_success(self, mock_post):
        """Test sending message with inline keyboard"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {"message_id": 123, "chat": {"id": "chat123"}}
        }
        mock_post.return_value = mock_response

        service = TelegramService()
        keyboard = [[
            {"text": "✅ Confirm", "callback_data": "confirm_123"},
            {"text": "❌ Reject", "callback_data": "reject_123"}
        ]]

        result = service.send_message_with_keyboard(
            chat_id="chat123",
            text="Test message",
            inline_keyboard=keyboard
        )

        # Verify result contains message_id
        assert result is not None
        assert result["message_id"] == 123

        # Verify payload structure
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        assert payload["chat_id"] == "chat123"
        assert payload["text"] == "Test message"
        assert payload["parse_mode"] == "HTML"
        assert payload["reply_markup"]["inline_keyboard"] == keyboard

    @patch('telegram_bot.services.requests.post')
    def test_send_message_with_keyboard_handles_error(self, mock_post):
        """Test error handling returns None"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response

        service = TelegramService()
        result = service.send_message_with_keyboard(
            chat_id="chat123",
            text="Test",
            inline_keyboard=[[{"text": "Button", "callback_data": "data"}]]
        )

        assert result is None


class TestTelegramServiceCallbackQueries:
    """Test answer_callback_query() method"""

    @patch('telegram_bot.services.requests.post')
    def test_answer_callback_query_success(self, mock_post):
        """Test answering callback query removes loading spinner"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        service = TelegramService()
        success = service.answer_callback_query("callback_id_123")

        assert success is True

        # Verify API endpoint
        call_args = mock_post.call_args
        assert "answerCallbackQuery" in call_args[0][0]
        assert call_args[1]["json"]["callback_query_id"] == "callback_id_123"

    @patch('telegram_bot.services.requests.post')
    def test_answer_callback_query_with_text(self, mock_post):
        """Test callback answer with notification text"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        service = TelegramService()
        service.answer_callback_query(
            callback_query_id="callback_id_123",
            text="Đã xác nhận!",
            show_alert=True
        )

        # Verify text and show_alert in payload
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        assert payload["text"] == "Đã xác nhận!"
        assert payload["show_alert"] is True

    @patch('telegram_bot.services.requests.post')
    def test_answer_callback_query_handles_error(self, mock_post):
        """Test error handling returns False"""
        mock_post.side_effect = Exception("Network error")

        service = TelegramService()
        success = service.answer_callback_query("callback_id_123")

        assert success is False


class TestTelegramServiceMessageEditing:
    """Test edit_message_text() method"""

    @patch('telegram_bot.services.requests.post')
    def test_edit_message_text_success(self, mock_post):
        """Test editing message text"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        service = TelegramService()
        success = service.edit_message_text(
            chat_id="chat123",
            message_id="456",
            new_text="Updated text"
        )

        assert success is True

        # Verify payload
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        assert payload["chat_id"] == "chat123"
        assert payload["message_id"] == "456"
        assert payload["text"] == "Updated text"
        assert payload["parse_mode"] == "HTML"

    @patch('telegram_bot.services.requests.post')
    def test_edit_message_text_remove_buttons(self, mock_post):
        """Test removing buttons by passing None"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        service = TelegramService()
        service.edit_message_text(
            chat_id="chat123",
            message_id="456",
            new_text="No buttons",
            reply_markup=None
        )

        # Verify reply_markup is None (removes buttons)
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        assert "reply_markup" not in payload  # None means omit from payload

    @patch('telegram_bot.services.requests.post')
    def test_edit_message_text_handles_deleted_message(self, mock_post):
        """Test non-critical error when message deleted by user"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Message not found"
        mock_post.return_value = mock_response

        service = TelegramService()
        success = service.edit_message_text(
            chat_id="chat123",
            message_id="456",
            new_text="Text"
        )

        # Should return False but not raise exception
        assert success is False


class TestTelegramUpdateOffset:
    """Test TelegramUpdateOffset model methods"""

    @patch('telegram_bot.models.TelegramUpdateOffset.objects')
    def test_get_offset_returns_stored_value(self, mock_objects):
        """Test get_offset() returns stored offset"""
        mock_instance = Mock()
        mock_instance.offset = 42
        mock_objects.get_or_create.return_value = (mock_instance, False)

        offset = TelegramUpdateOffset.get_offset()

        assert offset == 42
        mock_objects.get_or_create.assert_called_once_with(pk=1)

    @patch('telegram_bot.models.TelegramUpdateOffset.objects')
    def test_set_offset_updates_value(self, mock_objects):
        """Test set_offset() updates offset"""
        mock_instance = Mock()
        mock_instance.offset = 0
        mock_objects.get_or_create.return_value = (mock_instance, False)

        result = TelegramUpdateOffset.set_offset(100)

        assert mock_instance.offset == 100
        mock_instance.save.assert_called_once()


class TestSendPhotoUrlWithKeyboard:
    """Test _send_photo_url() with reply_markup parameter"""

    @patch('telegram_bot.services.requests.post')
    def test_send_photo_url_with_keyboard(self, mock_post):
        """Test sending photo with inline keyboard"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        service = TelegramService()
        keyboard = {
            "inline_keyboard": [[{"text": "Button", "callback_data": "data"}]]
        }

        service._send_photo_url(
            chat_id="chat123",
            photo_url="https://example.com/qr.png",
            caption="Test caption",
            reply_markup=keyboard
        )

        # Verify reply_markup in payload
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        assert payload["reply_markup"] == keyboard

    @patch('telegram_bot.services.requests.post')
    def test_send_photo_url_without_keyboard(self, mock_post):
        """Test sending photo without keyboard (backward compatibility)"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        service = TelegramService()
        service._send_photo_url(
            chat_id="chat123",
            photo_url="https://example.com/qr.png",
            caption="Test caption"
        )

        # Verify reply_markup not in payload
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        assert "reply_markup" not in payload
