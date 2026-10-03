import json
from pathlib import Path

# 1. Thư mục đích
data_dir = Path("data")
hospital_dir = data_dir / "hospital_e"
medical_dir = data_dir / "medical"
hospital_dir.mkdir(parents=True, exist_ok=True)
medical_dir.mkdir(parents=True, exist_ok=True)

# 2. Xây dựng data/hospital_e/departments.json
departments_data = [
    {
        "id": "tt-tim-mach",
        "name": "Trung tâm Tim mạch",
        "category": "center",
        "location": "Nhà I (Tòa nhà Trung tâm Tim mạch 9 tầng)",
        "lead": "GS.TS Lê Ngọc Thành (Chủ tịch Hội Tim mạch Lồng ngực VN, Cố vấn cao cấp) / TS.BS Nguyễn Công Hựu",
        "services": [
            "Khoa Phẫu thuật Tim mạch và Lồng ngực",
            "Khoa Nội Tim mạch người lớn",
            "Khoa Can thiệp Tim mạch",
            "Khoa Hồi sức và Gây mê Tim mạch",
        ],
        "keywords": [
            "tim",
            "ngực",
            "đau tim",
            "khó thở",
            "huyết áp",
            "van tim",
            "mạch vành",
            "động mạch",
            "suy tim",
            "nong mạch",
            "stent",
            "phù chân",
        ],
        "description": "Trung tâm tim mạch hàng đầu miền Bắc, thực hiện phẫu thuật tim hở, mổ nội soi ít xâm lấn, can thiệp mạch vành, điều trị suy tim và tăng huyết áp phức tạp.",
    },
    {
        "id": "tt-tieu-hoa",
        "name": "Trung tâm Tiêu hóa",
        "category": "center",
        "location": "Nhà F & Nhà E",
        "lead": "GS.TS Mai Hồng Bàng (Cố vấn chuyên môn)",
        "services": ["Khoa Nội Tiêu hóa - Gan mật", "Khoa Phẫu thuật Tiêu hóa", "Đơn vị Nội soi Tiêu hóa can thiệp"],
        "keywords": [
            "dạ dày",
            "tiêu hóa",
            "đại tràng",
            "gan",
            "mật",
            "tụy",
            "nôn",
            "ợ chua",
            "ợ nóng",
            "trào ngược",
            "đi ngoài",
            "táo bón",
            "loét",
            "nội soi",
        ],
        "description": "Chẩn đoán và điều trị bệnh lý ống tiêu hóa, gan mật tụy, nội soi phóng đại nhuộm màu tầm soát ung thư sớm, cắt polyp dạ dày - đại tràng qua nội soi không đau.",
    },
    {
        "id": "tt-co-xuong-khop",
        "name": "Trung tâm Cơ Xương Khớp",
        "category": "center",
        "location": "Tầng 2 - Nhà F & Nhà C",
        "lead": "Chuyên gia Cơ Xương Khớp Bệnh viện E",
        "services": ["Khoa Nội Cơ Xương Khớp", "Khoa Chấn thương Chỉnh hình", "Khoa Phục hồi Chức năng"],
        "keywords": [
            "khớp",
            "xương",
            "gout",
            "gút",
            "thoái hóa",
            "cột sống",
            "đau lưng",
            "thoát vị",
            "gãy xương",
            "viêm khớp",
            "cơ",
            "khớp gối",
            "axit uric",
        ],
        "description": "Điều trị chuyên sâu viêm khớp dạng thấp, thoái hóa khớp, loãng xương, tiêm huyết tương giàu tiểu cầu (PRP) khớp gối, phẫu thuật thay khớp háng, khớp gối nhân tạo.",
    },
    {
        "id": "khoa-cap-cuu",
        "name": "Khoa Cấp cứu 24/7",
        "category": "emergency",
        "location": "Tầng 1 - Nhà C (Ngay cổng chính 89 Trần Cung)",
        "hotline": "1900 1548 / 024.3754.3650",
        "services": [
            "Cấp cứu hồi sức ban đầu",
            "Phân loại người bệnh khẩn cấp ESI",
            "Vận chuyển cấp cứu ngoại viện 24/24",
        ],
        "keywords": [
            "cấp cứu",
            "khẩn cấp",
            "bất tỉnh",
            "tai nạn",
            "ngất",
            "hôn mê",
            "co giật",
            "khó thở dữ dội",
            "ngộ độc",
            "mất ý thức",
            "đột quỵ",
            "115",
        ],
        "description": "Tiếp nhận cấp cứu 24/24 giờ tất cả các ngày trong tuần. Người bệnh vào cấp cứu được thăm khám xử trí ngay lập tức, không phải chờ làm thủ tục tài chính.",
    },
    {
        "id": "khoa-kham-benh",
        "name": "Khoa Khám bệnh (Khám BHYT thông thường)",
        "category": "outpatient",
        "location": "Tầng 1 & Tầng 2 - Nhà E",
        "services": [
            "Cửa 2: Tiếp nhận người ưu tiên (người già > 75t, trẻ < 2t, phụ nữ mang thai, người khuyết tật)",
            "Cửa 3, 4, 5, 6: Đăng ký khám BHYT mới và chuyển tuyến",
            "Cửa 15, 19: Thu ngân thanh toán",
            "Cửa 25, 26: Lĩnh thuốc BHYT",
            "Các phòng khám chuyên khoa Nội, Ngoại, Sản, Nhi, Mắt, Tai Mũi Họng, Răng Hàm Mặt",
        ],
        "keywords": ["khám bhyt", "bảo hiểm", "lấy số", "tiếp nhận", "đăng ký khám", "lĩnh thuốc", "nhà e"],
        "description": "Khoa phụ trách khám ngoại trú BHYT ban đầu và theo dõi bệnh lý mạn tính.",
    },
    {
        "id": "khoa-kham-yeu-cau",
        "name": "Khoa Khám chữa bệnh theo Yêu cầu & Quốc tế",
        "category": "vip",
        "location": "Tầng 2 - Nhà E & Tầng 1 - Nhà H",
        "services": [
            "Khám GS, PGS, Tiến sĩ đầu ngành",
            "Khu vực tiếp đón riêng cửa 10, 11 Nhà E hoặc Quầy F114",
            "Hỗ trợ đưa đón làm cận lâm sàng nhanh",
            "Thanh toán QR code động tại bàn khám",
            "Nhà thuốc dịch vụ cung ứng thuốc theo đơn nhanh",
        ],
        "keywords": ["khám yêu cầu", "khám vip", "chuyên gia", "giáo sư", "tiến sĩ", "nhanh", "dịch vụ", "đặt lịch"],
        "description": "Dịch vụ khám chất lượng cao với bác sĩ theo yêu cầu, thời gian chờ tối thiểu, không gian tiện nghi.",
    },
    {
        "id": "khoa-chan-doan-hinh-anh",
        "name": "Khoa Chẩn đoán Hình ảnh & Thăm dò Chức năng",
        "category": "paraclinical",
        "location": "Tầng 1 Nhà F & Tầng 1 Nhà I",
        "services": [
            "Chụp cắt lớp vi tính CT đa dãy (128 - 256 lát cắt)",
            "Chụp cộng hưởng từ MRI 1.5 Tesla",
            "Siêu âm Doppler màu tim, mạch máu, ổ bụng",
            "X-quang kỹ thuật số (DR)",
            "Điện tâm đồ (ECG), Holter điện tâm đồ & huyết áp 24h",
        ],
        "keywords": ["chụp phim", "x-quang", "ct", "mri", "cộng hưởng từ", "siêu âm", "điện tim", "ecg"],
        "description": "Hệ thống trang thiết bị hiện đại bậc nhất đáp ứng chuẩn xác kết quả cận lâm sàng.",
    },
]

with open(hospital_dir / "departments.json", "w", encoding="utf-8") as f:
    json.dump(departments_data, f, ensure_ascii=False, indent=2)

# 3. Xây dựng data/hospital_e/workflows.json
workflows_data = {
    "bhyt": {
        "name": "Quy trình khám bệnh có thẻ Bảo hiểm Y tế (BHYT)",
        "location": "Tầng 1 - Nhà E",
        "steps": [
            {
                "step_number": 1,
                "title": "Hướng dẫn - Tiếp nhận - Đăng ký khám",
                "detail": "Người bệnh lấy số thứ tự tại CÂY PHÁT SỐ tự động. Xuất trình Thẻ BHYT / Ứng dụng VNeID / VssID + CCCD gắn chip (bản chính) tại CỬA 3, 4, 5, 6. (Ưu tiên người già > 75t, trẻ em < 2t, phụ nữ có thai tại CỬA 2). Nhận Phiếu hướng dẫn có số thứ tự và phòng khám.",
                "location": "Tầng 1 - Nhà E",
            },
            {
                "step_number": 2,
                "title": "Khám tại Phòng khám Chuyên khoa",
                "detail": "Di chuyển đến phòng khám ghi trên phiếu, chờ gọi số vào khám. Bác sĩ thăm khám lâm sàng, nếu không có chỉ định cận lâm sàng thì kê đơn và chuyển thẳng sang Bước 5.",
                "location": "Theo chỉ dẫn trên phiếu khám",
            },
            {
                "step_number": 3,
                "title": "Thực hiện Cận lâm sàng (nếu có chỉ định)",
                "detail": "Di chuyển đến phòng xét nghiệm, chẩn đoán hình ảnh (Nhà F hoặc Nhà I). Sau khi có đủ kết quả, quay trở lại phòng khám ban đầu.",
                "location": "Nhà F (Xét nghiệm / X-quang), Nhà I (Tim mạch / MRI)",
            },
            {
                "step_number": 4,
                "title": "Bác sĩ kết luận & Kê đơn thuốc",
                "detail": "Bác sĩ đọc kết quả xét nghiệm, chẩn đoán xác định, giải thích tình trạng bệnh, kê đơn thuốc điện tử hoặc tư vấn nhập viện.",
                "location": "Phòng khám ban đầu",
            },
            {
                "step_number": 5,
                "title": "Thanh toán & Lĩnh thuốc BHYT",
                "detail": "Thanh toán viện phí qua mã QR động ngay tại phòng khám hoặc nộp tại CỬA 15, 19 Nhà E. Lĩnh thuốc BHYT tại CỬA 25, 26 Tầng 1 Nhà E (hoặc Khoa Dược Tầng 1 Nhà F nếu thuốc đặc trị).",
                "location": "Cửa 15, 19 và Cửa 25, 26 Nhà E",
            },
        ],
    },
    "on_demand": {
        "name": "Quy trình khám bệnh theo Yêu cầu & Chuyên gia",
        "location": "Khoa Khám theo yêu cầu - Tầng 2 Nhà E hoặc Quầy F114",
        "steps": [
            {
                "step_number": 1,
                "title": "Đăng ký khám theo yêu cầu",
                "detail": "Đăng ký tại Quầy đón tiếp Cửa 10, 11 Tầng 1 Nhà E hoặc Quầy F114 Tầng 1 Nhà F. Chọn bác sĩ chuyên khoa hoặc Giáo sư, Tiến sĩ theo nguyện vọng. Điều dưỡng đo huyết áp, mạch, nhiệt độ.",
                "location": "Cửa 10, 11 Nhà E hoặc Quầy F114",
            },
            {
                "step_number": 2,
                "title": "Khám chuyên gia",
                "detail": "Được mời vào phòng khám ưu tiên, bác sĩ chuyên gia tư vấn kỹ lưỡng, chỉ định các thăm dò cần thiết.",
                "location": "Tầng 2 - Nhà E",
            },
            {
                "step_number": 3,
                "title": "Cận lâm sàng ưu tiên",
                "detail": "Nhân viên y tế hướng dẫn hoặc đưa đi làm cận lâm sàng theo luồng dịch vụ nhanh.",
                "location": "Khu cận lâm sàng dịch vụ",
            },
            {
                "step_number": 4,
                "title": "Kết luận & Mua thuốc",
                "detail": "Bác sĩ tư vấn phác đồ, kê đơn. Người bệnh nhận thuốc tại Nhà thuốc Bệnh viện hoặc thanh toán nhanh.",
                "location": "Nhà thuốc Bệnh viện E",
            },
        ],
    },
    "emergency": {
        "name": "Quy trình tiếp nhận Cấp cứu 24/7",
        "location": "Tầng 1 - Nhà C",
        "steps": [
            {
                "step_number": 1,
                "title": "Tiếp nhận khẩn cấp tức thì",
                "detail": "Đưa bệnh nhân vào thẳng phòng Hồi sức Cấp cứu Nhà C. Bác sĩ và điều dưỡng cấp cứu đánh giá tri giác, đường thở, tuần hoàn ngay lập tức.",
                "location": "Cửa cấp cứu Nhà C",
            },
            {
                "step_number": 2,
                "title": "Xử trí sinh mạng trước, thủ tục sau",
                "detail": "Mọi can thiệp cứu sống (thở oxy, ép tim, khử rung, đặt nội khí quản, cầm máu, truyền dịch cấp cứu) được ưu tiên số 1.",
                "location": "Khu hồi sức tích cực cấp cứu",
            },
            {
                "step_number": 3,
                "title": "Thủ tục hành chính và BHYT",
                "detail": "Người nhà hỗ trợ làm thủ tục hành chính sau khi người bệnh đã qua cơn nguy kịch.",
                "location": "Bàn tiếp đón cấp cứu Nhà C",
            },
        ],
    },
}

with open(hospital_dir / "workflows.json", "w", encoding="utf-8") as f:
    json.dump(workflows_data, f, ensure_ascii=False, indent=2)

# 4. Xây dựng data/hospital_e/pricing.json
pricing_data = {
    "examination_fees": [
        {
            "type": "Khám Bảo hiểm Y tế (BHYT)",
            "price": 42100,
            "note": "Theo thông tư quy định mức giá dịch vụ khám chữa bệnh BHYT của Bộ Y tế",
        },
        {"type": "Khám thông thường theo yêu cầu", "price": 150000, "note": "Khám dịch vụ không chỉ định bác sĩ"},
        {"type": "Khám Bác sĩ Chuyên khoa I / Thạc sĩ", "price": 250000, "note": "Theo yêu cầu chọn bác sĩ"},
        {"type": "Khám Bác sĩ Chuyên khoa II / Tiến sĩ", "price": 350000, "note": "Theo yêu cầu chuyên gia"},
        {"type": "Khám Giáo sư / Phó Giáo sư", "price": 500000, "note": "Khám chuyên gia đầu ngành theo lịch hẹn"},
    ],
    "health_checkup_packages": [
        {
            "package": "Khám sức khỏe đi làm, đi học",
            "price": 250000,
            "note": "Khám nội, ngoại, da liễu, mắt, tai mũi họng, chụp X-quang tim phổi",
        },
        {
            "package": "Khám sức khỏe lái xe (ô tô, xe máy)",
            "price": 360000,
            "note": "Bao gồm test ma túy 4 chất và nồng độ cồn theo quy định Bộ GTVT",
        },
        {
            "package": "Khám sức khỏe cho người nước ngoài tại VN",
            "price": 1200000,
            "note": "Đủ tiêu chuẩn cấp Work Permit theo Thông tư Bộ Y tế",
        },
    ],
    "common_services": [
        {"service": "Chụp X-quang ngực thẳng kỹ thuật số", "price_bhyt": 70000, "price_ondemand": 120000},
        {"service": "Siêu âm tim màu Doppler", "price_bhyt": 222000, "price_ondemand": 350000},
        {"service": "Siêu âm ổ bụng tổng quát", "price_bhyt": 49000, "price_ondemand": 150000},
        {"service": "Điện tâm đồ (ECG) 12 chuyển đạo", "price_bhyt": 35000, "price_ondemand": 70000},
        {"service": "Nội soi dạ dày gây mê (không đau)", "price_bhyt": 650000, "price_ondemand": 1200000},
        {"service": "Nội soi đại trực tràng toàn bộ gây mê", "price_bhyt": 950000, "price_ondemand": 1800000},
        {"service": "Chụp Cắt lớp vi tính CT lồng ngực / sọ não", "price_bhyt": 520000, "price_ondemand": 950000},
        {"service": "Chụp Cộng hưởng từ MRI cột sống / sọ não 1.5T", "price_bhyt": 1300000, "price_ondemand": 2200000},
    ],
}

with open(hospital_dir / "pricing.json", "w", encoding="utf-8") as f:
    json.dump(pricing_data, f, ensure_ascii=False, indent=2)

# 5. Xây dựng data/medical/drug_interactions.json (Dược thư Quốc gia Việt Nam)
drug_interactions_data = [
    {
        "pair": ["Warfarin", "Aspirin"],
        "severity": "Contraindicated",
        "mechanism": "Cả hai thuốc đều làm giảm khả năng đông máu theo các cơ chế cộng dồn (ức chế tổng hợp yếu tố đông máu phụ thuộc vitamin K và ức chế kết tập tiểu cầu).",
        "clinical_consequence": "Tăng vọt nguy cơ xuất huyết tiêu hóa nặng, xuất huyết nội sọ đe dọa tính mạng.",
        "recommendation": "Tránh phối hợp trừ khi có chỉ định bắt buộc của bác sĩ tim mạch can thiệp (ví dụ bệnh nhân có van tim cơ học đặt stent). Cần theo dõi sát chỉ số INR và hemoglobin.",
    },
    {
        "pair": ["Simvastatin", "Amiodarone"],
        "severity": "High",
        "mechanism": "Amiodarone ức chế mạnh enzym gan CYP3A4, làm giảm chuyển hóa và tích tụ nồng độ Simvastatin trong máu.",
        "clinical_consequence": "Tăng nguy cơ tiêu cơ vân cấp tính (Rhabdomyolysis), tổn thương cơ và suy thận cấp.",
        "recommendation": "Liều Simvastatin không được vượt quá 20mg/ngày khi dùng cùng Amiodarone, hoặc tốt nhất chuyển sang Statin ít chuyển hóa qua CYP3A4 như Rosuvastatin hoặc Pravastatin.",
    },
    {
        "pair": ["Metformin", "Iodinated Contrast"],
        "severity": "High",
        "mechanism": "Thuốc cản quang chứa iod có thể gây suy thận cấp, làm tích tụ nồng độ Metformin trong cơ thể.",
        "clinical_consequence": "Nhiễm toan lactic (Lactic Acidosis) nặng với tỷ lệ tử vong cao.",
        "recommendation": "Bắt buộc tạm ngưng Metformin trước khi chụp CT có thuốc cản quang và chỉ dùng lại sau 48 giờ khi chức năng thận (eGFR) được kiểm tra bình thường.",
    },
    {
        "pair": ["Clopidogrel", "Omeprazole"],
        "severity": "Moderate",
        "mechanism": "Omeprazole ức chế enzyme CYP2C19, enzyme cần thiết để chuyển hóa Clopidogrel thành dạng hoạt động.",
        "clinical_consequence": "Làm giảm hiệu quả chống kết tập tiểu cầu của Clopidogrel, tăng nguy cơ tái tắc mạch vành sau đặt stent.",
        "recommendation": "Thay thế Omeprazole bằng Pantoprazole hoặc Esomeprazole - các PPI ít ức chế CYP2C19 hơn.",
    },
    {
        "pair": ["ACEi", "Spironolactone"],
        "severity": "Moderate",
        "mechanism": "Cả thuốc ức chế men chuyển (Enalapril, Perindopril) và thuốc lợi tiểu giữ kali Spironolactone đều làm giảm thải trừ kali qua thận.",
        "clinical_consequence": "Tăng kali máu (Hyperkalemia) nghiêm trọng, có thể gây ngừng tim hoặc loạn nhịp tim nguy hiểm.",
        "recommendation": "Theo dõi nồng độ Kali máu và Creatinine định kỳ mỗi 1 - 2 tuần sau khi khởi đầu hoặc điều chỉnh liều.",
    },
]

with open(medical_dir / "drug_interactions.json", "w", encoding="utf-8") as f:
    json.dump(drug_interactions_data, f, ensure_ascii=False, indent=2)

# 6. Xây dựng data/medical/red_flags.json
red_flags_data = [
    {
        "category": "Tim mạch & Mạch máu",
        "symptoms": [
            "Đau thắt ngực",
            "Đè nặng ngực",
            "Đau lan lên hàm hoặc cánh tay trái",
            "Khó thở đột ngột kèm vã mồ hôi lạnh",
        ],
        "emergency_condition": "Nghi ngờ Nhồi máu cơ tim cấp / Hội chứng vành cấp",
        "action": "Gọi ngay Cấp cứu 115 hoặc di chuyển khẩn cấp tới Phòng Cấp cứu Nhà C - Bệnh viện E.",
    },
    {
        "category": "Thần kinh & Đột quỵ Não (FAST)",
        "symptoms": [
            "Méo miệng",
            "Lệch mặt",
            "Liệt nửa người",
            "Yếu tay chân",
            "Nói đớ",
            "Nói ngọng",
            "Không nói được",
            "Mất ý thức đột ngột",
        ],
        "emergency_condition": "Dấu hiệu Đột quỵ não cấp (Tai biến mạch máu não) trong giờ vàng",
        "action": "GỌI 115 NGAY. Đặt người bệnh nằm nghiêng an toàn, không cho ăn uống, không chích lể đầu ngón tay.",
    },
    {
        "category": "Hô hấp khẩn cấp",
        "symptoms": [
            "Khó thở dữ dội",
            "Thở rít",
            "Tím tái môi đầu chi",
            "Co kéo cơ hô hấp",
            "Cảm giác nghẹt thở sắp ngất",
        ],
        "emergency_condition": "Suy hô hấp cấp tính / Co thắt phế quản nặng / Dị vật đường thở",
        "action": "Gọi 115, nới rộng quần áo, giữ tư thế nửa nằm nửa ngồi (Fowler), chuẩn bị oxy nếu có.",
    },
    {
        "category": "Phản vệ & Dị ứng",
        "symptoms": [
            "Phù môi",
            "Sưng mắt lưỡi",
            "Nghẹn họng",
            "Mày đay toàn thân khó thở sau khi uống thuốc/tiêm/ăn hải sản",
        ],
        "emergency_condition": "Phản vệ độ 2 - 3 (Anaphylaxis)",
        "action": "Gọi 115 ngay. Nếu có bút tiêm Adrenaline tự động thì tiêm bắp đùi ngay lập tức.",
    },
    {
        "category": "Tiêu hóa & Xuất huyết",
        "symptoms": [
            "Nôn ra máu tươi hoặc máu bầm",
            "Đi ngoài phân đen như bã cà phê kèm chóng mặt tụt huyết áp",
            "Đau bụng dữ dội như dao đâm",
        ],
        "emergency_condition": "Xuất huyết tiêu hóa nặng / Thủng tạng rỗng",
        "action": "Di chuyển ngay tới Bệnh viện, tuyệt đối không ăn uống.",
    },
]

with open(medical_dir / "red_flags.json", "w", encoding="utf-8") as f:
    json.dump(red_flags_data, f, ensure_ascii=False, indent=2)

# 7. Xây dựng data/medical/icd10_common.json
icd10_data = [
    {"code": "I20", "name_vi": "Cơn đau thắt ngực", "specialty": "Trung tâm Tim mạch"},
    {"code": "I21", "name_vi": "Nhồi máu cơ tim cấp", "specialty": "Trung tâm Tim mạch / Cấp cứu"},
    {"code": "I10", "name_vi": "Tăng huyết áp vô căn (nguyên phát)", "specialty": "Trung tâm Tim mạch"},
    {"code": "K29.7", "name_vi": "Viêm dạ dày, không đặc hiệu", "specialty": "Trung tâm Tiêu hóa"},
    {
        "code": "K21.0",
        "name_vi": "Bệnh trào ngược dạ dày - thực quản có viêm thực quản",
        "specialty": "Trung tâm Tiêu hóa",
    },
    {"code": "K25", "name_vi": "Loét dạ dày", "specialty": "Trung tâm Tiêu hóa"},
    {"code": "M17", "name_vi": "Thoái hóa khớp gối", "specialty": "Trung tâm Cơ Xương Khớp"},
    {"code": "M10.0", "name_vi": "Bệnh Gout do vô căn", "specialty": "Trung tâm Cơ Xương Khớp"},
    {"code": "M54.5", "name_vi": "Đau vùng thắt lưng", "specialty": "Trung tâm Cơ Xương Khớp"},
    {
        "code": "E11",
        "name_vi": "Bệnh đái tháo đường không phụ thuộc insulin (Type 2)",
        "specialty": "Khoa Nội tiết - Chuyển hóa",
    },
]

with open(medical_dir / "icd10_common.json", "w", encoding="utf-8") as f:
    json.dump(icd10_data, f, ensure_ascii=False, indent=2)

print("Generated structured datasets successfully in data/hospital_e/ and data/medical/")
