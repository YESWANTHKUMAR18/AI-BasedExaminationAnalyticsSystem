<!-- components/navbar.php -->
<nav class="navbar">
    <div class="nav-left">
        <input type="text" placeholder="Search analytics..." class="nav-search">
    </div>
    
    <div class="nav-actions">
        <div class="notifications" style="cursor: pointer; font-size: 1.2rem;">🔔</div>
        <div class="user-profile">
            <div style="text-align: right;">
                <p style="font-size: 0.85rem; font-weight: 600; margin: 0;"><?php echo htmlspecialchars($_SESSION['name']); ?></p>
                <p style="font-size: 0.75rem; color: var(--text-muted); margin: 0;">Administrator</p>
            </div>
            <img src="<?php echo $_SESSION['picture']; ?>" alt="Profile" class="avatar">
        </div>
    </div>
</nav>
