@echo off
REM Batch file to start Next.js dev server on UNC paths
REM This uses pushd to map the UNC path to a drive letter

pushd "%~dp0"
call npm run dev
popd
