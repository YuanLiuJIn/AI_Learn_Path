$ErrorActionPreference = 'Stop'
$dest = Join-Path $PSScriptRoot '../docs/physics_foundation_models'
New-Item -ItemType Directory -Force -Path $dest | Out-Null
$queries = @('Poseidon PDE foundation','DPOT PDE','Walrus physics foundation','PROSE PDE foundation','PDE foundation physics informed','PDE foundation model finetuning')
$results = @()
foreach ($q in $queries) {
 try {
  $url='https://api.github.com/search/repositories?q='+[uri]::EscapeDataString($q)+'&per_page=4'
  $r=Invoke-RestMethod -Uri $url -TimeoutSec 30 -Headers @{'User-Agent'='research-survey'}
  foreach ($p in $r.items) {$results += [pscustomobject]@{query=$q;repo=$p.full_name;url=$p.html_url;description=$p.description;default_branch=$p.default_branch}}
 } catch { Write-Output ($q+' ERROR '+$_.Exception.Message) }
 Start-Sleep -Seconds 2
}
$results | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $dest 'github_search.json') -Encoding utf8
$results | ConvertTo-Json -Depth 5
$repos=@('camlab-ethz/poseidon','bitzhangcy/DPOT','PolymathicAI/walrus','microsoft/aurora','ACEsuit/mace','neuraloperator/physics_informed')
foreach ($repo in $repos) {
 try {
  $r=Invoke-RestMethod -Uri ('https://api.github.com/repos/'+$repo+'/readme') -TimeoutSec 30 -Headers @{'User-Agent'='research-survey'}
  $s=[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($r.content))
  $s | Set-Content -LiteralPath (Join-Path $dest (($repo -replace '/','__')+'.md')) -Encoding utf8
  Write-Output ('README '+$repo+' length='+$s.Length)
 } catch {Write-Output ($repo+' ERROR '+$_.Exception.Message)}
 Start-Sleep -Seconds 1
}
