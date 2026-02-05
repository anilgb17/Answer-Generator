# Test the Question Answer Generator API

Write-Host "Testing Question Answer Generator API..." -ForegroundColor Green

# Test 1: Health Check
Write-Host "`n1. Testing health endpoint..." -ForegroundColor Yellow
$health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
Write-Host "Health Status: $($health.status)" -ForegroundColor Cyan

# Test 2: Get Languages
Write-Host "`n2. Testing languages endpoint..." -ForegroundColor Yellow
$languages = Invoke-RestMethod -Uri "http://localhost:8000/api/languages" -Method Get
Write-Host "Supported Languages: $($languages.languages.Count)" -ForegroundColor Cyan

# Test 3: Upload File
Write-Host "`n3. Testing file upload..." -ForegroundColor Yellow
$filePath = "test_question.txt"

if (Test-Path $filePath) {
    $fileBytes = [System.IO.File]::ReadAllBytes((Resolve-Path $filePath))
    $fileContent = [System.Text.Encoding]::GetString($fileBytes)
    
    $boundary = [System.Guid]::NewGuid().ToString()
    $LF = "`r`n"
    
    $bodyLines = (
        "--$boundary",
        "Content-Disposition: form-data; name=`"file`"; filename=`"test_question.txt`"",
        "Content-Type: text/plain$LF",
        $fileContent,
        "--$boundary",
        "Content-Disposition: form-data; name=`"language`"$LF",
        "en",
        "--$boundary--$LF"
    ) -join $LF
    
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/api/upload" `
            -Method Post `
            -ContentType "multipart/form-data; boundary=$boundary" `
            -Body $bodyLines
        
        Write-Host "Upload successful!" -ForegroundColor Green
        Write-Host "Session ID: $($response.session_id)" -ForegroundColor Cyan
        Write-Host "Status: $($response.status)" -ForegroundColor Cyan
        
        # Test 4: Check Status
        Write-Host "`n4. Checking processing status..." -ForegroundColor Yellow
        $sessionId = $response.session_id
        
        for ($i = 1; $i -le 10; $i++) {
            Start-Sleep -Seconds 3
            $status = Invoke-RestMethod -Uri "http://localhost:8000/api/status/$sessionId" -Method Get
            Write-Host "Progress: $($status.progress)% - $($status.message)" -ForegroundColor Cyan
            
            if ($status.status -eq "complete") {
                Write-Host "`nProcessing complete!" -ForegroundColor Green
                Write-Host "Answers generated: $($status.answers.Count)" -ForegroundColor Cyan
                break
            }
            elseif ($status.status -eq "error") {
                Write-Host "`nProcessing failed!" -ForegroundColor Red
                break
            }
        }
        
    } catch {
        Write-Host "Upload failed: $_" -ForegroundColor Red
    }
} else {
    Write-Host "Test file not found: $filePath" -ForegroundColor Red
}

Write-Host "`nTest complete!" -ForegroundColor Green
