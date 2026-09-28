# 把「引用块原文 + **译**：中文」结构的双语稿，转换为中英左右分栏（Markdown 表格）并排版。
# 用法: powershell -ExecutionPolicy Bypass -File make_sidebyside.ps1 -Src <旧稿> -Dst <新稿>
param(
    [Parameter(Mandatory = $true)][string]$Src,
    [Parameter(Mandatory = $true)][string]$Dst
)

$ErrorActionPreference = 'Stop'

$C1 = [string][char]1   # 代码块行前缀
$C2 = [string][char]2   # 由配对生成、需要表头的表格行前缀

# 用码点拼中文，避免脚本文件编码造成乱码
$zhCN      = [string][char]0x4E2D + [string][char]0x6587                                                  # 中文
$zhTrans   = [string][char]0x8BD1 + [string][char]0x6587                                                  # 译文
$zhPending = [string][char]0xFF08 + [string][char]0x5F85 + [string][char]0x8BD1 + [string][char]0xFF09     # （待译）
$dash      = [string][char]0x2014 + [string][char]0x2014                                                  # ——

# 仅用于识别译稿开头的编者说明块（原文出处 / 译文说明 / 翻译进度）
$META = @(
    ([string][char]0x539F + [string][char]0x6587 + [string][char]0x51FA + [string][char]0x5904),
    ([string][char]0x8BD1 + [string][char]0x6587 + [string][char]0x8BF4 + [string][char]0x660E),
    ([string][char]0x7FFB + [string][char]0x8BD1 + [string][char]0x8FDB + [string][char]0x5EA6)
)

$HEADER = '| Original text (English) | ' + $zhCN + $zhTrans + ' |'
$SEP = '|:---|:---|'

$lines = [System.IO.File]::ReadAllLines($Src, [System.Text.Encoding]::UTF8)

$res = New-Object System.Collections.Generic.List[string]
$en = New-Object System.Collections.Generic.List[string]
$cn = New-Object System.Collections.Generic.List[string]
$inTrans = $false
$inCode = $false
$afterBlank = $false
$codeBuf = New-Object System.Collections.Generic.List[string]

function Esc([string]$s) { return $s.Replace('|', '\|') }

function FlushPair {
    if ($script:en.Count -eq 0 -and $script:cn.Count -eq 0) { return }
    $e = Esc (($script:en -join '<br>').Trim())
    $c = Esc (($script:cn -join '<br>').Trim())
    if ($e -eq '') { $e = $script:dash }
    if ($c -eq '') { $c = $script:zhPending }
    $script:res.Add($script:C2 + '| ' + $e + ' | ' + $c + ' |')
    $script:en.Clear(); $script:cn.Clear()
}

foreach ($raw in $lines) {
    $ln = $raw

    # ---- 代码块（公式、伪代码）：并入当前对照行，保持表格连续 ----
    if ($inCode) {
        if ($ln.TrimEnd().StartsWith('```')) {
            $inCode = $false
            $code = ($codeBuf -join '<br>').Trim()
            if ($code -ne '') { $en.Add($code); $cn.Add($code) }
            FlushPair
            $codeBuf.Clear()
        }
        else { $codeBuf.Add($ln.TrimEnd()) }
        continue
    }
    if ($ln.TrimEnd().StartsWith('```')) {
        $inTrans = $false
        $afterBlank = $false
        $inCode = $true
        continue
    }

    # ---- 原文引用块 ----
    if ($ln -match '^>\s?(.*)$') {
        $inner = $Matches[1]
        # 仅译稿开头的编者说明块（> **原文出处**：… 等）原样保留为文本，不进对照表
        $isMeta = $false
        foreach ($ml in $META) { if ($inner.StartsWith('**' + $ml + '**')) { $isMeta = $true; break } }
        # 译者补充说明：以 〔 或 【 开头的方括号标签，本身就是中文，不需要对照
        if ($inner.StartsWith('**' + [string][char]0x3014) -or $inner.StartsWith('**' + [string][char]0x3010)) { $isMeta = $true }
        if ($isMeta) {
            FlushPair
            $inTrans = $false
            $afterBlank = $false
            $res.Add('> ' + $inner)
            continue
        }
        if ($cn.Count -gt 0) { FlushPair }
        elseif ($afterBlank -and $en.Count -gt 0) { FlushPair }
        $inTrans = $false
        $afterBlank = $false
        $en.Add($inner)
        continue
    }

    # ---- 译文行：**X**：... 且标签长度为 1 ----
    if ($ln -match '^\*\*(?<lab>[^*]+)\*\*[:\uFF1A]?\s*(?<rest>.*)$' -and $Matches['lab'].Length -eq 1) {
        $inTrans = $true
        $afterBlank = $false
        $rest = $Matches['rest'].Trim()
        if ($rest -ne '') { $cn.Add($rest) }
        continue
    }

    # ---- 空行 ----
    if ($ln.Trim() -eq '') {
        if ($en.Count -gt 0 -and $cn.Count -gt 0) { FlushPair }
        $inTrans = $false
        $afterBlank = $true
        continue
    }

    # ---- 小节标签行：**English / 中文** 转为一行双语对照，避免打断表格 ----
    if ($ln -match '^\*\*(?<a>[^*]+?)\s+/\s+(?<b>[^*]+)\*\*\s*$') {
        FlushPair
        $inTrans = $false
        $afterBlank = $false
        $a = Esc $Matches['a'].Trim()
        $b = Esc $Matches['b'].Trim()
        $res.Add($C2 + '| **' + $a + '** | **' + $b + '** |')
        continue
    }

    # ---- 译文续行 ----
    if ($inTrans -and $cn.Count -ge 0 -and -not $ln.Trim().StartsWith('|') -and -not $ln.Trim().StartsWith('#')) {
        $cn.Add($ln.Trim())
        $afterBlank = $false
        continue
    }

    # ---- 其他一切（标题、编者说明、源文件自带表格等） ----
    FlushPair
    $inTrans = $false
    $afterBlank = $false
    $res.Add($ln)
}
FlushPair

# ---- 规范化：块之间补空行；对配对生成的表格块插入两列表头 ----
$final = New-Object System.Collections.Generic.List[string]
$prevType = 'none'
foreach ($l in $res) {
    $isCode = $l.StartsWith($C1)
    $isPair = $l.StartsWith($C2)
    $body = $l
    if ($isCode -or $isPair) { $body = $l.Substring(1) }
    $t = $body.Trim()

    if ($isCode) { $type = 'code' }
    elseif ($t -eq '') { continue }
    elseif ($t.StartsWith('|')) { $type = 'row' }
    elseif ($t.StartsWith('#')) { $type = 'head' }
    elseif ($t -eq '---') { $type = 'rule' }
    else { $type = 'text' }

    if ($type -ne 'code' -and $prevType -ne 'none' -and $type -ne $prevType) {
        if ($final.Count -gt 0 -and $final[$final.Count - 1].Trim() -ne '') { $final.Add('') }
    }
    if ($type -eq 'row' -and $isPair -and $prevType -ne 'row') {
        $final.Add($HEADER)
        $final.Add($SEP)
    }
    $final.Add($body)
    $prevType = $type
}

$text = ($final -join "`r`n")
[System.IO.File]::WriteAllText($Dst, $text, (New-Object System.Text.UTF8Encoding($false)))
Write-Output ("written: " + $Dst + "  lines=" + $final.Count)
