# 更新 DNS 记录保持代理开启
# 用法：$env:CF_TOKEN="你的token" .\cf-redirect.ps1

$t = $env:CF_TOKEN
if (-not $t) {
    $tokenFile = Join-Path $PSScriptRoot "cf-token.txt"
    if (Test-Path $tokenFile) { $t = Get-Content $tokenFile -Raw | ForEach-Object { $_.Trim() } }
}
if (-not $t) { Write-Error "请设置 CF_TOKEN 环境变量或创建 cf-token.txt"; exit 1 }

$h = @{ 'Authorization' = 'Bearer ' + $t; 'Content-Type' = 'application/json' }
$z = 'c74a31445fc010b71a4625b9d9098864'

$records = (Invoke-RestMethod -Uri "https://api.cloudflare.com/client/v4/zones/$z/dns_records?name=www.lawskill.cn" -Headers $h).result
foreach ($r in $records) {
    Write-Host "Found: $($r.type) $($r.name) proxied=$($r.proxied)"
    $body = @{type=$r.type; name=$r.name; content=$r.content; ttl=1; proxied=$true} | ConvertTo-Json
    $up = Invoke-RestMethod -Uri "https://api.cloudflare.com/client/v4/zones/$z/dns_records/$($r.id)" -Headers $h -Method Put -Body $body
    Write-Host "Updated: proxied=$($up.result.proxied)"
}
