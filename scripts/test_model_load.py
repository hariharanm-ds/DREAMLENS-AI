from groq_client import check_groq_health


if __name__ == "__main__":
    status = check_groq_health()
    print("Groq configured:", bool(status.get("connected")))
    print("Active model:", status.get("active_model"))
    print("Model available:", status.get("model_available"))
    if status.get("error"):
        print("Error:", status["error"])
