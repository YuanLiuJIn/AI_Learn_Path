$ErrorActionPreference = 'Stop'
$outDir = Join-Path $PSScriptRoot '../docs/pinn_recent_survey'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$queries = @(
 'physics informed neural networks optimizer preconditioning',
 'physics informed neural networks adaptive sampling weighting',
 'physics informed neural networks Kolmogorov Arnold',
 'physics informed neural networks domain decomposition multiscale',
 'physics informed neural networks hard constraints conservation',
 'physics informed neural networks transfer learning parametric',
 'physics informed neural networks inverse experimental',
 'physics informed neural networks uncertainty model misspecification',
 'physics informed neural networks weak form discontinuities',
 'physics informed neural networks causal long time',
 'physics informed neural networks battery experimental',
 'physics informed neural networks benchmark limitations'
)
$all = @()
foreach ($q in $queries) {
 $url = 'https://api.crossref.org/works?query.title=' + [uri]::EscapeDataString($q) + '&filter=from-pub-date:2024-09-27,until-pub-date:2026-09-27,type:journal-article&rows=12&sort=relevance&select=DOI,title,published,published-online,published-print,container-title,abstract,URL'
 try {
  $r = $null
  for ($attempt=0; $attempt -lt 3; $attempt++) {
   try { $r = Invoke-RestMethod -Uri $url -TimeoutSec 45; break }
   catch { if ($attempt -eq 2) { throw }; Start-Sleep -Seconds 4 }
  }
  foreach ($p in $r.message.items) {
   $all += [pscustomobject]@{query=$q;title=(@($p.title) -join ' ');doi=$p.DOI;date=$p.published.'date-parts';online=$p.'published-online'.'date-parts';journal=(@($p.'container-title') -join ' ');abstract=$p.abstract;url=$p.URL}
  }
 } catch { Write-Output ('ERROR: '+$q+' '+$_.Exception.Message) }
 Start-Sleep -Seconds 2
}
$all | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $outDir 'crossref_candidates.json') -Encoding utf8
$all | ForEach-Object { [pscustomobject]@{query=$_.query;title=$_.title;doi=$_.doi;date=($_.date -join '-');abstract_present=[bool]$_.abstract} } | ConvertTo-Json -Depth 4
