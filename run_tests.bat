@echo off
echo Starting OCR Validation Tests...
echo ==============================

:: Create timestamp for results file
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "timestamp=%dt:~0,4%-%dt:~4,2%-%dt:~6,2%_%dt:~8,2%-%dt:~10,2%"
set "RESULTS_FILE=test_results_%timestamp%.txt"

echo Running tests... This may take a few minutes...
echo.

:: Run the test script and save output
python test_ocr_validation.py > "%RESULTS_FILE%" 2>&1

:: Display completion message
echo.
echo ==============================
echo Test results have been saved to: %cd%\%RESULTS_FILE%
echo ==============================

:: Keep the window open
pause
