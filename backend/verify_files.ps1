$ErrorActionPreference = "Stop"
$baseUrl = "http://localhost:8001"

Write-Host "1. Creating Store..."
$storeBody = @{
    display_name = "Test Store for Files"
} | ConvertTo-Json

try {
    $store = Invoke-RestMethod -Uri "$baseUrl/stores/" -Method Post -Body $storeBody -ContentType "application/json"
    Write-Host "Store created: $($store.id) - $($store.display_name)"
} catch {
    Write-Host "Failed to create store: $_"
    exit 1
}

$storeId = $store.id

Write-Host "`n2. Uploading File..."
$filePath = "test_upload.txt"
# Create dummy file if not exists (though we created it via tool)
if (-not (Test-Path $filePath)) {
    "Dummy content" | Out-File $filePath
}

try {
    # PowerShell 7+ has -Form, but older might not.
    # We use curl.exe for multipart upload if Invoke-RestMethod is tricky with multipart in older PS.
    # But let's try curl.exe which is reliable for multipart.
    
    # We need to parse the response from curl
    $uploadResponse = curl.exe -s -X POST "$baseUrl/stores/$storeId/files/" -F "file=@$filePath"
    
    if ($LASTEXITCODE -ne 0) {
        throw "Curl failed"
    }
    
    Write-Host "Upload response: $uploadResponse"
    $file = $uploadResponse | ConvertFrom-Json
    Write-Host "File uploaded: $($file.id) - $($file.display_name)"
} catch {
    Write-Host "Failed to upload file: $_"
    # Cleanup store
    Invoke-RestMethod -Uri "$baseUrl/stores/$storeId" -Method Delete
    exit 1
}

$fileId = $file.id

Write-Host "`n3. Listing Files..."
try {
    $files = Invoke-RestMethod -Uri "$baseUrl/stores/$storeId/files/" -Method Get
    Write-Host "Files in store: $($files.total)"
    $files.files | Format-Table id, display_name, status
} catch {
    Write-Host "Failed to list files: $_"
}

Write-Host "`n4. Deleting File..."
try {
    Invoke-RestMethod -Uri "$baseUrl/stores/$storeId/files/$fileId" -Method Delete
    Write-Host "File deleted"
} catch {
    Write-Host "Failed to delete file: $_"
}

Write-Host "`n5. Deleting Store..."
try {
    Invoke-RestMethod -Uri "$baseUrl/stores/$storeId" -Method Delete
    Write-Host "Store deleted"
} catch {
    Write-Host "Failed to delete store: $_"
}

Write-Host "`nVerification Completed Successfully!"
