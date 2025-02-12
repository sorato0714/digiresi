//モーダルウィンドウ
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



//Ajax
document.querySelectorAll('.category-btn').forEach(button => {
    button.addEventListener('click', function () {
        const categoryId = this.getAttribute('data-category');

        fetch(`/get_receipts/${categoryId}`)
            .then(response => response.json())
            .then(receipts => {
                const receiptContainer = document.getElementById('receipt-container');
                receiptContainer.innerHTML = ''; // 現在の領収書をクリア

                receipts.forEach(receipt => {
                    const div = document.createElement('div');
                    div.classList.add('grid-item');
                    div.innerHTML = `<img src="${receipt.image_path}" alt="領収書画像" class="receipt_image">`;
                    receiptContainer.appendChild(div);
                });
            })
            .catch(error => {
                console.error('データ取得中にエラーが発生しました:', error);
            });
    });
});



//キーワード検索
document.getElementById('search-form').addEventListener('submit', function (e) {
    e.preventDefault();  // フォームの送信を防ぐ

    const keyword = document.getElementById('keyword').value;
    console.log("検索キーワード:", keyword);

    fetch(`/get_receipts_by_keyword?keyword=${encodeURIComponent(keyword)}`)
        .then(response => response.json())
        .then(data => {
            console.log("取得したデータ:", data);
            updateReceipts(data);
        })
        .catch(error => console.error("データ取得エラー:", error));
});

function updateReceipts(receipts) {
    const mainReceipt = document.querySelector('.main_receipt');
    mainReceipt.innerHTML = ''; // 一旦内容をクリア

    if (receipts.length === 0) {
        mainReceipt.innerHTML = '<p>該当する領収書がありません。</p>';
        return;
    }

    receipts.forEach(receipt => {
        const item = document.createElement('div');
        item.classList.add('grid-item');
        item.innerHTML = `<img src="${receipt.image_path}" alt="領収書画像" class="receipt_image">`;
        mainReceipt.appendChild(item);
    });
}



