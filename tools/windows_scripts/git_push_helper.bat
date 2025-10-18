@echo off
echo Changing to project directory...
cd /d "O:\Foundups-Agent"

echo Current directory:
cd

echo Git status:
git status --short

echo Adding all changes...
git add .

echo Creating commit...
git commit -m "Critical architectural clarification: FoundUps Cubes vs Enterprise Modules - WSP compliance achieved"

echo Pushing to remote...
git push

echo Done!
pause