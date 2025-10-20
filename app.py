from flask import Flask, render_template_string, jsonify
import json
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# HTML Template with Tailwind CSS
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>A16z Jobs Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        primary: '#2563eb',
                        secondary: '#7c3aed',
                    }
                }
            }
        }
    </script>
</head>
<body class="bg-gradient-to-br from-blue-50 to-purple-50 min-h-screen">
    <div class="container mx-auto px-4 py-8">
        <!-- Header -->
        <div class="text-center mb-12">
            <h1 class="text-5xl font-bold text-gray-800 mb-3">
                <span class="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    A16z Jobs Dashboard
                </span>
            </h1>
            <p class="text-gray-600 text-lg">Software Engineering Opportunities</p>
            <button id="refresh-btn" 
                    class="mt-4 px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-lg transition duration-200 shadow-md">
                🔄 Refresh Data
            </button>
        </div>

        <!-- Stats Cards -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div class="bg-white rounded-xl shadow-lg p-6 border-l-4 border-blue-500">
                <div class="text-gray-500 text-sm font-semibold uppercase">Total Jobs</div>
                <div class="text-3xl font-bold text-gray-800 mt-2" id="total-jobs">{{ total_jobs }}</div>
            </div>
            <div class="bg-white rounded-xl shadow-lg p-6 border-l-4 border-purple-500">
                <div class="text-gray-500 text-sm font-semibold uppercase">Companies</div>
                <div class="text-3xl font-bold text-gray-800 mt-2" id="total-companies">{{ total_companies }}</div>
            </div>
            <div class="bg-white rounded-xl shadow-lg p-6 border-l-4 border-green-500">
                <div class="text-gray-500 text-sm font-semibold uppercase">Filtered</div>
                <div class="text-3xl font-bold text-gray-800 mt-2" id="filtered-count">{{ total_jobs }}</div>
            </div>
            <div class="bg-white rounded-xl shadow-lg p-6 border-l-4 border-orange-500">
                <div class="text-gray-500 text-sm font-semibold uppercase">Locations</div>
                <div class="text-3xl font-bold text-gray-800 mt-2" id="total-locations">{{ total_locations }}</div>
            </div>
        </div>

        <!-- Filters -->
        <div class="bg-white rounded-xl shadow-lg p-6 mb-8">
            <h2 class="text-xl font-bold text-gray-800 mb-4">🔍 Filters</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <!-- Search -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Search Jobs</label>
                    <input type="text" id="search-input" 
                           placeholder="Search by title or company..."
                           class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                </div>
                
                <!-- Company Filter -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Company</label>
                    <select id="company-filter" 
                            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                        <option value="">All Companies</option>
                    </select>
                </div>
                
                <!-- Location Filter -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Location</label>
                    <select id="location-filter" 
                            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                        <option value="">All Locations</option>
                    </select>
                </div>
            </div>
            
            <button id="clear-filters" 
                    class="mt-4 px-6 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg transition duration-200">
                Clear Filters
            </button>
        </div>

        <!-- Jobs Grid -->
        <div id="jobs-container" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <!-- Jobs will be inserted here by JavaScript -->
        </div>

        <!-- Loading State -->
        <div id="loading" class="hidden text-center py-12">
            <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p class="mt-4 text-gray-600">Loading jobs...</p>
        </div>

        <!-- No Results -->
        <div id="no-results" class="hidden text-center py-12">
            <svg class="mx-auto h-24 w-24 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <h3 class="mt-4 text-xl font-semibold text-gray-700">No jobs found</h3>
            <p class="mt-2 text-gray-500">Try adjusting your filters</p>
        </div>
    </div>

    <script>
        let jobsData = {{ jobs_data | tojson }};
        let filteredJobs = [...jobsData];

        // Populate filter options
        function populateFilters() {
            const companies = [...new Set(jobsData.map(job => job.company))].sort();
            const locations = [...new Set(jobsData.map(job => job.location))].sort();

            const companySelect = document.getElementById('company-filter');
            const locationSelect = document.getElementById('location-filter');

            // Clear existing options (except "All")
            companySelect.innerHTML = '<option value="">All Companies</option>';
            locationSelect.innerHTML = '<option value="">All Locations</option>';

            companies.forEach(company => {
                const option = document.createElement('option');
                option.value = company;
                option.textContent = company;
                companySelect.appendChild(option);
            });

            locations.forEach(location => {
                const option = document.createElement('option');
                option.value = location;
                option.textContent = location;
                locationSelect.appendChild(option);
            });
        }

        // Update stats
        function updateStats() {
            const totalCompanies = new Set(jobsData.map(job => job.company)).size;
            const totalLocations = new Set(jobsData.map(job => job.location)).size;
            
            document.getElementById('total-jobs').textContent = jobsData.length;
            document.getElementById('total-companies').textContent = totalCompanies;
            document.getElementById('total-locations').textContent = totalLocations;
        }

        // Render jobs
        function renderJobs(jobs) {
            const container = document.getElementById('jobs-container');
            const noResults = document.getElementById('no-results');
            const loading = document.getElementById('loading');
            
            loading.classList.add('hidden');
            
            if (jobs.length === 0) {
                container.classList.add('hidden');
                noResults.classList.remove('hidden');
                return;
            }

            container.classList.remove('hidden');
            noResults.classList.add('hidden');

            container.innerHTML = jobs.map(job => `
                <div class="bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 overflow-hidden border border-gray-100">
                    <div class="p-6">
                        <div class="flex items-start justify-between mb-3">
                            <div class="flex-1">
                                <h3 class="text-lg font-bold text-gray-800 mb-2 line-clamp-2">${escapeHtml(job.title)}</h3>
                                <p class="text-sm font-semibold text-blue-600 mb-1">${escapeHtml(job.company)}</p>
                            </div>
                        </div>
                        
                        <div class="flex items-center text-sm text-gray-600 mb-4">
                            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                            </svg>
                            ${escapeHtml(job.location)}
                        </div>

                        <div class="flex gap-2">
                            <a href="${escapeHtml(job.url)}" target="_blank" rel="noopener noreferrer"
                               class="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-4 py-2 rounded-lg text-center font-semibold transition duration-200 text-sm">
                                Apply Now
                            </a>
                            <a href="${escapeHtml(job.scraped_from)}" target="_blank" rel="noopener noreferrer"
                               class="px-4 py-2 border border-gray-300 hover:border-gray-400 text-gray-700 rounded-lg transition duration-200 text-sm">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                                </svg>
                            </a>
                        </div>
                    </div>
                </div>
            `).join('');

            document.getElementById('filtered-count').textContent = jobs.length;
        }

        // Escape HTML to prevent XSS
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // Filter jobs
        function filterJobs() {
            const searchTerm = document.getElementById('search-input').value.toLowerCase();
            const companyFilter = document.getElementById('company-filter').value;
            const locationFilter = document.getElementById('location-filter').value;

            filteredJobs = jobsData.filter(job => {
                const matchesSearch = job.title.toLowerCase().includes(searchTerm) || 
                                     job.company.toLowerCase().includes(searchTerm);
                const matchesCompany = !companyFilter || job.company === companyFilter;
                const matchesLocation = !locationFilter || job.location === locationFilter;

                return matchesSearch && matchesCompany && matchesLocation;
            });

            renderJobs(filteredJobs);
        }

        // Refresh data from API
        async function refreshData() {
            const loading = document.getElementById('loading');
            const container = document.getElementById('jobs-container');
            const refreshBtn = document.getElementById('refresh-btn');
            
            loading.classList.remove('hidden');
            container.classList.add('hidden');
            refreshBtn.disabled = true;
            refreshBtn.textContent = '⏳ Refreshing...';
            
            try {
                const response = await fetch('/api/jobs');
                const data = await response.json();
                
                if (data && data.length > 0) {
                    jobsData = data;
                    filteredJobs = [...jobsData];
                    populateFilters();
                    updateStats();
                    filterJobs();
                }
            } catch (error) {
                console.error('Error refreshing data:', error);
                alert('Failed to refresh data. Please try again.');
            } finally {
                loading.classList.add('hidden');
                refreshBtn.disabled = false;
                refreshBtn.textContent = '🔄 Refresh Data';
            }
        }

        // Clear filters
        document.getElementById('clear-filters').addEventListener('click', () => {
            document.getElementById('search-input').value = '';
            document.getElementById('company-filter').value = '';
            document.getElementById('location-filter').value = '';
            filterJobs();
        });

        // Refresh button
        document.getElementById('refresh-btn').addEventListener('click', refreshData);

        // Event listeners
        document.getElementById('search-input').addEventListener('input', filterJobs);
        document.getElementById('company-filter').addEventListener('change', filterJobs);
        document.getElementById('location-filter').addEventListener('change', filterJobs);

        // Initialize
        populateFilters();
        renderJobs(jobsData);
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """Main dashboard page"""
    jobs_data = load_jobs_data()
    stats = calculate_stats(jobs_data)
    
    return render_template_string(
        HTML_TEMPLATE,
        jobs_data=jobs_data,
        **stats
    )

@app.route('/api/jobs')
def get_jobs():
    """API endpoint to get jobs data with CORS support"""
    jobs_data = load_jobs_data()
    return jsonify(jobs_data)

@app.route('/api/stats')
def get_stats():
    """API endpoint to get statistics"""
    jobs_data = load_jobs_data()
    stats = calculate_stats(jobs_data)
    return jsonify(stats)

def load_jobs_data():
    """Load jobs data from JSON file"""
    jobs_file = 'a16z_sde_jobs.json'
    
    if not os.path.exists(jobs_file):
        # Return sample data if file doesn't exist
        return [
            {
                "company": "Example Company",
                "title": "Software Engineer",
                "location": "San Francisco, CA",
                "url": "https://example.com/job",
                "scraped_from": "https://jobs.a16z.com/jobs/example"
            }
        ]
    
    try:
        with open(jobs_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading jobs data: {e}")
        return []

def calculate_stats(jobs_data):
    """Calculate statistics from jobs data"""
    return {
        'total_jobs': len(jobs_data),
        'total_companies': len(set(job['company'] for job in jobs_data)) if jobs_data else 0,
        'total_locations': len(set(job['location'] for job in jobs_data)) if jobs_data else 0
    }

if __name__ == '__main__':
    print("🚀 Starting A16z Jobs Dashboard...")
    print("📍 Server running at: http://localhost:6000")
    print("🔗 API endpoint: http://localhost:6000/api/jobs")
    app.run(debug=True, host='0.0.0.0', port=3000)
