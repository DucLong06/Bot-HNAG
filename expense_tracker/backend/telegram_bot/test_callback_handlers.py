"""
Unit tests for Phase 02: Payment Callback Handlers
Tests callback routing, initiation, confirmation, and rejection workflows.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal
from django.utils import timezone
from telegram_bot.callback_handlers import PaymentCallbackHandler
from telegram_bot.models import PaymentConfirmation
from members.models import Member
from expenses.models import Expense, ExpenseParticipant


@pytest.mark.django_db
class TestPaymentCallbackHandler:
    """Test callback handler routing and error handling"""

    @pytest.fixture
    def setup_members(self):
        """Create test members with expenses"""
        debtor = Member.objects.create(
            name="Alice",
            telegram_id="111111"
        )
        lender = Member.objects.create(
            name="Bob",
            telegram_id="222222"
        )
        expense = Expense.objects.create(
            payer=lender,
            amount=Decimal('100.00'),
            name="Test Expense"
        )
        participant = ExpenseParticipant.objects.create(
            member=debtor,
            expense=expense,
            amount_owed=Decimal('50.00'),
            is_paid=False
        )
        return debtor, lender, participant

    @patch('telegram_bot.callback_handlers.TelegramService')
    def test_handle_callback_answers_immediately(self, mock_service_class, setup_members):
        """Test answerCallbackQuery called first to remove spinner"""
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        callback_query = {
            "id": "cb123",
            "data": "unknown_action",
            "from": {"id": 111111},
            "message": {"chat": {"id": "111111"}}
        }

        handler = PaymentCallbackHandler()
        handler.handle_callback_query(callback_query)

        # Verify answer_callback_query called first
        mock_service.answer_callback_query.assert_called_once_with("cb123")

    @patch('telegram_bot.callback_handlers.TelegramService')
    def test_handle_unknown_callback_data(self, mock_service_class):
        """Test unknown callback_data returns False"""
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        callback_query = {
            "id": "cb123",
            "data": "unknown_action:123",
            "from": {"id": 111111},
            "message": {"chat": {"id": "111111"}}
        }

        handler = PaymentCallbackHandler()
        result = handler.handle_callback_query(callback_query)

        assert result is False


@pytest.mark.django_db
class TestInitiatePayment:
    """Test payment initiation logic"""

    @pytest.fixture
    def setup_members(self):
        """Create test members with expenses"""
        debtor = Member.objects.create(
            name="Alice",
            telegram_id="111111"
        )
        lender = Member.objects.create(
            name="Bob",
            telegram_id="222222"
        )
        expense = Expense.objects.create(
            payer=lender,
            amount=Decimal('100.00'),
            name="Test Expense"
        )
        participant = ExpenseParticipant.objects.create(
            member=debtor,
            expense=expense,
            amount_owed=Decimal('50.00'),
            is_paid=False
        )
        return debtor, lender, participant

    @patch('telegram_bot.callback_handlers.TelegramService')
    def test_initiate_payment_creates_confirmation(self, mock_service_class, setup_members):
        """Test initiation creates PaymentConfirmation with correct data"""
        debtor, lender, participant = setup_members
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.send_message_with_keyboard.return_value = {"message_id": 999}

        callback_query = {
            "id": "cb123",
            "data": f"initiate_payment:{debtor.id}:{lender.id}",
            "from": {"id": int(debtor.telegram_id)},
            "message": {"chat": {"id": "111111"}}
        }

        handler = PaymentCallbackHandler()
        result = handler.handle_callback_query(callback_query)

        assert result is True

        # Verify PaymentConfirmation created
        confirmation = PaymentConfirmation.objects.get(debtor=debtor, lender=lender)
        assert confirmation.status == 'pending'
        assert confirmation.total_amount == Decimal('50.00')
        assert confirmation.initiated_by == debtor
        assert confirmation.confirmation_message_id == "999"

    @patch('telegram_bot.callback_handlers.TelegramService')
    def test_duplicate_initiation_prevented(self, mock_service_class, setup_members):
        """Test duplicate pending confirmation rejected"""
        debtor, lender, participant = setup_members
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        # Create existing pending confirmation
        PaymentConfirmation.objects.create(
            debtor=debtor,
            lender=lender,
            total_amount=Decimal('50.00'),
            initiated_by=debtor,
            status='pending'
        )

        callback_query = {
            "id": "cb124",
            "data": f"initiate_payment:{debtor.id}:{lender.id}",
            "from": {"id": int(debtor.telegram_id)},
            "message": {"chat": {"id": "111111"}}
        }

        handler = PaymentCallbackHandler()
        result = handler.handle_callback_query(callback_query)

        # Verify rejection
        mock_service._send_text_message.assert_called()
        call_args = mock_service._send_text_message.call_args[0][1]
        assert "đã tồn tại" in call_args.lower()

    @patch('telegram_bot.callback_handlers.TelegramService')
    def test_unauthorized_user_cannot_initiate(self, mock_service_class, setup_members):
        """Test random user cannot initiate payment"""
        debtor, lender, participant = setup_members
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        attacker_id = "999999"

        callback_query = {
            "id": "cb_attack",
            "data": f"initiate_payment:{debtor.id}:{lender.id}",
            "from": {"id": int(attacker_id)},
            "message": {"chat": {"id": attacker_id}}
        }

        handler = PaymentCallbackHandler()
        result = handler.handle_callback_query(callback_query)

        assert result is False
        mock_service._send_text_message.assert_called()
        call_args = mock_service._send_text_message.call_args[0][1]
        assert "không có quyền" in call_args.lower()

    @patch('telegram_bot.callback_handlers.TelegramService')
    def test_initiate_with_no_unpaid_expenses(self, mock_service_class, setup_members):
        """Test initiation fails when no unpaid expenses"""
        debtor, lender, participant = setup_members
        # Mark all expenses as paid
        participant.is_paid = True
        participant.save()

        mock_service = Mock()
        mock_service_class.return_value = mock_service

        callback_query = {
            "id": "cb_no_debt",
            "data": f"initiate_payment:{debtor.id}:{lender.id}",
            "from": {"id": int(debtor.telegram_id)},
            "message": {"chat": {"id": "111111"}}
        }

        handler = PaymentCallbackHandler()
        result = handler.handle_callback_query(callback_query)

        # Verify no confirmation created
        assert not PaymentConfirmation.objects.exists()
        mock_service._send_text_message.assert_called()
        call_args = mock_service._send_text_message.call_args[0][1]
        assert "không có khoản nợ" in call_args.lower()


@pytest.mark.django_db
class TestConfirmPayment:
    """Test payment confirmation logic"""

    @pytest.fixture
    def setup_confirmation(self):
        """Create test confirmation"""
        debtor = Member.objects.create(
            name="Alice",
            telegram_id="111111"
        )
        lender = Member.objects.create(
            name="Bob",
            telegram_id="222222"
        )
        expense = Expense.objects.create(
            payer=lender,
            amount=Decimal('100.00'),
            name="Test Expense"
        )
        participant = ExpenseParticipant.objects.create(
            member=debtor,
            expense=expense,
            amount_owed=Decimal('50.00'),
            is_paid=False
        )
        confirmation = PaymentConfirmation.objects.create(
            debtor=debtor,
            lender=lender,
            total_amount=Decimal('50.00'),
            initiated_by=debtor,
            status='pending'
        )
        confirmation.expense_participants.add(participant)
        return debtor, lender, participant, confirmation

    @patch('telegram_bot.callback_handlers.TelegramService')
    def test_confirm_payment_marks_expenses_paid(self, mock_service_class, setup_confirmation):
        """Test confirmation updates ExpenseParticipants"""
        debtor, lender, participant, confirmation = setup_confirmation
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        callback_query = {
            "id": "cb126",
            "data": f"confirm_payment:{confirmation.id}",
            "from": {"id": int(lender.telegram_id)},
            "message": {"chat": {"id": "222222"}}
        }

        handler = PaymentCallbackHandler()
        result = handler.handle_callback_query(callback_query)

        assert result is True

        # Verify database updates
        participant.refresh_from_db()
        assert participant.is_paid is True

        confirmation.refresh_from_db()
        assert confirmation.status == 'confirmed'
        assert confirmation.confirmed_at is not None

    @patch('telegram_bot.callback_handlers.TelegramService')
    def test_only_counterparty_can_confirm(self, mock_service_class, setup_confirmation):
        """Test unauthorized user cannot confirm"""
        debtor, lender, participant, confirmation = setup_confirmation
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        # Debtor tries to confirm (should be lender)
        callback_query = {
            "id": "cb125",
            "data": f"confirm_payment:{confirmation.id}",
            "from": {"id": int(debtor.telegram_id)},
            "message": {"chat": {"id": "111111"}}
        }

        handler = PaymentCallbackHandler()
        result = handler.handle_callback_query(callback_query)

        assert result is False
        mock_service._send_text_message.assert_called()
        call_args = mock_service._send_text_message.call_args[0][1]
        assert "không có quyền" in call_args.lower()


@pytest.mark.django_db
class TestRejectPayment:
    """Test payment rejection logic"""

    @pytest.fixture
    def setup_confirmation(self):
        """Create test confirmation"""
        debtor = Member.objects.create(
            name="Alice",
            telegram_id="111111"
        )
        lender = Member.objects.create(
            name="Bob",
            telegram_id="222222"
        )
        confirmation = PaymentConfirmation.objects.create(
            debtor=debtor,
            lender=lender,
            total_amount=Decimal('50.00'),
            initiated_by=debtor,
            status='pending',
            confirmation_message_id="999"
        )
        return debtor, lender, confirmation

    @patch('telegram_bot.callback_handlers.TelegramService')
    def test_reject_payment_notifies_initiator(self, mock_service_class, setup_confirmation):
        """Test rejection sends notification to initiator"""
        debtor, lender, confirmation = setup_confirmation
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        callback_query = {
            "id": "cb127",
            "data": f"reject_payment:{confirmation.id}",
            "from": {"id": int(lender.telegram_id)},
            "message": {"chat": {"id": "222222"}}
        }

        handler = PaymentCallbackHandler()
        result = handler.handle_callback_query(callback_query)

        assert result is True

        confirmation.refresh_from_db()
        assert confirmation.status == 'rejected'

        # Verify initiator notified
        assert mock_service._send_text_message.call_count >= 1
