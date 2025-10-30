
#  HR Analytics – Cloud Deployment (Task 1)

##  Overview
The **HR Analytics Cloud Project** demonstrates a modern data-engineering deployment on **Microsoft Azure**.  
It collects job-advertisement data from the **Arbetsförmedlingen (JobTech) API**, processes it automatically, stores it in a local analytical database (**DuckDB**), and visualizes insights in a **Streamlit** dashboard.  
All components run in Docker containers orchestrated on Azure; intermediate data and logs are shared through a mounted volume (`/mnt/data/`).

---

##  Azure Resources Used
| Resource | Type | Purpose |
|-----------|------|----------|
| `dashdash` | App Service | Hosts the live Streamlit dashboard |
| `ASP-rcbigdatadev-8676` | App Service Plan | Compute plan for App Service |
| `dagstercontainer` | Azure Container Instance | Runs the Dagster ETL pipeline daily |
| `stabigdatadev` | Storage Account | Mounted as `/mnt/data/` for shared DuckDB and logs |
| `crbigdatadev7` | Container Registry (ACR) | Holds Docker images for dashboard and pipeline |


---

##  Architecture

```text
Arbetsförmedlingen API
      │
      ▼
Dagster Pipeline (ACI)
      │
      ▼
DuckDB Database (/mnt/data/job_ads.duckdb)
      │
      ▼
Streamlit Dashboard (App Service)
```

**Workflow**

1. **Dagster** (running in ACI) fetches new data from the API each day.  
2. The pipeline transforms and stores the data in a DuckDB file (`/mnt/data/job_ads.duckdb`).  
3. **Streamlit** (running in App Service) reads the same DuckDB file and renders interactive analytics.  
4. All files and logs are persisted in Azure Storage (`/mnt/data/`).

---

##  Local Development

```bash
git clone https://github.com/<your-org>/azure-cloud-datapipeline.git
cd azure-cloud-datapipeline
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run dashboard/dashboard.py
```

Default local database path → `/mnt/data/job_ads.duckdb`

---

## 🐳 Docker Build and Push

```bash
az login
az acr login --name crbigdatadev7

docker compose build dashboard
docker tag dashboard:latest crbigdatadev7.azurecr.io/dashboard:latest
docker push crbigdatadev7.azurecr.io/dashboard:latest
```

---

##  Deployment on Azure

### 1️⃣ Streamlit Dashboard (App Service)
- Connected to ACR `crbigdatadev7`  
- Image: `dashboard:latest`  
- Startup command:
  ```bash
  streamlit run dashboard/dashboard.py --server.address=0.0.0.0 --server.port=8501
  ```
- App Settings:
  ```
  DUCKDB_PATH = /mnt/data/job_ads.duckdb
  ```

### 2️⃣ Dagster Container Instance
- Image pulled from ACR  
- Mounts `/mnt/data/`  
- Runs daily ETL job that fetches data from the API and updates DuckDB  
- Logs written to `/mnt/data/logs/`

### 3️⃣ Azure Storage Account
- Mounted to both containers as `/mnt/data/`  
- Holds the DuckDB database, logs, and temporary ETL outputs  

---

## 🧾 Environment Variables
Configure these in **App Service → Configuration → Application Settings**  
and in the Dagster ACI environment:

```
DUCKDB_PATH = /mnt/data/job_ads.duckdb
DLT_STORAGE_PATH = /mnt/data
API_URL = https://jobstream.api.jobtechdev.se
```

---

## ✅ Verification
| Component | Expected Result |
|------------|----------------|
| Streamlit App | Loads at https://dashdash.azurewebsites.net |
| Data Pipeline | Dagster logs confirm daily ETL execution |
| Storage Account | `job_ads.duckdb` updates after each run |
| Dashboard KPIs | Display current vacancies and employer insights |


##  Task 2 – Cost Estimation (Azure Deployment – HR Analytics Project)

This section presents the **final cost estimation** for the HR Analytics – Cloud Deployment project, based on the official calculation from **Azure Pricing Calculator** (Sweden Central region, Pay-as-you-go model).

All resources used in the project are included:  
- Streamlit dashboard (App Service)  
- Dagster ETL container (ACI)  
- Docker image storage (ACR)  
- Blob storage for raw and processed data (Storage Account)

---

### 📊 Estimated Monthly Costs

| Component | Azure Service | Configuration / Usage | Monthly Cost (USD) | Notes |
|------------|----------------|------------------------|--------------------|-------|
| **Streamlit Dashboard** | App Service (Linux, B1 Plan) | 1 instance • 1 vCPU • 1.75 GB RAM • 730 hours/month | **$13.14** | Always-on web app for HR specialists |
| **Dagster Pipeline** | Azure Container Instance | 1 vCPU • 4 GB RAM • 108,000 seconds/month (≈ 1 hour/day) | **$2.01** | Runs ETL & DLT jobs daily |
| **Container Registry** | Azure Container Registry (Basic Tier) | 1 registry • 3 GB used (out of 10 GB included) | **$5.00** | Stores Docker images for Streamlit + Dagster |
| **Data Storage** | Azure Storage Account (Blob Hot, LRS) | 5 GB capacity • 10×10k Write • 10×10k List • 10×10k Read ops | **$1.14** | Stores raw / processed data + logs |
| **Total Estimated Cost** |  |  | **≈ $21.29 per month** |  |

---

### ⚙️ Breakdown and Technical Context

- **App Service (dashdash)**  
  Hosts the Streamlit dashboard. The Basic (B1) plan ensures 24/7 uptime with 1 vCore + 1.75 GB RAM.  
  This service is the largest cost driver (~62% of total).

- **Azure Container Instance (dagstercontainer)**  
  Executes the daily ETL pipeline. With 1 vCore + 4 GB RAM, runtime 1 hour/day, it costs roughly $2/month.

- **Azure Container Registry (crbigdatadev7)**  
  Maintains two Docker images (Dagster + Streamlit). Using the Basic tier (10 GB included), actual usage is ~3 GB.

- **Azure Storage Account (stabigdatadev)**  
  Keeps job-ad data fetched from JobTech API, transformed datasets, and log files.  
  Using 5 GB Hot tier with moderate read/write operations results in ≈ $1.14/month.

---

### 🔧 Assumptions

| Parameter | Value / Description |
|------------|---------------------|
| **Region** | Sweden Central |
| **Pricing model** | Pay-as-you-go |
| **Pipeline schedule** | Daily (1 hour runtime per day) |
| **Dashboard uptime** | Always on |
| **Storage usage** | ≈ 5 GB Hot LRS |
| **Registry usage** | ≈ 3 GB within 10 GB Basic tier |
| **Database** | DuckDB embedded (local compute included in ACI runtime) |
| **Cosmos DB** | Excluded (test only, no cost in final estimate) |

---

### 📈 Optimization Opportunities

| Category | Optimization | Potential Saving |
|-----------|---------------|------------------|
| **App Service Plan** | Switch to **Free (F1)** or **Shared (D1)** during development | − $13 / month |
| **Container Registry** | Use **Docker Hub** (public) instead of private ACR | − $5 / month |
| **Storage Tier** | Move to **Cool Tier** for infrequently accessed data | − 30–40 % of storage cost |
| **ETL Runtime** | Batch multiple jobs to reduce execution time | − $1–2 / month |

With these optimizations, the monthly cost could drop to **$10–12 (€9–11 / ≈ SEK 120–135)** while maintaining functionality.

---

### 🧾 References

- [Azure Pricing Calculator](https://azure.microsoft.com/en-us/pricing/calculator/)  
- [Azure App Service (Linux) Pricing](https://azure.microsoft.com/en-us/pricing/details/app-service/linux/)  
- [Azure Container Instances Pricing](https://azure.microsoft.com/en-us/pricing/details/container-instances/)  
- [Azure Container Registry Pricing](https://azure.microsoft.com/en-us/pricing/details/container-registry/)  
- [Azure Blob Storage Pricing](https://azure.microsoft.com/en-us/pricing/details/storage/blobs/)

---

### ✅ Summary

> **Total Estimated Cloud Cost:** ≈ **$21.29 / month**  
> (≈ €19.6  or  SEK 230 per month)  
>  
> This configuration provides a reliable and scalable cloud setup for the HR Analytics data pipeline, enabling daily data updates and a 24/7 dashboard for talent acquisition specialists.
