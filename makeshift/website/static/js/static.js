document.addEventListener('click', function() {
    const colors = ['#FF5733', '#33FF57', '#3357FF', '#FF33E6', '#E6FF33'];
    const titleElement = document.querySelector('h1');
    let colorIndex = 0;
    titleElement.addEventListener('click', function() {
        titleElement.style.color = colors[colorIndex];
        colorIndex = (colorIndex + 1) % colors.length;
    });
});