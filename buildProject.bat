@echo off

:: ����ű���ԭʼ·��
set script_dir=%~dp0

:: ����Ƿ��Թ���Ա�������
powershell -Command "if (-not ([Security.Principal.WindowsPrincipal]([Security.Principal.WindowsIdentity]::GetCurrent())).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { exit 1 }"
if %errorlevel% neq 0 (
    echo This script requires administrator privileges.
    echo Attempting to restart with administrator rights...
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

:: ���û���������֧���ӳٱ�����չ
setlocal enabledelayedexpansion

:: ������ǹ���ԱȨ�ޣ������ִ�нű�
echo Script successfully running as administrator!

:: �л����ű�����Ŀ¼
cd /d "%script_dir%"

:: ��ʾ��ǰĿ¼
echo Current script directory: %script_dir%

:: ɾ���ɵ� Electron ����Ŀ¼
rmdir /S /Q "%script_dir%sky-music-web\dist"
:: ɾ��python�Ĺ���Ŀ¼
rmdir /S /Q "%script_dir%sky-music-server\build"

:: ���� Electron Ӧ��
cd "%script_dir%sky-music-web"
call npm run build:win

:: ���� Python ������
cd "%script_dir%sky-music-server"
call .venv\Scripts\activate
call pyinstaller --uac-admin -w sky-music-server.py --distpath "%script_dir%sky-music-web\dist\win-unpacked\backend_dist" --hidden-import=main
call deactivate

:: ���� ffmpeg ��ִ���ļ�
copy "%script_dir%ffmpeg.exe" "%script_dir%sky-music-web\dist\win-unpacked\backend_dist\sky-music-server\ffmpeg.exe"

:: ����Դ·����Ŀ��·��
set source="%script_dir%template-resources"
set destination="%script_dir%sky-music-web\dist\win-unpacked\resources"

:: ʹ�� robocopy �����ļ�����������
echo Copying files with robocopy...
robocopy %source% %destination% /E /Z /COPYALL /R:3 /W:5

:: ɾ��Ŀ���ļ����µ����� .gitkeep �ļ�
echo Cleaning up .gitkeep files...
for /r "%destination%" %%f in (*.gitkeep) do (
    del /f /q "%%f"
)

echo File copy and cleanup completed!

:: �����ʾ
echo.
echo All tasks completed successfully!
pause
