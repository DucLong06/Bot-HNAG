import urllib.parse
import re


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

    @classmethod
    def get_vietqr_url(cls, bank_name, account_number, amount, description, account_name=None):
        """
        Tạo URL Quick Link của VietQR
        """
        if not bank_name or not account_number:
            return None

        # Ép kiểu an toàn cho bank_name
        bank_code = cls.BANK_MAPPING.get(str(bank_name), str(bank_name))

        amount_int = int(amount)

        # Làm sạch và Encode URL các tham số
        desc_cleaned = cls._clean_description(description)
        desc_encoded = urllib.parse.quote(desc_cleaned)

        base_url = f"https://img.vietqr.io/image/{bank_code}-{account_number}-compact.png"

        query_params = f"?amount={amount_int}&addInfo={desc_encoded}"

        if account_name:
            # Ép kiểu an toàn cho account_name
            acc_name_cleaned = cls._remove_vietnamese_accents(str(account_name))
            acc_name_encoded = urllib.parse.quote(acc_name_cleaned)
            query_params += f"&accountName={acc_name_encoded}"

        return base_url + query_params

    @classmethod
    def _clean_description(cls, description):
        """Làm sạch nội dung chuyển khoản (bỏ dấu, giới hạn ký tự)"""
        # ÉP KIỂU AN TOÀN VÀ KIỂM TRA ĐẦU VÀO
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
        # ÉP KIỂU AN TOÀN TỪ ĐẦU
        text = str(text)
        if not text:
            return ""

        text = text.lower()

        # Danh sách các ký tự có dấu (đã được rút gọn)
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

        # Xóa ký tự đặc biệt, chỉ giữ lại chữ, số và khoảng trắng
        result = re.sub(r'[^a-z0-9\s]', '', result)
        # Loại bỏ khoảng trắng thừa
        result = re.sub(r'\s+', ' ', result).strip()

        return result.title()
