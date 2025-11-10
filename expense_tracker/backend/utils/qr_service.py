import qrcode
import base64
from io import BytesIO


class QRService:
    # Bank codes theo chuẩn VietQR EMVCo
    BANK_CODES = {
        'TPBank': '970423',
        'Vietcombank': '970436',
        'VCB': '970436',
        'Techcombank': '970407',
        'TCB': '970407',
        'BIDV': '970418',
        'Vietinbank': '970415',
        'VTB': '970415',
        'Agribank': '970405',
        'ACB': '970416',
        'Sacombank': '970403',
        'MB': '970422',
        'MBBank': '970422',
        'VPBank': '970432',
        'SHB': '970443',
        'Eximbank': '970431',
        'SeABank': '970440',
        'VIB': '970441',
        'HDBank': '970437',
    }

    @classmethod
    def create_payment_qr_data(cls, bank_name, account_number, account_name, amount, description):
        """
        Tạo VietQR data theo CHÍNH XÁC format Viblo
        """
        try:
            # Lấy bank code (mặc định TPBank)
            bank_code = cls.BANK_CODES.get(bank_name, '970423')

            # Format amount (số nguyên)
            amount_str = str(int(amount))

            # Clean description - ĐƠN GIẢN như Viblo
            description_clean = cls._clean_description(description)

            # Tạo Merchant Account Information theo CHÍNH XÁC Viblo format
            # Structure: 0010A0000007270123 + 00 + LEN + BANK + 01 + LEN + ACCOUNT + 02 + 08 + QRIBFTTA

            # Service identifier (cố định)
            service_id = "0010A0000007270123"

            # Bank part: 00 + length + bank_code
            bank_part = f"00{len(bank_code):02d}{bank_code}"

            # Account part: 01 + length + account_number
            account_part = f"01{len(account_number):02d}{account_number}"

            # Service part: 02 + 08 + QRIBFTTA
            service_part = "0208QRIBFTTA"

            # Ghép merchant account
            merchant_account = service_id + bank_part + account_part + service_part

            # Additional Data Field: 08 + length + description
            additional_data = f"08{len(description_clean):02d}{description_clean}"

            # Tạo payload theo CHÍNH XÁC format Viblo
            payload = ""
            payload += "000201"  # Payload Format Indicator
            payload += "010212"  # Point of Initiation Method
            payload += f"38{len(merchant_account):02d}{merchant_account}"  # Merchant Account
            payload += "5303704"  # Currency (VND)
            payload += f"54{len(amount_str):02d}{amount_str}"  # Amount
            payload += "5802VN"   # Country Code
            payload += f"62{len(additional_data):02d}{additional_data}"  # Additional Data
            payload += "6304"     # CRC placeholder

            # Tính CRC16
            crc = cls._calculate_crc16(payload)
            payload += crc

            return payload

        except Exception as e:
            print(f"❌ Error creating VietQR: {e}")
            return None

    @classmethod
    def _clean_description(cls, description):
        """Tạo description ĐƠN GIẢN như Viblo"""
        if not description:
            return "CK"

        import re
        # Loại bỏ dấu và ký tự đặc biệt, chỉ giữ chữ số
        cleaned = cls._remove_vietnamese_accents(description.lower())
        cleaned = re.sub(r'[^a-z0-9]', '', cleaned)

        # Giới hạn 4-8 ký tự như "test" trong Viblo
        if len(cleaned) > 8:
            cleaned = cleaned[:8]

        return cleaned or "ck"

    @classmethod
    def _remove_vietnamese_accents(cls, text):
        """Loại bỏ dấu tiếng Việt"""
        vietnamese_map = {
            'à': 'a', 'á': 'a', 'ạ': 'a', 'ả': 'a', 'ã': 'a', 'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ậ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ặ': 'a', 'ẳ': 'a', 'ẵ': 'a',
            'è': 'e', 'é': 'e', 'ẹ': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ê': 'e', 'ề': 'e', 'ế': 'e', 'ệ': 'e', 'ể': 'e', 'ễ': 'e',
            'ì': 'i', 'í': 'i', 'ị': 'i', 'ỉ': 'i', 'ĩ': 'i',
            'ò': 'o', 'ó': 'o', 'ọ': 'o', 'ỏ': 'o', 'õ': 'o', 'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ộ': 'o', 'ổ': 'o', 'ỗ': 'o', 'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ợ': 'o', 'ở': 'o', 'ỡ': 'o',
            'ù': 'u', 'ú': 'u', 'ụ': 'u', 'ủ': 'u', 'ũ': 'u', 'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ự': 'u', 'ử': 'u', 'ữ': 'u',
            'ỳ': 'y', 'ý': 'y', 'ỵ': 'y', 'ỷ': 'y', 'ỹ': 'y',
            'đ': 'd'
        }

        result = ""
        for char in text:
            result += vietnamese_map.get(char, char)
        return result

    @classmethod
    def _calculate_crc16(cls, data):
        """Tính CRC16-CCITT cho VietQR"""
        def crc16_ccitt(data):
            crc = 0xFFFF
            polynomial = 0x1021

            for byte in data.encode('utf-8'):
                crc ^= byte << 8
                for _ in range(8):
                    if crc & 0x8000:
                        crc = (crc << 1) ^ polynomial
                    else:
                        crc <<= 1
                    crc &= 0xFFFF
            return crc

        crc = crc16_ccitt(data)
        return f"{crc:04X}"

    @classmethod
    def create_qr_image_base64(cls, qr_data):
        """Tạo QR code image"""
        try:
            if not qr_data:
                return None

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()

            return f"data:image/png;base64,{img_base64}"

        except Exception as e:
            print(f"❌ Error creating QR image: {e}")
            return None

    @classmethod
    def test_viblo_exact(cls):
        """Test với CHÍNH XÁC data từ Viblo"""
        print("🧪 Testing EXACT Viblo format...")

        result = cls.create_payment_qr_data(
            bank_name="TPBank",
            account_number="mynamebvh",
            account_name="Test User",
            amount=50000,
            description="test"
        )

        print("📋 Generated:")
        print(result)
        print()

        expected = "00020101021238530010A000000727012300069704230109mynamebvh0208QRIBFTTA53037045405500005802VN62080804test6304AB76"
        print("✅ Expected from Viblo:")
        print(expected)
        print()

        # So sánh từng phần
        if result:
            print("🔍 Comparison:")
            print(f"Match: {result == expected}")
            if len(result) == len(expected):
                print("Length matches ✅")
            else:
                print(f"Length differs: {len(result)} vs {len(expected)} ❌")

        return result

    @classmethod
    def debug_structure(cls, bank_name, account_number, account_name, amount, description):
        """Debug cấu trúc từng phần"""
        bank_code = cls.BANK_CODES.get(bank_name, '970423')
        amount_str = str(int(amount))
        description_clean = cls._clean_description(description)

        print(f"🔍 Input Analysis:")
        print(f"Bank: {bank_name} -> Code: {bank_code}")
        print(f"Account: {account_number} (length: {len(account_number)})")
        print(f"Amount: {amount} -> String: {amount_str} (length: {len(amount_str)})")
        print(f"Description: '{description}' -> Clean: '{description_clean}' (length: {len(description_clean)})")
        print()

        # Tạo từng phần
        service_id = "0010A0000007270123"
        bank_part = f"00{len(bank_code):02d}{bank_code}"
        account_part = f"01{len(account_number):02d}{account_number}"
        service_part = "0208QRIBFTTA"
        merchant_account = service_id + bank_part + account_part + service_part
        additional_data = f"08{len(description_clean):02d}{description_clean}"

        print(f"🔧 Structure:")
        print(f"Service ID: {service_id} (length: {len(service_id)})")
        print(f"Bank Part: {bank_part} (length: {len(bank_part)})")
        print(f"Account Part: {account_part} (length: {len(account_part)})")
        print(f"Service Part: {service_part} (length: {len(service_part)})")
        print(f"Merchant Account: {merchant_account} (length: {len(merchant_account)})")
        print(f"Additional Data: {additional_data} (length: {len(additional_data)})")
        print()

        return cls.create_payment_qr_data(bank_name, account_number, account_name, amount, description)

    @classmethod
    def get_supported_banks(cls):
        return list(cls.BANK_CODES.keys())

    @classmethod
    def validate_bank_code(cls, bank_name):
        return bank_name in cls.BANK_CODES
