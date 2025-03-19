function handleCredentialResponse(response) {
    console.log("Encoded JWT ID token: " + response.credential);

    // Decode the JWT to extract user information
    const base64Url = response.credential.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = JSON.parse(window.atob(base64));
    
    const email = jsonPayload.email; // Extract the user's email from the JWT

    // Check if the email ends with 'hyderabad.bits-pilani.ac.in'
    if (!email.endsWith('@hyderabad.bits-pilani.ac.in')) {
        alert('Please use your college email');
        return; // Stop further processing
    }

    // Store the email and token in localStorage
    localStorage.setItem('userEmail', email);
    localStorage.setItem('access_token', response.credential);
    console.log("User logged in successfully");

    // Redirect to dashboard after successful login
    window.location.href = 'dashboard.html';
}

window.onload = function () {
    google.accounts.id.initialize({
        client_id: '438702058106-br97sspq1g1vp81sk8h8hpk99f49t91c.apps.googleusercontent.com',
        callback: handleCredentialResponse,
        auto_select: false,
        cancel_on_tap_outside: true
    });

    google.accounts.id.renderButton(
        document.getElementById("googleBtn"),
        { theme: "outline", size: "large" }
    );

    // Check if user is already logged in
    const token = localStorage.getItem('access_token');
    if (token) {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = JSON.parse(window.atob(base64));
        const email = jsonPayload.email;

        if (email.endsWith('@hyderabad.bits-pilani.ac.in')) {
            window.location.href = 'dashboard.html';
        } else {
            alert('Only college emails are allowed.');
            localStorage.removeItem('access_token'); // Remove invalid token
        }
    } else {
        google.accounts.id.prompt();
    }
}

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('googleBtn').addEventListener('click', function() {
        google.accounts.id.prompt();
    });
});

