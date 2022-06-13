alias package-search="toolbox run sudo dnf search"
alias .="source"

if test -e /run/.toolboxenv
then
  alias ls="exa"
  alias ll="exa -l"
  alias cat="bat"
fi
