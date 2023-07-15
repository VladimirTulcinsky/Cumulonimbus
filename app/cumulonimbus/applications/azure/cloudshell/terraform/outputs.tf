output "domain_name" {
  value = data.azuread_domains.aad_domains.domains.*.domain_name[0]
}
