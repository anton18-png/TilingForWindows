@echo off
chcp 65001 >nul

cd C:\Apps\TilingForWindows

echo Установка шрифтов JetBrains Mono Nerd Font...
echo.

:: Проверка прав администратора
NET FILE >nul 2>&1
if '%errorlevel%' NEQ '0' (
    echo ОШИБКА: Запустите от имени администратора!
    pause
    exit /b 1
)

:: Установка всех .ttf файлов из папки Fonts
if exist "C:\Apps\TilingForWindows\Fonts" (
    echo Устанавливаю шрифты...
    xcopy /Y /I "C:\Apps\TilingForWindows\Fonts\*.ttf" "%windir%\Fonts\" >nul
    
    :: Регистрация шрифтов в реестре
    for %%f in ("C:\Apps\TilingForWindows\Fonts\*.ttf") do (
        reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" /v "%%~nf (TrueType)" /t REG_SZ /d "%%~nxf" /f >nul
    )
    
    echo Шрифты установлены!
) else (
    echo Папка Fonts не найдена!
    pause
    exit /b 1
)

:: Импорт настроек Nexus
if exist "nexus_config.reg" (
    echo Импортирую настройки Nexus...
    reg import "nexus_config.reg"
    nexussetup.exe /SILENT /VERYSILENT
    echo Настройки Nexus импортированы!
)

if exist glazewm xcopy /Y /E glazewm\* "%USERPROFILE%\.glzr\glazewm\"\
if exist yasb xcopy /Y /E yasb\* "%USERPROFILE%\.config\yasb\"\

echo.
echo Установка завершена!
echo Рекомендуется перезагрузить компьютер.
echo.
@REM pause
start "" "C:\Apps\TilingForWindows\TilingForWindows.exe"