let cleanedDataGlobal = null;
let chartInstance = null;

async function loadData() {
    // Load raw data
    try {
        const rawResponse = await fetch('http://localhost:5004/raw-data');
        const rawData = await rawResponse.json();
        // Show only first 10 records
        const preview = rawData.slice(0, 10);
        document.getElementById('rawData').innerHTML = '<pre>' + JSON.stringify(preview, null, 2) + '</pre>';
    } catch (error) {
        console.error('Error fetching raw data:', error);
        document.getElementById('rawData').textContent = 'Error loading raw data: ' + error.message;
    }
}

async function cleanDataML() {
    const cleanBtn = document.getElementById('cleanBtn');
    cleanBtn.disabled = true;
    cleanBtn.textContent = 'Cleaning...';

    try {
        const response = await fetch('http://localhost:5004/ml-clean-data');

        // Check if response is ok
        if (!response.ok) {
            const text = await response.text();
            throw new Error(`Server error (${response.status}): ${text}`);
        }

        const result = await response.json();

        if (result.success) {
            cleanedDataGlobal = result.cleaned_data;

            // Display report
            const report = result.report;
            document.getElementById('reportContent').innerHTML = `
                <p><strong>Original Records:</strong> ${report.original_count}</p>
                <p><strong>Unique Records:</strong> ${report.unique_records ?? report.cleaned_count}</p>
                <p><strong>Total In Stock:</strong> ${report.total_stock_quantity ?? 'N/A'}</p>
                <p><strong>Formats Normalized:</strong> ${report.formats_normalized}</p>
            `;
            document.getElementById('reportSection').style.display = 'block';

            // Enable save and simulate buttons
            document.getElementById('saveBtn').disabled = false;
            document.getElementById('simulateBtn').disabled = false;
            document.getElementById('simulateBtn').style.display = 'block';

            // Show cleaned data preview
            const preview = cleanedDataGlobal.slice(0, 10);
            document.getElementById('cleanData').innerHTML = '<pre>' + JSON.stringify(preview, null, 2) + '</pre>';

            // Save cleaned data to database for visualization
            await saveCleanedDataToDB(cleanedDataGlobal);

            cleanBtn.textContent = 'Clean Data with ML';
            cleanBtn.disabled = false;
        } else {
            const errorMsg = result.error + (result.traceback ? '\n\n' + result.traceback : '');
            console.error('Server error:', errorMsg);
            alert('Error: ' + result.error);
            cleanBtn.textContent = 'Clean Data with ML';
            cleanBtn.disabled = false;
        }
    } catch (error) {
        console.error('Error cleaning data:', error);
        alert('Error cleaning data: ' + error.message);
        cleanBtn.textContent = 'Clean Data with ML';
        cleanBtn.disabled = false;
    }
}

async function saveCleanedDataToDB(data) {
    try {
        const response = await fetch('http://localhost:5004/api/save-cleaned-data-to-db', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ data: data })
        });

        const result = await response.json();
        if (result.success) {
            console.log('Cleaned data saved to database');
        } else {
            console.error('Error saving to database:', result.error);
        }
    } catch (error) {
        console.error('Error saving to database:', error);
    }
}

function createChart(data) {
    // Aggregate count by artist
    const artistCounts = {};
    data.forEach(record => {
        const artist = record.artist;
        const count = record.count || 0;
        if (artistCounts[artist]) {
            artistCounts[artist] += count;
        } else {
            artistCounts[artist] = count;
        }
    });

    // Sort and take top 15
    const sorted = Object.entries(artistCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 15);

    const labels = sorted.map(x => x[0]);
    const values = sorted.map(x => x[1]);

    const ctx = document.getElementById('salesChart').getContext('2d');

    // Destroy existing chart if any
    if (chartInstance) {
        chartInstance.destroy();
    }

    chartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Total Count',
                data: values,
                backgroundColor: 'rgba(49, 116, 143, 0.6)', // Rosé Pine pine color with opacity
                borderColor: 'rgba(49, 116, 143, 1)', // Rosé Pine pine color
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: '#e0def4' // Rosé Pine text color
                    }
                },
                title: {
                    display: true,
                    text: 'Top 15 Artists by Total Count',
                    color: '#f6c177' // Rosé Pine gold color
                }
            }
        }
    });
}

// Event listeners
document.getElementById('cleanBtn').addEventListener('click', cleanDataML);
document.getElementById('saveBtn').addEventListener('click', saveCleanedData);
document.getElementById('simulateBtn').addEventListener('click', () => {
    window.location.href = 'route.html';
});

// Load initial data
loadData();
