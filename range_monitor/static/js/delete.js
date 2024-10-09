// static/js/delete.js
document.addEventListener("DOMContentLoaded", () => {
    const deleteBtn = document.querySelector(".delete-btn");
    deleteBtn.addEventListener("click", () => {
        return confirm("Are you sure you want to delete this user, this action cannot be undone?");
    });
});