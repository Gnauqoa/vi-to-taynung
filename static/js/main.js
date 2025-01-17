$(document).ready(function () {
	let currentMode = "vn_to_tn";
	let isSelecting = false; // Cờ xác định người dùng có đang chọn gợi ý hay không

	// Hàm chuyển trang
	// Xử lý sự kiện khi nhấn vào các liên kết trong menu
	$(".nav-link, .menu-link-item").click(function (e) {
		e.preventDefault(); // Ngăn trình duyệt tải lại trang

		// Lấy URL từ href
		let url = $(this).attr("href");

		// Nếu là trang chủ, ta không cần dùng AJAX
		if (url === "/") {
			location.reload(); // Tải lại trang
			return;
		}

		// Nếu không phải trang chủ, tiếp tục xử lý bằng AJAX
		if (url) {
			// Hiển thị trạng thái đang tải
			$("#content").html("<p>Đang tải nội dung...</p>");

			// Tải nội dung bằng AJAX
			$.ajax({
				url: url,
				method: "GET",
				success: function (data) {
					// Chèn nội dung tải được vào khu vực #content
					$("#content").html(data);
				},
				error: function () {
					$("#content").html(
						"<p>Không thể tải nội dung. Vui lòng thử lại sau.</p>"
					);
				},
			});
		}
	});

	$(document).ready(function () {
		// Hàm xử lý chuyển trang khi nhấn mũi tên
		$(".left-arrow, .right-arrow").click(function (e) {
			e.preventDefault(); // Ngăn trình duyệt tải lại trang

			// Lấy URL từ href của mũi tên
			let url = $(this).attr("href");

			if (url) {
				// Hiển thị trạng thái đang tải trong khu vực poem-content
				$(".poem-content").html("<p>Đang tải nội dung...</p>");

				// Tải nội dung bằng AJAX
				$.ajax({
					url: url,
					method: "GET",
					success: function (data) {
						// Lấy nội dung cần thay thế từ dữ liệu trả về
						// let newContent = $(data).find(".poem-content").html();

						// Cập nhật chỉ phần .poem-content
						$(".poem-content").html(data);
					},
					error: function () {
						$(".poem-content").html(
							"<p>Không thể tải nội dung. Vui lòng thử lại sau.</p>"
						);
					},
				});
			}
		});
	});

	// Hàm lấy gợi ý
	function fetchSuggestions(query) {
		if (query.length > 0) {
			$.getJSON(`/suggest?q=${query}&mode=${currentMode}`, function (data) {
				if (data.suggestions && data.suggestions.length > 0) {
					let suggestionHtml = data.suggestions
						.map(
							(suggestion) => `<div class='suggestion-item'>${suggestion}</div>`
						)
						.join("");
					$("#suggestions").html(suggestionHtml).addClass("show");
				} else {
					$("#suggestions").removeClass("show");
				}
			}).fail(function () {
				console.error("Lỗi khi lấy gợi ý từ server.");
				$("#suggestions").removeClass("show");
			});
		} else {
			$("#suggestions").removeClass("show");
		}
	}

	// Xử lý chuyển chế độ dịch
	$("#switch-button").click(function () {
		currentMode = currentMode === "vn_to_tn" ? "tn_to_vn" : "vn_to_tn";
		$("#language-from").text(
			currentMode === "vn_to_tn" ? "Tiếng Việt" : "Tày / Nùng"
		);
		$("#language-to").text(
			currentMode === "vn_to_tn" ? "Tày / Nùng" : "Tiếng Việt"
		);

		// Lấy nội dung hiện tại trong ô nhập
		let currentText = $("#text_input").val().trim();
		if (currentText !== "") {
			fetchSuggestions(currentText); // Cập nhật gợi ý
		} else {
			$("#suggestions").removeClass("show");
		}
	});

	// Xử lý nút dịch
	// Xử lý nút dịch
	$("#translate-button").click(function () {
		let text = $("#text_input").val().trim();

		if (text === "") {
			alert("Vui lòng nhập văn bản cần dịch!");
			return;
		}

		$("#result").val("Đang dịch...");

		$.ajax({
			url: "/",
			type: "POST",
			data: { text_input: text, mode: currentMode },
			success: function (response) {
				if (response && response.ket_qua) {
					// Chuyển các ký tự xuống dòng trở lại dạng hiển thị
					$("#result").val(response.ket_qua.replace(/\\n/g, "\n"));
				} else {
					$("#result").val("Không nhận được kết quả từ server.");
				}
			},
			error: function () {
				$("#result").val("Lỗi kết nối đến server. Vui lòng thử lại.");
			},
			timeout: 5000, // Timeout sau 5 giây
		});
	});

	// Xử lý nhập liệu để lấy gợi ý
	$("#text_input").on("input", function () {
		let query = $(this).val().trim();
		fetchSuggestions(query); // Không kiểm tra lỗi nhập liệu nữa
	});

	// Xử lý chọn gợi ý
	$(document).on("mousedown", ".suggestion-item", function () {
		let selectedSuggestion = $(this).text(); // Lấy nội dung gợi ý
		$("#text_input").val(selectedSuggestion); // Gán gợi ý vào ô input
		$("#suggestions").removeClass("show"); // Ẩn gợi ý
		isSelecting = true; // Đánh dấu người dùng đang chọn gợi ý
	});

	// Ẩn gợi ý khi click ra ngoài
	$(document).click(function (e) {
		if (!$(e.target).closest("#text_input, #suggestions").length) {
			$("#suggestions").removeClass("show");
		}
	});

	// Ngăn sự kiện `blur` làm ẩn gợi ý khi chọn gợi ý
	$("#suggestions").on("mousedown", function () {
		isSelecting = true; // Cờ bật khi chọn gợi ý
	});

	$("#text_input").on("blur", function () {
		setTimeout(function () {
			if (!isSelecting) {
				$("#suggestions").removeClass("show");
			}
			isSelecting = false; // Reset cờ
		}, 200); // Delay để đảm bảo chọn gợi ý không bị xung đột
	});
});
