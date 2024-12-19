import unicodedata
import json
import os
from flask import Flask, render_template, request

app = Flask(__name__)

# Đường dẫn tới file từ điển
DEFAULT_DICTIONARY_PATH = os.path.join(os.path.dirname(__file__), 'taydictionary.json')


def chuan_hoa_unicode(text):
    """Chuẩn hóa chuỗi Unicode để đảm bảo đồng nhất."""
    if text:
        return unicodedata.normalize('NFC', text.strip().lower())
    return ""


def tai_tu_dien():
    """Tải từ điển tích hợp sẵn từ file JSON."""
    try:
        if not os.path.exists(DEFAULT_DICTIONARY_PATH):
            return {}, f"File từ điển không tồn tại: {DEFAULT_DICTIONARY_PATH}"
        with open(DEFAULT_DICTIONARY_PATH, 'r', encoding='utf-8') as f:
            return json.load(f), None
    except json.JSONDecodeError:
        return {}, f"File từ điển {DEFAULT_DICTIONARY_PATH} không đúng định dạng JSON."
    except Exception as e:
        return {}, f"Đã xảy ra lỗi khi tải từ điển: {str(e)}"


def dich_cau(cau, tu_dien):
    """
    Dịch cả câu bằng cách ghép từ hoặc cụm từ trong từ điển.
    Nếu từ hoặc cụm từ không tồn tại trong từ điển, giữ nguyên từ gốc.
    """
    cau_chuan = chuan_hoa_unicode(cau)  # Chuẩn hóa câu
    tu_da_dich = []
    tu_tieng_viet = cau_chuan.split()  # Tách câu thành danh sách từ

    i = 0
    while i < len(tu_tieng_viet):
        da_dich = False
        # Kiểm tra cụm từ từ dài nhất xuống ngắn nhất
        for j in range(len(tu_tieng_viet), i, -1):
            cum_tu = " ".join(tu_tieng_viet[i:j])  # Ghép các từ thành cụm
            if cum_tu in tu_dien:
                tu_da_dich.append(tu_dien[cum_tu])  # Dịch cụm từ
                i = j  # Bỏ qua các từ trong cụm đã dịch
                da_dich = True
                break
        if not da_dich:
            # Nếu không có cụm từ, kiểm tra từ lẻ
            tu_dich = tu_dien.get(tu_tieng_viet[i], tu_tieng_viet[i])  # Dịch từ lẻ
            tu_da_dich.append(tu_dich)
            i += 1

    return " ".join(tu_da_dich)  # Ghép kết quả thành câu


@app.route('/', methods=['GET', 'POST'])
def index():
    ket_qua = ""
    cau_goc = ""
    if request.method == 'POST':
        cau_goc = request.form.get('text_input', '').strip()
        tu_dien, error_msg = tai_tu_dien()

        if error_msg:
            ket_qua = error_msg
        elif not cau_goc:
            ket_qua = "Vui lòng nhập văn bản cần dịch."
        else:
            ket_qua = dich_cau(cau_goc, tu_dien)

    return render_template('index.html', cau_goc=cau_goc, ket_qua=ket_qua)


if __name__ == '__main__':
    if not os.path.exists(DEFAULT_DICTIONARY_PATH):
        print(f"File từ điển không tồn tại: {DEFAULT_DICTIONARY_PATH}. Vui lòng kiểm tra lại.")
    else:
        print(f"Sử dụng file từ điển: {DEFAULT_DICTIONARY_PATH}")
    app.run(debug=True)
