from flask import Flask, render_template, request, jsonify, send_from_directory, abort
import os
import json
import unicodedata

app = Flask(__name__)

# Đường dẫn file từ điển
DEFAULT_DICTIONARY_PATH_VN_TN = os.path.join(os.path.dirname(__file__), 'taydictionary.json')
DEFAULT_DICTIONARY_PATH_TN_VN = os.path.join(os.path.dirname(__file__), 'vietdictionary.json')

# Thư mục chứa các file nội dung HTML
CONTENT_FOLDER = os.path.join(os.path.dirname(__file__), 'content')

# Hàm chuẩn hóa chuỗi Unicode
def chuan_hoa_unicode(text):
    """Chuẩn hóa chuỗi Unicode."""
    return unicodedata.normalize('NFC', text.strip().lower()) if text else ""

# Hàm tải từ điển
def tai_tu_dien(path):
    """Tải từ điển."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f), None
    except FileNotFoundError:
        return {}, f"Lỗi: File '{path}' không tìm thấy."
    except json.JSONDecodeError:
        return {}, f"Lỗi: Dữ liệu trong file '{path}' không hợp lệ."

# Hàm dịch câu
def dich_cau(cau, tu_dien):
    """Dịch câu, giữ nguyên các ký tự xuống dòng."""
    # Chia câu thành các dòng dựa trên ký tự xuống dòng
    cau_theo_dong = cau.split("\n")
    dong_da_dich = []

    for dong in cau_theo_dong:
        cau_chuan = chuan_hoa_unicode(dong)
        tu_da_dich = []
        tu_list = cau_chuan.split()  # Tách từ trong từng dòng

        i = 0
        while i < len(tu_list):
            for j in range(len(tu_list), i, -1):
                cum_tu = " ".join(tu_list[i:j])  # Lấy cụm từ từ i đến j
                tu_dich = tu_dien.get(cum_tu)
                if tu_dich:
                    tu_da_dich.append(tu_dich[0] if isinstance(tu_dich, list) else tu_dich)
                    i = j
                    break
            else:
                tu_dich = tu_dien.get(tu_list[i], tu_list[i])  # Dịch từ đơn
                tu_da_dich.append(tu_dich[0] if isinstance(tu_dich, list) else tu_dich)
                i += 1

        # Ghép từ đã dịch trong dòng
        dong_da_dich.append(" ".join(tu_da_dich))

    # Ghép các dòng lại, giữ nguyên xuống dòng
    return "\n".join(dong_da_dich)

# Route chính
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        cau_goc = request.form.get('text_input', '').strip()
        mode = request.form.get('mode', 'vn_to_tn')

        if not cau_goc:
            return jsonify({"ket_qua": "Vui lòng nhập văn bản cần dịch."})

        # Tải từ điển theo chế độ dịch
        dictionary_path = (
            DEFAULT_DICTIONARY_PATH_TN_VN if mode == 'tn_to_vn' else DEFAULT_DICTIONARY_PATH_VN_TN
        )
        tu_dien, error_msg = tai_tu_dien(dictionary_path)

        if error_msg:
            return jsonify({"ket_qua": error_msg})

        # Dịch câu
        ket_qua = dich_cau(cau_goc, tu_dien)
        return jsonify({"ket_qua": ket_qua})

    return render_template('index.html')

# Route xử lý gợi ý
@app.route('/suggest', methods=['GET'])
def suggest():
    query = request.args.get('q', '').strip().lower()
    mode = request.args.get('mode', 'vn_to_tn')

    if not query:
        return jsonify({"suggestions": []})

    # Tải từ điển theo chế độ dịch
    dictionary_path = (
        DEFAULT_DICTIONARY_PATH_TN_VN if mode == 'tn_to_vn' else DEFAULT_DICTIONARY_PATH_VN_TN
    )
    tu_dien, error_msg = tai_tu_dien(dictionary_path)

    if error_msg:
        return jsonify({"suggestions": []})

    # Lấy gợi ý bắt đầu với chuỗi `query`
    suggestions = [tu for tu in tu_dien.keys() if tu.startswith(query)]
    return jsonify({"suggestions": suggestions})

# Route xử lý tải nội dung các file HTML
@app.route('/content/<path:filename>', methods=['GET'])
def load_content(filename):
    """Tải nội dung file HTML từ thư mục `content`."""
    filepath = os.path.join(CONTENT_FOLDER, filename)

    if os.path.exists(filepath):
        # Đảm bảo chỉ gửi file HTML
        if filepath.endswith(".html"):
            return send_from_directory(CONTENT_FOLDER, filename)
        else:
            abort(400, "Chỉ hỗ trợ các tệp HTML.")
    else:
        abort(404, "Nội dung không tồn tại.")

if __name__ == '__main__':
    app.run(debug=True)