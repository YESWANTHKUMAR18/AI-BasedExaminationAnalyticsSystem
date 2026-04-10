<!-- components/sidebar.php -->
<aside class="sidebar">
    <div class="sidebar-header">
        <div class="sidebar-logo">AI</div>
        <h2 style="font-size: 1.1rem; color: white;">Analytics Pro</h2>
    </div>
    
    <ul class="sidebar-nav">
        <li class="nav-item">
            <a href="dashboard.php" class="nav-link <?php echo basename($_SERVER['PHP_SELF']) == 'dashboard.php' ? 'active' : ''; ?>">
                <span>📊</span> Dashboard
            </a>
        </li>
        <li class="nav-item">
            <a href="#" class="nav-link">
                <span>👨‍🎓</span> Student Performance
            </a>
        </li>
        <li class="nav-item">
            <a href="#" class="nav-link">
                <span>📚</span> Subject Analytics
            </a>
        </li>
        <li class="nav-item">
            <a href="#" class="nav-link">
                <span>📝</span> Reports
            </a>
        </li>
        <li class="nav-item">
            <a href="#" class="nav-link">
                <span>📁</span> Data Upload
            </a>
        </li>
        <li class="nav-item">
            <a href="#" class="nav-link">
                <span>⚙️</span> Settings
            </a>
        </li>
        <li class="nav-item" style="margin-top: 3rem; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 1rem;">
            <a href="logout.php" class="nav-link">
                <span>🚪</span> Logout
            </a>
        </li>
    </ul>
</aside>
