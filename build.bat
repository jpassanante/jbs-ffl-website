@echo off
REM Batch file to build Next.js project on UNC paths
REM This uses pushd to map the UNC path to a drive letter

pushd "%~dp0"
call npm run build
popd
