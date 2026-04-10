<?php
// dashboard.php
require_once 'config.php';

// Check if logged in
if (!isset($_SESSION['user_id'])) {
    header("Location: login.php");
    exit();
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - AI-Based Examination Analytics System</title>
    <link rel="stylesheet" href="assets/css/style.css">
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>

    <div class="app-container">
        <!-- Sidebar -->
        <?php include 'components/sidebar.php'; ?>

        <main class="main-content">
            <!-- Navbar -->
            <?php include 'components/navbar.php'; ?>

            <div class="content-wrapper animate-fade-in">
                <div style="margin-bottom: 2rem;">
                    <h1 style="font-size: 1.5rem; font-weight: 700; color: var(--secondary);">System Overview</h1>
                    <p style="color: var(--text-muted); font-size: 0.9rem;">Welcome back! Here's what's happening today.</p>
                </div>

                <!-- Stats Cards -->
                <div class="card-grid">
                    <div class="stat-card">
                        <span class="stat-label">Total Students</span>
                        <div class="stat-value">1,248</div>
                        <div style="margin-top: 0.5rem; font-size: 0.8rem; color: var(--success);">↑ 12% from last term</div>
                    </div>
                    <div class="stat-card">
                        <span class="stat-label">Average Score</span>
                        <div class="stat-value">76.4%</div>
                        <div style="margin-top: 0.5rem; font-size: 0.8rem; color: var(--success);">↑ 4.2% improvement</div>
                    </div>
                    <div class="stat-card">
                        <span class="stat-label">Pass Percentage</span>
                        <div class="stat-value" style="color: var(--primary);">88.2%</div>
                        <div style="margin-top: 0.5rem; font-size: 0.8rem; color: var(--text-muted);">Target: 90%</div>
                    </div>
                    <div class="stat-card">
                        <span class="stat-label">Top Subject</span>
                        <div class="stat-value">Mathematics</div>
                        <div style="margin-top: 0.5rem; font-size: 0.8rem; color: var(--primary);">Avg. 84.5</div>
                    </div>
                </div>

                <!-- Charts Area -->
                <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 1.5rem; margin-bottom: 2rem;">
                    <div class="chart-container">
                        <h3 style="margin-bottom: 1.5rem; font-size: 1rem;">Subject-wise Performance</h3>
                        <canvas id="subjectChart" height="250"></canvas>
                    </div>
                    <div class="chart-container">
                        <h3 style="margin-bottom: 1.5rem; font-size: 1rem;">Pass vs Fail Ratio</h3>
                        <canvas id="ratioChart" height="250"></canvas>
                    </div>
                </div>

                <!-- Student Table -->
                <div class="data-table-container">
                    <div class="table-header">
                        <h3 style="font-size: 1rem; margin: 0;">Recent Student Performance</h3>
                        <button style="padding: 0.5rem 1rem; background: #F1F5F9; border: 1px solid var(--border); border-radius: 6px; font-size: 0.85rem; font-weight: 600; cursor: pointer;">Export CSV</button>
                    </div>
                    <table>
                        <thead>
                            <tr>
                                <th>Student Name</th>
                                <th>Reg Number</th>
                                <th>Maths</th>
                                <th>Physics</th>
                                <th>Chemistry</th>
                                <th>Total</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td style="font-weight: 600;">Arjun Kumar</td>
                                <td>REG2024001</td>
                                <td>85</td>
                                <td>78</td>
                                <td>92</td>
                                <td style="font-weight: 600;">255</td>
                                <td><span class="badge badge-pass">PASS</span></td>
                            </tr>
                            <tr>
                                <td style="font-weight: 600;">Priya Sharma</td>
                                <td>REG2024002</td>
                                <td>92</td>
                                <td>81</td>
                                <td>88</td>
                                <td style="font-weight: 600;">261</td>
                                <td><span style="background: #DCFCE7; color: #166534; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600;">PASS</span></td>
                            </tr>
                            <tr>
                                <td style="font-weight: 600;">Rahul Verma</td>
                                <td>REG2024003</td>
                                <td>35</td>
                                <td>42</td>
                                <td>38</td>
                                <td style="font-weight: 600;">115</td>
                                <td><span style="background: #FEE2E2; color: #991B1B; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600;">FAIL</span></td>
                            </tr>
                            <tr>
                                <td style="font-weight: 600;">Sneha Reddy</td>
                                <td>REG2024004</td>
                                <td>78</td>
                                <td>88</td>
                                <td>74</td>
                                <td style="font-weight: 600;">240</td>
                                <td><span style="background: #DCFCE7; color: #166534; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600;">PASS</span></td>
                            </tr>
                        </tbody>
                    </table>
                    <div style="padding: 1rem; text-align: center; border-top: 1px solid var(--border);">
                        <a href="#" style="color: var(--primary); font-size: 0.85rem; font-weight: 600; text-decoration: none;">View All Students →</a>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <!-- Charts Script -->
    <script src="assets/js/charts.js"></script>
</body>
</html>
