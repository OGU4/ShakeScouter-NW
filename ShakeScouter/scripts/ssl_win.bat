@ECHO OFF
SETLOCAL

SET HOSTNAME=localhost

SET ENVFILE=..\.env.test
SET ENVSAMPLE_FILE=..\.env.sample

SET DEVDIR=..\.dev
SET SSLDIR=%DEVDIR%\ssl

REM Check mkcert
CALL :EXECUTE_FUNCTION "winget ls -q FiloSottile.mkcert -e --disable-interactivity | FINDSTR /i mkcert" && (
	winget install mkcert -h
	CALL ssl_win.bat
	EXIT -1
)
CALL mkcert -install

REM Check folders
IF NOT EXIST %DEVDIR% (
	MD %DEVDIR%
)
IF NOT EXIST %SSLDIR% (
	MD %SSLDIR%
)

REM Create SSL server certificate
CALL mkcert %HOSTNAME%

REM Move files
MOVE "%HOSTNAME%.pem" "%SSLDIR%\%HOSTNAME%.crt"
MOVE "%HOSTNAME%-key.pem" "%SSLDIR%\%HOSTNAME%.key"

REM Copy `.env` if not exists
IF NOT EXIST %ENVFILE% (
	COPY %ENVSAMPLE_FILE% %ENVFILE%
)

REM Write SSL files
ECHO WS_SSLCERT=%SSLDIR%\%HOSTNAME%.crt> %ENVFILE%
ECHO WS_SSLKEY=%SSLDIR%\%HOSTNAME%.key> %ENVFILE%

EXIT /b

:EXECUTE_FUNCTION
	CMD /c %* > NUL
	if %ERRORLEVEL% NEQ 0 (
		EXIT /b 0
	)
	EXIT /b 1
