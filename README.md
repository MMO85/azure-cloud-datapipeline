# azure-cloud-datapipeline
## 💰 Task 2 – Cost Estimation

This section provides an estimation of the **monthly cost** of running the HR Analytics data pipeline and dashboard on Microsoft Azure.  
All resources are deployed in the **Sweden Central** region using the **Pay-as-you-go** pricing model.  
The purpose of this estimation is to give management a clear overview of what it would cost to keep the system running continuously in production.

---

### 🧩 Overview of Resources

The project consists of four main Azure components:

1. **Data Extraction & Transformation (Dagster + DLT)**  
   Runs once per day inside a **Container Instance** that connects to the JobTech API and updates the DuckDB data warehouse.

2. **Data Visualization (Streamlit Dashboard)**  
   Hosted on an **Azure App Service** under a Basic (B1) plan so it remains online 24/7 and accessible for HR specialists.

3. **Data & File Storage**  
   Raw CSV/JSON data, transformed files and logs are stored in a **Storage Account** (Blob Storage V2).

4. **Container Registry**  
   A private **Azure Container Registry (ACR)** stores Docker images for the Dagster pipeline and Streamlit dashboard.

---

### 📊 Estimated Monthly Costs

| Component | Azure Service | Configuration / Usage | Est. Monthly Cost (EUR) | Est. Monthly Cost (SEK) |
|------------|----------------|------------------------|--------------------------|--------------------------|
| **Streamlit Dashboard** | App Service Plan (ASP-rcbigdatadev-8676) | Linux B1 plan, Always On, 1 instance | **€ 12.00** | ≈ SEK 136 |
| **Dagster Pipeline** | Azure Container Instance (dagstercontainer) | 1 vCPU + 4 GB RAM, 1 hr/day × 30 days | **€ 1.85** | ≈ SEK 21 |
| **Docker Images** | Azure Container Registry (crbigdatadev7) | Basic tier (10 GB included), 3 GB used | **€ 4.60** | ≈ SEK 52 |
| **Data Storage** | Azure Storage Account (stabigdatadev) | Blob Storage V2 Hot tier, 5 GB LRS | **€ 1.05** | ≈ SEK 12 |
| **Network + Monitoring** | Bandwidth + Application Insights | ~10 GB outbound traffic + basic logs | **€ 0.50** | ≈ SEK 6 |
| **Total Estimated Cost** | | | **≈ € 19.5 / month** | **≈ SEK 225 / month** |

---

### ⚙️ Assumptions and Methodology

- **Region:** Sweden Central  
- **Pricing model:** Pay-as-you-go (no reserved instances)  
- **Pipeline schedule:** Dagster container runs **once per day**, runtime ≈ 1 hour.  
- **Dashboard:** App Service (Streamlit) is **always on** for users.  
- **DuckDB:** Runs locally inside the container, so no extra database compute cost.  
- **Storage usage:** ~5 GB in Hot tier (LRS replication).  
- **Container Registry:** 3 GB used within the Basic tier (10 GB included).  
- **Cosmos DB accounts** were used only for testing and are **excluded** from active costs.

---

### 🔍 Cost Drivers and Optimization Options

| Category | Explanation | Optimization Tip |
|-----------|--------------|------------------|
| **App Service Plan** | Major cost (~60 % of total). Keeps dashboard always online. | Could switch to **Free (F1)** or **Shared (D1)** plan for testing environments. |
| **Container Registry** | Stores Docker images (3 GB used). | Move images to **Docker Hub** → save € 4–5 / month. |
| **Storage Account** | Minimal cost; scales with dataset size. | Change tier to **Cool** if data is accessed rarely. |
| **Container Instance** | Lightweight cost for ETL execution. | Batch multiple jobs in one run to keep runtime short. |

With small optimizations, the monthly cost could drop below **€ 10 / SEK 115**, making the deployment very economical for a small data-engineering team.

---

### 🧾 References

- [Azure Pricing Calculator](https://azure.microsoft.com/en-us/pricing/calculator/)  
- [Azure App Service Pricing Details](https://azure.microsoft.com/en-us/pricing/details/app-service/linux/)  
- [Azure Container Instances Pricing](https://azure.microsoft.com/en-us/pricing/details/container-instances/)  
- [Azure Blob Storage Pricing](https://azure.microsoft.com/en-us/pricing/details/storage/blobs/)  
- [Azure Container Registry Pricing](https://azure.microsoft.com/en-us/pricing/details/container-registry/)

---

### ✅ Summary

> The total estimated cost for running the **HR Analytics – Cloud Deployment** pipeline is around  
> **€ 19.5 per month (≈ SEK 225)** under current usage conditions.  
> This setup provides a scalable, automated, and continuously available analytics platform for HR talent acquisition specialists.

