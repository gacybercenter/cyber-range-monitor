const TOGGLE_BUTTON = document.getElementById("toggle-btn")
const SIDEBAR = document.getElementById("sidebar")

function toggleSideBar() {
    SIDEBAR.classList.toggle("close")
    TOGGLE_BUTTON.classList.toggle("rotate")

    closeAllSubMenus()
}

function toggleSubMenu(button) {
    if (button.nextElementSibling.classList.contains("show") == false) {
        closeAllSubMenus()
    }

    button.nextElementSibling.classList.toggle("show")
    button.classList.toggle("rotate")

    if (SIDEBAR.classList.contains("close")) {
        SIDEBAR.classList.toggle("close")
        TOGGLE_BUTTON.classList.toggle("rotate")
    }
}

function closeAllSubMenus() {
    Array.from(SIDEBAR.getElementsByClassName("show")).forEach(ul => {
        ul.classList.remove("show")
        ul.previousElementSibling.classList.remove("rotate")
    })
}