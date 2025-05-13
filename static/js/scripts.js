// Upload form validation and submission handling
document.getElementById('upload-form')?.addEventListener('submit', function (e) {
    const fileInput = document.getElementById('file');
    const file = fileInput.files[0];
    const spinner = document.getElementById('upload-spinner');

    // Validate file
    if (!file) {
        e.preventDefault();
        alert('Please select a file to upload.');
        return;
    }
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        e.preventDefault();
        alert('Only PDF files are allowed.');
        return;
    }

    // Show spinner
    spinner.style.display = 'inline-block';
});

// Filter form submission handling
document.getElementById('filter-form')?.addEventListener('submit', function () {
    const spinner = document.getElementById('filter-spinner');
    spinner.style.display = 'inline-block';
});

// Clear filters
document.getElementById('clear-filters')?.addEventListener('click', function () {
    const form = document.getElementById('filter-form');
    form.querySelectorAll('select').forEach(select => select.value = '');
    form.submit();
});

// Delete form submission handling
document.querySelectorAll('.delete-form').forEach(form => {
    form.addEventListener('submit', function () {
        const spinner = this.querySelector('.delete-spinner');
        spinner.style.display = 'inline-block';
    });
});

// Show success message if present (e.g., after upload/delete)
const urlParams = new URLSearchParams(window.location.search);
if (urlParams.get('success')) {
    alert(urlParams.get('success'));
}

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
            plugins: { legend: { position: 'bottom' }, tooltip: { enabled: true } }
        }
    });

    // Refresh Dashboard button
    document.getElementById('refresh-dashboard')?.addEventListener('click', function () {
        window.location.reload();
    });
}