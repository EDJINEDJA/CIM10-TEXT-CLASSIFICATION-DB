initialize_git:
	@echo "initialization ..."
	git init
	sleep 2
	git add .
	sleep 2
	git commit -m "My first commit"
	sleep 2
	git branch -M main
	sleep 2
	git remote add origin https://github.com/EDJINEDJA/CIM10-TEXT-CLASSIFICATION-DB.git
	sleep 2
	git push -u origin main


pip_git:
	@echo "pushing ..."
	sleep 2
	git add .
	sleep 2
	git commit -m "commit"
	sleep 2
	git push -u origin main

pull_git:
	@echo "pulling back ..."
	sleep 2
	git pull origin main



setup: initialize_git
run: pip_git
