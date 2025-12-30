@echo off
echo ========================================
echo SCADA System Docker Build for Windows
echo ========================================
echo.

echo Checking Docker status...
docker version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo Docker is running...
echo.

echo Stopping any existing containers...
docker-compose down

echo.
echo Building containers (this may take a few minutes)...
docker-compose build --no-cache

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo Check WINDOWS_SETUP.txt for troubleshooting steps.
    pause
    exit /b 1
)

echo.
echo Build successful!
echo Starting containers...
docker-compose up -d

if errorlevel 1 (
    echo.
    echo ERROR: Failed to start containers!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Containers are running!
echo ========================================
echo Vulnerable System: http://localhost:5002
echo Patched System:    http://localhost:5001
echo.
echo Username: admin
echo Password: admin123
echo.
echo To view logs: docker-compose logs -f
echo To stop:      docker-compose down
echo ========================================
pause

