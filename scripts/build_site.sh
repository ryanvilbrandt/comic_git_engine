echo "Install dependencies"
pip install -r comic_git_engine/scripts/requirements.txt
python comic_git_engine/scripts/make_requirements_hooks_file.py
pip install -r comic_git_engine/scripts/requirements_hooks.txt

echo "Run python build script"
export GITHUB_REPOSITORY=$1
echo "GITHUB_REPOSITORY: $GITHUB_REPOSITORY"
python comic_git_engine/scripts/build_site.py --delete-scheduled-posts
python_exit_code=$?
echo "python script exit code: $python_exit_code"
if [ $python_exit_code -ne 0 ]; then
  exit $python_exit_code
fi

echo "Commit files"
git config --local user.name "Github Action"
git config --local user.email "action@github.com"
git add --all
git diff-index --quiet HEAD || git commit -m "Auto-build"

echo "Push changes"
git push -f --set-upstream origin master
