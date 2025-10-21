resource "azurerm_storage_account" "my_storage" {
  name                     = "mystorage${random_string.suffix.result}"
  account_tier             = "Standard"
  location                 = var.location
  resource_group_name      = azurerm_resource_group.storage_rg_Mary.name
  account_replication_type = "LRS"

  tags = { environment = "staging" }
}

resource "azurerm_storage_container" "csv_container" {
  name                  = "youtube-analytics"
  storage_account_id    = azurerm_storage_account.my_storage.id
  container_access_type = "private"
}

resource "azurerm_storage_blob" "upload_csv" {
  for_each               = fileset("data", "*.csv")
  name                   = each.value
  storage_account_name   = azurerm_storage_account.my_storage.name
  storage_container_name = azurerm_storage_container.csv_container.name
  type                   = "Block"
  source                 = "data/${each.value}"
}
 resource "azurerm_storage_blob" "upload_csv" {
   name                   = "Totalt.csv"
   storage_account_name   = azurerm_storage_account.my_storage.name
   storage_container_name = azurerm_storage_container.csv_container.name
   type                   = "Block"
   source                 = "data/Totalt.csv"
 }
