STOW ?= xstow
.PHONY: stow
stow:
	ls -d */ | sed 's/\/$$//' | xargs $(STOW)
