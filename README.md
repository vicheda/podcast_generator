# Podcast Generator
CS310 Scalable Software Architecture Final Project

Authors: Vicheda Narith, Viktoriia Sokolenko

We developed an application that generates podcast-style audio based on the topic the user chooses (e.g., technology, sports, books). The podcast script incorporates information from The Guardian API articles related to the user query. 

The application consists of a server-side infrastructure and a Python script client-side interface for interacting with the backend.
  
![Architecture](https://github.com/user-attachments/assets/4705098d-5cef-4748-b71d-36a86f70b97c)

Each folder corresponds to a specific lambda function. Those lambda functions are used to set up API Gateway.
## API Endpoints

### **📌 Articles**
- `GET /articles` – Retrieve details of all articles that were fetched to generate podcast scripts.

### **📊 Queries**
- `GET /queries` – Retrieve past queries including their status and S3 keys corresponding to their audio and script files.

### **🔍 Fetch**
- `POST /fetch/{query}` – Fetch articles based on a query.

### **📝 Summarize**
- `POST /summarize/{queryid}` – Summarize the five collected articles into a structured podcast script using generative AI with Llama 3.3 70B Instruct provider.

### **🎙️ Podcast**
- `POST /podcast/{queryid}` – Generate a podcast episode from the script for this query using Amazon Polly.

### **🛑 Reset**
- `DELETE /reset` – Reset stored data.
  
## Client Walkthrough
![walkthrough](https://github.com/user-attachments/assets/4563e988-5cc1-4b43-8cc8-b5205a281408)
