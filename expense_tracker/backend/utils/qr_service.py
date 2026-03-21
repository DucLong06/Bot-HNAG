import urllib.parse
import re
import io
import qrcode


class QRService:
    # Mapping từ tên ngân hàng trong DB sang mã chuẩn VietQR (BIN/ShortName)
    BANK_MAPPING = {
        'Vietcombank': 'VCB',
        'Techcombank': 'TCB',
        'BIDV': 'BIDV',
        'VietinBank': 'ICB',
        'Agribank': 'VBA',
        'MB Bank': 'MB',
        'ACB': 'ACB',
        'Sacombank': 'STB',
        'Eximbank': 'EIB',
        'SHB': 'SHB',
        'TPBank': 'TPB',
        'VPBank': 'VPB',
        'HDBank': 'HDB',
        'OCB': 'OCB',
        'LienVietPostBank': 'LPB',
        'SeABank': 'SEAB',
        'VIB': 'VIB',
        'MSB': 'MSB',
        'Nam A Bank': 'NAMABANK',
        'Bac A Bank': 'BAB'
    }

    BANK_BINS = {
        'VCB': '970436', 'TCB': '970407', 'BIDV': '970418',
        'ICB': '970415', 'VBA': '970405', 'MB': '970422',
        'ACB': '970416', 'STB': '970403', 'EIB': '970431',
        'SHB': '970443', 'TPB': '970423', 'VPB': '970432',
        'HDB': '970437', 'OCB': '970448', 'LPB': '970449',
        'SEAB': '970440', 'VIB': '970441', 'MSB': '970426',
        'NAMABANK': '970428', 'BAB': '970409'
    }

    @classmethod
    def get_vietqr_url(cls, bank_name, account_number, amount, description, account_name=None):
        """
        [DEPRECATED] Tạo URL Quick Link của VietQR (external service).
        Use generate_qr_image() for local generation instead.
        """
        if not bank_name or not account_number:
            return None

        bank_code = cls.BANK_MAPPING.get(str(bank_name), str(bank_name))
        amount_int = int(amount)
        desc_cleaned = cls._clean_description(description)
        desc_encoded = urllib.parse.quote(desc_cleaned)
        base_url = f"https://img.vietqr.io/image/{bank_code}-{account_number}-compact.png"
        query_params = f"?amount={amount_int}&addInfo={desc_encoded}"

        if account_name:
            acc_name_cleaned = cls._remove_vietnamese_accents(str(account_name))
            acc_name_encoded = urllib.parse.quote(acc_name_cleaned)
            query_params += f"&accountName={acc_name_encoded}"

        return base_url + query_params

    @classmethod
    def generate_qr_image(cls, bank_name, account_number, amount, description, account_name=None):
        """Returns PNG bytes of a locally-generated VietQR EMV QR code."""
        if not bank_name or not account_number:
            return None

        bank_code = cls.BANK_MAPPING.get(str(bank_name), str(bank_name))
        bank_bin = cls.BANK_BINS.get(bank_code)
        if not bank_bin:
            return None

        clean_desc = cls._clean_description(description)
        payload = cls._build_emv_payload(bank_bin, account_number, amount, clean_desc)

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4
        )
        qr.add_data(payload)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer.getvalue()

    @classmethod
    def _build_emv_payload(cls, bank_bin, account_number, amount, description):
        member_info = cls._tlv('00', bank_bin) + cls._tlv('01', account_number)
        consumer_info = (
            cls._tlv('00', 'A000000727') +
            cls._tlv('01', member_info) +
            cls._tlv('02', 'QRIBFTTA')
        )

        payload = ''
        payload += cls._tlv('00', '01')
        payload += cls._tlv('01', '12')
        payload += cls._tlv('38', consumer_info)
        payload += cls._tlv('53', '704')
        if amount and int(amount) > 0:
            payload += cls._tlv('54', str(int(amount)))
        payload += cls._tlv('58', 'VN')
        if description:
            payload += cls._tlv('62', cls._tlv('08', description[:25]))
        payload += '6304'
        payload += cls._crc16_ccitt(payload)
        return payload

    @staticmethod
    def _tlv(tag: str, value: str) -> str:
        return f"{tag}{len(value):02d}{value}"

    @staticmethod
    def _crc16_ccitt(data: str) -> str:
        """CRC-CCITT (0xFFFF) checksum"""
        crc = 0xFFFF
        for byte in data.encode('utf-8'):
            crc ^= byte << 8
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ 0x1021
                else:
                    crc <<= 1
                crc &= 0xFFFF
        return format(crc, '04X')

    @classmethod
    def _clean_description(cls, description):
        """Làm sạch nội dung chuyển khoản (bỏ dấu, giới hạn ký tự)"""
        text = str(description)
        if not text:
            return ""
        cleaned = cls._remove_vietnamese_accents(text)
        return cleaned[:50]

    @classmethod
    def _remove_vietnamese_accents(cls, text):
        """
        Loại bỏ dấu tiếng Việt an toàn bằng phương thức replace.
        FIX: Sử dụng string.replace thay vì vòng lặp dựa trên index.
        """
        text = str(text)
        if not text:
            return ""

        text = text.lower()

        patterns = {
            '[àáạảãâầấậẩẫăằắặẳẵ]': 'a',
            '[èéẹẻẽêềếệểễ]': 'e',
            '[ìíịỉĩ]': 'i',
            '[òóọỏõôồốộổỗơờớợởỡ]': 'o',
            '[ùúụủũưừứựửữ]': 'u',
            '[ỳýỵỷỹ]': 'y',
            'đ': 'd'
        }

        result = text
        for pattern, replacement in patterns.items():
            result = re.sub(pattern, replacement, result)

        result = re.sub(r'[^a-z0-9\s]', '', result)
        result = re.sub(r'\s+', ' ', result).strip()

        return result.title()
