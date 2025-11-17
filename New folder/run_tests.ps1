Write-Host "=== Starting OCR Validation Tests ===`n" -ForegroundColor Cyan

# Create results directory if it doesn't exist
$resultsDir = "test_results"
if (-not (Test-Path -Path $resultsDir)) {
    New-Item -ItemType Directory -Path $resultsDir | Out-Null
}

# Generate timestamp for results file
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$resultsFile = "$resultsDir/test_results_$timestamp.txt"

# Function to write to both console and file
function Write-TestOutput {
    param([string]$Message)
    Write-Host $Message
    Add-Content -Path $resultsFile -Value $Message
}

# Start the test
Write-TestOutput "=== Test started at $(Get-Date) ==="

# Run the test script
Write-TestOutput "`n=== Running Unit Tests ==="
$unitTestStart = Get-Date

# Run the test script and capture output
$testOutput = python test_ocr_validation.py 2>&1

# Write test output to file and console
Write-TestOutput $testOutput

# Calculate test duration
$testDuration = (Get-Date) - $unitTestStart
Write-TestOutput "`n=== Unit Tests completed in $($testDuration.TotalSeconds.ToString('0.00')) seconds ==="

# Check if server is running
Write-TestOutput "`n=== Checking Server Status ==="
try {
    $response = Invoke-WebRequest -Uri "http://localhost:10000/health" -UseBasicParsing -ErrorAction Stop
    $status = $response.Content | ConvertFrom-Json
    $serverStatus = $status.status
    $tesseractStatus = $status.tesseract
    Write-TestOutput "Server Status: $serverStatus"
    Write-TestOutput "Tesseract Status: $tesseractStatus"
} catch {
    Write-TestOutput "ERROR: Could not connect to server. Make sure the server is running on port 10000"
}

# Generate summary
Write-TestOutput "`n=== Test Summary ==="
Write-TestOutput "Results saved to: $((Get-Item $resultsFile).FullName)"
Write-TestOutput "Test completed at: $(Get-Date)"

Write-Host "`n=== Test Complete ===" -ForegroundColor Green
Write-Host "Results saved to: $((Get-Item $resultsFile).FullName)" -ForegroundColor Green

# Keep the window open
Write-Host "`nPress any key to exit..." -NoNewline
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
