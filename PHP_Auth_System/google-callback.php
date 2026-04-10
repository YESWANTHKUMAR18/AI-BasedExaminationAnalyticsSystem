<?php
// google-callback.php
require_once 'config.php';

// Google Identity Services sends the credential (ID Token) in a POST request
if ($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_POST['credential'])) {
    $id_token = $_POST['credential'];

    // In a real production environment, you should use the Google API Client Library for verification:
    // $client = new Google_Client(['client_id' => GOOGLE_CLIENT_ID]);
    // $payload = $client->verifyIdToken($id_token);
    
    // For this demonstration, we'll decode the JWT payload manually. 
    // WARNING: In production, ALWAYS use a library to verify the signature.
    $parts = explode('.', $id_token);
    if (count($parts) != 3) {
        die("Invalid token format");
    }
    
    $payload = json_decode(base64_decode(str_replace(['-', '_'], ['+', '/'], $parts[1])), true);

    if ($payload && isset($payload['sub'])) {
        $google_id = $payload['sub'];
        $name = $payload['name'];
        $email = $payload['email'];
        $profile_picture = $payload['picture'];

        $conn = getDbConnection();

        // Check if user exists
        $stmt = $conn->prepare("SELECT id FROM users WHERE google_id = ?");
        $stmt->bind_param("s", $google_id);
        $stmt->execute();
        $result = $stmt->get_result();

        if ($result->num_rows > 0) {
            // User exists, update info just in case
            $user = $result->fetch_assoc();
            $user_id = $user['id'];
            
            $update = $conn->prepare("UPDATE users SET name = ?, profile_picture = ? WHERE id = ?");
            $update->bind_param("ssi", $name, $profile_picture, $user_id);
            $update->execute();
        } else {
            // New user, insert
            $insert = $conn->prepare("INSERT INTO users (google_id, name, email, profile_picture) VALUES (?, ?, ?, ?)");
            $insert->bind_param("ssss", $google_id, $name, $email, $profile_picture);
            $insert->execute();
            $user_id = $conn->insert_id;
        }

        // Set session
        $_SESSION['user_id'] = $user_id;
        $_SESSION['name'] = $name;
        $_SESSION['email'] = $email;
        $_SESSION['picture'] = $profile_picture;

        // Redirect to dashboard
        header("Location: dashboard.php");
        exit();
    } else {
        die("Authentication failed: Invalid payload.");
    }
} else {
    header("Location: login.php");
    exit();
}
?>
