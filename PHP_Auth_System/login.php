<?php
// login.php
require_once 'config.php';

if (isset($_SESSION['user_id'])) {
    header("Location: dashboard.php");
    exit();
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - AI-Based Examination Analytics System</title>
    <link rel="stylesheet" href="assets/css/style.css">
    <script src="https://accounts.google.com/gsi/client" async defer></script>
</head>
<body class="login-body">

    <div class="login-card animate-fade-in">
        <div style="margin-bottom: 2rem;">
            <div style="width: 64px; height: 64px; background: var(--primary); border-radius: 16px; margin: 0 auto 1.5rem; display: flex; align-items: center; justify-content: center; color: white; font-size: 1.5rem; font-weight: bold;">AI</div>
            <h1 style="font-size: 1.75rem; color: var(--secondary); margin-bottom: 0.5rem; font-weight: 700;">Welcome Back</h1>
            <p style="color: var(--text-muted); font-size: 0.95rem;">AI-Based Examination Analytics System</p>
        </div>

        <form style="text-align: left; margin-bottom: 1.5rem;">
            <div style="margin-bottom: 1.25rem;">
                <label style="display: block; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.5rem; color: var(--secondary);">Email Address</label>
                <input type="email" placeholder="name@school.edu" style="width: 100%; padding: 0.75rem 1rem; border-radius: 10px; border: 1px solid var(--border); font-family: inherit; outline: none;">
            </div>
            <div style="margin-bottom: 1.5rem;">
                <label style="display: block; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.5rem; color: var(--secondary);">Password</label>
                <input type="password" placeholder="••••••••" style="width: 100%; padding: 0.75rem 1rem; border-radius: 10px; border: 1px solid var(--border); font-family: inherit; outline: none;">
            </div>
            <button type="button" style="width: 100%; padding: 0.85rem; background: var(--primary); color: white; border: none; border-radius: 10px; font-weight: 600; font-family: inherit; cursor: pointer; transition: background 0.2s;">Sign In</button>
        </form>

        <div style="display: flex; align-items: center; margin: 1.5rem 0; color: #CBD5E1;">
            <div style="flex: 1; height: 1px; background: #E2E8F0;"></div>
            <span style="padding: 0 1rem; font-size: 0.8rem; font-weight: 500;">OR</span>
            <div style="flex: 1; height: 1px; background: #E2E8F0;"></div>
        </div>

        <div id="g_id_onload"
             data-client_id="<?php echo GOOGLE_CLIENT_ID; ?>"
             data-context="signin"
             data-ux_mode="popup"
             data-login_uri="<?php echo GOOGLE_REDIRECT_URI; ?>"
             data-auto_prompt="false">
        </div>

        <div class="g_id_signin"
             data-type="standard"
             data-shape="pill"
             data-theme="outline"
             data-text="signin_with"
             data-size="large"
             data-logo_alignment="left"
             data-width="370">
        </div>

        <p style="margin-top: 2rem; font-size: 0.85rem; color: var(--text-muted);">
            Don't have an account? <a href="#" style="color: var(--primary); text-decoration: none; font-weight: 600;">Contact Administrator</a>
        </p>
    </div>

</body>
</html>
