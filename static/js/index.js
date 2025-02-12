document.addEventListener('DOMContentLoaded', () => {
    // カテゴリーボタンのクリックイベント処理
    document.querySelectorAll('.category-btn').forEach(button => {
        button.addEventListener('click', function () {
            const categoryId = this.getAttribute('data-category');
            console.log(`選択されたカテゴリーID: ${categoryId}`);

            // 選択状態を確認して切り替え処理
            if (this.classList.contains('selected')) {
                console.log("カテゴリー選択が解除されました。すべての領収書を表示します。");
                this.classList.remove('selected');
                fetchReceipts('/get_receipts/all');  // 全領収書を取得
            } else {
                console.log(`カテゴリー ${categoryId} が選択されました。`);
                
                // すべてのボタンの選択状態をリセット
                document.querySelectorAll('.category-btn').forEach(btn => btn.classList.remove('selected'));

                // 現在のボタンを選択状態に設定
                this.classList.add('selected');
                fetchReceipts(`/get_receipts/${categoryId}`);  // 選択カテゴリーの領収書を取得
            }
        });
    });

    // キーワード検索処理
    document.getElementById('search-form').addEventListener('submit', function (e) {
        e.preventDefault();
        const keyword = document.getElementById('keyword').value;
        console.log("検索キーワード:", keyword);
        fetchReceipts(`/get_receipts_by_keyword?keyword=${encodeURIComponent(keyword)}`);
    });
});

// データを取得して領収書を画面に表示する関数
function fetchReceipts(url) {
    fetch(url)
        .then(response => response.json())
        .then(receipts => {
            console.log("取得したデータ:", receipts);
            displayReceipts(receipts);
        })
        .catch(error => console.error("データ取得中にエラーが発生しました:", error));
}

// 領収書を画面に描画する汎用関数
function displayReceipts(receipts) {
    const receiptContainer = document.querySelector('.main_receipt');
    receiptContainer.innerHTML = '';

    if (receipts.length === 0) {
        receiptContainer.innerHTML = '<p>該当する領収書がありません。</p>';
        return;
    }

    receipts.forEach(receipt => {
        const gridItem = document.createElement('div');
        gridItem.classList.add('grid-item');
        gridItem.innerHTML = `<img src="${receipt.image_path}" alt="領収書画像" class="receipt_image" onclick="openModal('${receipt.image_path}')">`;
        receiptContainer.appendChild(gridItem);
    });
}

// モーダルウィンドウの処理
function openModal(imagePath) {
    const modal = document.getElementById("imageModal");
    const modalImage = document.getElementById("modalImage");
    modal.style.display = "block";
    modalImage.src = imagePath;
}

function closeModal() {
    const modal = document.getElementById("imageModal");
    modal.style.display = "none";
}



//日付検索
document.querySelector('.date_box').addEventListener('submit', function (e) {
    e.preventDefault();

    const startDate = document.querySelector('input[name="start_date"]').value;
    const endDate = document.querySelector('input[name="end_date"]').value;

    console.log(`選択された日付範囲: ${startDate} ～ ${endDate}`);

    // 日付の順序を確認
    if (new Date(startDate) > new Date(endDate)) {
        alert('開始日は終了日より前の日付にしてください。');
        return;
    }

    if (!startDate || !endDate) {
        alert('開始日と終了日を両方入力してください。');
        return;
    }

    fetch(`/get_receipts_by_date?start_date=${encodeURIComponent(startDate)}&end_date=${encodeURIComponent(endDate)}`)
        .then(response => response.json())
        .then(receipts => {
            console.log("取得したデータ:", receipts);
            displayReceipts(receipts);  // 領収書を表示する関数を呼び出す
        })
        .catch(error => console.error("データ取得中にエラーが発生しました:", error));
});

