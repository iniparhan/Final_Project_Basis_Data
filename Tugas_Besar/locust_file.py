"""
Run this file with:
python -m locust -f locust_file.py --host=http://127.0.0.1:5000

Then go to http://localhost:8089 to simulate users.
"""

from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 2)
   
    TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NjAwMDAxLCJyb2xlIjoiYWRtaW4ifQ.KL-mUYtdauu54vmzcDkLVAg5QsbGHdc60pJHZDschTM'
   
    def on_start(self):
        # Called when a simulated user starts — login to get JWT
        response = self.client.post("/login", json={"email": "parhanganteng@example.com"})
        if response.status_code == 200 and "token" in response.json():
            self.token = response.json()["token"]
        else:
            self.token = None
            print("⚠️ Failed to log in — check email or backend")

    @task
    def get_users(self):
        if self.token:
            self.client.get(
                "/api/users?page=1&limit=50",
                headers={"Authorization": f"Bearer {self.token}"}
            )
        else:
            print("⚠️ Skipping /api/users because no token available")
