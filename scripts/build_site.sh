echo "Checkout the correct comic_git_engine branch"
ENGINE_VERSION=$(sed -n 's/Engine version = \(.*\)/\1/p' your_content/comic_info.ini)
echo "Engine version: $ENGINE_VERSION"
cd comic_git_engine
git checkout "$ENGINE_VERSION"
cd ..

echo "Install dependencies"
pip install -r comic_git_engine/scripts/requirements.txt
python comic_git_engine/scripts/make_requirements_hooks_file.py
pip install -r comic_git_engine/scripts/requirements_hooks.txt

echo "Run python build script"
echo "GITHUB_REPOSITORY: $1"
export GITHUB_REPOSITORY=$1
echo "GITHUB_REPOSITORY: $GITHUB_REPOSITORY"
python comic_git_engine/scripts/build_site.py --delete-scheduled-posts

echo "Commit files"
git config --local user.name "Github Action"
git config --local user.email "action@github.com"
git add --all
git diff-index --quiet HEAD || git commit -m "Auto-build"

echo "Push changes"
git push -f --set-upstream origin master
