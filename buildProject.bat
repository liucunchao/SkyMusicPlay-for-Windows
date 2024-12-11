@echo off
setlocal enabledelayedexpansion

:: ��ʾ��ǰĿ¼
echo %~dp0

:: ���� Electron Ӧ��
cd %~dp0sky-music-web
call npm run electron:build

:: ���� Python ������
cd %~dp0sky-music-server
call .venv\Scripts\activate
call pyinstaller --uac-admin -w sky-music-server.py --distpath %~dp0sky-music-web\dist_electron\win-unpacked\backend_dist --hidden-import=main
call deactivate

:: ���� ffmpeg ��ִ���ļ�
copy %~dp0ffmpeg.exe %~dp0sky-music-web\dist_electron\win-unpacked\backend_dist\sky-music-server\ffmpeg.exe

:: ����Դ·����Ŀ��·��
set source="%~dp0template-resources"
set destination="%~dp0sky-music-web\dist_electron\win-unpacked\resources"

echo ���ڸ����ļ���...
robocopy %source% %destination% /E /Z /COPYALL /R:3 /W:5
:: ɾ��Ŀ���ļ��������е� .gitkeep �ļ�
echo ����ɾ��Ŀ���ļ����е� .gitkeep �ļ�...
for /r %destination% %%f in (*.gitkeep) do (
    del /f /q "%%f"
)
echo �ļ��и��Ʋ�������ɣ�


echo.
echo �ļ�������ɣ�
pause
