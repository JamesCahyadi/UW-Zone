const openPopupBtns = document.querySelectorAll('[data-popup-target]');
const closePopupBtns = document.querySelectorAll('[data-close-button]');
const overlay = document.getElementById('overlay');
const body = document.body;

openPopupBtns.forEach(button => {
    button.addEventListener('click', () => {
        // the popup to display is the clicked button's parent's parent's next sibling
        const popup = button.parentElement.parentElement.nextElementSibling;
        openPopup(popup);
    });
});

overlay.addEventListener('click', () => {
    const popups = document.querySelectorAll('.popup.active');
    popups.forEach(popup => {
        closePopup(popup);
    });
});

closePopupBtns.forEach(button => {
    button.addEventListener('click', () => {
        const popup = button.closest('.popup');
        closePopup(popup);
    });
});

function openPopup(popup) {
    if (!popup) return;
    body.classList.add('scroll-lock');
    popup.classList.add('active');
    overlay.classList.add('active');
}

function closePopup(popup) {
    if (!popup) return;
    body.classList.remove('scroll-lock');
    popup.classList.remove('active');
    overlay.classList.remove('active');
}