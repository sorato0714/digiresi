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


