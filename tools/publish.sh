#!/bin/zsh
# First publication of a site folder to its own GitHub Pages repo, in small pushes
# (a single large push returns HTTP 408 on this connection).
#   tools/publish.sh site-v2 cobalt-creation-site-v2 "V2 « Maison »"
set -e
dir=$1; repo=$2; label=$3
G=(git -c user.name=TimoteoAdrogue -c user.email=Teo@elysium.cc)
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>'
cd $dir
[ -d .git ] || git init -q -b main
step() { # message, then pathspecs
  local msg=$1; shift
  $G add -- "$@"
  if ! git diff --cached --quiet; then $G commit -q -m "$msg$TRAILER"; git push -q -u origin main; echo "pushed: $msg"; fi
}
if ! git remote get-url origin >/dev/null 2>&1; then
  gh repo create TimoteoAdrogue/$repo --public --description "Cobalt Création, $label (staging, noindex)" >/dev/null
  git remote add origin https://github.com/TimoteoAdrogue/$repo.git
fi
step "$label : pages, styles, scripts, polices, données" ':!assets/media' .
step "$label : logos, vidéo d'atelier, icônes" 'assets/media/*.png' 'assets/media/*.mp4' 'assets/media/logos'
step "$label : images AVIF" 'assets/media/*.avif'
jpgs=(assets/media/*.jpg); half=$(( ${#jpgs} / 2 ))
step "$label : images JPEG (1/2)" ${jpgs[1,$half]}
step "$label : images JPEG (2/2)" ${jpgs[$((half+1)),-1]}
step "$label : book PDF" 'assets/media/*.pdf'
git status --short | head
