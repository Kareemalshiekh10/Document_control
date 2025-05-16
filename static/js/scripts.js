// scripts.js

// Custom popup function
function showPopup(message, type = 'success') {
    const popup = document.getElementById('custom-popup');
    const popupMessage = document.getElementById('popup-message');
    const popupOkButton = document.getElementById('popup-ok');
    if (!popup || !popupMessage || !popupOkButton) return;

    popupMessage.textContent = message;
    popup.classList.remove('hidden', 'success', 'error');
    popup.classList.add(type);

    // Show popup
    popup.style.display = 'flex';

    // Close on "X" button click
    document.getElementById('popup-close')?.addEventListener('click', () => {
        popup.style.display = 'none';
    }, { once: true });

    // Close on "OK" button click
    popupOkButton.addEventListener('click', () => {
        popup.style.display = 'none';
    }, { once: true });

    // Close on overlay click
    popup.addEventListener('click', (e) => {
        if (e.target === popup) {
            popup.style.display = 'none';
        }
    }, { once: true });
}

// Upload form validation and submission handling (Documents page)
document.getElementById('upload-form')?.addEventListener('submit', function (e) {
    const fileInput = document.getElementById('file');
    const file = fileInput.files[0];
    const spinner = document.getElementById('upload-spinner');

    // Validate file
    if (!file) {
        e.preventDefault();
        showPopup('Please select a file to upload.', 'error');
        return;
    }
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        e.preventDefault();
        showPopup('Only PDF files are allowed.', 'error');
        return;
    }

    // Show spinner
    spinner.style.display = 'inline-block';
    this.querySelector('button[type="submit"]').disabled = true;
});

// Filter form submission handling (Documents page)
document.getElementById('filter-form')?.addEventListener('submit', function () {
    const spinner = document.getElementById('filter-spinner');
    spinner.style.display = 'inline-block';
    this.querySelector('button[type="submit"]').disabled = true;
});

// Clear filters (Documents page)
document.getElementById('clear-filters')?.addEventListener('click', function () {
    const form = document.getElementById('filter-form');
    form.querySelectorAll('select').forEach(select => select.value = '');
    form.querySelector('input[type="date"]').value = ''; // Clear date input as well
    form.submit();
});

// Report issue form submission handling
document.getElementById('report-issue-form')?.addEventListener('submit', function (e) {
    const fileInput = document.getElementById('issue-file');
    const file = fileInput?.files[0];
    const spinner = document.getElementById('report-issue-spinner');

    // Validate file if provided
    if (file) {
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            e.preventDefault();
            showPopup('Only PDF files are allowed.', 'error');
            return;
        }
    }

    // Show spinner
    spinner.style.display = 'inline-block';
    this.querySelector('button[type="submit"]').disabled = true;
});

// Filter form submission handling (Issues page)
document.getElementById('filter-issues-form')?.addEventListener('submit', function () {
    const spinner = document.getElementById('filter-issues-spinner');
    spinner.style.display = 'inline-block';
    this.querySelector('button[type="submit"]').disabled = true;
});

// Clear filters (Issues page)
document.getElementById('clear-issue-filters')?.addEventListener('click', function () {
    const form = document.getElementById('filter-issues-form');
    form.querySelectorAll('select').forEach(select => select.value = '');
    form.querySelector('input[type="date"]').value = ''; // Clear date input as well
    form.submit();
});

// Delete form submission handling (Documents)
document.querySelectorAll('.delete-form').forEach(form => {
    form.addEventListener('submit', function () {
        const spinner = this.querySelector('.delete-spinner');
        spinner.style.display = 'inline-block';
        this.querySelector('button[type="submit"]').disabled = true;
    });
});

// Delete form submission handling (Issues)
document.querySelectorAll('.delete-issue-form').forEach(form => {
    form.addEventListener('submit', function () {
        const spinner = this.querySelector('.delete-issue-spinner');
        spinner.style.display = 'inline-block';
        this.querySelector('button[type="submit"]').disabled = true;
    });
});

// Show success or error message if present and clear URL parameter
const urlParams = new URLSearchParams(window.location.search);
if (urlParams.get('success')) {
    showPopup(urlParams.get('success'), 'success');
    urlParams.delete('success');
    const newUrl = window.location.pathname + (urlParams.toString() ? '?' + urlParams.toString() : '');
    history.replaceState(null, '', newUrl);
} else if (urlParams.get('error')) {
    showPopup(urlParams.get('error'), 'error');
    urlParams.delete('error');
    const newUrl = window.location.pathname + (urlParams.toString() ? '?' + urlParams.toString() : '');
    history.replaceState(null, '', newUrl);
}

// Configure PDF.js worker
if (typeof pdfjsLib !== 'undefined') {
    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.9.359/pdf.worker.min.js';
}

// Handle preview button clicks
document.querySelectorAll('.preview-btn').forEach(button => {
    button.addEventListener('click', async function() {
        const filePath = this.getAttribute('data-filepath');
        console.log('Attempting to preview PDF at:', filePath); // Debug log
        const modal = document.getElementById('previewModal');
        const canvas = document.getElementById('pdfCanvas');
        const context = canvas.getContext('2d');

        // Show the modal
        modal.classList.remove('hidden');

        try {
            // Load the PDF
            const pdf = await pdfjsLib.getDocument(filePath).promise;
            const page = await pdf.getPage(1); // Render the first page

            // Set canvas dimensions with scaling
            const scale = 1.5; // Increase scale for better readability
            const viewport = page.getViewport({ scale: scale });
            canvas.height = viewport.height;
            canvas.width = viewport.width;

            // Render the PDF page into the canvas
            await page.render({
                canvasContext: context,
                viewport: viewport
            }).promise;
        } catch (error) {
            console.error('Error loading PDF:', error);
            showPopup('Failed to load PDF preview. Ensure the file exists and is accessible.', 'error');
            modal.classList.add('hidden');
        }
    });
});

// Handle preview modal close
document.querySelectorAll('.close-modal').forEach(button => {
    button.addEventListener('click', function() {
        const modal = document.getElementById('previewModal');
        modal.classList.add('hidden');
        // Clear the canvas
        const canvas = document.getElementById('pdfCanvas');
        const context = canvas.getContext('2d');
        context.clearRect(0, 0, canvas.width, canvas.height);
    });
});

// Dashboard chart initialization
if (document.getElementById('typeChart')) {
    // Documents by Type (Bar)
    const typeChart = new Chart(document.getElementById('typeChart'), {
        type: 'bar',
        data: {
            labels: window.dashboardStats?.documents_by_type.map(item => item.type_name) || [],
            datasets: [{
                label: 'Documents',
                data: window.dashboardStats?.documents_by_type.map(item => item.count) || [],
                backgroundColor: ['#3182ce', '#63b3ed', '#90cdf4', '#bee3f8'],
                borderColor: ['#2b6cb0', '#4299e1', '#63b3ed', '#90cdf4'],
                borderWidth: 1
            }]
        },
        options: {
            scales: { y: { beginAtZero: true } },
            plugins: { legend: { display: false }, tooltip: { enabled: true } }
        }
    });

    // Documents by Project (Pie)
    const projectChart = new Chart(document.getElementById('projectChart'), {
        type: 'pie',
        data: {
            labels: window.dashboardStats?.documents_by_project.map(item => item.project_name) || [],
            datasets: [{
                data: window.dashboardStats?.documents_by_project.map(item => item.count) || [],
                backgroundColor: ['#3182ce', '#63b3ed', '#90cdf4', '#bee3f8']
            }]
        },
        options: {
            plugins: { legend: { position: 'bottom' }, tooltip: { enabled: true } }
        }
    });

    // Documents by Status (Doughnut)
    const statusChart = new Chart(document.getElementById('statusChart'), {
        type: 'doughnut',
        data: {
            labels: window.dashboardStats?.documents_by_status.map(item => item.status_name) || [],
            datasets: [{
                data: window.dashboardStats?.documents_by_status.map(item => item.count) || [],
                backgroundColor: ['#3182ce', '#63b3ed', '#90cdf4', '#bee3f8']
            }]
        },
        options: {
            plugins: { legend: { position: "bottom" }, tooltip: { enabled: true } }
        }
    });


}