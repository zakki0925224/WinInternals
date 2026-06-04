# cleanup_vcxproj.ps1
# Directory.Build.props/targetsに委譲する形にvcxprojを整理する
#
# 使い方:
#   # 単一ファイル
#   .\cleanup_vcxproj.ps1 -Path .\Aarw\Aarw.vcxproj
#
#   # ソリューション配下を一括処理
#   .\cleanup_vcxproj.ps1 -All
#
#   # 確認だけ (ファイルを変更しない)
#   .\cleanup_vcxproj.ps1 -All -DryRun

param(
    [string]$Path,
    [switch]$All,
    [switch]$DryRun
)

# Directory.Build.targetsで管理するプロパティ
# vcxproj側から削除する対象
$DELEGATED_COMPILE_PROPS = @(
    "WarningLevel",
    "Optimization",
    "FunctionLevelLinking",
    "IntrinsicFunctions",
    "SDLCheck",
    "BufferSecurityCheck",
    "ControlFlowGuard",
    "RuntimeLibrary",
    "LanguageStandard"
)

$DELEGATED_LINK_PROPS = @(
    "GenerateDebugInformation",
    "OptimizeReferences",
    "RandomizedBaseAddress",
    "DataExecutionPrevention",
    "ImageHasSafeExceptionHandlers",
    "GuardCF"
)

# Directory.Build.propsで管理するプロパティ
$DELEGATED_OUTPUT_PROPS = @(
    "OutDir",
    "IntDir",
    "OutDirWasSpecified",
    "WholeProgramOptimization"
)

function Clean-Vcxproj {
    param([string]$FilePath)

    $xml = [xml](Get-Content $FilePath -Encoding UTF8)
    $ns = New-Object System.Xml.XmlNamespaceManager($xml.NameTable)
    $ns.AddNamespace("ms", "http://schemas.microsoft.com/developer/msbuild/2003")
    $changed = $false

    # 1. Debug構成エントリを削除 (ProjectConfiguration)
    $debugConfigs = $xml.SelectNodes(
        "//ms:ProjectConfiguration[contains(@Include, 'Debug')]", $ns
    )
    foreach ($node in $debugConfigs) {
        $node.ParentNode.RemoveChild($node) | Out-Null
        $changed = $true
    }

    # 2. Debug条件のPropertyGroup / ItemDefinitionGroup / ImportGroup を削除
    $debugNodes = $xml.SelectNodes(
        "//*[contains(@Condition, 'Debug')]", $ns
    )
    foreach ($node in $debugNodes) {
        $node.ParentNode.RemoveChild($node) | Out-Null
        $changed = $true
    }

    # 3. Release の ItemDefinitionGroup を削除 (Directory.Build.targetsに委譲)
    $releaseIdg = $xml.SelectNodes(
        "//ms:ItemDefinitionGroup[contains(@Condition, 'Release')]", $ns
    )
    foreach ($node in $releaseIdg) {
        $node.ParentNode.RemoveChild($node) | Out-Null
        $changed = $true
    }

    # 4. Release の PropertyGroup から委譲済みプロパティを削除
    $releasePg = $xml.SelectNodes(
        "//ms:PropertyGroup[contains(@Condition, 'Release')]", $ns
    )
    foreach ($pg in $releasePg) {
        foreach ($prop in $DELEGATED_OUTPUT_PROPS) {
            $node = $pg.SelectSingleNode("ms:$prop", $ns)
            if ($node) {
                $pg.RemoveChild($node) | Out-Null
                $changed = $true
            }
        }
        # PropertyGroupが空になったら削除 (Label="Configuration"は残す)
        $label = $pg.GetAttribute("Label")
        if ($label -ne "Configuration" -and $pg.ChildNodes.Count -eq 0) {
            $pg.ParentNode.RemoveChild($pg) | Out-Null
        }
    }

    # 5. Globals / UserMacros等のPropertyGroupから委譲済みプロパティを削除
    $allPg = $xml.SelectNodes(
        "//ms:PropertyGroup[not(@Condition)]", $ns
    )
    foreach ($pg in $allPg) {
        foreach ($prop in ($DELEGATED_OUTPUT_PROPS + $DELEGATED_COMPILE_PROPS)) {
            $node = $pg.SelectSingleNode("ms:$prop", $ns)
            if ($node) {
                $pg.RemoveChild($node) | Out-Null
                $changed = $true
            }
        }
    }

    if (-not $changed) {
        Write-Host "  (変更なし)" -ForegroundColor DarkGray
        return
    }

    if ($DryRun) {
        Write-Host "  [DryRun] 変更あり (ファイルは保存しない)" -ForegroundColor Yellow
    } else {
        $xml.Save($FilePath)
        Write-Host "  保存完了" -ForegroundColor Green
    }
}

# エントリポイント
if ($All) {
    $targets = Get-ChildItem -Recurse -Filter "*.vcxproj"
} elseif ($Path) {
    $targets = @(Get-Item $Path)
} else {
    Write-Error "-Path または -All を指定してください"
    exit 1
}

foreach ($file in $targets) {
    Write-Host "$($file.Name)" -ForegroundColor Cyan
    Clean-Vcxproj -FilePath $file.FullName
}
