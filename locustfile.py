from locust import HttpUser, task, between

class AgentUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def ask_question(self):
        self.client.get("/ask", params={"q": "what is the capital of France"})

    @task(2)
    def ask_weather(self):
        self.client.get("/ask", params={"q": "what is the weather in London"})

    @task(1)
    def check_health(self):
        self.client.get("/health")

    @task(1)
    def check_stats(self):
        self.client.get("/stats")
