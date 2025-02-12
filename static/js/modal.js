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
