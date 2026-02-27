@echo off
setlocal
set DIR=%~dp0
set JAVA_EXE=java.exe
if defined JAVA_HOME if exist "%JAVA_HOME%\bin\java.exe" set JAVA_EXE=%JAVA_HOME%\bin\java.exe
set CLASSPATH=%DIR%\gradle\wrapper\gradle-wrapper.jar
"%JAVA_EXE%" -classpath "%CLASSPATH%" org.gradle.wrapper.GradleWrapperMain %*
endlocal
