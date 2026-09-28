$ErrorActionPreference = 'Stop'
$outDir = Join-Path $PSScriptRoot '../docs/pinn_recent_survey/sources'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$sources = @{
 'hidden_physics'='https://www.nature.com/articles/s42005-026-02743-z';
 'weak_form'='https://www.nature.com/articles/s41598-025-24427-4';
 'schlieren'='https://link.springer.com/article/10.1007/s00348-026-04268-1';
 'battery_hard'='https://www.mdpi.com/2032-6653/17/5/275';
 'tunnel_transfer'='https://www.mdpi.com/2227-7390/14/11/1846';
 'budget_evaluation'='https://www.mdpi.com/2076-3417/16/19/9508'
}
foreach ($key in $sources.Keys) {
 try {
  $r=Invoke-WebRequest -Uri $sources[$key] -TimeoutSec 35
  $r.Content | Set-Content -LiteralPath (Join-Path $outDir ($key+'.html')) -Encoding utf8
  Write-Output ($key+' '+$r.StatusCode+' length='+$r.Content.Length)
 } catch { Write-Output ($key+' ERROR '+$_.Exception.Message) }
}
