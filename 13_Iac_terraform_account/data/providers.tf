terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.4" # 4.4 ≤ x ≤ 5.0
    }
  }
  # pessimistic operator 
  # 1.12 ≤ x ≤ 2.0
  required_version = "~> 1.12"
}

provider "azurerm" {
  features {

  }
}

