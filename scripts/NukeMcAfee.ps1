# NukeMcAfee.ps1 — McAfee Exorcism Tool by ChatGPT x Q
# Total wipe: services, registry, scheduled tasks, folders, files.
# Must be run as Administrator.

$LogPath = "$env:SystemDrive\McAfee_KillLog.txt"
$Targets = @(
    "HKLM:\SYSTEM\CurrentControlSet\Services\McCHSvc",
    "HKLM:\SOFTWARE\McAfee",
    "HKLM:\SOFTWARE\WOW6432Node\McAfee",
    "HKCU:\SOFTWARE\McAfee",
    "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run\McAfee*"
)
$FilePaths = @(
    "C:\Program Files\McAfee",
    "C:\Program Files (x86)\McAfee",
    "C:\ProgramData\McAfee",
    "$env:LOCALAPPDATA\McAfee",
    "$env:APPDATA\McAfee"
)

# Function to write to log
function Log {
    param ($msg)
    $timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    "$timestamp - $msg" | Out-File -Append $LogPath
}

# Start logging
Log "=========== McAfee NUKE STARTED ==========="

# 1. Stop and disable services
$mcSvcs = Get-Service | Where-Object { $_.DisplayName -match "McAfee" }
foreach ($svc in $mcSvcs) {
    try {
        Stop-Service $svc.Name -Force -ErrorAction SilentlyContinue
        Set-Service $svc.Name -StartupType Disabled
        Log "Stopped and disabled service: $($svc.DisplayName)"
    } catch {
        Log "Failed to stop/disable service: $($svc.DisplayName)"
    }
}

# 2. Kill McAfee-related processes
$mcProcs = Get-Process | Where-Object { $_.Name -like "*mcafee*" }
foreach ($proc in $mcProcs) {
    try {
        Stop-Process -Id $proc.Id -Force
        Log "Killed process: $($proc.Name)"
    } catch {
        Log "Failed to kill process: $($proc.Name)"
    }
}

# 3. Delete scheduled tasks
$tasks = Get-ScheduledTask | Where-Object { $_.TaskName -match "McAfee" }
foreach ($task in $tasks) {
    try {
        Unregister-ScheduledTask -TaskName $task.TaskName -Confirm:$false
        Log "Deleted task: $($task.TaskName)"
    } catch {
        Log "Failed to delete task: $($task.TaskName)"
    }
}

# 4. Remove registry keys
foreach ($key in $Targets) {
    try {
        if (Test-Path $key) {
            Remove-Item -Path $key -Recurse -Force
            Log "Deleted registry key: $key"
        }
    } catch {
        Log "Failed to delete registry key: $key"
    }
}

# 5. Remove files and folders
foreach ($path in $FilePaths) {
    try {
        if (Test-Path $path) {
            Remove-Item -Path $path -Recurse -Force
            Log "Deleted folder: $path"
        }
    } catch {
        Log "Failed to delete folder: $path"
    }
}

# 6. Check leftover entries in event logs (optional)
$events = Get-WinEvent -FilterHashtable @{
    LogName = 'System'
    StartTime = (Get-Date).AddHours(-1)
} | Where-Object { $_.Message -match 'McAfee' }

foreach ($event in $events) {
    Log "Leftover Event: $($event.TimeCreated) - $($event.Message)"
}

# Done
Log "=========== McAfee NUKE COMPLETED ==========="
Write-Host "`n✅ McAfee has been evicted. Log saved at $LogPath" -ForegroundColor Green
