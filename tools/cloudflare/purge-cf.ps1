# 清除 Cloudflare 全站缓存
# 用法：$env:CF_TOKEN="你的token" .\purge-cf.ps1
# 或先在同目录创建 cf-token.txt 写入 token

$t = $env:CF_TOKEN
if (-not $t) {
    $tokenFile = Join-Path $PSScriptRoot "cf-token.txt"
    if (Test-Path $tokenFile) { $t = Get-Content $tokenFile -Raw | ForEach-Object { $_.Trim() } }
}
if (-not $t) { Write-Error "请设置 CF_TOKEN 环境变量或创建 cf-token.txt"; exit 1 }

$h = @{ 'Authorization' = 'Bearer ' + $t; 'Content-Type' = 'application/json' }
$z = 'c74a31445fc010b71a4625b9d9098864'
$body = '{"purge_everything":true}'
$r = Invoke-RestMethod -Uri "https://api.cloudflare.com/client/v4/zones/$z/purge_cache" -Headers $h -Method Post -Body $body
$r | ConvertTo-Json -Depth 2
