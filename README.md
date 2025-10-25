## 💰 Task 2 – Cost Estimation (Azure Deployment – HR Analytics Project)

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
