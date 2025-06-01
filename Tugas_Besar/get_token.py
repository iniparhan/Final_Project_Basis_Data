import requests

def get_token(email="parhanganteng@example.com"):
    response = requests.post("http://localhost:5000/login", json={"email": email})
    data = response.json()

    if "token" in data:
        print("Token retrieved:")
        print(data["token"])
        return data["token"]
    else:
        print("Error:", data)
        return None

if __name__ == "__main__":
    get_token()
