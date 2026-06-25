# Admin Deactivation Logout Flow

When an admin deactivates a user, the backend invalidates the user's API token and sends a Firebase data message if an FCM token is available.

Frontend behavior:

1. Listen for Firebase data messages.
2. Poll `GET /accounts/session_status/` every 5-10 seconds while a user is logged in.
3. When either path returns `force_logout: true`, show a blocking modal:

```text
Your account has been deactivated by admin.
[Logout]
```

4. On `Logout` button click:
   - remove auth token from local storage/session storage/cookies
   - clear current user state
   - redirect to the login page
   - show the backend message as a toast

Backend inactive response shape:

```json
{
  "success": false,
  "message": "Your account has been deactivated by admin.",
  "force_logout": true
}
```

Firebase data message shape:

```json
{
  "type": "force_logout",
  "force_logout": "true",
  "message": "Your account has been deactivated by admin."
}
```

Example frontend polling logic:

```js
async function checkSessionStatus() {
  const token = localStorage.getItem("token");
  if (!token) return;

  const response = await fetch(`${API_URL}/accounts/session_status/`, {
    headers: {
      Authorization: `Token ${token}`,
    },
  });
  const result = await response.json();

  if (response.status === 401 || result.force_logout) {
    showDeactivatedModal(result.message || "Your account has been deactivated by admin.");
  }
}

setInterval(checkSessionStatus, 5000);

function logoutAfterDeactivation() {
  localStorage.removeItem("token");
  clearCurrentUser();
  navigate("/login");
}
```
