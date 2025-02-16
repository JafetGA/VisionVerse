const buttonMenuHide = document.getElementById('buttonMenu');
const buttonMenuShow = document.getElementById('buttonMenuShow');
const header = document.querySelector('.item:nth-child(1)');
const sidebar = document.querySelector('.item:nth-child(2)');
const container = document.querySelector('.container');

window.addEventListener('load', function() {
    const isSidebarHidden = localStorage.getItem('sidebarHidden') === 'true';
    if (isSidebarHidden) {
        // Add no-transition class to prevent animation
        sidebar.classList.add('no-transition');
        container.classList.add('no-transition');
        header.classList.add('no-transition');

        // Apply hidden states
        sidebar.classList.add('sidebar-hidden');
        container.classList.add('sidebar-hidden');
        header.classList.remove('header-hidden');
        header.classList.add('header');
        buttonMenuShow.style.display = 'block';

        // Force reflow
        sidebar.offsetHeight;
        container.offsetHeight;
        header.offsetHeight;

        // Remove no-transition class
        requestAnimationFrame(() => {
            sidebar.classList.remove('no-transition');
            container.classList.remove('no-transition');
            header.classList.remove('no-transition');
        });
    }
});

buttonMenuHide.addEventListener('click', function() {
    sidebar.classList.toggle('sidebar-hidden');
    container.classList.toggle('sidebar-hidden');
    header.classList.toggle('header-hidden');
    header.classList.toggle('header');
    buttonMenuShow.style.display = 'block';
    // Save state to localStorage
    localStorage.setItem('sidebarHidden', 'true');
});

buttonMenuShow.addEventListener('click', function() {
    sidebar.classList.toggle('sidebar-hidden');
    container.classList.toggle('sidebar-hidden');
    header.classList.toggle('header-hidden');
    header.classList.toggle('header');
    buttonMenuShow.style.display = 'none';
    // Save state to localStorage
    localStorage.setItem('sidebarHidden', 'false');
});