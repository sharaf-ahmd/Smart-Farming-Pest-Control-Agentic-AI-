# Smart Farming Pest Control using Agentic AI
## 📌 Project Overview
This project presents an **AI-driven digital agronomist platform** designed to empower farmers in protecting their crops efficiently. The system uses a flexible, multi-agent AI architecture—orchestrated by **LangGraph** and **LangChain**—to provide an end-to-end solution for pest management. By leveraging powerful LLMs from **OpenAI**, **Mistral**, and **Hugging Face**, the platform offers robust analysis and recommendations. Farmers can upload an image of a pest, and the system will identify it, analyze the potential crop damage, and suggest eco-friendly treatments.

The platform's core objective is to reduce yield loss, increase farmer profitability, and ensure agricultural sustainability through intelligent, data-driven insights. It serves farmers and agronomists through an intuitive web-based dashboard.

---
## 🧪 Key Features
- **Instant Pest Detection:** Upload a pest image via drag-and-drop or a direct camera feed to identify the species using a YOLO detection model.
- **Automated Impact Analysis:** The system quantifies the threat by estimating the **Risk Level**, **Average Damage %**, and potential **Yield Loss %**.
- **Eco-Friendly Recommendations:** Receive tailored and sustainable treatment suggestions (organic, biological, chemical) based on the specific pest and crop.
- **Interactive Dashboard:** A user-friendly web application built with React that presents results in clear formats like charts, tables, and text.
- **Secure Access:** Features robust authentication and authorization for different user roles like Farmers and Agronomists.
- **Advanced Agentic Workflow:** An intelligent orchestrator built with **LangGraph** manages a stateful pipeline of specialized AI agents to handle detection, analysis, and recommendations sequentially.

---
## 🧠 System Architecture & Technologies Used
The platform is built on a modern, multi-layered architecture to ensure scalability, flexibility, and maintainability.

### Frontend (Web Application)
- **Frameworks:** **HTML/CSS/JS (React)**
- **Purpose:** Provides the main Farmer Dashboard for user interaction, image uploads, and results visualization.

### Backend Layer (Flask API)
- **Orchestration:** **LangChain** & **LangGraph** are used to define, compose, and manage the stateful, cyclical workflow between the different AI agents.
- **AI Agents:**
    - **YOLO Pest Detection Agent:** Identifies pest species from user-uploaded images.
    - **Impact Analyzer Agent (RAG Model):** A Retrieval-Augmented Generation model that assesses the pest's impact by querying a specialized knowledge base.
    - **Treatment Recommender Agent:** Suggests appropriate and eco-friendly treatment plans.
- **LLM APIs:** The system is designed to be model-agnostic and can be configured to use various powerful LLMs:
    - **OpenAI (GPT-4, etc.)**
    - **Mistral AI (Mistral Large, etc.)**
    - **Groq** for high-speed inference.
    - **Hugging Face** for open-source models.
- **Embeddings:** Utilizes **Hugging Face Sentence Transformers** to generate vector embeddings for the RAG pipeline's knowledge base.

### Database Layer
- **Vector Store:** **FAISS / Chroma** is used to store and retrieve pest-crop knowledge efficiently for the RAG model.
- **User Database:** **MongoDB** stores user profiles, farm data, and historical reports.



---
## ⚙️ Workflow
The system operates as a stateful graph managed by **LangGraph**, where each agent functions as a node in the workflow. This ensures a reliable and logical progression from one step to the next.

1.  **Image Upload:** A farmer uploads a pest image and specifies the crop name via the Farmer Dashboard.
2.  **Pest Detection:** The image is sent to the **YOLO Pest Detection Agent**, which outputs the pest's name (Pest ID) and a confidence score.
3.  **Impact Analysis:** The Pest ID and crop name are passed to the **Impact Analyzer Agent**. It uses its RAG capabilities to generate a risk report detailing the risk level, average damage, and yield loss.
4.  **Treatment Recommendation:** The risk report, along with the pest and crop data, is fed to the **Treatment Recommender Agent**, which suggests eco-friendly treatments.
5.  **Report Generation:** The outputs from all agents are consolidated into a comprehensive, easy-to-understand report and displayed on the Farmer Dashboard.

---
## ✅ Responsible AI & Commercial Viability
The project is designed with responsible AI principles and a clear path to commercialization.

### Responsible AI Compliance
- **Transparency:** The system shows confidence scores from the detection model and cites the sources used for analysis.
- **Fairness:** Utilizes datasets from diverse geographical regions to minimize bias.
- **Safety:** All treatment recommendations adhere to guidelines approved by the WHO/FAO.
- **Data Privacy:** User data is securely stored with robust authentication and encryption measures.
- **Accountability:** System logs are maintained for complete auditability.
- **Human-in-the-Loop:** Farmers are encouraged to cross-verify the AI's recommendations with local extension officers.

### Commercialization Concept
- **Value Proposition:** Instantly detects pests, quantifies crop damage risk, and recommends eco-friendly, cost-effective treatments to reduce yield loss.
- **Target Market:** Smallholder farmers, agri-business cooperatives, and government agriculture departments.
- **Revenue Streams:** A **freemium model** for basic features, **enterprise licenses** for larger organizations, and an **API-as-a-Service** for integration into other platforms.
- **Unique Differentiator:** Unlike generic apps, this platform integrates a multi-agent pipeline (detection + impact + treatment) that is both scientifically robust and highly practical for farmers.

---
## 🛠 Getting Started
### Prerequisites
- Python 3.9+
- Flask & React
- Docker
- **LangChain & LangGraph**
- **Hugging Face Transformers** & **Sentence-Transformers**
- Dependencies listed in `requirements.txt` (for backend) and `package.json` (for frontend).

### Configuration
Before running the application, you need to configure your API keys. Create a `.env` file in the `backend` directory and add your keys:
```env
# .env file
OPENAI_API_KEY="your-openai-api-key"
MISTRAL_API_KEY="your-mistral-api-key"
GROQ_API_KEY="your-groq-api-key"
HUGGINGFACEHUB_API_TOKEN="your-huggingface-api-token"
